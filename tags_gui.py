from tkinter import StringVar, IntVar
from tkinter.ttk import Frame, Button, Entry, Checkbutton, Style, Radiobutton, Label
from typing import List, TypeVar, Tuple

from base_widgets import edit_class_tags
from modules import ReaderModule
from scrolled_frame import VScrolledFrame

T = TypeVar('T')


class TagIntVar(IntVar):
    def __init__(self, tag, **kwargs):
        super(TagIntVar, self).__init__(**kwargs)

        self._tag = tag

    @property
    def tag(self):
        return self._tag


class TagsFrameV2(Frame):
    def __init__(self, reader: ReaderModule, **kwargs):
        super(TagsFrameV2, self).__init__(**kwargs)

        edit_class_tags(self)

        self._reader = reader

        self._all_tags = ()
        self._selected_tags = ()
        self._unselected_tags = ()

        self._filter_var = StringVar(master=self, value='', name='tags_filter')
        self._trace = self._filter_var.trace_add('write', self.repack)
        self._tag_vars: List[TagIntVar] = []
        self._sort_var = IntVar(master=self, value=self._reader.tags_autosort, name='sort')
        self._type_int = IntVar(master=self, name='type_var_int')
        self._type_str = StringVar(master=self, name='type_var_str')

        self._type_int.trace_add('write', self.set_filter_type)

        self.inner = {'side': 'left', 'fill': 'x', 'expand': True}
        self.outer = {'side': 'top', 'fill': 'x'}

        self._popup_button = Button(master=self, text='Tags', command=self.popup)
        self._popup_button.pack(fill='x', expand=True)

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
        self._filter_holder.pack(fill='x', expand=True, ipady=1)

        self._buttons = Frame(master=self, width=self.winfo_width() - 15, height=self.winfo_height() - 47)

        self._buttons.pack(fill='both', expand=True)

        self._options_holder = Frame(master=self)
        self._type_holder = Frame(master=self._options_holder)
        self._type_0 = Radiobutton(master=self._type_holder, value=0, text='', variable=self._type_int)
        self._type_1 = Radiobutton(master=self._type_holder, value=1, text='', variable=self._type_int)
        self._type_2 = Radiobutton(master=self._type_holder, value=2, text='', variable=self._type_int)
        self._type_label = Label(master=self._type_holder, textvariable=self._type_str)
        self._sort = Checkbutton(master=self._options_holder, variable=self._sort_var, text='autosort',
                                 command=self.toggle_autosort)
        self._type_0.pack(side='left')
        self._type_1.pack(side='left')
        self._type_2.pack(side='left')
        self._type_label.pack(side='right', fill='x')
        self._type_holder.pack(side='left')
        self._sort.pack(side='right')
        self._options_holder.pack(side='bottom', fill='x', expand=True)

        self.style = Style()
        self.style.configure('selected.TCheckbutton', background='dark gray')
        self.style.configure('entry_has.TCheckbutton', foreground='purple')
        self.style.configure('entry_has.selected.TCheckbutton', foreground='purple')
        self.style.configure('clear.TButton', padding=0)
        self.style.configure('clear.TEntry', padding=3)

        self.bind('<Configure>', self.repack)
        self.bind_class('JournalWidget', '<<Selected Id>>', self.repack)

        self._type_int.set(self._reader.tag_filter)

        tags = self._reader.tags
        if tags:
            self.selected_tags = list(tags)
        else:
            self.selected_tags = self.selected_tags

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
        self.event_generate('<<Update Ids>>')

    @property
    def unselected_tags(self):
        return self._unselected_tags

    def refresh(self):
        """Refreshes tags information from the reader"""
        pass

    def repack(self, *args):
        frame = VScrolledFrame(master=self, width=self.winfo_width() - 15, height=self.winfo_height() - 47)
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
            button = Checkbutton(master=frame, text=var.tag, variable=var, command=self.swap)
            style = ''
            if var.get() == 1 or var.tag in tags:
                if var.tag in tags and var.get() == 1:
                    style = 'entry_has.selected.TCheckbutton'
                elif var.get() == 1:
                    style = 'selected.TCheckbutton'
                elif var.tag in tags:
                    style = 'entry_has.TCheckbutton'
            button.configure(style=style)
            button.pack(fill='x', expand=True)
        self._buttons = frame
        self._buttons.pack(fill='both', expand=True)
        temp.destroy()

    def add(self, *args):
        tag = self._filter_var.get()
        if tag:
            tags = list(self._selected_tags)
            tags.append(tag)
            self.selected_tags = tuple(tags)
            self._filter_var.set('')

    def swap(self):
        tags = tuple([x.tag for x in self._tag_vars if x.get() == 1])
        self.selected_tags = tags

    def select_all(self):
        self._filter_var.set('')
        self.selected_tags = self.all_tags

    def select_none(self):
        self._filter_var.set('')
        self.selected_tags = []

    def select_invert(self):
        temp = self._unselected_tags
        self._unselected_tags = self._selected_tags
        self._filter_var.set('')
        self.selected_tags = temp

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
    tags = TagsFrameV2(master=root, reader=reader)
    tags.pack(fill='both', expand=True)
    # tags.selected_tags = ['Purple', 'Green', 'Blue', '1', '2', '3']
    root.mainloop()


if __name__ == '__main__':
    _test()
