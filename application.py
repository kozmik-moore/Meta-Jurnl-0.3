"""Contains the classes and functions that form the underlying logic of the journal application"""
from math import floor
from os import scandir, remove
from tkinter import Event, Tk
from tkinter.ttk import Notebook, Button, Style, Frame
from typing import Union

from PIL import Image, ImageTk

from configurations import pages, current_page, dimensions
from pages import ReaderPage, WriterPage


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

        img = Image.open('.resources/trash_icon.png')
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
        self.save_button = Button(master=toolbar, image=save_icon, command=self.save_entry)
        self.edit_button = Button(master=toolbar, image=edit_icon)
        self.link_button = Button(master=toolbar, image=link_icon)
        self.delete_button = Button(master=toolbar, image=delete_icon)
        new_reader.pack(side='left', padx=(0, 5))
        new_writer.pack(side='left', padx=(0, 5))
        close_panel.pack(side='right')

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

        self.change_buttons()

        self.bind('<Configure>', self.update_dimensions)
        self.bind_all('<<Check Save Button>>', self.check_save_button)
        self.bind('<<NotebookTabChanged>>', self.change_buttons)

        self.mainloop()

    def update_dimensions(self, event):
        dimensions((self.winfo_width(), self.winfo_height()))

    def change_buttons(self, event=None):
        if self.journal.current_page.class_ == 'Writer':
            self.edit_button.pack_forget()
            self.link_button.pack_forget()
            self.delete_button.pack_forget()
            self.save_button.pack(side='left', padx=(0, 5))
            self.delete_button.pack(side='left', padx=(0, 5))
            self.check_save_button()
        else:
            self.save_button.pack_forget()
            self.delete_button.pack_forget()
            self.edit_button.pack(side='left', padx=(0, 5))
            self.link_button.pack(side='left', padx=(0, 5))
            self.delete_button.pack(side='left', padx=(0, 5))

    def check_save_button(self, event=None):
        if self.journal.current_page.class_ == 'Writer':
            saved = self.journal.current_page.writer.check_saved(event)
            self.save_button.state(['disabled' if saved else '!disabled'])
        else:
            self.save_button.state(['disabled'])

    def save_entry(self):
        self.journal.current_page.writer.save()
        self.save_button.state(['disabled'])


class Journal(Notebook):
    def __init__(self, **kwargs):
        super(Journal, self).__init__(**kwargs)

        img = Image.open('.resources/purple_book.png')
        img = img.resize((16, 16))
        self._book_image = ImageTk.PhotoImage(image=img)
        img = Image.open('.resources/green_pencil.png')
        img = img.resize((16, 16))
        self._pencil_image = ImageTk.PhotoImage(image=img)

        style = Style()
        style.configure('writer.TNotebook.Tab', foreground='red')
        style.configure('reader.TNotebook.Tab', foreground='green')

        self._pages = []

        tempfiles = pages()

        files = [x.path for x in scandir('.tempfiles/Reader')] + [x.path for x in scandir('.tempfiles/Writer')]

        for path in files:
            if path not in tempfiles:
                tempfiles.append(path)

        r_len = len([x for x in tempfiles if 'Reader' in x])
        w_len = len([x for x in tempfiles if 'Writer' in x])
        r_count = 1
        w_count = 1

        for i in range(r_len + w_len):
            if 'Reader' in tempfiles[i]:
                bind_name = 'Reader{}'.format(r_count)
                r_count += 1
            else:
                bind_name = 'Writer{}'.format(w_count)
                w_count += 1
            tempfiles[i] = (tempfiles[i], bind_name)

        pgs = [
            ReaderPage(tempfile=x[0], bind_name=x[1]) if 'Reader' in x[0] else WriterPage(tempfile=x[0], bind_name=x[1])
            for x in tempfiles]

        for page in pgs:
            page.id_ = page.bind_name[-1]
            self.add(child=page,
                     image=self._book_image if page.class_ == 'Reader' else self._pencil_image,
                     text='{} {}'.format(page.class_, page.id_),
                     compound='left')
            pages(added=page.path)
            self._pages.append(page)
            if page.path == current_page():
                self.select(str(page))

        self.bind('<<NotebookTabChanged>>', self.update_current_setting)

    @property
    def current_page(self) -> Union[ReaderPage, WriterPage]:
        """Returns the currently selected page object

        """
        for page in self._pages:
            if page.path == current_page():
                return page

    def add_page(self, mode: str = 'Reader'):
        id_ = self._get_tab_id(mode)
        bind_name = '{}{}'.format(mode, id_)
        page = ReaderPage(bind_name=bind_name) if mode == 'Reader' else WriterPage(bind_name=bind_name)
        page.id_ = id_
        self.add(child=page,
                 image=self._book_image if mode == 'Reader' else self._pencil_image,
                 text='{} {}'.format(mode, id_),
                 compound='left')
        pages(added=page.path)
        self._pages.append(page)
        self.select(str(page))

    def remove_page(self):
        file = current_page()
        remove(file)
        pages(removed=file)
        c = self.current_page
        self.forget(tab_id='current')
        self._pages.remove(c)

    def update_current_setting(self, event: Event):
        """Updates the currently selected tempfile in settings.config

        :param event:
        """
        for page in self._pages:
            if str(page) == self.select():
                current_page(page.path)
                break

    def _get_tab_id(self, page_type: str):
        ids = [x.id_ for x in self._pages if page_type in x.class_]
        ids = [int(x) for x in ids]
        ids.sort()
        diff = False
        i = 1
        while not diff and i < len(ids) + 1:
            if i != ids[i - 1]:
                diff = True
            i += 1
        if diff:
            id_ = i - 1
        else:
            id_ = i
        return id_


def _test():
    App()


if __name__ == '__main__':
    _test()
