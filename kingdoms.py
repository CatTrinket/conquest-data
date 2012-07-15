from struct import Struct

from common import decode_name, types

class Kingdom:
    struct = Struct('<11s13s')
    types = iter(types)

    def __init__(self, raw_struct):
        """Parse everything.  Sort of."""

        self.name, self.mystery = self.struct.unpack(raw_struct)
        self.name = decode_name(self.name)
        self.type = next(self.types)


kingdoms = []

with open('/tmp/conquest/fsroot/data/Kuni.dat', 'rb') as kingdom_data:
    for kingdom in range(17):
        kingdoms.append(Kingdom(kingdom_data.read(0x18)))

if __name__ == '__main__':
    from binascii import hexlify
    for kingdom in kingdoms:
        print('{0:11} {1}'.format(kingdom.name,
          hexlify(kingdom.mystery).decode('ASCII')))
