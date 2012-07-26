from struct import Struct

from common import decode_name, types
from pokemon import pokemon

class Warrior():
    struct = Struct('<5L')

    def __init__(self, raw_struct):
        data = self.struct.unpack(raw_struct)
        data = iter(data)

        # Link percentage to evolve, name, gender, mystery indexes
        group = next(data)
        self.sprite_id_maybe = int(group & 0xFF)
        self.dialogue_id_maybe = int(group >> 8 & 0xFF)
        self.gender = genders[group >> 16 & 1]
        self.name = names[group >> 17 & 0xFF]
        self.evo_link_percent = int(group >> 25)

        # Mystery bytes, specialties
        group = next(data)

        self.types = [types[group & 0x1F]]
        try:
            self.types.append(types[group >> 5 & 0x1F])
        except IndexError:
            pass

        self.mystery_types = [types[group >> 10 & 0x1F]]
        try:
            self.mystery_types.append(types[group >> 15 & 0x1F])
        except IndexError:
            pass

        self.evo_parameter_1a = group >> 20 & 0x1FF
        if self.evo_parameter_1a == 0x1FF:
            self.evo_parameter_1a = None
        else:
            self.evo_parameter_1a = pokemon[self.evo_parameter_1a]

        # Skills and evolution conditions
        group = next(data)

        self.skill = warrior_skills[group & 0x7F]

        self.mystery_4 = group >> 7 & 0xFF

        self.next_rank = group >> 15 & 0xFF

        self.evo_condition_1 = group >> 24 & 0xF
        if self.evo_condition_1 == 0b1101:
            self.evo_condition_1 = None

        self.evo_condition_2 = group >> 28
        if self.evo_condition_2 == 0b1101:
            self.evo_condition_2 = None

        # Stats
        group = next(data)
        self.power = group & 0x7F
        self.wisdom = group >> 7 & 0x7F
        self.charisma = group >> 14 & 0x7F
        self.capacity = group >> 21 & 0xF
        self.mystery_5 = group >> 25

        # Evolution parameters
        group = next(data)

        try:
            self.evo_parameter_1b = pokemon[group & 0x1FF]
        except IndexError:
            self.evo_parameter_1b = self.evo_parameter_1a

        self.evo_parameter_2a = group >> 9 & 0x1FF
        if self.evo_parameter_2a == 0x1FF:
            self.evo_parameter_2a = None

        self.evo_parameter_2b = group >> 18 & 0x1FF
        if self.evo_parameter_2b == 0x1FF:
            self.evo_parameter_2b = None

class WarriorSkill:
    struct = Struct('19s9s')

    def __init__(self, raw_struct):
        self.name, self.mystery = self.struct.unpack(raw_struct)
        self.name = decode_name(self.name)

genders = ["male", "female"]

with open('/tmp/conquest/fsroot/data/Saihai.dat', 'rb') as skill_data:
    warrior_skills = []
    for warrior_skill in range(73):
        warrior_skills.append(WarriorSkill(skill_data.read(28)))

with open('/tmp/conquest/fsroot/data/BaseBushou.dat', 'rb') as warrior_data:
    warrior_data.seek(5040)
    name_struct = Struct('11s1x')

    names = []
    for name in range(210):
        name, = name_struct.unpack(warrior_data.read(12))
        name = decode_name(name)
        names.append(name)

    warrior_data.seek(0)

    warriors = []
    for warrior in range(252):
        warrior = Warrior(warrior_data.read(20))
        warriors.append(warrior)

    warrior_id = []
    for warrior in warriors:
        if warrior.name not in warrior_id:
            warrior_id.append(warrior.name)

with open('/tmp/conquest/fsroot/data/BaseBushouMaxSyncTable.dat', 'rb') as link_data:
    for warrior in warriors:
        warrior.max_links = dict(zip(pokemon, link_data.read(200)))

with open('/tmp/conquest/fsroot/data/Episode.dat', 'rb') as episode_data:
    episode_struct = Struct('B7x')

    episodes = []
    for episode in range(38):
        episode, = episode_struct.unpack(episode_data.read(8))
        episode = warrior_id[episode]
        episodes.append(episode)

if __name__ == "__main__":
    template = ('{n:3} {name:11}  '
      '{mystery_4:08b}  {mystery_5:07b}')

    for n, warrior in enumerate(warriors):
        try:
            print(template.format(n=n, **warrior.__dict__))
        except AttributeError:
            pass
