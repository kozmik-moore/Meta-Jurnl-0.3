from tkinter import Toplevel, StringVar, END
from tkinter.ttk import Entry, Button

from base_widgets import edit_class_tags
from modules import ReaderModule


class BodyButton(Button):
    def __init__(self, reader: ReaderModule, **kwargs):
        super(BodyButton, self).__init__(**kwargs)

        self.reader = reader

        self.configure(text='Search Contents', command=self.popup)

    def popup(self):
        popup = BodyPopup(self.reader)
        popup.grab_set()
        popup.focus()


class BodyPopup(Toplevel):
    def __init__(self, reader: ReaderModule, **kwargs):
        super(BodyPopup, self).__init__(**kwargs)

        edit_class_tags(self)

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

    def save_and_close(self, *args):
        self.reader.body = self.body_var.get()
        self.event_generate('<<Update Ids>>')
        self.destroy()

    def clear(self, *args):
        self.body_var.set('')
        self.reader.body = ''
        self.event_generate('<<Update Ids>>')

    def select_all(self, *args):
        self.search_field.select_range(0, END)


def _test():
    reader = ReaderModule('.tempfiles/Reader/000')

    from tkinter import Tk
    root = Tk()
    button = BodyButton(master=root, text='Search Contents', reader=reader)
    button.pack()
    root.mainloop()


if __name__ == '__main__':
    _test()
