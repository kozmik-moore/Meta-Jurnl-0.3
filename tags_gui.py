from tkinter import StringVar, Toplevel, IntVar
from tkinter.ttk import Frame, Button, Entry, Label, Checkbutton, Style
from typing import List, TypeVar

from base_widgets import JournalWidget
from filter import FilteredReader
from scrolled_frame import VScrolledFrame

T = TypeVar('T')


class TagButton(Button):
    def __init__(self, tag: str, **kwargs):
        super(TagButton, self).__init__(**kwargs)

        self._tag = tag

    @property
    def tag(self):
        return self._tag


class TagsFrame(Frame, JournalWidget):
    def __init__(self, reader: FilteredReader = None, **kwargs):
        super(TagsFrame, self).__init__(**kwargs)

        # self.grid_columnconfigure(index=0, weight=1)
        self._reader = reader

        self._all_tags = []
        self._selected_tags = []
        self._unselected_tags = []

        self._filter_var = StringVar(master=self, value='', name='tags_filter')
        self._trace = self._filter_var.trace_add('write', self.repack)

        self._popup_button = Button(master=self, text='Tags', command=self.popup)
        self._filter = Entry(master=self, textvariable=self._filter_var)
        self._buttons_frame = Frame(master=self)
        self._buttons_inner = Frame(self._buttons_frame, width=self.winfo_width() - 15, height=self.winfo_height() - 47)

        self._popup_button.pack(fill='x', expand=True)
        self._filter.pack(fill='x', expand=True)
        self._buttons_inner.pack(fill='both', expand=True)
        self._buttons_frame.pack(fill='both', expand=True)

        self.bind('<Configure>', self.repack)

    @property
    def all_tags(self):
        return self._all_tags

    @property
    def selected_tags(self):
        return self._selected_tags

    @selected_tags.setter
    def selected_tags(self, tags: List[str]):
        self._all_tags = list(set(self._all_tags).union(tags).union(self._reader.all_tags))
        self._selected_tags = tags
        self._unselected_tags = list(set(self._all_tags).difference(self._selected_tags))
        self._reader.tags_has = tuple(tags)
        self.repack()

    @property
    def unselected_tags(self):
        return self._unselected_tags

    def refresh(self):
        """Refreshes tags information from the reader"""
        pass

    def repack(self, *args):
        frame = VScrolledFrame(master=self._buttons_frame, width=self.winfo_width() - 15,
                               height=self.winfo_height() - 47)
        temp = self._buttons_inner
        for tag in self._selected_tags:
            if self._filter_var.get().lower() in tag.lower():
                button = TagButton(master=frame, text=tag, tag=tag)
                button.configure(command=lambda b=button: self.remove(b))
                button.pack(fill='x', expand=True)
        temp.destroy()
        self._buttons_inner = frame
        self._buttons_inner.pack(fill='both', expand=True)

    def remove(self, button: TagButton):
        button.destroy()
        tag = button.tag
        self._selected_tags.remove(tag)
        self._unselected_tags.append(tag)
        self._unselected_tags.sort()
        # TODO figure out how to fix scrollbar bug without this
        # self.repack()

    def popup(self):
        popup = TagsPopup(self, self._selected_tags, self._unselected_tags)
        popup.grab_set()
        popup.focus()


class TagsPopup(Toplevel):

    def __init__(self, parent: TagsFrame, selected: List[str], unselected: List[str], **kwargs):
        super(TagsPopup, self).__init__(**kwargs)

        self.geometry('330x400')
        self.resizable(width=False, height=False)
        for i in range(6):
            self.grid_columnconfigure(index=i, weight=1)
        self.protocol('WM_DELETE_WINDOW', self.exit)

        self.inner = {'side': 'left', 'fill': 'x', 'expand': True}
        self.outer = {'side': 'top', 'fill': 'x'}

        self._parent = parent
        self._selected_tags = selected
        self._selected_buttons: List[TagButton] = []
        self._unselected_tags = unselected
        self._unselected_buttons: List[TagButton] = []

        self._filter_var = StringVar()
        self._trace = self._filter_var.trace_add('write', self.regrid)

        self._button_holder = Frame(master=self)
        self._none = Button(master=self._button_holder, text='None', command=self.select_none)
        self._invert = Button(master=self._button_holder, text='Invert', command=self.select_invert)
        self._all = Button(master=self._button_holder, text='All', command=self.select_all)
        self._none.pack(**self.inner)
        self._invert.pack(**self.inner)
        self._all.pack(**self.inner)
        self._button_holder.pack(**self.outer)

        self._filter = Entry(master=self, textvariable=self._filter_var)
        self._filter.pack(side='top', fill='x')

        self._label_holder = Frame(master=self)
        self._unselected_label = Label(master=self._label_holder, text='Out', anchor='c')
        self._selected_label = Label(master=self._label_holder, text='In', anchor='c')
        self._unselected_label.pack(**self.inner)
        self._selected_label.pack(**self.inner)
        self._label_holder.pack(**self.outer)

        self._frame_holder = Frame(master=self)
        self._unselected_frame = VScrolledFrame(master=self._frame_holder)
        self._selected_frame = VScrolledFrame(master=self._frame_holder)
        self._unselected_frame.pack()
        self._selected_frame.pack()
        self._frame_holder.pack(side='top')
        self.bind('<Configure>', self.resize)

        self.regrid()

    @property
    def selected_tags(self):
        return self._selected_tags

    @property
    def unselected_tags(self):
        return self._unselected_tags

    def resize(self, event=None):
        # TODO finish
        # self._frame_holder.config(width=self.winfo_width(), height=self.winfo_height())
        # print([x.winfo_width() for x in self._unselected_frame.outer.pack_slaves()])
        pass

    def swap(self, button: TagButton):
        tag = button.tag
        found = False
        for b in self._selected_buttons:
            if found:
                break
            if tag == b.tag:
                self._selected_tags.remove(tag)
                self._unselected_tags.append(tag)
                found = True
        if not found:
            self._unselected_tags.remove(tag)
            self._selected_tags.append(tag)
        # self._filter_var.set('')
        self._filter.focus()
        self.regrid()

    def select_all(self):
        self._selected_tags += self._unselected_tags
        self._unselected_tags.clear()
        self.regrid()

    def select_none(self):
        self._unselected_tags += self._selected_tags
        self._selected_tags.clear()
        self.regrid()

    def select_invert(self):
        temp = self._unselected_tags
        self._unselected_tags = self._selected_tags
        self._selected_tags = temp
        self.regrid()

    def regrid(self, *args):
        unselected_frame = VScrolledFrame(master=self._frame_holder, width=150, height=332, background='dark gray')
        selected_frame = VScrolledFrame(master=self._frame_holder, width=150, height=332, background='dark gray')

        self._unselected_buttons.clear()
        self._selected_buttons.clear()
        self._selected_tags.sort()
        self._unselected_tags.sort()
        for tag in self._unselected_tags:
            if self._filter_var.get().lower() in tag.lower():
                button = TagButton(tag=tag, text=tag, master=unselected_frame, takefocus=True)
                button.configure(command=lambda b=button: self.swap(b))
                self._unselected_buttons.append(button)
        for tag in self._selected_tags:
            if self._filter_var.get().lower() in tag.lower():
                button = TagButton(tag=tag, text=tag, master=selected_frame, takefocus=True)
                button.configure(command=lambda b=button: self.swap(b))
                self._selected_buttons.append(button)

        for i in range(len(self._unselected_buttons)):
            self._unselected_buttons[i].pack(fill='x', expand=True)

        for i in range(len(self._selected_buttons)):
            self._selected_buttons[i].pack(fill='x', expand=True)

        temp1 = self._unselected_frame
        temp2 = self._selected_frame
        self._unselected_frame = unselected_frame
        self._selected_frame = selected_frame
        self._unselected_frame.pack(side='left')
        self._selected_frame.pack(side='left')

        temp1.destroy()
        temp2.destroy()

    def exit(self):
        self._selected_tags.sort()
        self._parent.selected_tags = self.selected_tags
        self._filter_var.trace_remove('unset', self._trace)
        self.unbind('<Configure>')
        self.destroy()


class TagIntVar(IntVar):
    def __init__(self, tag, **kwargs):
        super(TagIntVar, self).__init__(**kwargs)

        self._tag = tag

    @property
    def tag(self):
        return self._tag


class TagsFrameV2(Frame):
    # TODO finish
    def __init__(self, reader: FilteredReader, **kwargs):
        super(TagsFrameV2, self).__init__(**kwargs)

        self._reader = reader

        self._all_tags = []
        self._selected_tags = []
        self._unselected_tags = []

        self._filter_var = StringVar(master=self, value='', name='tags_filter')
        self._trace = self._filter_var.trace_add('write', self.repack)
        self._tag_vars: List[TagIntVar] = []
        self._sort_var = IntVar(master=self, value=1, name='sort')

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

        self._popup_button = Button(master=self, text='Tags', command=self.popup)
        self._filter = Entry(master=self, textvariable=self._filter_var)
        self._buttons = Frame(master=self, width=self.winfo_width() - 15, height=self.winfo_height() - 47)

        self._popup_button.pack(fill='x', expand=True)
        self._filter.pack(fill='x', expand=True)
        self._buttons.pack(fill='both', expand=True)

        self._options_frame = Frame(master=self)
        self._sort = Checkbutton(master=self._options_frame, variable=self._sort_var, text='autosort',
                                 command=self.repack)
        self._sort.pack(side='right')
        self._options_frame.pack(side='bottom', fill='x', expand=True)

        self.style = Style()
        self.style.configure('selected.TCheckbutton', background='dark gray')

        self.bind('<Configure>', self.repack)

    @property
    def all_tags(self):
        return self._all_tags

    @property
    def selected_tags(self):
        return self._selected_tags

    @selected_tags.setter
    def selected_tags(self, tags: List[str]):
        self._all_tags = list(set(self._all_tags).union(tags).union(self._reader.all_tags))
        self._tag_vars = [TagIntVar(tag=tag, value=1 if tag in tags else 0) for tag in self._all_tags]
        self._tag_vars.sort(key=lambda x: x.tag)
        self._selected_tags = tags
        self._unselected_tags = list(set(self._all_tags).difference(self._selected_tags))
        self._reader.tags_has = tuple(tags)
        self.repack()

    @property
    def unselected_tags(self):
        return self._unselected_tags

    def refresh(self):
        """Refreshes tags information from the reader"""
        pass

    def repack(self, *args):
        frame = VScrolledFrame(master=self, width=self.winfo_width() - 15, height=self.winfo_height() - 47)
        temp = self._buttons
        if self._sort_var.get() == 1:
            selected = [var for var in self._tag_vars if
                        self._filter_var.get().lower() in var.tag.lower() and var.get() == 1]
            unselected = [var for var in self._tag_vars if
                          all([var not in selected, self._filter_var.get().lower() in var.tag.lower(), var.get() == 0])]
            all_ = selected + unselected
        else:
            all_ = [var for var in self._tag_vars if self._filter_var.get().lower() in var.tag.lower()]
        for var in all_:
            button = Checkbutton(master=frame, text=var.tag, variable=var, command=self.swap, style='selected.TCheckbutton' if var.get() == 1 else '')
            button.pack(fill='x', expand=True)
        self._buttons = frame
        self._buttons.pack(fill='both', expand=True)
        temp.destroy()

    def swap(self):
        tags = [x.tag for x in self._tag_vars if x.get() == 1]
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
    reader = FilteredReader()
    root = Tk()
    root.geometry('400x500')
    # for i in range(6):
    #     root.grid_columnconfigure(index=i, weight=1)
    root.grid_rowconfigure(index=0, weight=1)
    tags = TagsFrameV2(master=root, reader=reader)
    tags.pack(fill='both', expand=True)
    tags.selected_tags = ['Purple', 'Green', 'Blue', '1', '2', '3']
    root.mainloop()


if __name__ == '__main__':
    _test()
