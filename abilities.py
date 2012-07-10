from collections import namedtuple
from struct import unpack

_Ability = namedtuple('ability', ['name', 'mystery'])

abilities = []

with open('/tmp/conquest/fsroot/data/Tokusei.dat', 'rb') as ability_data:
    for ability in range(128):
        name, mystery = unpack('15s5s', ability_data.read(20))
        name = name.decode('Shift_JIS').rstrip('\x00')
        abilities.append(_Ability(name, mystery))

if __name__ == '__main__':
    for n, ability in enumerate(abilities):
        print('{0:3}. {1}'.format(n, ability.name))
