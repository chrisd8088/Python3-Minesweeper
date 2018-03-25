# Python 3 Minesweeper


## Command-Line Minesweeper in Python 3

In an effort to learn [Python](https://python.org), and
[Python 3](https://docs.python.org/3/) in particular, I took up
a suggestion to try writing a command-line version of
[Minesweeper](https://en.wikipedia.org/wiki/Microsoft_Minesweeper),
and here's the result.

I'm sure there are a number of ways it could be more Pythonic,
more efficient, and more elegant, but one has to start somewhere.

I chose to use a square grid, for simplicity, and on each turn
the player enters a grid coordinate in `x,y` format, where the horizontal
and vertical coordinates are both demarcated using letters
(e.g., `a`, `b`, `c`, etc.)

Cells can be marked with flags by preceding the coordinates
with either `#` or `?`.  Once flagged, a cell cannot be accidentally
cleared.

The `?` flag is intended to indicate you are uncertain
as to a cell's contents; this flag does not count when determining
the number of flagged neighbours of a numbered cell (see the notes
on [Middle-Clicking](#clearing-faster-with-middle-clicks) below).

Enter `q` to quit the game.  Enter `h` for a brief help message
summarizing the game command options.


## References

I used the excellent [KMines](https://www.kde.org/applications/games/kmines/)
as a reference, and also delved into the treasure trove of information
that is the [Strategy](http://www.minesweeper.info/wiki/Strategy) page
of the [Authoritative Minesweeper](http://minesweeper.info/)
[Wiki](http://www.minesweeper.info/wiki/Main_Page).


### Clearing Faster with Middle-Clicks

From reading the KMines [Howto](https://games.kde.org/game.php?game=kmines)
and the Authoritative Minesweeper [Mouse Handling] pages, and then
implementing and testing the "middle-click" or "two-button-click"
functionality they described, I gradually realized that for many years
I've been playing Minesweeper with one metaphorical hand tied behind my back!

Specifically, if you have a cleared cell which shows a number
(indicating the number of mines in neighbouring cells), and if you
can deduce where those mines are and flag them, then middle-clicking on
the numbered cell clears all of its remaining hidden neighbours which are
not flagged.

This is especially useful when the number is low, e.g., a 1 or a 2.
It opens up neighbouring cells much faster than clearing them
individually.

In my command-line implementation, simply entering the `x,y` coordinates
of a numbered cell will clear all neighbouring hidden cells, but only when
you have flagged a corresponding number of the surrounding cells
with `#` flags.

As with the original game, beware flagging incorrectly: if you've
got the right number of `#` flags around the numbered cell, but in the
wrong places, then "middle-clicking" will end the game!


## Implementation Notes

- The grid size may be specified on the command-line:
  `./minesweeper.py [4-24]`
  - Grids are always square and are limited to sizes between 4x4 and 24x24.

- The player's first selection must be guaranteed to be safe, and
  moreover, all the cells surrounding the first selection must be empty
  of mines as well.
  - Therefore, any nearby mines have to be moved after the first selection,
    and before the neighbourhood counts are calculated.
  - The requirement that the cells surrounding the first selection be
    safe implies that the smallest possible (square) game grid is 4x4.
    (In a 3x3 game, an initial click on the centre cell of a 3x3 grid would
    require all nine cells to be empty.)
  - Any flag commands entered before the first `x,y` command do not count
    as this one always-safe selection; mines are moved only after the first
    regular `x,y` command, and only then.

- Coordinates may also be entered without the `,` separator (`xy`), or
  using either `.` or `:` as the separator (`x.y` or `x:y`).

- Adding flags to the game is a necessary step toward supporting
  "middle-click" functionality, and also allows one to protect against
  accidentally exposing a known mine.
  - Preceding cell coordinates with a `#` will mark that cell with a
    `#` "known" flag.  Repeating the same `#` command will convert the
    flag to an `?` "uncertain" flag, and repeating the command a third
    time will clear all flags on the cell.  This cycle is similar to
    how right-clicking a cell behaves in the original game.
  - For convenience, preceding cell coordinates with a `?` will directly
    mark the cell with an `?` "uncertain" flag, and repeating this command
    will clear the flag.
  - Both types of flags will prevent an inadvertent exposure of the
    cell they mark.
  - Both types of flags also prevent cells from being automatically cleared
    when a neighbouring cell is cleared, even if the flagged cell
    does not contain a mine (and therefore would be cleared, if they
    weren't flagged).

- The handy "middle-click" behaviour described above is implemented
  when an `x,y` command used under specific conditions.
  - If an exposed cell contains a number, and `#` flags have been
    placed on a corresponding number of surrounding cells, then re-entering
    the cell's coordinates using an `x,y` command will expose
    all of the remaining hidden neighbouring cells.
  - In this manner, multiple unknown cells may be exposed at once, and so
    this introduces the possibility of exposing more than one mine
    simultaneously.
  - Note that `?` "uncertain" flags are ignored when determining the
    number of neighbouring flags.

- If a mine is accidentally exposed, the game ends, and the final
  grid is shown with the following symbols:
  - `#` marks all correctly placed "known" flags.
  - `x` marks all incorrectly placed "known" flags (i.e., cells which
    did not contain mines).
  - `X` marks all accidentally exposed mines.
  - `*` marks all mines which were neither exposed nor marked with
    "known" flags.
  - `.` marks all cells which were not cleared, did not contain mines,
    and were not marked with "known" flags (but may have been marked
    with `?` "uncertain" flags).


[Mouse Handling]: http://www.minesweeper.info/archive/MinesweeperStrategy/mine_general.html

