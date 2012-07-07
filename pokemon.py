from collections import OrderedDict
from struct import unpack

def pokemon_parser(pokemon_struct):
    info = iter(unpack('<11sB6LQL', pokemon_struct))

    # Name
    yield ('name', next(info).decode('Shift_JIS').rstrip('\x00'))

    # Mystery — generally lower for higher evolutions
    yield ('mystery_1', next(info))

    # HP, evolution conditions, stuff
    group = next(info)
    def evo_condition(condition):
        return None if condition == 0b1001 else condition
    yield ('stat_hp', group & 0x1ff)
    yield ('evo_condition_1', evo_condition(group >> 10 & 0xf))
    yield ('evo_condition_2', evo_condition(group >> 14 & 0xf))
    yield ('attack_animation_probably', group >> 18 & 0xf)
    yield ('mystery_2', group >> 23)

    # The rest of the stats, mystery flags
    group = next(info)
    for stat in ('stat_attack', 'stat_defense', 'stat_speed'):
        yield (stat, group & 0x1ff)
        group >>= 10
    yield ('is_legendary', bool(group & 1))
    yield ('mystery_flag_1', bool(group >> 1))

    # Types, move
    group = next(info)
    yield ('type_1', group & 0x1f)

    type_2 = group >> 5 & 0x1f
    if type_2 == 0b11111:
        type_2 = None
    yield ('type_2', type_2)

    yield ('move', group >> 10 & 0x7f)

    # Abilities
    group = next(info)
    for ability in range(1, 4):
        yield ('ability_{0}'.format(ability), group & 0x7f)
        yield ('ability_{0}_is_placeholder'.format(ability),
               bool(group & 0x80))
        group >>= 9
    assert group == 0b01010

    # Evolution, range, another mystery flag
    group = next(info)
    yield ('evo_parameter_1', group & 0x1ff)
    yield ('evo_parameter_2', group >> 18 & 0x1ff)
    yield ('range', group >> 27 & 0b111)
    yield ('mystery_flag_2', bool(group >> 31))

    # Evolved forms, national dex number
    group = next(info)
    yield ('first_evolution', (group & 0x7ff) + 1)
    yield ('last_evolution', (group >> 11 & 0x7ff) + 1)
    yield ('national_dex_no', group >> 22)

    # Habitat — this is the quad
    group = next(info)
    habitat = []
    for kingdom in range(17):
        habitat.append((bool(group & 0b01), bool(group & 0b10)))
        group >>= 3
    yield ('habitat', habitat)

    # Alphabetical order
    yield ('alphabetical_order', next(info))

ability_data = open('/tmp/conquest/fsroot/data/Tokusei.dat', 'rb')
pokemon_data = open('/tmp/conquest/fsroot/data/Pokemon.dat', 'rb')

ability_names = []
for ability in range(128):
    name, = unpack('15s5x', ability_data.read(20))
    ability_names.append(name.rstrip(b'\x00').decode('ASCII'))

for pokemon in range(200):
    pokemon = OrderedDict(pokemon_parser(pokemon_data.read(0x30)))
    print(pokemon)
