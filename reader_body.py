from tkinter import Toplevel, StringVar, END, Text
from tkinter.font import Font
from tkinter.ttk import Entry, Button, Frame, Scrollbar, Style, Label

from PIL import Image, ImageTk

from base_widgets import add_child_class_to_bindtags
from modules import ReaderModule


class BodyButton(Button):
    def __init__(self, reader: ReaderModule, bind_name: str, **kwargs):
        super(BodyButton, self).__init__(**kwargs)

        img = Image.open('.resources/filter_icon.png')
        img = img.resize((16, 16))
        self.filters_icon = ImageTk.PhotoImage(image=img)

        self._bind_name = bind_name

        self.reader = reader

        # font = Font(font='TkDefaultFont')
        # font.configure(slant='italic')
        # style = Style()
        # style.configure('popup.TButton', font=font, foreground='blue')

        self.configure(text='Filter', image=self.filters_icon, command=self.popup)

    def popup(self):
        popup = BodyPopup(reader=self.reader, bind_name=self._bind_name)
        popup.grab_set()
        popup.focus()


class BodyPopup(Toplevel):
    def __init__(self, reader: ReaderModule, bind_name: str, **kwargs):
        super(BodyPopup, self).__init__(**kwargs)

        self.protocol('WM_DELETE_WINDOW', self.save_and_close)

        self._bind_name = bind_name

        add_child_class_to_bindtags(self)

        self.title('Search Contents For...')
        self.bind('<Escape>', lambda e: self.destroy())

        self.reader = reader

        self.body_var = StringVar(value=self.reader.body)

        self.search_field = Entry(master=self, width=50, textvariable=self.body_var)
        self.search_field.pack(side='left', fill='x')

        self.search_field.bind('<Return>', self.save_and_close)
        self.search_field.bind('<KP_Enter>', self.save_and_close)

        clear = Button(master=self, text='Clear', command=self.clear)
        clear.pack(side='right')
        self.search_field.focus()
        self.select_all()
        self.search_field.icursor(END)

    @property
    def bind_name(self):
        return self._bind_name

    def save_and_close(self, *args):
        self.reader.body = self.body_var.get()
        self.event_generate('<<Update Ids>>')
        self.destroy()

    def clear(self, *args):
        self.body_var.set('')
        self.reader.body = ''

    def select_all(self, *args):
        self.search_field.select_range(0, END)


class BodyText(Frame):
    def __init__(self, reader: ReaderModule, bind_name: str, **kwargs):
        super(BodyText, self).__init__(**kwargs)

        self._bind_name = bind_name

        self.reader = reader

        scrollbar = Scrollbar(master=self)
        self.text = Text(master=self, yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.text.yview)
        self.text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')

        self.bind_class('Parent.{}'.format(self._bind_name), '<<Selected Id>>', self.update_text, add=True)

        self.update_text()

    def update_text(self, *args):
        self.text.configure(state='normal')
        self.text.replace('0.0', 'end', self.reader.entry_body)
        self.text.configure(state='disabled')


class BodyFrame(Frame):
    def __init__(self, reader: ReaderModule, bind_name: str, **kwargs):
        super(BodyFrame, self).__init__(**kwargs)

        header = Frame(master=self, relief='ridge', borderwidth=1, padding=5)
        header.pack(side='top', fill='x')
        Label(master=header, text='Contents').pack(side='left')
        BodyButton(master=header, reader=reader, bind_name=bind_name).pack(side='right')
        BodyText(master=self, reader=reader, bind_name=bind_name).pack(side='top', fill='both', expand=True)


def _test():
    reader = ReaderModule('.tempfiles/Reader/000')

    from tkinter import Tk
    root = Tk()
    BodyFrame(master=root, reader=reader).pack()
    root.mainloop()


if __name__ == '__main__':
    _test()
