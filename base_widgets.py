"""Contains widget templates"""
from tkinter import Widget
from tkinter.ttk import Frame, Button
from typing import Any


def edit_class_tags(w: Any):
    bindtags = list(w.bindtags())
    bindtags.append('JournalWidget')
    w.bindtags(tuple(bindtags))


class JournalWidget(Widget):
    """A class for identifying and accessing widgets with shared methods"""

    def __init__(self, **kwargs):
        super(JournalWidget, self).__init__(**kwargs)
        bindtags = list(self.bindtags())
        index = bindtags.index('Widget')
        bindtags.insert(index, 'JournalWidget')
        self.bindtags(tuple(bindtags))


class ButtonsFrame(Frame):
    """Accepts a list of str and returns a Frame of vertically stacked buttons"""

    def __init__(self, buttons=None, text=None, command=None, **kwargs):
        """

        :param buttons: either a 2-tuple of a list of string and a callable or a tuple of 2-tuples of str and callable
        :param kwargs:
        """
        super(ButtonsFrame, self).__init__(**kwargs)

        self._frame = Frame(self)
        self._buttons = buttons
        self.set_buttons(buttons, text, command)

    def set_buttons(self, buttons=None, text=None, command=None):
        """Updates the buttons in the frame

        :param buttons:
        :param command:
        :param text:
        """
        if buttons or text and command:
            frame = Frame(master=self)
            if buttons:
                [Button(master=frame, text=tup[0], command=tup[1]).pack() for tup in buttons]
            elif text and command:
                [Button(master=frame, text=t, command=command).pack() for t in text]
            temp = self._frame
            self._frame = frame
            self._frame.pack()
            temp.destroy()
            self._frame.update()

    @property
    def new(self):
        return None

    @new.setter
    def new(self, v):
        frame = Frame(master=self)
        buttons = self._frame.pack_slaves()
        button = Button(master=frame, text=v[0], command=v[1])
        button.pack()
        buttons.append(button)
