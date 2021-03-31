from os import scandir, remove, makedirs
from os.path import exists
from tkinter import Event, Menu
from tkinter.ttk import Notebook, Style
from typing import Union

from PIL import Image, ImageTk

from configurations import pages, current_page
from pages import ReaderPage, WriterPage
from themes import get_icon


class Journal(Notebook):
    def __init__(self, **kwargs):
        super(Journal, self).__init__(**kwargs)

        self._book_image = get_icon('ic_library_books')
        self._pencil_image = get_icon('ic_mode_edit')

        style = Style()
        style.configure('writer.TNotebook.Tab', foreground='red')
        style.configure('reader.TNotebook.Tab', foreground='green')

        self._pages = []

        tempfiles = pages()

        for d in '.tempfiles/Reader', '.tempfiles/Writer':
            if not exists(d):
                makedirs(d)

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
                bind_tag = 'Reader{}'.format(r_count)
                r_count += 1
            else:
                bind_tag = 'Writer{}'.format(w_count)
                w_count += 1
            tempfiles[i] = (tempfiles[i], bind_tag)

        pgs = [
            ReaderPage(tempfile=x[0], bind_tag=x[1]) if 'Reader' in x[0] else WriterPage(tempfile=x[0], bind_tag=x[1])
            for x in tempfiles]

        for page in pgs:
            page.id_ = page.bind_tag[-1]
            self.add(child=page,
                     image=self._book_image if page.class_ == 'Reader' else self._pencil_image,
                     text='{} {}'.format(page.class_, page.id_),
                     compound='left')
            pages(added=page.path)
            self._pages.append(page)
            if page.path == current_page():
                self.select(str(page))

        self.bind('<<NotebookTabChanged>>', self.update_settings)
        self.bind('<Button-3>', self.launch_tab_menu)

        self.enable_traversal()

    @property
    def id_(self):
        if self._current_page():
            return self._current_page().entry_id
        else:
            return None

    @property
    def mode_(self):
        if self._current_page():
            return self._current_page().class_
        else:
            return None

    def _current_page(self) -> Union[ReaderPage, WriterPage, None]:
        """Returns the currently selected page object

        """
        if self.tabs():
            c = current_page()
            if c:
                for page in self._pages:
                    if page.path == c:
                        return page
            else:
                p = self._pages[0]
                current_page(p.path)
                return p
        else:
            return None

    def add_page(self, mode: str = 'Reader', **kwargs):
        id_ = self._get_tab_id(mode)
        bind_tag = '{}{}'.format(mode, id_)
        page = ReaderPage(bind_tag=bind_tag) if mode == 'Reader' else WriterPage(bind_tag=bind_tag)
        if 'parent' in kwargs.keys():
            page.link_entry(entry_id=kwargs['parent'])
        if 'entry_id' in kwargs.keys():
            page.edit_entry(entry_id=kwargs['entry_id'])
        page.id_ = id_
        self.add(child=page,
                 image=self._book_image if mode == 'Reader' else self._pencil_image,
                 text='{} {}'.format(mode, id_),
                 compound='left')
        pages(added=page.path)
        self._pages.append(page)
        self.select(str(page))

    def remove_page(self, tab_id: int = 'current'):
        tab_id = self.index(tab_id)
        file = self._pages[tab_id].path
        remove(file)
        pages(removed=file)
        self.forget(tab_id=tab_id)
        self._pages.pop(tab_id)

    def update_settings(self, event: Event):
        # TODO rewrite to use tab_id instead
        """Updates the currently selected tempfile in settings.config

        :param event:
        """
        for page in self._pages:
            if str(page) == self.select():
                current_page(page.path)
                break

    def save(self):
        try:
            self._current_page().save()
            self.event_generate('<<Refresh ReaderPages>>')
        except AttributeError:
            pass

    def check_saved(self, event=None):
        if self._current_page() and self._current_page().class_ == 'Writer':
            return self._current_page().check_saved(event)

    def refresh_readers(self):
        self.event_generate('<<Refresh ReaderPages>>')

    def clear(self):
        self._current_page().reset_fields()

    def launch_tab_menu(self, event: Event):
        # TODO figure out how to grab click outside of menu
        tab_id = self.tk.call(self, "identify", "tab", event.x, event.y)
        if type(tab_id) == int:

            menu = Menu(master=self, tearoff=0)

            def _check_click(e: Event):
                if str(menu) not in str(self.focus_get()):
                    menu.destroy()
            self.bind('<Button-1>', _check_click)

            menu.add_command(label='Close       ', command=lambda: self.remove_page(tab_id))
            menu.add_separator()
            menu.add_command(label='Cancel', command=menu.destroy)
            try:
                menu.tk_popup(x=event.x_root, y=event.y_root)
            finally:
                menu.grab_release()

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
