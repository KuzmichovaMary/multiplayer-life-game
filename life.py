from random import randint
from config import COLORS


class CellList:
    """Maintain a list of (x, y) cells."""

    def __init__(self):
        self.cells = {}
        self.items = {}

    def getitem(self, cell):
        if cell in self.items:
            return self.items[cell]
        return None

    def has(self, x, y):
        """Check if a cell exists in this list."""
        return x in self.cells.get(y, [])

    def set(self, x, y, item=None):
        row = self.cells.setdefault(y, set())
        if x not in row:
            row.add(x)
        self.items[(y, x)] = item

    def delete(self, x, y):
        try:
            self.cells[y].remove(x)
            del self.items[(x, y)]
        except KeyError:
            pass
        else:
            if not self.cells[y]:
                del self.cells[y]

    def __iter__(self):
        """Iterator over the cells in this list."""
        for y in self.cells:
            for x in self.cells[y]:
                yield (x, y)

    def __str__(self):
        return str(self.cells)


class Life:
    """Game of Life simulation."""

    def __init__(self, survival=(2, 3), birth=(3,)):
        self.survival = survival
        self.birth = birth
        self.alive = CellList()

    def rules_str(self):
        """Return the rules of the game as a printable string."""
        survival_rule = "".join([str(n) for n in self.survival])
        birth_rule = "".join([str(n) for n in self.birth])
        return f'{survival_rule}/{birth_rule}'

    def load(self, filename):
        """Load a pattern from a file into the game grid."""
        with open(filename, "rt") as f:
            header = f.readline()
            if header == '#Life 1.05\n':
                x = y = 0
                for line in f.readlines():
                    if line.startswith('#D'):
                        continue
                    elif line.startswith('#N'):
                        self.survival = [2, 3]
                        self.birth = [3]
                    elif line.startswith('#R'):
                        self.survival, self.birth = [
                            [int(n) for n in i]
                            for i in line[2:].strip().split('/', 1)]
                    elif line.startswith('#P'):
                        x, y = [int(i) for i in line[2:].strip().split(' ', 1)]
                    else:
                        i = line.find('*')
                        while i != -1:
                            self.alive.set(x + i, y, True)
                            i = line.find('*', i + 1)
                        y += 1
            elif header == '#Life 1.06\n':
                for line in f.readlines():
                    if not line.startswith('#'):
                        x, y = [int(i) for i in line.strip().split(' ', 1)]
                        self.alive.set(x, y, True)
            else:
                raise RuntimeError('Unknown file format')

    def toggle(self, x, y, color):
        """Toggle a cell in the grid."""
        if self.alive.has(x, y):
            if self.alive.getitem((x, y)) == color:
                self.alive.delete(x, y)
        else:
            self.alive.set(x, y, color)

    def living_cells(self):
        """Iterate over the living cells."""
        return self.alive.__iter__()

    def bounding_box(self):
        """Return the bounding box that includes all living cells."""
        minx = miny = maxx = maxy = None
        for cell in self.living_cells():
            x = cell[0]
            y = cell[1]
            if minx is None or x < minx:
                minx = x
            if miny is None or y < miny:
                miny = y
            if maxx is None or x > maxx:
                maxx = x
            if maxy is None or y > maxy:
                maxy = y
        return minx or 0, miny or 0, maxx or 0, maxy or 0

    def calculate_cells_by_color(self, color_id):
        counter = 0
        for cell in self.living_cells():
            if self.alive.getitem(cell) == color_id:
                counter += 1
        return counter

    def advance(self):
        """Advance the simulation by one time unit."""
        processed = CellList()
        new_alive = CellList()
        for x, y in self.living_cells():
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    if (x + i, y + j) in processed:
                        continue
                    processed.set(x + i, y + j, True)
                    color = self.alive.getitem((y + j, x + i))
                    if color is None:
                        color = randint(1, 3)
                    if self._advance_cell(x + i, y + j):
                        new_alive.set(x + i, y + j, color)
        self.alive = new_alive

    def _advance_cell(self, x, y):
        """Calculate the new state of a cell."""
        all_neighbors = 0
        my_color_neighbours = 0
        neighbors = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i != 0 or j != 0:
                    neighbors += 1 if self.alive.has(x + i, y + j) else 0

        if self.alive.has(x, y):
            return neighbors in self.survival
        else:
            return neighbors in self.birth