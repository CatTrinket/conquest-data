from struct import unpack

from stuff import types, format_str

def star_rating(num):
    if num > 50:
        return 5
    elif num > 40:
        return 4
    elif num > 30:
        return 3
    elif num > 20:
        return 2
    elif num > 0:
        return 1
    else:
        return 0

class Move():
    """A move."""
    
    def __init__(self, bytes):
        """Parse stuff."""
        
        data = unpack("<15sB5L", bytes)
        data = iter(data)
        
        # Name
        group = next(data)
        self.name = format_str(group)
        
        # Movement - separate for some reason
        group = next(data)
        self.movement_1 = group
        
        # Range, effects, power, type
        group = next(data)
        self.range = group >> 27
        self.parameter = group >> 20 & 0x7F
        self.effect_1_flag = not bool(group >> 19 & 1)
        self.effect_1 = group >> 13 & 0x3F
        self.power = group >> 5 & 0xFF
        self.type = types[group & 0x1F]
        
        # Animation, mysteries
        group = next(data)
        self.animation = group >> 18 & 0xFF
        self.mystery_1 = group >> 9 & 0xFF
        self.mystery_2 = group & 0xFF
        
        # Effects
        group = next(data)
        self.effect_2_flag = not bool(group >> 6 & 1)
        self.effect_2 = group & 0x3F
        
        # Movement, mysteries, accuracy
        group = next(data)
        self.movement_2 = group >> 30
        self.mystery_3 = group >> 27 & 0b111 # contact is in here
        self.mystery_flag = bool(group >> 26 & 1) # probably part of mystery_3
        self.accuracy = group >> 19 & 0x7F
        self.mystery_4 = group >> 7 & 0x3F
        self.mystery_5 = group & 0x3F
        
        # No clue
        group = next(data)
        self.mystery_6 = group >> 18 & 0x3F
        self.mystery_7 = group >> 10 & 0x7F
        self.mystery_8 = group & 0x7F # ascending for x-range moves

squares = [
    [" ", 2, 6, 5, " "],
    [8, 7, 22, 21, 20],
    [9, 23, 30, 29, 19],
    [10, 24, "P", 28, 18],
    [11, 25, 26, 27, 17],
    [12, 13, 14, 15, 16],
    [" ", 1, 3, 4, " "]
]

def draw_range(bits, blank=" "):
    """Map bits to a grid and print it."""
    
    grid = [row[:] for row in squares]
    bits = "{0:032b}".format(bits)
    
    for i, char in enumerate(bits):
        if 0 < i < 31:
            
            # Find the correct cell
            x = 0
            y = 0
            for n, row in enumerate(squares):
                if i in row:
                    x = row.index(i)
                    y = n
                    break
            
            if char == "1":
                grid[y][x] = char
            else:
                grid[y][x] = blank
    
    for row in grid[:-2]:
        print " ".join(str(n) for n in row[1:-1])

ranges = []
with open("Conquest/WazaRange.dat", 'rb') as range_data:
    for _range in range(22):
        data, = unpack("<L", range_data.read(4))
        ranges.append(data)

moves = []
with open("Conquest/Waza.dat", 'rb') as move_data:
    for move in range(143):
        move = Move(move_data.read(36))
        moves.append(move)

if __name__ == "__main__":
    effects = set(move.effect_1 for move in moves) | set(move.effect_2 for move in moves)
    for effect in effects:
        print "{0:2}: {1}".format(
            effect,
            ", ".join(move.name for move in moves
                      if ((move.effect_1_flag and move.effect_1 == effect)
                          or (move.effect_2_flag and move.effect_2 == effect))
                      and "dummy" not in move.name)
        )
