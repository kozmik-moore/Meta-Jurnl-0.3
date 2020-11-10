"""Contains the classes and functions that form the underlying logic of the journal application"""
from math import floor
from tkinter import Tk, Menu
from tkinter.messagebox import askquestion
from tkinter.ttk import Button, Frame

from PIL import Image, ImageTk

from autoimport import import_entries, delete_imports
from backup import check_backup
from configurations import dimensions, backup_enabled, autodelete_imports
from database_info import database_is_empty
from notebook import Journal

# TODO add methods for creating new database
# TODO add menu option to auto-clean imports
# TODO add auto-import methods
# TODO add "close all pages" method with prompt (right-click on existing button)
from themes import ThemeEngine, get_icon


class App(Tk):
    def __init__(self, **kwargs):
        super(App, self).__init__(**kwargs)
        tags = list(self.bindtags())
        tags.insert(2, 'App')
        self.bindtags(tags)

        themes = ThemeEngine()
        self.option_readfile(themes.options_file)
        themes.set_ttk_style()

        self.new_reader_icon = get_icon('ic_new_reader')
        self.new_writer_icon = get_icon('ic_new_writer')
        self.close_panel_icon = get_icon('ic_close')
        self.save_icon = get_icon('ic_save')
        self.edit_icon = get_icon('ic_mode_edit')
        self.link_icon = get_icon('ic_insert_link')
        self.clear_content_icon = get_icon('ic_delete_sweep')
        self.delete_icon = get_icon('ic_delete_forever')

        img = Image.open('.resources/wm_icon.png')
        app_icon = ImageTk.PhotoImage(image=img)

        if backup_enabled():
            check = check_backup()
            if check != 1:
                # print(check)
                pass

        self.title('Meta-Jurnl')
        self.iconphoto(True, app_icon)

        self.withdraw()

        menu_bar = Menu(master=self)
        self.config(menu=menu_bar)
        # menu_bar.pack(fill='x')

        file_menu = Menu(master=menu_bar, tearoff=0, relief='flat', borderwidth=1)
        file_menu.add_command(label='New Entry', command=self.add_writer)
        file_menu.add_command(label='New Linked Entry')

        page_menu = Menu(master=file_menu, tearoff=0)
        page_menu.add_command(label='New Reader', command=self.add_reader)
        page_menu.add_command(label='New Writer', command=self.add_writer)

        file_menu.add_cascade(label='New', menu=page_menu, underline=0)
        file_menu.add_command(label='Save')
        file_menu.add_command(label='Quit', command=self.destroy)

        edit_menu = Menu(master=menu_bar, tearoff=0)
        edit_menu.add_command(label='Preferences')

        help_menu = Menu(master=menu_bar, tearoff=0)
        help_menu.add_command(label='Keyboard Shortcuts')
        help_menu.add_command(label='About')

        menu_bar.add_cascade(label='File', menu=file_menu, underline=0)
        menu_bar.add_cascade(label='Edit', menu=edit_menu, underline=0)
        menu_bar.add_cascade(label='Help', menu=help_menu, underline=0)

        toolbar = Frame(master=self, relief='flat', borderwidth=0, padding=5)
        toolbar.pack(fill='x')

        self.journal = Journal(master=self)
        self.journal.pack(fill='both', expand=True)

        self.autoimport()

        self.new_reader = Button(master=toolbar, image=self.new_reader_icon, command=self.add_reader)
        new_writer = Button(master=toolbar, image=self.new_writer_icon, command=self.add_writer)

        self.close_panel = Button(master=toolbar,
                                  text='Close Tab',
                                  image=self.close_panel_icon,
                                  command=self.journal.remove_page)
        self.clear_button = Button(master=toolbar, image=self.clear_content_icon, command=self.clear_fields)

        self.save_button = Button(master=toolbar, image=self.save_icon, command=self.save_entry)
        self.edit_button = Button(master=toolbar, image=self.edit_icon, command=self.edit_entry)
        self.link_button = Button(master=toolbar, image=self.link_icon, command=self.link_entry)
        self.delete_button = Button(master=toolbar, image=self.delete_icon)

        self.new_reader.pack(side='left', padx=(0, 5))
        new_writer.pack(side='left', padx=(0, 5))
        self.close_panel.pack(side='left', padx=(0, 5))
        self.clear_button.pack(side='left', padx=(0, 5))

        self.close_panel.state(['disabled'])
        self.clear_button.state(['disabled'])

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

        self.bind('<Configure>', self.update_dimensions)
        self.bind_all('<<Check Save Button>>', self.check_writer_buttons)
        self.bind_all('<<Id Selected>>', self.check_reader_buttons)
        self.bind('<<NotebookTabChanged>>', self.change_buttons)

        self.change_buttons()

        self.after(1000, self.deiconify)

        self.mainloop()

    def update_dimensions(self, event):
        # s_width = self.winfo_screenwidth() / 2
        # s_height = self.winfo_screenheight() / 2
        w_width = max(self.winfo_width(), 1500)
        w_height = max(self.winfo_height(), 600)
        # pos = w_width, w_height, self.winfo_rootx(), self.winfo_rooty()
        # self.geometry('{}x{}+{}+{}'.format(
        #     int(pos[0]), int(pos[1]), int(pos[2]), int(pos[3])
        # ))
        dimensions((w_width, w_height))

    def add_reader(self):
        if not database_is_empty():
            self.journal.add_page('Reader')

    def add_writer(self):
        self.journal.add_page('Writer')

    # def add_tagged_writer(self):
    #     self.journal.add_page('Writer', tags=True)

    def change_buttons(self, event=None):
        self.new_reader.state(['disabled' if database_is_empty() else '!disabled'])
        if self.journal.mode_ == 'Writer':
            self.close_panel.state(['!disabled'])
            self.clear_button.state(['!disabled'])
            self.save_button.pack_forget()
            self.edit_button.pack_forget()
            self.link_button.pack_forget()
            self.delete_button.pack_forget()
            self.save_button.pack(side='left', padx=(0, 5))
            self.link_button.pack(side='left', padx=(0, 5))
            self.check_writer_buttons()
        elif self.journal.mode_ == 'Reader':
            self.close_panel.state(['!disabled'])
            self.clear_button.state(['!disabled'])
            self.save_button.pack_forget()
            self.edit_button.pack_forget()
            self.link_button.pack_forget()
            self.delete_button.pack_forget()
            self.edit_button.pack(side='left', padx=(0, 5))
            self.link_button.pack(side='left', padx=(0, 5))
            self.delete_button.pack(side='left', padx=(0, 5))
            self.check_reader_buttons()
        else:
            self.close_panel.state(['disabled'])
            self.clear_button.state(['disabled'])
            self.save_button.pack_forget()
            self.edit_button.pack_forget()
            self.link_button.pack_forget()
            self.delete_button.pack_forget()

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
        self.change_buttons()

    def edit_entry(self):
        self.journal.add_page(mode='Writer', entry_id=self.journal.id_)

    def link_entry(self):
        self.journal.add_page(mode='Writer', parent=self.journal.id_)

    def delete_entry(self):
        # TODO Implement
        pass

    def clear_fields(self):
        if self.journal.mode_ == 'Writer':
            saved = self.journal.check_saved()
            if not saved:
                if askquestion('Clear Window Contents?',
                               'There are unsaved edits in this tab.\nSave before continuing?'):
                    self.save_entry()
        self.journal.clear()

    def autoimport(self):
        import_entries()
        self.journal.refresh_readers()
        if autodelete_imports():
            delete_imports()


def _test():
    App(className='app')


if __name__ == '__main__':
    _test()
