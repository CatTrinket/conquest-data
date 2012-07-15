from struct import Struct

class Kingdom:
    struct = Struct('<11s13s')

    # XXX Figure out where type names are, ideally
    types = {
        'Aurora': 'normal',
        'Avia': 'flying',
        'Chrysalia': 'bug',
        'Cragspur': 'rock',
        'Dragnor': 'dragon',
        'Fontaine': 'water',
        'Greenleaf': 'grass',
        'Ignis': 'fire',
        'Illusio': 'psychic',
        'Nixtorm': 'ice',
        'Pugilis': 'fighting',
        'Spectra': 'ghost',
        'Terrera': 'ground',
        'Valora': 'steel',
        'Violight': 'electric',
        'Viperia': 'poison',
        'Yaksha': 'dark'
    }

    def __init__(self, raw_struct):
        """Parse everything."""

        self.name, self.mystery = self.struct.unpack(raw_struct)
        self.name = self.name.decode('Shift_JIS').rstrip('\x00')
        self.type = self.types[self.name]


kingdoms = []

with open('/tmp/conquest/fsroot/data/Kuni.dat', 'rb') as kingdom_data:
    for kingdom in range(17):
        kingdoms.append(Kingdom(kingdom_data.read(0x18)))

if __name__ == '__main__':
    from binascii import hexlify
    for kingdom in kingdoms:
        print('{0:11} {1}'.format(kingdom.name,
          hexlify(kingdom.mystery).decode('ASCII')))
