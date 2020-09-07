from tkinter.ttk import Frame, PanedWindow

from base_widgets import add_parent_class_to_bindtags
from reader_attributes import AttributesFrame
from reader_body import BodyFrame as ReaderBodyFrame
from reader_dates import DatesFrame as ReaderDatesFrame
from modules import ReaderModule, WriterModule
from reader_tags import TagsFrame as ReaderTagsFrame
from writer_attachments import AttachmentsButton
from writer_body import BodyFrame as WriterBodyFrame
from writer_dates import DateFrame
from writer_tags import TagsFrame as WriterTagsFrame


class ReaderPage(Frame):
    def __init__(self, tempfile: str = None, bind_name: str = None, **kwargs):
        super(ReaderPage, self).__init__(**kwargs)

        self._bind_name = bind_name if bind_name else 'Reader0'

        self._class_ = 'Reader'

        self._id = None

        self._reader = ReaderModule(tempfile)

        left = ReaderDatesFrame(reader=self._reader, bind_name=bind_name, relief='ridge', borderwidth=1, padding=3)

        middle = ReaderBodyFrame(reader=self._reader, relief='ridge', borderwidth=1, padding=3, bind_name=bind_name)

        right = Frame(relief='ridge', borderwidth=1, padding=3)
        AttributesFrame(master=right, reader=self._reader, bind_name=bind_name).pack(fill='x')
        ReaderTagsFrame(master=right, reader=self._reader, bind_name=bind_name).pack(fill='both', expand=True)

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

    @property
    def name(self):
        return self._name

    def reset_fields(self):
        self._reader.reset_fields()


class WriterPage(Frame):
    def __init__(self, tempfile: str = None, bind_name: str = None, **kwargs):
        super(WriterPage, self).__init__(**kwargs)

        self._bind_name = bind_name if bind_name else 'Writer0'

        self._class_ = 'Writer'

        self._id = None

        self._writer = WriterModule(tempfile)

        top_left = Frame(relief='ridge', borderwidth=1, padding=3)
        top_left.pack(fill='both', expand=True)

        left_header = Frame(master=top_left)
        left_header.pack(fill='x')

        attachments = Frame(master=left_header)
        attachments.pack(fill='x', expand=True, side='left')

        attachments_button = AttachmentsButton(master=attachments, writer=self._writer, bind_name=self._bind_name)
        attachments_button.pack(side='left')

        date = DateFrame(master=left_header, writer=self._writer, bind_name=self._bind_name)
        date.pack(fill='x', expand=True, side='left', anchor='c')

        body = WriterBodyFrame(master=top_left, writer=self._writer, bind_name=self._bind_name)
        body.pack(fill='both', expand=True)

        top_right = Frame(relief='ridge', borderwidth=1, padding=3)
        top_right.pack(fill='both', expand=True)

        tags = WriterTagsFrame(master=top_right, writer=self._writer, bind_name=self._bind_name)
        tags.pack(fill='both', expand=True)

        window = PanedWindow(master=self, orient='horizontal')
        window.add(top_left, weight=2)
        window.add(top_right, weight=1)
        window.pack(fill='both', expand=True)

        add_parent_class_to_bindtags(self)

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
    def writer(self):
        return self._writer

    @property
    def path(self):
        return self._writer.path

    @property
    def entry_id(self):
        return self._writer.id_

    @property
    def name(self):
        return self._name

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, v: int):
        self._id = v

    def save(self):
        self._writer.save()
        self.event_generate('<<Refresh Widgets>>')

    def link_entry(self, entry_id: int):
        self._writer.link_entry(entry_id)
        self.event_generate('<<Refresh Widgets>>')

    def edit_entry(self, entry_id: int):
        self._writer.edit_entry(entry_id)
        self.event_generate('<<Refresh Widgets>>')

    def check_saved(self, event=None):
        return self._writer.check_saved(event)

    def reset_fields(self):
        self._writer.reset_all_fields()
        self.event_generate('<<Refresh Widgets>>')


def _test_reader():
    r = '.tempfiles/Reader/000'
    from tkinter import Tk

    root = Tk()
    ReaderPage(master=root, tempfile=r).pack(fill='both', expand=True)
    root.mainloop()


def _test_writer():
    r = '.tempfiles/Writer/000'
    from tkinter import Tk

    root = Tk()
    WriterPage(master=root, tempfile=r).pack(fill='both', expand=True)
    root.mainloop()


if __name__ == '__main__':
    _test_writer()
