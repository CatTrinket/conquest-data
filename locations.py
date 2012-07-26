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

class Area:
    """Any area within a kingdom, e.g. a shop or a wild Pokémon area."""

    struct = Struct('19s8sB2L')

    def __init__(self, raw_struct):
        data = iter(self.struct.unpack(raw_struct))

        self.name = decode_name(next(data))
        self.mystery_areas = next(data)
        self.kingdom = kingdoms[next(data)]
        self.mystery_1 = next(data)
        self.mystery_2 = next(data)


kingdoms = []

with open('/tmp/conquest/fsroot/data/Kuni.dat', 'rb') as kingdom_data:
    for kingdom in range(17):
        kingdoms.append(Kingdom(kingdom_data.read(0x18)))

areas = []

with open('/tmp/conquest/fsroot/data/Building.dat', 'rb') as area_data:
    for area in range(119):
        areas.append(Area(area_data.read(0x24)))

if __name__ == '__main__':
    template = '{kingdom.name:9} {name:19} {mystery_1:016b} {mystery_2:032b}'

    for area in areas:
        print(template.format(**area.__dict__),
          *('{0:14}'.format('—' if a == 0x77 else areas[a].name[:14])
            for a in area.mystery_areas),
          sep='  ')
