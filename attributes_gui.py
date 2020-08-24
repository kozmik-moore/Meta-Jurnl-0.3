from os import makedirs
from os.path import exists, join
from tkinter import IntVar, Toplevel
from tkinter.ttk import Frame, Checkbutton, Button, Label

from base_widgets import add_child_class_to_bindtags
from modules import ReaderModule
from scrolled_frame import VScrolledFrame


class AttributesFrame(Frame):
    def __init__(self, reader: ReaderModule, **kwargs):
        super(AttributesFrame, self).__init__(**kwargs)

        self.reader = reader

        self.attachments_chk_var = IntVar(value=0, name='attachments_chk')
        self.parent_chk_var = IntVar(value=0, name='parent_chk')
        self.children_chk_var = IntVar(value=0, name='children_chk')

        self.attachments_frame = Frame(master=self)
        self.attachments_chk = Checkbutton(master=self.attachments_frame, variable=self.attachments_chk_var)
        self.attachments_btn = Button(master=self.attachments_frame, text='Has Attachments',
                                      command=self.attachments_popup)
        self.attachments_chk.pack(side='left')
        self.attachments_btn.pack(side='left', expand=True, fill='x')
        self.attachments_frame.pack(fill='x')

        self.parent_frame = Frame(master=self)
        self.parent_chk = Checkbutton(master=self.parent_frame, variable=self.parent_chk_var)
        self.parent_btn = Button(master=self.parent_frame, text='Has Parent', command=self.set_id_to_parent)
        self.parent_chk.pack(side='left')
        self.parent_btn.pack(side='left', expand=True, fill='x')
        self.parent_frame.pack(fill='x')

        self.children_frame = Frame(master=self)
        self.children_chk = Checkbutton(master=self.children_frame, variable=self.children_chk_var)
        self.children_btn = Button(master=self.children_frame, text='Has Children', command=self.children_popup)
        self.children_chk.pack(side='left')
        self.children_btn.pack(side='left', expand=True, fill='x')
        self.children_frame.pack(fill='x')

        self.attachments_chk_var.set(self.reader.has_attachments)
        self.parent_chk_var.set(self.reader.has_parent)
        self.children_chk_var.set(self.reader.has_children)

        self.attachments_chk_var.trace_add('write', self.set_flag)
        self.parent_chk_var.trace_add('write', self.set_flag)
        self.children_chk_var.trace_add('write', self.set_flag)

        self.set_buttons()

        add_child_class_to_bindtags(self)

        self.bind_class('Parent', '<<Selected Id>>', self.set_buttons, add=True)

    def set_buttons(self, *args):
        self.attachments_btn.state(['!disabled' if self.reader.entry_has_attachments else 'disabled'])
        self.parent_btn.state(['!disabled' if self.reader.entry_has_parent else 'disabled'])
        self.children_btn.state(['!disabled' if self.reader.entry_has_children else 'disabled'])

    def set_flag(self, *args):
        flag = args[0]
        num = int(self.getvar(flag))
        if 'attachments' in flag:
            self.reader.has_attachments = num
        elif 'parent' in flag:
            self.reader.has_parent = num
        elif 'children' in flag:
            self.reader.has_children = num
        self.event_generate('<<Update Ids>>')

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
        self.event_generate('<<Selected Id>>')

    def children_popup(self):
        t = Toplevel()
        t.title('Children: {}'.format(self.reader.get_date(self.reader.id_).strftime('%a, %b %d, %Y %H:%M')))
        add_child_class_to_bindtags(t)
        t.bind('<Escape>', lambda x: t.destroy())

        def set_id(id_: int):
            self.reader.id_ = id_
            t.event_generate('<<Selected Id>>')
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
