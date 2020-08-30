from datetime import datetime
from tkinter import StringVar, Toplevel
from tkinter.ttk import Frame, Label, Button, Combobox

from modules import WriterModule


class DateFrame(Frame):
    def __init__(self, writer: WriterModule, bind_name: str = None, **kwargs):
        super(DateFrame, self).__init__(**kwargs)

        self._bind_name = bind_name if bind_name is not None else ''

        self._label_var = StringVar(name='{}label_var'.format(self._bind_name))

        self._writer = writer

        self._label = Label(master=self, textvariable=self._label_var, width=30, anchor='c')
        self._label.pack(side='left', expand=True, fill='x')

        self.button = Button(master=self, text='Set Date', command=self.popup)
        self.button.pack(side='left')

        if self._writer.date:
            d = self._writer.date.strftime('%a, %b %d, %Y %H:%M')
        else:
            d = 'Not Set'
        self._label_var.set(d)

        self.button.bind('<Button-3>', self.set_date)
        self.bind_class('Parent.{}'.format(self._bind_name), '<<Clear Contents>>', self.clear)

    def set_date(self, event):
        d = datetime.now()
        ds = d.strftime('%a, %b %d, %Y %H:%M')
        self._writer.date = d
        self._label_var.set(ds)

    def clear(self):
        self._label_var.set('')
        self._writer.date = None

    def popup(self):

        def get_days(m: str, y: str):
            d = ['{:02d}'.format(x) for x in range(1, 32)]
            if m in ['Apr', 'Jun', 'Sep', 'Nov']:
                d.pop(-1)
            elif m == 'Feb':
                d = d[0:29]
                if (int(y) % 100 == 0 and int(y) % 400 != 0) or int(y) % 4 != 0:
                    d = d[0:28]
            return d

        t = Toplevel()
        t.title('Set Date')
        # t.overrideredirect(True)

        # TODO get this working
        def _set_position(*args):
            t.update_idletasks()
            pos = self.button.winfo_rootx(), self.winfo_rooty()
            size = self.button.winfo_width(), self.winfo_height()
            offset = pos[0] + size[0], pos[1] + size[1]

            t.geometry('{}x{}+{}+{}'.format(t.winfo_reqwidth(), t.winfo_reqheight(), offset[0] - t.winfo_width(), offset[1]))
            print(args)

        # self.button.bind('<Configure>', _set_position)

        b = list(t.bindtags())
        b.insert(2, 'Child.{}'.format(self._bind_name))
        t.bindtags(b)

        if self._writer.date:
            year = self._writer.date.year
            month = self._writer.date.month
            day = self._writer.date.day
            hour = self._writer.date.hour
            minute = self._writer.date.minute
        else:
            year = self._writer.current_year
            month = self._writer.current_month
            day = self._writer.current_day
            hour = self._writer.current_hour
            minute = self._writer.current_minute

        years = [str(x) for x in range(1900, self._writer.current_year + 1)]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        days = []
        hours = ['{:02d}'.format(x) for x in range(0, 24)]
        minutes = ['{:02d}'.format(x) for x in range(0, 60)]

        year_var = StringVar(name='{}.year_var'.format(self._bind_name), value=str(year))
        month_var = StringVar(name='{}.month_var'.format(self._bind_name), value=months[month - 1])
        day_var = StringVar(name='{}.day_var'.format(self._bind_name), value=str(day))
        hour_var = StringVar(name='{}.hour_var'.format(self._bind_name), value='{:02d}'.format(hour))
        minute_var = StringVar(name='{}.minute_var'.format(self._bind_name), value='{:02d}'.format(minute))

        frame = Frame(master=t)

        year_box = Combobox(master=frame, textvariable=year_var, values=years, justify='center', width=10)
        month_box = Combobox(master=frame, textvariable=month_var, values=months, justify='center', width=10)
        day_box = Combobox(master=frame, textvariable=day_var, values=days, justify='center', width=10)
        hour_box = Combobox(master=frame, textvariable=hour_var, values=hours, justify='center', width=10)
        minute_box = Combobox(master=frame, textvariable=minute_var, values=minutes, justify='center', width=10)

        def check_month(*args):
            d = get_days(month_var.get(), year_var.get())
            day_box.configure(values=d)
            check_day()

        def check_day(*args):
            d = get_days(month_var.get(), year_var.get())
            if day_var.get() not in d:
                day_var.set(d[-1])

        year_var.trace_add('write', check_day)
        month_var.trace_add('write', check_day)
        day_box.configure(postcommand=check_month)

        year_box.pack(side='left')
        month_box.pack(side='left')
        day_box.pack(side='left')
        hour_box.pack(side='left')
        minute_box.pack(side='left')
        frame.pack(fill='x')
        # _set_position()

        def on_close(*args):
            v = {'year': int(year_var.get()),
                 'month': months.index(month_var.get()) + 1,
                 'day': int(day_var.get()),
                 'hour': int(hour_var.get()),
                 'minute': int(minute_var.get()),
                 'second': 0,
                 'microsecond': 0}
            date = datetime(**v)
            self._label_var.set(date.strftime('%a, %b %d, %Y %H:%M'))
            self._writer.date = date
            self.unbind('<Configure>')
            t.destroy()

        t.protocol('WM_DELETE_WINDOW', on_close)
        t.bind('<Escape>', on_close)

        t.grab_set()
        t.focus()


def _test():
    from tkinter import Tk

    r = Tk()

    w = WriterModule('.tempfiles/Writer/000')

    d = DateFrame(master=r, writer=w)
    d.pack(fill='x')

    r.mainloop()


if __name__ == '__main__':
    _test()
    # TODO make comboboxes, link to IntVars, create commands to autoupdate for specific vars (trace_adds?)
