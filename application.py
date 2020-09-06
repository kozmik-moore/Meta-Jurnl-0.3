"""Contains the classes and functions that form the underlying logic of the journal application"""
from math import floor
from tkinter import Tk
from tkinter.ttk import Button, Frame

from PIL import Image, ImageTk

from configurations import dimensions
from notebook import Journal


class App(Tk):
    def __init__(self, **kwargs):
        super(App, self).__init__(**kwargs)

        img = Image.open('.resources/new_reader.png')
        img = img.resize((16, 16))
        new_reader_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/new_writer.png')
        img = img.resize((16, 16))
        new_writer_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/close_icon.png')
        img = img.resize((16, 16))
        close_panel_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/save_icon.png')
        img = img.resize((16, 16))
        save_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/edit_icon.png')
        img = img.resize((16, 16))
        edit_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/link_icon.png')
        img = img.resize((16, 16))
        link_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/clear_content_icon.png')
        img = img.resize((16, 16))
        clear_content_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/delete_icon.png')
        img = img.resize((16, 16))
        delete_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/wm_icon.png')
        app_icon = ImageTk.PhotoImage(image=img)

        self.title('Meta-Jurnl')
        self.iconphoto(True, app_icon)

        self.withdraw()

        toolbar = Frame(master=self, relief='ridge', borderwidth=1, padding=5)
        toolbar.pack(fill='x')

        self.journal = Journal(master=self)
        self.journal.pack(fill='both', expand=True)

        new_reader = Button(master=toolbar, image=new_reader_icon, command=lambda: self.journal.add_page('Reader'))
        new_writer = Button(master=toolbar, image=new_writer_icon, command=lambda: self.journal.add_page('Writer'))

        close_panel = Button(master=toolbar,
                             text='Close Tab',
                             image=close_panel_icon,
                             compound='right',
                             command=self.journal.remove_page)
        clear_button = Button(master=toolbar, image=clear_content_icon)

        self.save_button = Button(master=toolbar, image=save_icon, command=self.save_entry)
        self.edit_button = Button(master=toolbar, image=edit_icon, command=self.edit_entry)
        self.link_button = Button(master=toolbar, image=link_icon, command=self.link_entry)
        self.delete_button = Button(master=toolbar, image=delete_icon)

        new_reader.pack(side='left', padx=(0, 5))
        new_writer.pack(side='left', padx=(0, 5))
        close_panel.pack(side='right', padx=(5, 0))
        clear_button.pack(side='right', padx=(5, 0))

        self.bind('<Configure>', self.update_dimensions)
        self.bind_all('<<Check Save Button>>', self.check_writer_buttons)
        self.bind_all('<<Selected Id>>', self.check_reader_buttons)
        self.bind('<<NotebookTabChanged>>', self.change_buttons)

        self.journal.update_idletasks()

        s_width = self.winfo_screenwidth() / 2
        s_height = self.winfo_screenheight() / 2
        dims = dimensions()
        try:
            w_width = self.winfo_reqwidth() if not dims[0] else dims[0]
            w_height = self.winfo_reqheight() if not dims[1] else dims[1]
        except IndexError:
            w_width = self.winfo_reqwidth()
            w_height = self.winfo_reqheight()
        pos = w_width, w_height, s_width - floor(w_width / 2), s_height - floor(w_height / 2)
        self.geometry('{}x{}+{}+{}'.format(
            int(pos[0]), int(pos[1]), int(pos[2]), int(pos[3])
        ))
        self.after(1000, self.deiconify)

        self.mainloop()

    def update_dimensions(self, event):
        dimensions((self.winfo_width(), self.winfo_height()))

    def change_buttons(self, event=None):
        if self.journal.class_ == 'Writer':
            self.save_button.pack_forget()
            self.edit_button.pack_forget()
            self.link_button.pack_forget()
            self.delete_button.pack_forget()
            self.save_button.pack(side='left', padx=(0, 5))
            self.link_button.pack(side='left', padx=(0, 5))
            self.check_writer_buttons()
        else:
            self.save_button.pack_forget()
            self.edit_button.pack_forget()
            self.link_button.pack_forget()
            self.delete_button.pack_forget()
            self.edit_button.pack(side='left', padx=(0, 5))
            self.link_button.pack(side='left', padx=(0, 5))
            self.delete_button.pack(side='left', padx=(0, 5))
            self.check_reader_buttons()

    def check_writer_buttons(self, event=None):
        saved = self.journal.check_saved(event)
        self.save_button.state(['disabled' if saved else '!disabled'])
        self.link_button.state(['disabled' if not self.journal.id_ else '!disabled'])

    def check_reader_buttons(self, event=None):
        entry = True if self.journal.id_ else False
        self.edit_button.state(['disabled' if not entry else '!disabled'])
        self.link_button.state(['disabled' if not entry else '!disabled'])
        self.delete_button.state(['disabled' if not entry else '!disabled'])

    def save_entry(self):
        self.journal.save()
        self.save_button.state(['disabled'])
        self.link_button.state(['!disabled'])

    def edit_entry(self):
        self.journal.add_page(mode='Writer', entry_id=self.journal.id_)

    def link_entry(self):
        self.journal.add_page(mode='Writer', parent=self.journal.id_)

    def delete_entry(self):
        pass


def _test():
    App()


if __name__ == '__main__':
    _test()
