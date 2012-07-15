def decode_name(name):
    name = name.decode('Shift_JIS')
    name = name.rstrip('\x00')
    name = name.translate(text_translation_table)
    return name

text_translation_table = str.maketrans({'ю': 'ō', 'п': 'ū'})

types = ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting',
  'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 'dragon',
  'dark', 'steel']
