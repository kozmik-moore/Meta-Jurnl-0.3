from tkinter import StringVar, IntVar
from tkinter.font import Font
from tkinter.ttk import Frame, Button, Entry, Checkbutton, Style, Radiobutton, Label
from typing import List, TypeVar, Tuple

from PIL import Image, ImageTk

from base_widgets import ScrollingFrame, add_child_class_to_bindtags
from modules import ReaderModule, WriterModule

T = TypeVar('T')


class TagIntVar(IntVar):
    def __init__(self, tag, **kwargs):
        super(TagIntVar, self).__init__(**kwargs)

        self._tag = tag

    @property
    def tag(self):
        return self._tag


class TagsFrame(Frame):
    def __init__(self, writer: WriterModule, bind_tag: str = None, **kwargs):
        super(TagsFrame, self).__init__(**kwargs)

        self._bind_tag = bind_tag

        self._writer = writer

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

        self._filter_var = StringVar(master=self, value='', name='{}tags_filter'.format(bind_tag))
        self._trace = self._filter_var.trace_add('write', self.repack)
        self._tag_vars: List[TagIntVar] = []

        self.inner = {'side': 'left', 'fill': 'x', 'expand': True}
        self.outer = {'side': 'top', 'fill': 'x'}

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

        tags = self._writer.tags
        if tags:
            self.selected_tags = list(tags)
        else:
            self.selected_tags = []

        self.bind_class(self._bind_tag, '<<Selected Id>>', self.repack, add=True)
        self.bind_class(self._bind_tag, '<<Refresh Widgets>>', self.refresh, add=True)

    @property
    def bind_tag(self):
        return self._bind_tag

    @property
    def all_tags(self):
        return self._all_tags

    @property
    def selected_tags(self):
        return self._selected_tags

    @selected_tags.setter
    def selected_tags(self, tags: Tuple[str]):
        self._all_tags = list(set(self._all_tags).union(tags).union(self._writer.all_tags))
        try:
            self._all_tags.remove('(UNTAGGED)')
        except ValueError:
            pass
        self._tag_vars = [TagIntVar(tag=tag, value=1 if tag in tags else 0) for tag in self._all_tags]
        self._tag_vars.sort(key=lambda x: x.tag)
        self._selected_tags = tags
        self._unselected_tags = tuple(set(self._all_tags).difference(self._selected_tags))
        self._writer.tags = tuple(tags)
        self.repack()

    @property
    def unselected_tags(self):
        return self._unselected_tags

    def refresh(self, *args):
        """Refreshes tags information from the writer"""
        self.selected_tags = self._writer.tags

    def repack(self, *args):
        frame = ScrollingFrame(master=self)
        temp = self._buttons
        selected = []
        unselected = []
        for var in self._tag_vars:
            if all([self._filter_var.get().lower() in var.tag.lower(),
                    var.get() == 1]):
                selected.append(var)
            elif all([var not in selected,
                      self._filter_var.get().lower() in var.tag.lower(),
                      var.get() == 0]):
                unselected.append(var)
        all_ = selected + unselected
        for var in all_:
            button = Checkbutton(master=frame.inner, text=var.tag, variable=var, command=self.swap)
            if var.get() == 1:
                b_style = 'selected.TCheckbutton'
            else:
                b_style = 'unselected.TCheckbutton'
            button.configure(style=b_style)
            button.pack(fill='x', expand=True)
        frame.update_idletasks()
        self._buttons = frame
        self._buttons.pack(fill='both', expand=True)
        temp.destroy()
        self.event_generate('<<Check Save Button>>')

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

    def popup(self):
        # TODO create popup for grid representation of tags
        pass


def _test():
    from tkinter import Tk
    root = Tk()
    writer = WriterModule('.tempfiles/Writer/000')
    tags = TagsFrame(master=root, writer=writer)
    tags.pack(fill='both', expand=True)
    # tags.selected_tags = ['Purple', 'Green', 'Blue', '1', '2', '3']
    root.mainloop()


if __name__ == '__main__':
    _test()
