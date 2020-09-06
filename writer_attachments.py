from tkinter.ttk import Button

from PIL import Image, ImageTk

from modules import WriterModule


class AttachmentsButton(Button):
    def __init__(self, writer: WriterModule, bind_name: str = None, **kwargs):
        super(AttachmentsButton, self).__init__(**kwargs)

        img = Image.open('.resources/attachments_icon.png')
        img = img.resize((16, 16))
        self.attachments_icon = ImageTk.PhotoImage(image=img)

        self._bind_name = bind_name if bind_name is not None else ''

        self._writer = writer

        self.configure(image=self.attachments_icon)
