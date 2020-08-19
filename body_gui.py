from tkinter import Toplevel, StringVar, END
from tkinter.ttk import Frame, Entry, Button

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

        self.options_holder = Frame(master=self, width=300)
        self.options_holder.pack(fill='x')

        self.search_field = Entry(master=self, textvariable=self.body_var)
        self.search_field.pack(fill='x')

        self.search_field.bind('<Return>', self.save_and_close)
        self.search_field.bind('<KP_Enter>', self.save_and_close)

        self.close_buttons = Frame(master=self)
        cancel = Button(master=self.close_buttons, text='Cancel', command=self.destroy)
        confirm = Button(master=self.close_buttons, text='Okay', command=self.save_and_close)
        cancel.pack(side='left')
        confirm.pack(side='right')
        self.close_buttons.pack(fill='x')

    def save_and_close(self, *args):
        self.reader.body = self.body_var.get()
        self.event_generate('<<Update Ids>>')
        self.destroy()

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
