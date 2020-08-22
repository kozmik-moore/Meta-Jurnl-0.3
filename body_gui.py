from tkinter import Toplevel, StringVar, END, Text
from tkinter.ttk import Entry, Button, Frame, Scrollbar

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


class BodyText(Frame):
    def __init__(self, reader: ReaderModule, **kwargs):
        super(BodyText, self).__init__(**kwargs)

        self.reader = reader

        scrollbar = Scrollbar(master=self)
        self.text = Text(master=self, yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.text.yview)
        self.text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y', expand=True)

        self.bind_class('JournalWidget', '<<Selected Id>>', self.update_text)
        self.update_text()

    def update_text(self):
        self.text.configure(state='normal')
        self.text.replace('0.0', 'end', self.reader.entry_body)
        self.text.configure(state='disabled')


class BodyFrame(Frame):
    def __init__(self, reader: ReaderModule, **kwargs):
        super(BodyFrame, self).__init__(**kwargs)

        BodyButton(master=self, reader=reader).pack()
        BodyText(master=self, reader=reader).pack()


def _test():
    reader = ReaderModule('.tempfiles/Reader/000')

    from tkinter import Tk
    root = Tk()
    BodyFrame(master=root, reader=reader).pack()
    root.mainloop()


if __name__ == '__main__':
    _test()
