from math import floor
from tkinter import StringVar, IntVar, Menu, Toplevel, Event
from tkinter.ttk import Frame, Button, Entry, Checkbutton, Label, Menubutton
from typing import List, TypeVar, Tuple

from PIL import Image, ImageTk

from base_widgets import ScrollingFrame, add_bind_tag_to_bindtags
from modules import ReaderModule
from themes import get_icon

T = TypeVar('T')


class TagIntVar(IntVar):
    def __init__(self, tag, **kwargs):
        super(TagIntVar, self).__init__(**kwargs)

        self._tag = tag

    @property
    def tag(self):
        return self._tag


class TagsPopup(Toplevel):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        location = kwargs.pop('location') if 'location' in kwargs.keys() else ()
        dims = [400, 300, location[0], location[1]] if location else [400, 300]
        super(TagsPopup, self).__init__(**kwargs)

        self.overrideredirect(False)

        self._inside = False
        self._has_focus = True

        self.withdraw()

        self.protocol('WM_DELETE_WINDOW', self.save_and_close)

        self._bind_tag = bind_tag if bind_tag else ''

        self._reader = reader

        self._all_tags = []
        self._selected_tags = []
        self._unselected_tags = []
        self._tag_vars: List[TagIntVar] = []

        self._filter_var = StringVar(master=self,
                                     value='',
                                     name='{}.tags_filter'.format(self._bind_tag))
        self._sort_var = IntVar(master=self,
                                name='{}.sort_var'.format(self._bind_tag))
        self._type_int = IntVar(master=self,
                                name='{}type_var_int'.format(self._bind_tag))
        self._type_str = StringVar(master=self,
                                   name='{}type_var_str'.format(self._bind_tag))

        inner_kwargs = {'side': 'left', 'fill': 'x', 'expand': True}
        outer_kwargs = {'side': 'top', 'fill': 'x'}

        button_holder = Frame(master=self)
        none_button = Button(master=button_holder, text='None', command=self.select_none)
        invert_button = Button(master=button_holder, text='Invert', command=self.select_invert)
        all_button = Button(master=button_holder, text='All', command=self.select_all)
        none_button.pack(**inner_kwargs)
        invert_button.pack(**inner_kwargs)
        all_button.pack(**inner_kwargs)
        button_holder.pack(**outer_kwargs)

        filter_holder = Frame(master=self)
        filter_entry = Entry(master=filter_holder, textvariable=self._filter_var, style='clear.TEntry')
        filter_entry.bind('<Return>', self.add)
        filter_clear_button = Button(master=filter_holder, text='Clear', style='clear.TButton')
        filter_clear_button.configure(command=lambda s='': self._filter_var.set(s))
        filter_entry.pack(side='left', fill='x', expand=True)
        filter_clear_button.pack(side='right')
        filter_holder.pack(fill='x', ipady=1)

        buttons_frame = ScrollingFrame(master=self, width=self.winfo_width() - 15, height=self.winfo_height() - 47)
        buttons_frame.pack(fill='both', expand=True)

        self._inner = buttons_frame.inner

        options_holder = Frame(master=self)
        options_holder.pack(side='bottom', fill='x')

        type_button = Menubutton(master=options_holder,
                                 textvariable=self._type_str,
                                 width=15,
                                 direction='above',
                                 style='tags.TMenubutton')
        type_button.pack(side='left', fill='both', anchor='center')

        # TODO class type_menu or type_button for styling purposes (tk styling restrictions)
        type_menu = Menu(master=type_button, tearoff=0, relief='flat', borderwidth=1)
        type_menu.add_radiobutton(label='Contains Any Of...', value=0, variable=self._type_int, indicatoron=0)
        type_menu.add_radiobutton(label='Contains At Least...', value=1, variable=self._type_int, indicatoron=0)
        type_menu.add_radiobutton(label='Contains Only...', value=2, variable=self._type_int, indicatoron=0)

        type_button['menu'] = type_menu

        sort_button = Checkbutton(master=options_holder, variable=self._sort_var, text='autosort',
                                  command=self.toggle_autosort)
        sort_button.pack(side='right', fill='both', anchor='center')

        self._filter_var_trace = self._filter_var.trace_add('write', self.repack)
        self._type_int_trace = self._type_int.trace_add('write', self.set_filter_type)

        add_bind_tag_to_bindtags(self)

        self._type_int.set(self._reader.tag_filter)
        self._sort_var.set(self._reader.tags_autosort)

        self.selected_tags = self._reader.tags

        dims[2] = dims[2] - dims[0] + 27
        dims[3] = dims[3] + 27
        dims_str = '{}x{}+{}+{}'.format(*dims)

        self.geometry(dims_str)

        self.after(50, self.deiconify)

        self.bind('<Button-1>', self._check_click)

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

    def repack(self, *args):
        if self._sort_var.get() == 1:
            selected = [x for x in self._tag_vars if all([self._filter_var.get().lower() in x.tag.lower(),
                                                          x.get() == 1])]
            unselected = [x for x in self._tag_vars if all([self._filter_var.get().lower() in x.tag.lower(),
                                                            x.get() == 0])]
            all_ = selected + unselected
        else:
            all_ = [var for var in self._tag_vars if self._filter_var.get().lower() in var.tag.lower()]

        for b in self._inner.pack_slaves():
            b.pack_forget()

        for var in all_:
            button = Checkbutton(master=self._inner, text=var.tag, variable=var, command=self.swap)
            button.pack(fill='x', expand=True)

    def add(self, *args):
        tag = self._filter_var.get()
        if tag and tag in self._reader.all_tags:
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
        type_ = ['Contains Any Of...', 'Contains At Least...', 'Contains Only...'][num]
        self._type_str.set(type_)

    def save_and_close(self, *args):
        self._filter_var.trace_remove('write', self._filter_var_trace)
        self._type_int.trace_remove('write', self._type_int_trace)
        self._reader.tags = self.selected_tags
        self.event_generate('<<Tempfile Updated>>')
        self.destroy()

    def _on_enter(self, event: Event):
        self._inside = True

    def _on_exit(self, event: Event):
        self._inside = False

    def _on_focus(self, event: Event):
        self._has_focus = True

    def _on_focus_loss(self, event: Event):
        if 'tagspopup' not in str(event.widget):
            self._has_focus = False

    def _check_click(self, event: Event):
        if str(self) not in str(self.focus_get()):
            self.save_and_close()


class TagsButton(Button):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        super(TagsButton, self).__init__(**kwargs)

        self.filters_icon = get_icon('ic_filter_list')

        self._bind_tag = bind_tag if bind_tag else ''

        self._reader = reader

        self.configure(text='Filter', image=self.filters_icon, command=self.call_popup)

    def call_popup(self, *args):
        popup = TagsPopup(reader=self._reader,
                          bind_tag=self._bind_tag,
                          location=(self.winfo_rootx(), self.winfo_rooty()))
        popup.grab_set()
        popup.focus_set()


class TagsFrame(Frame):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        super(TagsFrame, self).__init__(**kwargs)

        self._bind_tag = bind_tag if bind_tag else ''

        self._reader = reader

        header = Frame(master=self, relief='ridge', borderwidth=1, padding=5)
        header.pack(fill='x')

        header_label = Label(master=header, text='TAGS')
        header_label.pack(side='left')

        popup_button = TagsButton(master=header, reader=self._reader, bind_tag=self._bind_tag)
        popup_button.pack(side='right')

        self._tags_frame = ScrollingFrame(master=self, relief='ridge', borderwidth=1, padding=5)
        self._tags_frame.pack(fill='both', expand=True)

        self._update_tags()

        self.bind_class(self._bind_tag, '<<Id Selected>>', self._update_tags, add=True)

    def _update_tags(self, *args):
        for label in self._tags_frame.inner.pack_slaves():
            label.pack_forget()
        for tag in self._reader.entry_tags:
            label = Label(master=self._tags_frame.inner, text=tag)
            label.pack(fill='x', expand=True, anchor='center')


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
