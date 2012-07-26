from collections import namedtuple
from struct import Struct

from abilities import abilities
from common import decode_name, types

class Pokemon:
    struct = Struct('<11sB6LQL')

    def __init__(self, raw_struct):
        """Parse everything."""

        info = iter(self.struct.unpack(raw_struct))

        # Name
        self.name = decode_name(next(info))

        # Mystery — generally lower for higher evolutions
        self.mystery_1 = next(info)

        # HP, evolution conditions, stuff
        group = next(info)
        def evo_condition(condition):
            return None if condition == 0b1001 else condition
        self.stat_hp = group & 0x1FF
        self.evo_condition_1 = evo_condition(group >> 10 & 0xF)
        self.evo_condition_2 = evo_condition(group >> 14 & 0xF)
        self.attack_animation_probably = group >> 18 & 0xF
        self.mystery_2 = group >> 23

        # The rest of the stats, mystery flags
        group = next(info)
        for stat in ('stat_attack', 'stat_defense', 'stat_speed'):
            setattr(self, stat, group & 0x1FF)
            group >>= 10
        self.is_legendary = bool(group & 1)
        self.mystery_flag_1 = bool(group >> 1)

        # Types, move
        group = next(info)
        self.type_1 = types[group & 0x1F]
        try:
            self.type_2 = types[group >> 5 & 0x1F]
        except IndexError:
            self.type_2 = None

        self.move = group >> 10 & 0x7F

        # Abilities
        group = next(info)
        self.abilities = []
        for ability in range(3):
            if group & 0x80:
                break

            self.abilities.append(abilities[group & 0x7F])
            group >>= 9

        # Evolution, range, another mystery flag
        group = next(info)
        self.evo_parameter_1 = (None if self.evo_condition_1 is None
                                else group & 0x1FF)
        self.evo_parameter_2 = (None if self.evo_condition_2 is None
                                else group >> 18 & 0x1FF)
        self.range = group >> 27 & 0b111
        self.mystery_flag_2 = bool(group >> 31)

        # Evolved forms, national dex number
        group = next(info)
        evo = group & 0x7FF
        self.first_evolution = None if evo == 1400 else evo + 1
        evo = group >> 11 & 0x7FF
        self.last_evolution = None if evo == 1400 else evo + 1
        self.national_id = group >> 22

        # Habitat — this is the quad
        group = next(info)
        habitat = []
        for kingdom in range(17):
            habitat.append((bool(group & 0b01), bool(group & 0b10)))
            group >>= 3
        self.habitat = habitat

        # Alphabetical order
        self.alphabetical_order = next(info)

pokemon = []

with open('/tmp/conquest/fsroot/data/Pokemon.dat', 'rb') as pokemon_data:
    for single_pokemon in range(200):
        # Read all the Pokémon
        single_pokemon = pokemon_data.read(0x30)
        single_pokemon = Pokemon(single_pokemon)
        pokemon.append(single_pokemon)

if __name__ == '__main__':
    for single_pokemon in pokemon:
        print(single_pokemon.__dict__, end='\n\n')
