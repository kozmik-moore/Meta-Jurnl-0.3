from tkinter import StringVar, Text
from tkinter.ttk import Frame, Scrollbar

from base_widgets import add_child_class_to_bindtags
from modules import WriterModule


class BodyFrame(Frame):
    def __init__(self, writer: WriterModule, bind_name: str = None, **kwargs):
        super(BodyFrame, self).__init__(**kwargs)

        self._bind_name = bind_name if bind_name else ''

        add_child_class_to_bindtags(self)

        self._writer = writer

        self._body = Text(master=self)
        self._body.insert('1.0', self._writer.body)
        self._body.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(master=self, command=self._body.yview)
        scrollbar.pack(fill='y', expand=True)

        self._body.configure(yscrollcommand=scrollbar.set)

        self._body.bind('<KeyRelease>', lambda x: self.set_body(x))

    @property
    def bind_name(self):
        return self._bind_name

    def set_body(self, event):
        text = self._body.get('1.0', 'end')
        self._writer.body = text.strip('\n')
        self.event_generate('<<Check Save Button>>')

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
