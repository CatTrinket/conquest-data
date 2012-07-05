from struct import unpack

def parse_abilities(abilities):
    return [
        abilities & 0x7f,
        abilities >> 9 & 0x7f,
        abilities >> 18 & 0x7f
    ]

ability_data = open('/tmp/conquest/fsroot/data/Tokusei.dat', 'rb')
pokemon_data = open('/tmp/conquest/fsroot/data/Pokemon.dat', 'rb')

ability_names = []
for ability in range(128):
    name, = unpack('15s5x', ability_data.read(20))
    ability_names.append(name.rstrip(b'\x00').decode('ASCII'))

for pokemon in range(200):
    name, abilities = unpack('<11s13xL20x', pokemon_data.read(0x30))
    name = name.rstrip(b'\x00').decode('ASCII')
    abilities = [ability_names[a] for a in parse_abilities(abilities)]

    print('{0:10}: {1}'.format(name, ', '.join(abilities)))
