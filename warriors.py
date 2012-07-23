from struct import unpack

from common import decode_name, types
from pokemon import pokemon

class Warrior():
    def __init__(self, bytes):
        data = unpack("<5L", bytes)
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

        self.type_1 = types[group & 0x1F]
        try:
            self.type_2 = types[group >> 5 & 0x1F]
        except IndexError:
            self.type_2 = None

        self.mystery_1 = group >> 10 & 0x1F
        self.mystery_2 = group >> 15 & 0x1F

        self.evo_parameter_1 = group >> 20 & 0x1FF
        if self.evo_parameter_1 == 0x1FF:
            self.evo_parameter_1 = None
        else:
            self.evo_parameter_1 = pokemon[self.evo_parameter_1]

        self.mystery_3 = group >> 29

        # Skills and evolution conditions
        group = next(data)

        self.skill = skills[group & 0x7F]

        self.mystery_4 = group >> 7 & 0x1FFFF

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

        self.mystery_6 = group & 0x1FF

        self.evo_parameter_2 = group >> 9 & 0x1FF
        if self.evo_parameter_2 == 0x1FF:
            self.evo_parameter_2 = None

        self.mystery_7 = group >> 18

genders = ["male", "female"]

with open('/tmp/conquest/fsroot/data/Saihai.dat', 'rb') as skill_data:
    skills = []
    for skill in range(73):
        name, = unpack("19s9x", skill_data.read(28))
        name = decode_name(name)
        skills.append(name)

with open('/tmp/conquest/fsroot/data/BaseBushou.dat', 'rb') as warrior_data:
    warrior_data.seek(5040)

    names = []
    for name in range(210):
        name, = unpack("11s1x", warrior_data.read(12))
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

with open('/tmp/conquest/fsroot/data/Episode.dat', 'rb') as episode_data:
    episodes = []
    for episode in range(38):
        episode, = unpack("B7x", episode_data.read(8))
        episode = warrior_id[episode]
        episodes.append(episode)

if __name__ == "__main__":
    template = ('{n:3} {name:11}  '
      '{mystery_3:03b} {mystery_2:05b} {mystery_1:05b}  '
      '{mystery_4:017b}  {mystery_5:07b}  {mystery_7:014b} {mystery_6:09b}')

    for n, warrior in enumerate(warriors):
        print(template.format(n=n, **warrior.__dict__))
