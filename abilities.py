abilities = open('/tmp/conquest/fsroot/data/Tokusei.dat', 'rb')
pokemons = open('/tmp/conquest/fsroot/data/Pokemon.dat', 'rb')

ability_names = []
while True:
    ability = abilities.read(20)
    if not ability:
        break

    ability_names.append(ability[:15].rstrip(b'\x00').decode('ASCII'))

while True:
    pokemon = pokemons.read(0x30)
    if not pokemon:
        break

    name = pokemon[:11].rstrip(b'\x00').decode('ASCII')

    pokemon_abilities = (pokemon[24], pokemon[25] >> 1,
        pokemon[26] >> 2 | (pokemon[27] & 1) << 6)
    print('{0:10}: {1}'.format(name, ', '.join(ability_names[a] for a in
                                               pokemon_abilities)))
