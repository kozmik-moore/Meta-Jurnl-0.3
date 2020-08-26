from tkinter.ttk import Frame, PanedWindow, Style

from reader_attributes import AttributesFrame
from reader_body import BodyFrame
from reader_dates import DatesFrame
from modules import ReaderModule, WriterModule
from reader_tags import TagsFrame


class ReaderPage(Frame):
    def __init__(self, tempfile: str = None, bind_name: str = None, **kwargs):
        super(ReaderPage, self).__init__(**kwargs)

        self._bind_name = bind_name if bind_name else 'Reader0'

        self._class_ = 'Reader'

        self._id = None

        self._reader = ReaderModule(tempfile)

        left = DatesFrame(reader=self._reader, bind_name=bind_name, relief='ridge', borderwidth=1, padding=3)

        middle = BodyFrame(reader=self._reader, relief='ridge', borderwidth=1, padding=3, bind_name=bind_name)

        right = Frame(relief='ridge', borderwidth=1, padding=3)
        AttributesFrame(master=right, reader=self._reader, bind_name=bind_name).pack(fill='x')
        TagsFrame(master=right, reader=self._reader, bind_name=bind_name).pack(fill='both', expand=True)

        window = PanedWindow(master=self, orient='horizontal')
        window.add(left, weight=1)
        window.add(middle, weight=6)
        window.add(right, weight=1)
        window.pack(fill='both', expand=True)

        left.update_ids()
        left.set_id_from_child()

    @property
    def bind_name(self):
        return self._bind_name

    @bind_name.setter
    def bind_name(self, v: str):
        self._bind_name = v

    @property
    def class_(self):
        return self._class_

    @property
    def entry_id(self):
        return self._reader.id_

    @property
    def reader(self):
        return self._reader

    @property
    def path(self):
        return self._reader.path

    @property
    def date(self):
        return self._reader.entry_date.strftime('%a, %b %d, %Y %H:%M')

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, v: int):
        self._id = v


class WriterPage(Frame):
    def __init__(self, tempfile: str, bind_name: str = None, **kwargs):
        super(WriterPage, self).__init__(**kwargs)

        self._bind_name = bind_name if bind_name else 'Writer0'

        self._class_ = 'Writer'

        self.writer = WriterModule(tempfile)

    @property
    def bind_name(self):
        return self._bind_name

    @bind_name.setter
    def bind_name(self, v: str):
        self._bind_name = v

    @property
    def class_(self):
        return self._class_


if __name__ == '__main__':
    r = '.tempfiles/Reader/000'
    from tkinter import Tk

    root = Tk()
    ReaderPage(master=root, tempfile=r).pack(fill='both', expand=True)
    root.mainloop()
