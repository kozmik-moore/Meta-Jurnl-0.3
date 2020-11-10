"""Contains widget templates"""
from tkinter import Widget, Canvas
from tkinter.ttk import Frame, Button, Scrollbar, Style, Entry
from typing import Any

from modules import ReaderModule


def add_filter_class_to_bindtags(w: Any):
    bindtags = list(w.bindtags())
    bindtags.insert(2, 'FilterSetter')
    w.bindtags(tuple(bindtags))


def add_child_class_to_bindtags(w: Any):
    bindtags = list(w.bindtags())
    id_ = w.bind_tag
    bindtags.insert(2, 'Child.{}'.format(id_))
    w.bindtags(tuple(bindtags))


def add_parent_class_to_bindtags(w: Any):
    bindtags = list(w.bindtags())
    id_ = w.bind_tag
    bindtags.insert(2, 'Parent.{}'.format(id_))
    w.bindtags(tuple(bindtags))


def add_bind_tag_to_bindtags(w: Any):
    bindtags = list(w.bindtags())
    id_ = w.bind_tag
    bindtags.insert(2, id_)
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


class TagEntry(Entry):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        super(TagEntry, self).__init__(**kwargs)

        self._bind_tag = bind_tag if bind_tag else ''

        self._reader = reader


class ScrollingFrame(Frame):
    def __init__(self, **kwargs):
        super(ScrollingFrame, self).__init__(**kwargs)

        style = Style()

        canvas = Canvas(master=self)
        scrollbar = Scrollbar(master=self, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        self.inner = inner = Frame(master=canvas)

        self.inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        inner_id = canvas.create_window((0, 0), window=self.inner, anchor='nw')
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        def _bind_mouse(event=None):
            canvas.bind_all("<4>", _on_mousewheel)
            canvas.bind_all("<5>", _on_mousewheel)
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mouse(event=None):
            canvas.unbind_all("<4>")
            canvas.unbind_all("<5>")
            canvas.unbind_all("<MouseWheel>")

        def _on_mousewheel(event):
            """Linux uses event.num; Windows / Mac uses event.delta"""
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                canvas.yview_scroll(1, "units")

        def _configure_inner(event):
            # update the scrollbars to match the size of the inner frame
            size = (inner.winfo_reqwidth(), inner.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if inner.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=inner.winfo_reqwidth())

        inner.bind('<Configure>', _configure_inner)

        def _configure_canvas(event):
            if inner.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(inner_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)

        canvas.bind("<Enter>", _bind_mouse)
        canvas.bind("<Leave>", _unbind_mouse)


# class GraphGrid:
#     def __init__(self, height=1, width=1, **kwargs):
#
#         self._grid = [[None for y in range(width)] for x in range(height)]


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()
    f = ScrollingFrame(master=root)
    for i in range(20):
        frame = Frame(master=f.inner)
        for j in range(3):
            Button(master=frame, text='{}-{}'.format(i, j)).pack(side='left')
        frame.pack()
    f.pack()
    root.mainloop()
