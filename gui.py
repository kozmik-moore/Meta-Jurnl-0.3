from tkinter import StringVar, Toplevel
from tkinter.ttk import Frame, Button, Entry, Label
from typing import List

from base_widgets import JournalWidget
from filter import FilteredReader


class TagsFrame(Frame, JournalWidget):
    def __init__(self, reader: FilteredReader = None, **kwargs):
        super(TagsFrame, self).__init__(**kwargs)

        self.grid_columnconfigure(index=0, weight=1)

        self._reader = reader

        self._all_tags = []
        self._selected_tags = []
        self._unselected_tags = []

        self._filter_var = StringVar(master=self, value='', name='tags_filter')

        self._popup_button = Button(master=self, text='Tags', command=self.popup)
        self._filter = Entry(master=self, textvariable=self._filter_var)
        self._buttons_frame = Frame(master=self)
        frame = Frame(self._buttons_frame)

        self._popup_button.grid(row=0, sticky='ew')
        self._filter.grid(row=1, sticky='ew')
        frame.grid()
        self._buttons_frame.grid(row=2, sticky='ew')
        self._buttons_frame.grid_columnconfigure(index=0, weight=1)

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
        frame = Frame(master=self._buttons_frame)
        frame.grid_columnconfigure(index=0, weight=1)
        temp = self._buttons_frame.grid_slaves()[0]
        for i in range(len(self._selected_tags)):
            button = Button(master=frame, text=self._selected_tags[i])
            button.configure(command=lambda b=button, t=self._selected_tags[i]: self.remove(b, t))
            button.grid(row=i, sticky='ew')
        temp.destroy()
        frame.grid(row=0, sticky='ew')
        self._reader.tags_has = tuple(tags)

    @property
    def unselected_tags(self):
        return self._unselected_tags

    def refresh(self):
        """Refreshes tags information from the reader"""
        pass

    def remove(self, button: Button, tag: str):
        button.destroy()
        self._selected_tags.remove(tag)
        self._unselected_tags.append(tag)
        self._unselected_tags.sort()

    def popup(self):
        popup = TagsPopup(self, self._selected_tags, self._unselected_tags)
        popup.grab_set()
        popup.focus()


class TagButton(Button):
    def __init__(self, tag: str, **kwargs):
        super(TagButton, self).__init__(**kwargs)

        self._tag = tag

    @property
    def tag(self):
        return self._tag


class TagsPopup(Toplevel):

    def __init__(self, parent: TagsFrame, selected: List[str], unselected: List[str], **kwargs):
        super(TagsPopup, self).__init__(**kwargs)

        self.geometry('300x300')
        for i in range(6):
            self.grid_columnconfigure(index=i, weight=1)
        self.protocol('WM_DELETE_WINDOW', self.exit)
        self._parent = parent

        self._filter_var = StringVar()
        self._trace = self._filter_var.trace_add('write', self.regrid)

        self._selected_label = Label(master=self, text='In')
        self._unselected_label = Label(master=self, text='Out')
        self._selected_frame = Frame(master=self)
        self._unselected_frame = Frame(master=self)
        self._none = Button(master=self, text='None', command=self.select_none)
        self._invert = Button(master=self, text='Invert', command=self.select_invert)
        self._all = Button(master=self, text='All', command=self.select_all)
        self._filter = Entry(master=self, textvariable=self._filter_var)

        self._selected_tags = selected
        self._selected_buttons: List[TagButton] = []
        self._unselected_tags = unselected
        self._unselected_buttons: List[TagButton] = []

        self._none.grid(row=0, column=0, columnspan=2, sticky='ew')
        self._invert.grid(row=0, column=2, columnspan=2, sticky='ew')
        self._all.grid(row=0, column=4, columnspan=2, sticky='ew')
        self._filter.grid(row=1, columnspan=6, sticky='ew')
        self._unselected_label.grid(row=2, column=0, columnspan=3)
        self._selected_label.grid(row=2, column=3, columnspan=3)
        self.regrid()

    @property
    def selected_tags(self):
        return self._selected_tags

    @property
    def unselected_tags(self):
        return self._unselected_tags

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
        self._filter_var.set('')
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
        unselected = Frame(master=self)
        selected = Frame(master=self)
        self._unselected_buttons.clear()
        self._selected_buttons.clear()
        self._selected_tags.sort()
        self._unselected_tags.sort()
        for tag in self._unselected_tags:
            if self._filter_var.get().lower() in tag.lower():
                button = TagButton(tag=tag, text=tag, master=unselected, takefocus=True)
                button.configure(command=lambda b=button: self.swap(b))
                self._unselected_buttons.append(button)
        for tag in self._selected_tags:
            if self._filter_var.get().lower() in tag.lower():
                button = TagButton(tag=tag, text=tag, master=selected, takefocus=True)
                button.configure(command=lambda b=button: self.swap(b))
                self._selected_buttons.append(button)

        for i in range(len(self._unselected_buttons)):
            self._unselected_buttons[i].grid(row=i, sticky='ew')

        for i in range(len(self._selected_buttons)):
            self._selected_buttons[i].grid(row=i, sticky='ew')

        selected.columnconfigure(index=0, weight=1)
        unselected.columnconfigure(index=0, weight=1)

        temp1 = self._selected_frame
        temp2 = self._unselected_frame
        self._selected_frame = selected
        self._unselected_frame = unselected
        self._unselected_frame.grid(row=3, column=0, columnspan=3, sticky='ewn')
        self._selected_frame.grid(row=3, column=3, columnspan=3, sticky='ewn')
        temp1.destroy()
        temp2.destroy()

    def exit(self):
        self._selected_tags.sort()
        self._parent.selected_tags = self.selected_tags
        self._filter_var.trace_remove('unset', self._trace)
        self.destroy()


def _test():
    from tkinter import Tk
    reader = FilteredReader()
    root = Tk()
    root.grid_columnconfigure(index=0, weight=1)
    tags = TagsFrame(master=root, reader=reader)
    tags.pack()
    tags.selected_tags = ['Purple', 'Green', 'Blue']
    root.mainloop()


if __name__ == '__main__':
    _test()
