from tkinter import StringVar, Text
from tkinter.ttk import Frame, Scrollbar

from base_widgets import add_child_class_to_bindtags, add_bind_tag_to_bindtags
from modules import WriterModule


class BodyFrame(Frame):
    def __init__(self, writer: WriterModule, bind_tag: str = None, **kwargs):
        super(BodyFrame, self).__init__(**kwargs)

        self._bind_tag = bind_tag if bind_tag else ''

        add_bind_tag_to_bindtags(self)

        self._writer = writer

        self._body = Text(master=self, wrap='word', undo=True)
        self._body.insert('1.0', self._writer.body)
        self._body.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(master=self, command=self._body.yview)
        scrollbar.pack(fill='y', expand=True)

        self._body.configure(yscrollcommand=scrollbar.set)

        self._body.bind('<KeyRelease>', lambda x: self.set_body(x))
        self.bind_class(self._bind_tag, '<<Refresh Widgets>>', self.refresh, add=True)

        self.refresh()

    @property
    def bind_tag(self):
        return self._bind_tag

    def set_body(self, event):
        text = self._body.get('1.0', 'end')
        self._writer.body = text.strip('\n')
        self.event_generate('<<Check Save Button>>')
        self.event_generate('<<Writer Changed>>')

    def refresh(self, *args):
        self._body.replace('1.0', 'end', self._writer.body)
        self.event_generate('<<Writer Changed>>')

    def clear(self):
        self._writer.body = ''
        self._body.delete('1.0', 'end')
        self._body.insert('1.0', '')


def _test():
    from tkinter import Tk
    from tkinter.ttk import Button

    r = Tk()

    w = WriterModule('.tempfiles/Writer/000')

    b = BodyFrame(master=r, writer=w)
    b.pack()

    r.mainloop()


if __name__ == '__main__':
    _test()
