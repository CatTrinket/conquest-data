from struct import Struct

from common import decode_name, types

class Kingdom:
    struct = Struct('<11sB3L')

    def __init__(self, raw_struct):
        """Parse everything.  Sort of."""

        data = iter(self.struct.unpack(raw_struct))

        self.name = decode_name(next(data))
        self.mystery_1 = next(data)
        self.mystery_2 = next(data)
        self.mystery_3 = next(data)

        # Type, and some mystery
        group = next(data)
        self.mystery_4 = group & 0x7FFF
        self.type = types[group >> 15 & 0x1F]
        self.mystery_5 = group >> 20


kingdoms = []

with open('/tmp/conquest/fsroot/data/Kuni.dat', 'rb') as kingdom_data:
    for kingdom in range(17):
        kingdoms.append(Kingdom(kingdom_data.read(0x18)))

if __name__ == '__main__':
    template = ('{name:11} {mystery_1:08b} {mystery_2:032b} {mystery_3:032b} '
                '{mystery_5:012b} {type:8} {mystery_4:015b}')

    for kingdom in kingdoms:
        print(template.format(**kingdom.__dict__))
