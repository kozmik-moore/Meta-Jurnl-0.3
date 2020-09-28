from tkinter import StringVar, IntVar, Menu, Menubutton, Event
from tkinter.font import Font
from tkinter.ttk import Frame, Button, Entry, Checkbutton, Style, Radiobutton, Label
from typing import List, TypeVar, Tuple

from PIL import Image, ImageTk

from base_widgets import ScrollingFrame, add_child_class_to_bindtags
from modules import ReaderModule, WriterModule
from themes import get_icon

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

        self._search = get_icon('ic_search')
        self._filter = get_icon('ic_filter_list')

        self._bind_tag = bind_tag

        self._writer = writer

        self._all_tags = ()
        self._selected_tags = ()
        self._unselected_tags = ()

        self._filter_var = StringVar(master=self, value='', name='{}tags_filter'.format(bind_tag))
        self._trace = self._filter_var.trace_add('write', self.repack)
        self._tag_vars: List[TagIntVar] = []

        filter_holder = Frame(master=self, padding=5, relief='sunken', borderwidth=1)
        inner_left = Frame(master=filter_holder)
        inner_left.pack(side='left')
        label = Label(master=inner_left, image=self._search)
        label.pack(side='left')
        filter_entry = Entry(master=inner_left, textvariable=self._filter_var, width=45)
        filter_entry.bind('<Return>', self.add)
        filter_entry.pack(side='left', expand=True)
        filter_holder.pack(fill='x')
        mass_filter = Menubutton(master=filter_holder)
        menu = Menu(master=mass_filter, tearoff=0)
        menu.add_command(label='All', command=self.select_all)
        menu.add_command(label='None', command=self.select_none)
        menu.add_command(label='Invert                  ', command=self.select_invert)
        mass_filter.configure(menu=menu,
                              image=self._filter,
                              indicatoron=0, relief='raised',
                              height=25,
                              width=25,
                              direction='left')
        mass_filter.pack(side='right')

        # test_button = Button(master=filter_holder, text='Press me!')
        # test_button.pack()
        # test_button.bind('<Button-1>', self.popup)

        scrolling_frame = ScrollingFrame(master=self, width=self.winfo_width() - 15, height=self.winfo_height() - 47)
        scrolling_frame.pack(fill='both', expand=True)
        self._inner = scrolling_frame.inner

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
        for b in self._inner.pack_slaves():
            b.pack_forget()
        for var in all_:
            button = Checkbutton(master=self._inner, text=var.tag, variable=var, command=self.swap)
            if var.get() == 1:
                b_style = 'selected.TCheckbutton'
            else:
                b_style = 'unselected.TCheckbutton'
            button.configure(style=b_style)
            button.pack(fill='x', expand=True)
        self.update_idletasks()
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

    def popup(self, event: Event):
        # TODO create popup for grid representation of tags
        frame = Frame(master=self)
        button = Button(master=frame, command=frame.destroy, text='Press me!')
        button.pack(fill='both')
        frame.place(x=event.x, y=event.y)


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
