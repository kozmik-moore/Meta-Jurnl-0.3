from tkinter.ttk import Frame

from body_gui import BodyFrame
from dates_gui import DatesFrame
from modules import ReaderModule


class ReaderPage(Frame):
    def __init__(self, reader: ReaderModule, **kwargs):
        super(ReaderPage, self).__init__(**kwargs)

        self.reader = reader

        left = DatesFrame(master=self, reader=reader)

        middle = BodyFrame(master=self, reader=reader)

        right = Frame(master=self)
