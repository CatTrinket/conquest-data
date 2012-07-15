from struct import Struct

class Item:
    struct = Struct('<21s15s')

    def __init__(self, raw_struct):
        self.name, self.mystery = self.struct.unpack(raw_struct)
        self.name = self.name.decode('Shift_JIS').rstrip('\x00')

items = []

with open('/tmp/conquest/fsroot/data/Item.dat', 'rb') as item_data:
    for item in range(134):
        items.append(Item(item_data.read(0x24)))

if __name__ == '__main__':
    from binascii import hexlify
    for item in items:
        print('{0:21} {1}'.format(item.name,
          hexlify(item.mystery).decode('ASCII')))
