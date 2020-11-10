from os import makedirs
from os.path import exists, join
from tkinter import IntVar, Toplevel, Event, Menubutton, Menu
from tkinter.ttk import Frame, Button, Label

from base_widgets import add_bind_tag_to_bindtags
from modules import ReaderModule
from scrolled_frame import VScrolledFrame
from themes import get_icon


class AttributesButton(Menubutton):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        super(AttributesButton, self).__init__(**kwargs)

        self.filters_icon = get_icon('ic_filter_list')

        self._bind_tag = bind_tag if bind_tag else ''

        self._reader = reader

        self.attachments_chk_var = IntVar(value=self._reader.has_attachments,
                                          name='{}attachments_chk'.format(self._bind_tag))
        self.parent_chk_var = IntVar(value=self._reader.has_parent, name='{}parent_chk'.format(self._bind_tag))
        self.children_chk_var = IntVar(value=self._reader.has_children, name='{}children_chk'.format(self._bind_tag))

        menu = Menu(master=self, tearoff=0)
        menu.add_checkbutton(label='Has Attachments',
                             variable=self.attachments_chk_var,
                             command=lambda: self._update_reader('attachments'))
        menu.add_checkbutton(label='Has Parent',
                             variable=self.parent_chk_var,
                             command=lambda: self._update_reader('parent'))
        menu.add_checkbutton(label='Has Children',
                             variable=self.children_chk_var,
                             command=lambda: self._update_reader('children'))

        self.configure(menu=menu,
                       image=self.filters_icon,
                       indicatoron=0, relief='raised',
                       height=25,
                       width=25,
                       direction='left')

        add_bind_tag_to_bindtags(self)

        self.bind_class(self._bind_tag, '<<Tempfile Updated>>', self.update_from_tempfile, add=True)

    @property
    def bind_tag(self):
        return self._bind_tag

    def _update_reader(self, *args):
        if args[0] == 'attachments':
            self._reader.has_attachments = self.attachments_chk_var.get()
        if args[0] == 'parent':
            self._reader.has_parent = self.parent_chk_var.get()
        if args[0] == 'children':
            self._reader.has_children = self.children_chk_var.get()
        self.event_generate('<<Tempfile Updated>>')

    def update_from_tempfile(self, *args):
        # TODO finish
        pass


class AttributesFrame(Frame):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        super(AttributesFrame, self).__init__(**kwargs)

        self.attachments_icon = get_icon('ic_attach_file')
        self.parent_icon = get_icon('ic_person')
        self.children_icon = get_icon('ic_people')

        self._bind_tag = bind_tag if bind_tag else ''

        self.reader = reader

        header = Frame(master=self, padding=5, relief='sunken', borderwidth=1)
        header.pack(fill='x')

        Label(master=header, text='ATTRIBUTES').pack(side='left')
        AttributesButton(master=header, reader=self.reader, bind_tag=self._bind_tag).pack(side='right', fill='both')

        content_frame = Frame(master=self, padding=5, relief='sunken', borderwidth=1)
        content_frame.pack(fill='x')

        self.attachments_btn = Button(master=content_frame,
                                      text='Has Attachments',
                                      image=self.attachments_icon,
                                      command=self.attachments_popup)
        self.attachments_btn.pack(side='left', expand=True, fill='x')

        self.parent_btn = Button(master=content_frame,
                                 text='Has Parent',
                                 command=self.set_id_to_parent,
                                 image=self.parent_icon)
        self.parent_btn.pack(side='left', expand=True, fill='x')

        self.children_btn = Button(master=content_frame,
                                   text='Has Children',
                                   command=self.children_popup,
                                   image=self.children_icon)
        self.children_btn.pack(side='left', expand=True, fill='x')

        self.set_buttons()

        add_bind_tag_to_bindtags(self)

        self.bind_class('{}'.format(self._bind_tag), '<<Id Selected>>', self.set_buttons, add=True)
        self.bind_class(self._bind_tag, '<<Tempfile Updated>>', self.set_buttons, add=True)

    @property
    def bind_tag(self):
        return self._bind_tag

    def set_buttons(self, event: Event = None):
        self.attachments_btn.state(['!disabled' if self.reader.entry_has_attachments else 'disabled'])
        self.parent_btn.state(['!disabled' if self.reader.entry_has_parent else 'disabled'])
        self.children_btn.state(['!disabled' if self.reader.entry_has_children else 'disabled'])

    def attachments_popup(self):
        t = Toplevel()
        t.title('Attachments: {}'.format(self.reader.get_date(self.reader.id_).strftime('%a, %b %d, %Y %H:%M')))
        t.bind('<Escape>', lambda x: t.destroy())

        def export_file(id_: int):
            out = 'Exports'
            if not exists(out):
                makedirs(out)
            with open(join(out, self.reader.get_attachment_name(id_)), 'wb') as file:
                file.write(self.reader.get_attachment_file(id_))
                file.close()

        e = self.reader.id_
        f = VScrolledFrame(master=t)
        for att in self.reader.entry_attachments:
            button = Button(master=f, text=self.reader.get_attachment_name(att), command=lambda x=att: export_file(x))
            button.pack(fill='x')
        f.pack()
        t.grab_set()
        t.focus()

    def set_id_to_parent(self):
        self.reader.id_ = self.reader.entry_parent
        self.event_generate('<<Id Selected>>')

    def children_popup(self):
        t = Toplevel()
        t.title('Children: {}'.format(self.reader.get_date(self.reader.id_).strftime('%a, %b %d, %Y %H:%M')))
        b = list(t.bindtags())
        b.insert(2, '{}'.format(self._bind_tag))
        t.bindtags(b)

        t.bind('<Escape>', lambda x: t.destroy())

        def set_id(id_: int):
            self.reader.id_ = id_
            t.event_generate('<<Id Selected>>')
            t.destroy()

        f = VScrolledFrame(master=t)
        c = self.reader.entry_children
        for child in c:
            button = Button(master=f, text='{} ({})'.format(self.reader.get_date(child).strftime('%a, %b %d, %Y %H:%M'),
                                                            child),
                            command=lambda x=child: set_id(x))
            button.pack(fill='x')
        f.pack()
        t.grab_set()
        t.focus()


def _test():
    from tkinter import Tk
    root = Tk()
    reader = ReaderModule('.tempfiles/Reader/000')
    a = AttributesFrame(master=root, reader=reader)
    a.pack()
    root.mainloop()


if __name__ == '__main__':
    _test()
