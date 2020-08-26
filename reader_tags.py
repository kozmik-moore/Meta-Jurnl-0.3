from tkinter import StringVar, IntVar
from tkinter.font import Font
from tkinter.ttk import Frame, Button, Entry, Checkbutton, Style, Radiobutton, Label
from typing import List, TypeVar, Tuple

from PIL import Image, ImageTk

from base_widgets import ScrollingFrame, add_child_class_to_bindtags
from modules import ReaderModule

T = TypeVar('T')


class TagIntVar(IntVar):
    def __init__(self, tag, **kwargs):
        super(TagIntVar, self).__init__(**kwargs)

        self._tag = tag

    @property
    def tag(self):
        return self._tag


class TagsFrame(Frame):
    def __init__(self, reader: ReaderModule, bind_name: str = None, **kwargs):
        super(TagsFrame, self).__init__(**kwargs)

        img = Image.open('check.png')
        img = img.resize((12, 12))
        self._check_image = ImageTk.PhotoImage(image=img)

        self._bind_name = bind_name

        self._reader = reader

        self._all_tags = ()
        self._selected_tags = ()
        self._unselected_tags = ()

        style = Style()
        font = Font(font='TkDefaultFont')
        font.configure(slant='italic')
        style.configure('selected.TCheckbutton', background='dark gray')
        style.configure('unselected.TCheckbutton', background='light gray')
        style.configure('selected.TFrame', background='dark gray')
        style.configure('unselected.TFrame', background='light gray')
        style.configure('selected.TLabel', background='dark gray')
        style.configure('entry.selected.TLabel', font=font, foreground='blue')
        style.configure('unselected.TLabel', background='light gray')
        style.configure('entry.unselected.TLabel', font=font, foreground='blue')
        style.configure('header.TLabel', font=font, foreground='blue')
        style.configure('clear.TButton', padding=0)
        style.configure('clear.TEntry', padding=3)

        self._filter_var = StringVar(master=self, value='', name='{}tags_filter'.format(bind_name))
        self._trace = self._filter_var.trace_add('write', self.repack)
        self._tag_vars: List[TagIntVar] = []
        self._sort_var = IntVar(master=self, value=self._reader.tags_autosort, name='{}sort'.format(bind_name))
        self._type_int = IntVar(master=self, name='{}type_var_int'.format(bind_name))
        self._type_str = StringVar(master=self, name='{}type_var_str'.format(bind_name))

        self.inner = {'side': 'left', 'fill': 'x', 'expand': True}
        self.outer = {'side': 'top', 'fill': 'x'}

        # self._popup_button = Button(master=self, text='Tags', command=self.popup)
        # self._popup_button.pack(fill='x')

        label = Label(master=self, text='Tag Filters', anchor='c', padding=5, style='header.TLabel')
        label.pack(fill='x')

        self._button_holder = Frame(master=self)
        self._none = Button(master=self._button_holder, text='None', command=self.select_none)
        self._invert = Button(master=self._button_holder, text='Invert', command=self.select_invert)
        self._all = Button(master=self._button_holder, text='All', command=self.select_all)
        self._none.pack(**self.inner)
        self._invert.pack(**self.inner)
        self._all.pack(**self.inner)
        self._button_holder.pack(**self.outer)

        self._filter_holder = Frame(master=self)
        self._filter = Entry(master=self._filter_holder, textvariable=self._filter_var, style='clear.TEntry')
        self._filter.bind('<Return>', self.add)
        self._filter_clear = Button(master=self._filter_holder, text='Clear', style='clear.TButton')
        self._filter_clear.configure(command=lambda s='': self._filter_var.set(s))
        self._filter.pack(side='left', fill='x', expand=True)
        self._filter_clear.pack(side='right')
        self._filter_holder.pack(fill='x', ipady=1)

        self._buttons = Frame(master=self, width=self.winfo_width() - 15, height=self.winfo_height() - 47)

        self._buttons.pack(fill='both', expand=True)

        self._options_holder = Frame(master=self)
        self._type_holder = Frame(master=self._options_holder)
        self._type_0 = Radiobutton(master=self._type_holder, value=0, text='', variable=self._type_int)
        self._type_1 = Radiobutton(master=self._type_holder, value=1, text='', variable=self._type_int)
        self._type_2 = Radiobutton(master=self._type_holder, value=2, text='', variable=self._type_int)
        self._type_label = Label(master=self._type_holder, textvariable=self._type_str, width=30)
        self._sort = Checkbutton(master=self._options_holder, variable=self._sort_var, text='autosort',
                                 command=self.toggle_autosort)
        self._type_0.pack(side='left')
        self._type_1.pack(side='left')
        self._type_2.pack(side='left')
        self._type_label.pack(side='right', fill='x')
        self._type_holder.pack(side='left')
        self._sort.pack(side='right', fill='x')
        self._options_holder.pack(side='bottom', fill='x')

        self._type_int.trace_add('write', self.set_filter_type)

        self._type_int.set(self._reader.tag_filter)

        tags = self._reader.tags
        if tags:
            self.selected_tags = list(tags)
        else:
            self.selected_tags = []

        self.bind_class('Parent.{}'.format(self._bind_name), '<<Selected Id>>', self.repack, add=True)
        add_child_class_to_bindtags(self)

    @property
    def bind_name(self):
        return self._bind_name

    @property
    def all_tags(self):
        return self._all_tags

    @property
    def selected_tags(self):
        return self._selected_tags

    @selected_tags.setter
    def selected_tags(self, tags: Tuple[str]):
        self._all_tags = list(set(self._all_tags).union(tags).union(self._reader.all_tags))
        self._tag_vars = [TagIntVar(tag=tag, value=1 if tag in tags else 0) for tag in self._all_tags]
        self._tag_vars.sort(key=lambda x: x.tag)
        self._selected_tags = tags
        self._unselected_tags = tuple(set(self._all_tags).difference(self._selected_tags))
        self._reader.tags = tuple(tags)
        self.repack()

    @property
    def unselected_tags(self):
        return self._unselected_tags

    def refresh(self):
        """Refreshes tags information from the reader"""
        pass

    def repack(self, *args):
        frame = ScrollingFrame(master=self)
        temp = self._buttons
        tags = self._reader.entry_tags
        if self._sort_var.get() == 1:
            selected_entry = []
            selected = []
            unselected_entry = []
            unselected = []
            for var in self._tag_vars:
                if all([var.tag in tags,
                        self._filter_var.get().lower() in var.tag.lower(),
                        var.get() == 1]):
                    selected_entry.append(var)
                elif all([var.tag not in tags,
                          self._filter_var.get().lower() in var.tag.lower(),
                          var.get() == 1]):
                    selected.append(var)
                elif all([var not in selected,
                          self._filter_var.get().lower() in var.tag.lower(),
                          var.get() == 0,
                          var.tag in tags]):
                    unselected_entry.append(var)
                elif all([var not in selected,
                          self._filter_var.get().lower() in var.tag.lower(),
                          var.get() == 0,
                          var.tag not in tags]):
                    unselected.append(var)
            all_ = selected_entry + selected + unselected_entry + unselected
        else:
            all_ = [var for var in self._tag_vars if self._filter_var.get().lower() in var.tag.lower()]
        for var in all_:
            inner = Frame(master=frame.inner)
            button = Checkbutton(master=inner, text=var.tag, variable=var, command=self.swap)
            label = Label(master=inner, image=self._check_image, padding=(0, 0, 5))
            f_style = 'unselected.TFrame'
            l_style = 'unselected.TLabel'
            b_style = 'unselected.TCheckbutton'
            if var.get() == 1 or var.tag in tags:
                if var.tag in tags and var.get() == 1:
                    f_style = 'selected.TFrame'
                    l_style = 'entry.selected.TLabel'
                    b_style = 'selected.TCheckbutton'
                    label.pack(side='right')
                elif var.get() == 1:
                    f_style = 'selected.TFrame'
                    b_style = 'selected.TCheckbutton'
                    l_style = 'selected.TLabel'
                elif var.tag in tags:
                    l_style = 'entry.unselected.TLabel'
                    label.pack(side='right')
            inner.configure(style=f_style)
            label.configure(style=l_style)
            button.configure(style=b_style)
            button.pack(side='left', fill='x', expand=True)
            inner.pack(fill='x', expand=True)
        frame.update()
        self._buttons = frame
        self._buttons.pack(fill='both', expand=True)
        temp.destroy()

    def add(self, *args):
        tag = self._filter_var.get()
        if tag and tag in self._reader.all_tags:
            tags = list(self._selected_tags)
            tags.append(tag)
            self.selected_tags = tuple(tags)
        self._filter_var.set('')
        self.event_generate('<<Update Ids>>')

    def swap(self):
        tags = tuple([x.tag for x in self._tag_vars if x.get() == 1])
        self.selected_tags = tags
        self.event_generate('<<Update Ids>>')

    def select_all(self):
        self._filter_var.set('')
        self.selected_tags = self.all_tags
        self.event_generate('<<Update Ids>>')

    def select_none(self):
        self._filter_var.set('')
        self.selected_tags = []
        self.event_generate('<<Update Ids>>')

    def select_invert(self):
        temp = self._unselected_tags
        self._unselected_tags = self._selected_tags
        self._filter_var.set('')
        self.selected_tags = temp
        self.event_generate('<<Update Ids>>')

    def toggle_autosort(self):
        setting = self._sort_var.get()
        self._reader.tags_autosort = setting
        self.repack()

    def set_filter_type(self, *args):
        num = self.getvar(args[0])
        self._reader.tag_filter = num
        type_ = ['Contains At Least One Of...', 'Contains At Least...', 'Contains Only...'][num]
        self._type_str.set(type_)
        self.event_generate('<<Update Ids>>')

    def popup(self):
        # TODO create popup for grid representation of tags
        pass


def _test():
    from tkinter import Tk
    root = Tk()
    root.geometry('400x500')
    root.grid_rowconfigure(index=0, weight=1)
    reader = ReaderModule('.tempfiles/Reader/000')
    tags = TagsFrame(master=root, reader=reader)
    tags.pack(fill='both', expand=True)
    # tags.selected_tags = ['Purple', 'Green', 'Blue', '1', '2', '3']
    root.mainloop()


if __name__ == '__main__':
    _test()
