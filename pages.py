from tkinter.ttk import Frame, PanedWindow, Style

from attributes_gui import AttributesFrame
from body_gui import BodyFrame
from dates_gui import DatesFrame
from modules import ReaderModule
from tags_gui import TagsFrame


class ReaderPage(Frame):
    def __init__(self, reader: ReaderModule, **kwargs):
        super(ReaderPage, self).__init__(**kwargs)

        self.reader = reader

        style = Style()
        style.configure('sunken.TFrame', relief='groove')

        left = DatesFrame(reader=reader, relief='ridge', borderwidth=1, padding=3)

        middle = BodyFrame(reader=reader, relief='ridge', borderwidth=1, padding=3)

        right = Frame(relief='ridge', borderwidth=1, padding=3)
        AttributesFrame(master=right, reader=reader).pack(fill='x')
        TagsFrame(master=right, reader=reader).pack(fill='both', expand=True)

        window = PanedWindow(master=self, orient='horizontal')
        window.add(left)
        window.add(middle)
        window.add(right)
        window.pack()

        left.update_ids()
        left.set_id_from_child()


if __name__ == '__main__':
    r = ReaderModule('.tempfiles/Reader/000')
    from tkinter import Tk

    root = Tk()
    ReaderPage(master=root, reader=r).pack()
    root.mainloop()
