#!/usr/bin/env python3

import random
import re
import sys


MIN_SIZE = 4
MAX_SIZE = 24
MINE_RATIO = 0.2

MINE_FLAG = 0x80
HIDE_FLAG = 0x40
MARK_FLAG = 0x20
UNK_FLAG = 0x10

OPT_FLAGS = (MARK_FLAG | UNK_FLAG)
DEAD_FLAGS = OPT_FLAGS

COORD_RE = re.compile(r"^([#\?])?\s*([a-z])\s*[,.:]?\s*([a-z])$",
                      re.IGNORECASE)


def print_help():
    print("""\
x,y  - Clear cell at coordinates (x,y)
         (ignored if cell cleared or marked with flag)
x,y  - Clear neighbours of numbered cell (x,y)
         (ignored if number does not equal total of all neighbouring '#' flags)
#x,y - Set '#' flag, change to '?' flag, or remove all flags on cell (x,y)
         (ignored if cell already cleared)
?x,y - Set uncertain flag '?' or remove all flags on cell (x,y)
         (ignored if cell already cleared)
h    - Print this help message
q    - Quit""")

    return


def print_usage():
    print("Usage: {:s} [size {:d}-{:d}]\n".format(sys.argv[0],
                                                  MIN_SIZE, MAX_SIZE))
    sys.exit(0)


def check_size(size):
    if size < MIN_SIZE or size > MAX_SIZE:
        raise ValueError

    return size


def read_size():
    while True:
        try:
            size = int(input("Enter grid dimension "
                             "({:d}-{:d}): ".format(MIN_SIZE, MAX_SIZE)))
        except ValueError:
            size = 0

        try:
            check_size(size)
            break
        except ValueError:
            print("Not a valid size")

    return size


def min_adjc(v):
    return max(v - 1, 0)


def max_adjc(v, size):
    return min(v + 2, size)


def range_adjc(v, size):
    return range(min_adjc(v), max_adjc(v, size))


def list_adjc(size, x, y):
    return [(i, j) for i in range_adjc(x, size) for j in range_adjc(y, size)]


def calc_cell(size, minefield, x, y):
    return sum(minefield[i][j] & MINE_FLAG > 0
               for (i, j) in list_adjc(size, x, y))


def calc_field(size, minefield):
    for x in range(size):
        for y in range(size):
            if not minefield[x][y] & MINE_FLAG:
                minefield[x][y] |= calc_cell(size, minefield, x, y)

    return


def seed_cell(size, minefield, test=None):
    while True:
        x = random.randrange(size)
        y = random.randrange(size)
        if not minefield[x][y] & MINE_FLAG and \
                (test is None or not test(x, y)):
            minefield[x][y] |= MINE_FLAG
            break

    return


def seed_field(size, num_mines):
    minefield = [[HIDE_FLAG for x in range(size)] for y in range(size)]

    for i in range(num_mines):
        seed_cell(size, minefield)

    return minefield


def empty_cells(size, minefield, x, y):
    test = lambda a, b :     min_adjc(x) <= a < max_adjc(x, size) \
                         and min_adjc(y) <= b < max_adjc(y, size)

    for (i, j) in list_adjc(size, x, y):
        if minefield[i][j] & MINE_FLAG:
            seed_cell(size, minefield, test)
            minefield[i][j] &= ~MINE_FLAG

    return


def get_coord(c, size):
    i = ord(c) - 97

    if i < 0 or i >= size:
        raise ValueError

    return i


def read_coords(size):
    while True:
        line = input("Enter grid coordinates ([#?]x,y): ").strip().lower()
        if line == "h":
            print_help()
            continue
        elif line == "q":
            sys.exit(0)

        coords_match = COORD_RE.match(line)
        if coords_match is not None:
            try:
                coords_groups = list(coords_match.groups())
                if len(coords_groups) == 3:
                    req_flags = MARK_FLAG if coords_groups[0] == "#" else \
                        (UNK_FLAG if coords_groups[0] == "?" else 0)
                    coords_groups.pop(0)
                coords = (get_coord(coords_groups[1], size),
                          get_coord(coords_groups[0], size))
                break
            except ValueError:
                print("Coordinate out of range (A-{:c})".format(size + 64))
        else:
            print("Invalid coordinate format")

    return (coords, req_flags)


def format_cell(val, showall):
    if val == 0:
        fmt = " "
    elif val < 9:
        fmt = str(val)
    elif showall:
        if val & MINE_FLAG:
            if (val & DEAD_FLAGS) == DEAD_FLAGS:
                fmt = "X"
            elif val & MARK_FLAG:
                fmt = "#"
            else:
                fmt = "*"
        elif val & MARK_FLAG:
            fmt = "x"
        else:
            fmt = "."
    else:
        assert val & HIDE_FLAG
        if val & MARK_FLAG:
            fmt = "#"
        elif val & UNK_FLAG:
            fmt = "?"
        else:
            fmt = "."

    return fmt


def print_field(size, minefield, show = False):
    print("  " + " ".join([chr(x + 65) for x in range(size)]))
    ## print array with outer (x) coord on vertical axis; then flip user input
    for x in range(size):
        print(chr(x + 65) + " " +
              " ".join([format_cell(c, show) for c in minefield[x]]))


def mark_cell(val, req_flags):
    curr_flags = val & OPT_FLAGS

    if req_flags & MARK_FLAG:
        if curr_flags == 0:
            new_flags = MARK_FLAG
        elif curr_flags & MARK_FLAG:
            new_flags = UNK_FLAG
        else:
            new_flags = 0
    else:
        assert req_flags & UNK_FLAG
        new_flags = (curr_flags & UNK_FLAG) ^ UNK_FLAG

    return (val & ~OPT_FLAGS) | new_flags


def count_marks(size, minefield, x, y):
    return sum(minefield[i][j] & MARK_FLAG > 0
               for (i, j) in list_adjc(size, x, y)
               if minefield[i][j] & OPT_FLAGS)


def clear_cell(size, minefield, x, y):
    if not minefield[x][y] & HIDE_FLAG or minefield[x][y] & OPT_FLAGS:
        return (0, False)

    minefield[x][y] &= ~HIDE_FLAG
    n = 1

    dead = minefield[x][y] & MINE_FLAG > 0
    if dead:
        minefield[x][y] |= DEAD_FLAGS

    if not dead and minefield[x][y] == 0:
        (num_cleared, dead) = clear_cells(size, minefield, x, y)
        n += num_cleared

    return (n, dead)


def clear_cells(size, minefield, x, y):
    n = 0
    dead = False
    for (i, j) in list_adjc(size, x, y):
        (num_cleared, is_dead) = clear_cell(size, minefield, i, j)
        n += num_cleared
        dead = is_dead or dead

    return (n, dead)

    ## NOTE: fancier, but is harder to comprehend and just feels less elegant
    ##    l = [clear_cell(size, minefield, i, j)
    ##         for (i, j) in list_adjc(size, x, y)]
    ##    if not l:
    ##        l = [(0, False)]
    ##    s = [sum(p) for p in zip(*l)]
    ##    return (s[0], s[1] > 0)


## main program

if len(sys.argv) > 2:
    print_usage()

if len(sys.argv) == 2:
    try:
        size = check_size(int(sys.argv[1]))
    except ValueError:
        print_usage()
else:
    size = read_size()

num_cells = size ** 2
num_mines = int(num_cells * MINE_RATIO)
num_to_clear = num_cells - num_mines

random.seed()

minefield = seed_field(size, num_mines)

first = True
dead = False
num_clear = 0
while not dead and num_clear < num_to_clear:
    print_field(size, minefield)

    ((x, y), req_flags) = read_coords(size)

    if first:
        ## move all mines out of neighbourhood of first guess
        empty_cells(size, minefield, x, y)
        calc_field(size, minefield)
        first = False

    if minefield[x][y] & HIDE_FLAG:
        if req_flags > 0:
            minefield[x][y] = mark_cell(minefield[x][y], req_flags)
        else:
            (num_cleared, dead) = clear_cell(size, minefield, x, y)
            num_clear += num_cleared
    elif req_flags == 0 and minefield[x][y] > 0:
        assert minefield[x][y] < 9
        ## emulate a middle-click clearing action
        if minefield[x][y] == count_marks(size, minefield, x, y):
            (num_cleared, dead) = clear_cells(size, minefield, x, y)
            num_clear += num_cleared

print_field(size, minefield, True)

if dead:
    print("Sorry, try again!")
else:
    print("Congratulations!")

sys.exit(0)


#### References
## https://docs.python.org/3/tutorial/datastructures.html
## https://docs.python.org/3/tutorial/controlflow.html
## https://docs.python.org/3/tutorial/controlflow.html#unpacking-argument-lists
## https://docs.python.org/3/reference/expressions.html
## https://docs.python.org/3/library/functions.html
## https://docs.python.org/3/library/re.html
## https://docs.python.org/3/howto/regex.html
## https://docs.python.org/3/tutorial/errors.html
## https://docs.python.org/3.5/library/string.html#formatspec

