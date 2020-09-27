from tkinter import StringVar, Event
from tkinter.ttk import Button, Label, Frame

from modules import ReaderModule


class ReaderStatsFrame(Frame):
    def __init__(self, reader: ReaderModule, bind_tag: str = None, **kwargs):
        super(ReaderStatsFrame, self).__init__(**kwargs)

        self._bind_tag = bind_tag if bind_tag is not None else ''

        self._reader = reader

        stats_button = Button(master=self, text='Stats')
        stats_button.pack(side='left', padx=(5, 0))

        self.status_label_var = StringVar(name='status_var.{}'.format(self._bind_tag))

        self._status_label = Label(master=self, textvariable=self.status_label_var)

        self.counter_label_var = StringVar(name='counter_var.{}'.format(self._bind_tag), value='0 | 0')

        counter_label = Label(master=self, textvariable=self.counter_label_var)
        counter_label.pack(side='right', padx=5)

        count_descriptor = Label(master=self, text='Proportion: ')
        count_descriptor.pack(side='right', padx=(5, 0))

        self.update_counter()

        self.bind_class(self._bind_tag, '<<Filter Attributes Changed>>', self.update_counter, add=True)
        self.bind_class(self._bind_tag, '<<Status Updated>>', self.update_status, add=True)
        self.bind_class(self._bind_tag, '<<Tempfile Updated>>', self.update_counter, add=True)

    def update_counter(self, event: Event = None):
        num = len(self._reader.filtered_ids)
        den = len(self._reader.all_ids)
        try:
            prop = round(100 * num / den)
            text = '{} | {} ({}%)'.format(num, den, prop)
        except ZeroDivisionError:
            text = '{} | {} (N/A)'.format(num, den)
        self.counter_label_var.set(text)

    def update_status(self, event: Event = None):
        # TODO implement events
        pass
