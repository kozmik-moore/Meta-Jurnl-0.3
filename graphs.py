from math import floor, ceil
from tkinter import Toplevel, Canvas
from tkinter.ttk import Button

from modules import ReaderModule
from reader_functions import get_parent, get_children


class RelativesGraph(Toplevel):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        super(RelativesGraph, self).__init__(**kwargs)
        self._bind_tag = bind_tag if bind_tag is not None else ''

        self._reader = reader

        self.canvas = Canvas(master=self)
        self.canvas.pack(fill='both', expand=True)

        self.draw_graph()

    def draw_graph(self):
        source = entry = self._reader.id_
        if self._reader.entry_has_parent:
            database = self._reader.database
            has_parent = True if get_parent(source, database) else False
            while has_parent:
                source = get_parent(source, database)
                has_parent = True if get_parent(source, database) else False

            # Explore relatives and build adjacency list
            queue = [source]
            visited = []
            lvl = 0
            level = []
            adjacency = {}

            while queue:
                node = queue.pop(0)
                if node not in visited:
                    visited.append(node)
                    level.append(lvl)
                    children = list(get_children(node, database))
                    queue += children
                    if children:
                        adjacency[node] = children
                    if queue:
                        if get_parent(node, database) != get_parent(queue[0], database):
                            lvl += 1
            print(visited, level, adjacency)

            # Find width of graph
            height = level[-1] + 1
            width = 1
            if adjacency:
                for i in adjacency.keys():
                    length = len(adjacency[i])
                    if length > width:
                        width = length

            # Assign relatives to positions in grid
            grid = [[None for i in range(width)] for i in range(height)]
            grid[0][ceil(width / 2) - 1] = visited.pop(0)    # Place root in center
            level.pop(0)
            for i in range(len(visited)):
                row = level[i]
                node = visited[i]
                pos = parent_pos = adjacency[get_parent(node, database)].index(node)
                placed = False
                while not placed:
                    if 0 <= pos < parent_pos:
                        if grid[row][pos] is None:
                            grid[row][pos] = node
                            placed = True
                        else:
                            if pos >= 0:
                                pos -= 1
                            else:
                                pos = parent_pos
                    else:
                        if grid[row][pos] is None:
                            grid[row][pos] = node
                            placed = True
                        else:
                            if pos >= 0:
                                pos += 1

                # if level:
                #     if level[0] != i:
                #         pass
                #     else:
                #         node = visited.pop(0)
                #         parent_pos = adjacency[get_parent(node, database)].index(node)
                #         level.pop(0)
            print(grid)


def test():
    from tkinter import Tk

    reader = ReaderModule('.tempfiles/Reader/000')

    def popup():
        p = RelativesGraph(reader)
        p.grab_set()
        p.focus()

    root = Tk()
    button = Button(master=root, text='Test', command=popup)
    button.pack()
    root.mainloop()


if __name__ == '__main__':
    test()
