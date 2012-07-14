from collections import namedtuple
from struct import unpack

from abilities import abilities

# I KNOW this is brickish but I really don't like working with construct.
Pokemon = namedtuple('Pokemon', [
  'name', 'mystery_1', 'stat_hp', 'evo_condition_1', 'evo_condition_2',
  'attack_animation_probably', 'mystery_2', 'stat_attack', 'stat_defense',
  'stat_speed', 'is_legendary', 'mystery_flag_1', 'type_1', 'type_2',
  'move', 'ability_1', 'ability_2', 'ability_3', 'evo_parameter_1',
  'evo_parameter_2', 'range', 'mystery_flag_2', 'first_evolution',
  'last_evolution', 'national_dex_no', 'habitat', 'alphabetical_order'
])

def pokemon_parser(pokemon_struct):
    """Parse a Pokémon's data and yield it all as tuples for keyword assignment
    to build a Pokemon.

    This way, if anything gets mixed up, which is quite likely given that we're
    putting together a brick in the form of a namedtuple, things won't silently
    silently go wrong, and it's clear which value is being yielded.
    """

    info = iter(unpack('<11sB6LQL', pokemon_struct))

    # Name
    yield ('name', next(info).decode('Shift_JIS').rstrip('\x00'))

    # Mystery — generally lower for higher evolutions
    yield ('mystery_1', next(info))

    # HP, evolution conditions, stuff
    group = next(info)
    def evo_condition(condition):
        return None if condition == 0b1001 else condition
    yield ('stat_hp', group & 0x1FF)
    yield ('evo_condition_1', evo_condition(group >> 10 & 0xF))
    yield ('evo_condition_2', evo_condition(group >> 14 & 0xF))
    yield ('attack_animation_probably', group >> 18 & 0xF)
    yield ('mystery_2', group >> 23)

    # The rest of the stats, mystery flags
    group = next(info)
    for stat in ('stat_attack', 'stat_defense', 'stat_speed'):
        yield (stat, group & 0x1FF)
        group >>= 10
    yield ('is_legendary', bool(group & 1))
    yield ('mystery_flag_1', bool(group >> 1))

    # Types, move
    group = next(info)
    yield ('type_1', group & 0x1F)

    type_2 = group >> 5 & 0x1F
    if type_2 == 0b11111:
        type_2 = None
    yield ('type_2', type_2)

    yield ('move', group >> 10 & 0x7F)

    # Abilities
    group = next(info)
    for ability in range(1, 4):
        ability = 'ability_{0}'.format(ability)
        if group & 0x80:
            yield (ability, None)
        else:
            yield (ability, abilities[group & 0x7F])
        group >>= 9
    assert group == 0b01010

    # Evolution, range, another mystery flag
    group = next(info)
    yield ('evo_parameter_1', group & 0x1FF)
    yield ('evo_parameter_2', group >> 18 & 0x1FF)
    yield ('range', group >> 27 & 0b111)
    yield ('mystery_flag_2', bool(group >> 31))

    # Evolved forms, national dex number
    group = next(info)
    evo = group & 0x7FF
    yield ('first_evolution', None if evo == 1400 else evo + 1)
    evo = group >> 11 & 0x7FF
    yield ('last_evolution', None if evo == 1400 else evo + 1)
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

pokemon = []

with open('/tmp/conquest/fsroot/data/Pokemon.dat', 'rb') as pokemon_data:
    for single_pokemon in range(200):
        # Read each Pokémon's data, parse it, and package it
        single_pokemon = pokemon_data.read(0x30)
        single_pokemon = pokemon_parser(single_pokemon)
        single_pokemon = dict(single_pokemon)
        single_pokemon = Pokemon(**single_pokemon)
        pokemon.append(single_pokemon)

if __name__ == '__main__':
    for single_pokemon in pokemon:
        print(single_pokemon, end='\n\n')
