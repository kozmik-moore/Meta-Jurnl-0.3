from math import floor, ceil
from tkinter import Toplevel, Canvas
from tkinter.ttk import Button

from matplotlib.pyplot import show
from networkx import DiGraph, draw_networkx, draw_planar, draw_circular

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from modules import ReaderModule
from reader_functions import get_parent, get_children


class RelativesGraph(Toplevel):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        super(RelativesGraph, self).__init__(**kwargs)
        self._bind_tag = bind_tag if bind_tag is not None else ''

        self._reader = reader

        # self.canvas = Canvas(master=self)
        # self.canvas.pack(fill='both', expand=True)

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

            digraph = DiGraph()
            digraph.add_nodes_from(visited)
            for u in adjacency:
                for v in adjacency[u]:
                    digraph.add_edge(u, v)
            print(digraph.edges, digraph.nodes)
            fig = Figure(figsize=(8, 6))
            plt = fig.add_subplot(111)
            plt.plot()
            # plt.draw_planar(digraph, with_labels=True)

            draw_planar(digraph, with_labels=True)
            # plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            # plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
            # for pos in ['right', 'top', 'bottom', 'left']:
            #     plt.gca().spines[pos].set_visible(False)

            show()
            canvas = FigureCanvasTkAgg(fig, master=self)
            toolbar = NavigationToolbar2Tk(canvas, self)
            toolbar.update()
            canvas.get_tk_widget().pack()


def test():
    from tkinter import Tk

    reader = ReaderModule('.tempfiles/Reader/001')

    def popup():
        p = RelativesGraph(reader)
        # p.grab_set()
        # p.focus()

    root = Tk()
    button = Button(master=root, text='Test', command=popup)
    button.pack()
    root.mainloop()


if __name__ == '__main__':
    test()
