"""Contains the classes and functions that form the underlying logic of the journal application"""
from os import scandir
from tkinter.ttk import Notebook, Button
from typing import Union

from configurations import current_database, pages
from pages import ReaderPage, WriterPage


class App:
    def __init__(self):
        self._path = current_database()
        self._pages = []


class Journal(Notebook):
    def __init__(self, **kwargs):
        super(Journal, self).__init__(**kwargs)

        self._pages = []

        tempfiles = pages()

        files = [x.path for x in scandir('.tempfiles/Reader')] + [x.path for x in scandir('.tempfiles/Writer')]

        for path in files:
            if path not in tempfiles:
                tempfiles.append(path)

        r_len = len([x for x in tempfiles if 'Reader' in x])
        w_len = len([x for x in tempfiles if 'Writer' in x])
        r_count = 0
        w_count = 0

        for i in range(r_len + w_len):
            if 'Reader' in tempfiles[i]:
                bind_name = 'Reader{}'.format(r_count)
                r_count += 1
            else:
                bind_name = 'Writer{}'.format(w_count)
                w_count += 1
            tempfiles[i] = (tempfiles[i], bind_name)

        pgs = [ReaderPage(tempfile=x[0], bind_name=x[1]) if 'Reader' in x[0] else WriterPage(tempfile=x[0], bind_name=x[1]) for x in
               tempfiles]

        for page in pgs:
            self.add_page(page)

    def add_page(self, page: Union[ReaderPage, WriterPage]):
        page.id_ = self._get_tab_id(page.class_)
        page.bind_name = '{}{}'.format(page.class_, page.id_)
        self.add(child=page, text='{} {}'.format(page.class_, page.id_))
        pages(added=page.path)
        self._pages.append(page)

    def remove_page(self, path: str = None):
        self.forget(tab_id=path)

    def _get_tab_id(self, page_type: str):
        ids = [x.replace('.!{}page'.format(page_type.lower()), '') for x in self.tabs() if page_type.lower() in x]
        try:
            ids.remove('')
            ids.insert(0, 1)
        except ValueError:
            pass
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
    from tkinter import Tk
    root = Tk()
    journal = Journal(master=root)

    def _print_tabs():
        for tab in journal.tabs():
            print(tab)

    button = Button(master=root, text='Tabs', command=_print_tabs)
    button.pack()
    journal.pack(fill='both', expand=True)
    journal.update_idletasks()
    root.mainloop()


if __name__ == '__main__':
    _test()
