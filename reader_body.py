from math import floor
from tkinter import Toplevel, StringVar, END, Text, Event
from tkinter.ttk import Entry, Button, Frame, Scrollbar, Label

from PIL import Image, ImageTk

from base_widgets import add_child_class_to_bindtags
from modules import ReaderModule
from themes import get_icon


class BodyButton(Button):
    def __init__(self, reader: ReaderModule, bind_tag: str, **kwargs):
        super(BodyButton, self).__init__(**kwargs)

        self.filters_icon = get_icon('ic_filter_list')

        self._bind_tag = bind_tag

        self.reader = reader

        self.configure(text='Filter', image=self.filters_icon, command=self.popup)

    def popup(self):
        popup = BodyPopup(reader=self.reader,
                          bind_tag=self._bind_tag,
                          location=(self.winfo_rootx(), self.winfo_rooty()))
        popup.grab_set()
        popup.focus()


class BodyPopup(Toplevel):
    def __init__(self, reader: ReaderModule, bind_tag: str, **kwargs):
        location = kwargs.pop('location') if 'location' in kwargs.keys() else ()
        dims = [50, 27, location[0], location[1]] if location else [50, 27]
        super(BodyPopup, self).__init__(**kwargs)

        self.protocol('WM_DELETE_WINDOW', self.save_and_close)

        self._bind_tag = bind_tag

        add_child_class_to_bindtags(self)

        self.withdraw()

        self.title('Search Contents For...')
        self.bind('<Escape>', lambda e: self.destroy())

        self.reader = reader

        self.body_var = StringVar(value=self.reader.body)

        self.search_field = Entry(master=self, width=40, textvariable=self.body_var)
        self.search_field.pack(side='left', fill='x')

        self.search_field.bind('<Return>', self.save_and_close)
        self.search_field.bind('<KP_Enter>', self.save_and_close)

        clear = Button(master=self, text='Clear', command=self.clear)
        clear.pack(side='right')
        self.search_field.focus()
        self.select_all()
        self.search_field.icursor(END)
        
        self.update_idletasks()

        dims[0], dims[1] = self.winfo_reqwidth(), self.winfo_reqheight()
        dims[2] = dims[2] - dims[0] + 27
        dims[3] = dims[3] + 27
        dims_str = '{}x{}+{}+{}'.format(*dims)

        self.geometry(dims_str)

        self.after(50, self.deiconify)

        self.bind('<Button-1>', self._check_click)

    @property
    def bind_tag(self):
        return self._bind_tag

    def save_and_close(self, *args):
        self.reader.body = self.body_var.get()
        self.event_generate('<<Filter Attributes Changed>>')
        self.destroy()

    def clear(self, *args):
        self.body_var.set('')
        self.reader.body = ''

    def select_all(self, *args):
        self.search_field.select_range(0, END)

    def _check_click(self, event: Event):
        if str(self) not in str(self.focus_get()):
            self.save_and_close()


class BodyText(Frame):
    def __init__(self, reader: ReaderModule, bind_tag: str, **kwargs):
        super(BodyText, self).__init__(**kwargs)

        self._bind_tag = bind_tag

        self.reader = reader

        scrollbar = Scrollbar(master=self)
        self.text = Text(master=self, yscrollcommand=scrollbar.set, wrap='word')
        scrollbar.configure(command=self.text.yview)
        self.text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')

        self.update_text()

        self.bind_class(self._bind_tag, '<<Id Selected>>', self.update_text, add=True)
        self.bind_class(self._bind_tag, '<<Tempfile Updated>>', self.update_text, add=True)

    def update_text(self, *args):
        self.text.configure(state='normal')
        self.text.replace('0.0', 'end', self.reader.entry_body)
        self.text.configure(state='disabled')


class BodyFrame(Frame):
    def __init__(self, reader: ReaderModule, bind_tag: str, **kwargs):
        super(BodyFrame, self).__init__(**kwargs)

        header = Frame(master=self, relief='ridge', borderwidth=1, padding=5)
        header.pack(side='top', fill='x')
        Label(master=header, text='CONTENTS').pack(side='left')
        BodyButton(master=header, reader=reader, bind_tag=bind_tag).pack(side='right')
        BodyText(master=self, reader=reader, bind_tag=bind_tag).pack(side='top', fill='both', expand=True)


def _test():
    reader = ReaderModule('.tempfiles/Reader/000')

    from tkinter import Tk
    root = Tk()
    BodyFrame(master=root, reader=reader).pack()
    root.mainloop()


if __name__ == '__main__':
    _test()
