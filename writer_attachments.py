from os import makedirs
from os.path import exists, join, basename
from tkinter import Toplevel
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Button, Frame, Label

from PIL import Image, ImageTk

from base_widgets import ScrollingFrame
from modules import WriterModule
from scrolled_frame import VScrolledFrame


class AttachmentsButton(Button):
    def __init__(self, writer: WriterModule, bind_tag: str = None, **kwargs):
        super(AttachmentsButton, self).__init__(**kwargs)

        img = Image.open('.resources/attachments_icon.png')
        img = img.resize((16, 16))
        self.attachments_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/add_icon.png')
        img = img.resize((16, 16))
        self.add_icon = ImageTk.PhotoImage(image=img)

        img = Image.open('.resources/subtract_icon.png')
        img = img.resize((16, 16))
        self.subtract_icon = ImageTk.PhotoImage(image=img)

        self._bind_tag = bind_tag if bind_tag is not None else ''

        self._writer = writer

        self.configure(image=self.attachments_icon, command=self.popup)

    #     self.bind('<B1-Motion>', self.wait_for_mouse)
    #     self.bind('<Leave>', self.on_exit)
    #
    # def wait_for_mouse(self, *args):
    #     self.bind('<Enter>', self.on_enter)
    #
    # def on_enter(self, *args):
    #     self.bind('<ButtonRelease-1>', self.add_attachment)
    #     print('enter')
    #
    # def on_exit(self, *args):
    #     print('exit')
    #     self.unbind('<ButtonRelease-1>')
    #     self.unbind('<Enter>')
    #
    # def add_attachment(self, *args):
    #     print(args)

    def popup(self):
        t = Toplevel()
        t.title('Attachments')

        def export_file(id_: int):
            out = 'Exports'
            if not exists(out):
                makedirs(out)
            with open(join(out, self._writer.attachment_name(id_)), 'wb') as file:
                file.write(self._writer.attachment_file(id_))
                file.close()

        f = ScrollingFrame(master=t)
        f.pack(side='top', fill='x', expand=True)

        def repack():
            for child in f.inner.pack_slaves():
                child.pack_forget()
            for att in self._writer.attachments:
                text = self._writer.attachment_name(att) if type(att) == int else basename(att) + ' *'
                label = Label(master=f.inner, text=text, relief='solid', anchor='center')
                label.pack(fill='x', expand=True, padx=5, pady=(5, 0))

        repack()

        def open_file_dialog():
            incoming = 'Imports'
            if not exists(incoming):
                makedirs(incoming)
            path = askopenfilename(initialdir=incoming, title='Add Attachment')
            if path:
                self._writer.add_attachment(path)
                repack()
            t.lift()
            t.focus_get()

        footer = Frame(master=t, relief='ridge', borderwidth=1)
        footer.pack(fill='x', expand=True, ipady=5)
        add = Button(master=footer, text='Add', image=self.add_icon, compound='right', command=open_file_dialog)
        add.pack(side='left', padx=(5, 5))
        remove = Button(master=footer, text='Remove', image=self.subtract_icon, compound='right')
        remove.pack(side='left', padx=(0, 5))
        remove.state(['disabled'])

        def close_window():
            t.event_generate('<<Check Save Button>>')
            t.destroy()

        t.protocol('WM_DELETE_WINDOW', close_window)
        t.bind('<Escape>', lambda x: close_window())
        t.grab_set()
        t.focus()
