from tkinter import Frame, StringVar, Event
from tkinter.ttk import Button, Label

from modules import WriterModule


# TODO add stats about tags usage, attachments, last edit, connections
class WriterStatsFrame(Frame):
    def __init__(self, writer: WriterModule, bind_tag: str = None, **kwargs):
        super(WriterStatsFrame, self).__init__(**kwargs)

        self._bind_tag = bind_tag if bind_tag is not None else ''

        self._writer = writer
        
        stats_button = Button(master=self, text='Stats')
        stats_button.pack(side='left', padx=(5, 0))

        self.status_label_var = StringVar(name='status_var.{}'.format(self._bind_tag))

        self._status_label = Label(master=self, textvariable=self.status_label_var)

        self.counter_label_var = StringVar(name='counter_var.{}'.format(self._bind_tag), value='0 | 0')
        
        counter_label = Label(master=self, textvariable=self.counter_label_var)
        counter_label.pack(side='right', padx=5)
        
        count_descriptor = Label(master=self, text='character | word')
        count_descriptor.pack(side='right', padx=(5, 0))

        self.bind_class(self._bind_tag, '<<Writer Changed>>', self.update_counter)
        self.bind_class(self._bind_tag, '<<Status Updated>>', self.update_status, add=True)
        self.update_counter()

    def update_counter(self, event: Event = None):
        words = self._writer.body.split(' ')
        words = len([x for x in words if x])
        chars = len(self._writer.body)
        try:
            prop = round(chars / words, 2)
            text = '{} | {} ({:.2f})'.format(chars, words, prop)
        except ZeroDivisionError:
            text = '{} | {} (UNDEF)'.format(chars, words)
        self.counter_label_var.set(text)

    def update_status(self, event: Event = None):
        # TODO implement events
        pass
