from datetime import datetime
from tkinter import Toplevel, StringVar, IntVar
from tkinter.font import Font
from tkinter.ttk import Frame, Checkbutton, Button, Scale, Label, Style, Radiobutton, Separator, Labelframe
from typing import Tuple

from PIL import Image, ImageTk

from base_widgets import add_parent_class_to_bindtags, add_child_class_to_bindtags
from filter import check_day_against_month
from modules import ReaderModule
from scrolled_frame import VScrolledFrame

DateId = Tuple[datetime, int]


class DateRadiobutton(Radiobutton):
    def __init__(self, id_: int, **kwargs):
        super(DateRadiobutton, self).__init__(**kwargs)

        self._id = id_

    @property
    def id_(self):
        return self._id


class DatesFrame(Frame):
    def __init__(self, reader: ReaderModule, bind_name: str = None, **kwargs):
        super(DatesFrame, self).__init__(**kwargs)

        self._bind_name = bind_name

        self._reader = reader

        self._ids: Tuple = ()

        font = Font(font='TkDefaultFont')
        font.configure(slant='italic')
        style = Style()
        style.configure('justified.TRadiobutton', anchor='e')

        self.current = IntVar()

        header = Frame(master=self, relief='ridge', borderwidth=1, padding=5)
        header.pack(fill='x')

        img = Image.open('.resources/filter_icon.png')
        img = img.resize((16, 16))
        self.filters_icon = ImageTk.PhotoImage(image=img)

        label = Label(master=header, text='DATES')
        popup = Button(master=header, text='Filters', image=self.filters_icon, command=self.call_popup)
        label.pack(side='left')
        popup.pack(side='right')

        self._buttons = VScrolledFrame(master=self, relief='ridge', borderwidth=1)
        self._buttons.pack(fill='both', expand=True)

        add_parent_class_to_bindtags(self)

        self.bind_class('Child.{}'.format(self._bind_name), '<<Update Ids>>', self.update_ids, add=True)
        self.bind_class('Child.{}'.format(self._bind_name), '<<Selected Id>>', self.set_id_from_child, add=True)
        self.bind_class('TNotebook', '<<Refresh ReaderPages>>', self.refresh, add=True)

    @property
    def bind_name(self):
        return self._bind_name

    @property
    def reader(self):
        return self._reader

    @property
    def dates(self):
        return self._reader.all_dates

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, v: Tuple[int]):
        self._ids = v
        self.repack()

    def repack(self):
        temp = self._buttons
        new = VScrolledFrame(master=self, relief='ridge', borderwidth=1)
        for i in self._ids:
            button = DateRadiobutton(master=new, id_=i,
                                     text=self._reader.get_date(i).strftime('%a, %b %d, %Y %H:%M') + ' ({})'.format(i),
                                     value=i, variable=self.current, style='justified.TRadiobutton',
                                     command=self.set_id_from_self)
            button.pack(fill='x', anchor='e', expand=True)
        new.pack(fill='both', expand=True)
        self._buttons = new
        self._buttons.pack(fill='both', expand=True)
        temp.destroy()

    def call_popup(self):
        popup = DatesPopup(self.current, DateVars(self.reader), old=self.reader.oldest_year,
                           new=self.reader.newest_year, bind_name=self._bind_name)
        popup.grab_set()
        popup.focus()

    def set_id_from_self(self, *args):
        self.reader.id_ = self.current.get()
        self.event_generate('<<Selected Id>>')
        if args and args[0]:
            print(args[0])

    def set_id_from_child(self, *args):
        self.current.set(self.reader.id_ if self.reader.id_ else 0)
        self.event_generate('<<Selected Id>>')

    def update_ids(self, *args):
        self.ids = self.reader.filtered_ids
        if self.reader.id_ in self._ids:
            self.current.set(self.reader.id_)
        else:
            self.current.set(0)
            self.reader.id_ = 0
        self.event_generate('<<Selected Id>>')

    def refresh(self, *args):
        """Refreshes dates information from the reader"""
        self.update_ids()


def month_str(value: int, fmt: str = 'long'):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    s = months[value - 1]
    s = s if fmt == 'long' else s[0:3]
    return s


def weekday_str(value: int, fmt: str = 'long'):
    months = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    s = months[value]
    s = s if fmt == 'long' else s[0:3]
    return s


# TODO subclass Widget to take advantage of getting variables directly
class DateVars:
    def __init__(self, reader: ReaderModule):
        self._reader = reader

        self.sort_var = IntVar()

        self.low_year_int = IntVar(name='low_year_int', value=self._reader.dates['low year'])
        self.high_year_int = IntVar(name='high_year_int', value=self._reader.dates['high year'])
        self.low_month_int = IntVar(name='low_month_int', value=self._reader.dates['low month'])
        self.high_month_int = IntVar(name='high_month_int', value=self._reader.dates['high month'])
        self.low_day_int = IntVar(name='low_day_int', value=self._reader.dates['low day'])
        self.high_day_int = IntVar(name='high_day_int', value=self._reader.dates['high day'])
        self.low_hour_int = IntVar(name='low_hour_int', value=self._reader.dates['low hour'])
        self.high_hour_int = IntVar(name='high_hour_int', value=self._reader.dates['high hour'])
        self.low_minute_int = IntVar(name='low_minute_int', value=self._reader.dates['low minute'])
        self.high_minute_int = IntVar(name='high_minute_int', value=self._reader.dates['high minute'])
        self.low_weekday_int = IntVar(name='low_weekday_int', value=self._reader.dates['low weekday'])
        self.high_weekday_int = IntVar(name='high_weekday_int', value=self._reader.dates['high weekday'])

        self.low_year_str = StringVar(name='low_year_str')
        self.high_year_str = StringVar(name='high_year_str')
        self.low_month_str = StringVar(name='low_month_str')
        self.high_month_str = StringVar(name='high_month_str')
        self.low_day_str = StringVar(name='low_day_str')
        self.high_day_str = StringVar(name='high_day_str')
        self.low_hour_str = StringVar(name='low_hour_str')
        self.high_hour_str = StringVar(name='high_hour_str')
        self.low_minute_str = StringVar(name='low_minute_str')
        self.high_minute_str = StringVar(name='high_minute_str')
        self.low_weekday_str = StringVar(name='low_weekday_str')
        self.high_weekday_str = StringVar(name='high_weekday_str')

        self.low_date_str = StringVar(name='low_date_str')
        self.high_date_str = StringVar(name='high_date_str')

        self.low_year_int.trace_add('write', self._set_strings)
        self.high_year_int.trace_add('write', self._set_strings)
        self.low_month_int.trace_add('write', self._set_strings)
        self.high_month_int.trace_add('write', self._set_strings)
        self.low_day_int.trace_add('write', self._set_strings)
        self.high_day_int.trace_add('write', self._set_strings)
        self.low_hour_int.trace_add('write', self._set_strings)
        self.high_hour_int.trace_add('write', self._set_strings)
        self.low_minute_int.trace_add('write', self._set_strings)
        self.high_minute_int.trace_add('write', self._set_strings)
        self.low_weekday_int.trace_add('write', self._set_strings)
        self.high_weekday_int.trace_add('write', self._set_strings)

        self.sort_var.set(self._reader.date_filter)
        self.set_date_int_vars()
        self._set_date_strings()

    def _set_strings(self, *args):
        e = list(filter(lambda x: x in args[0], ['low', 'high']))[0]
        try:
            t = list(filter(lambda x: x in args[0], ['year', 'day', 'hour', 'minute', 'month']))[0]
        except IndexError:
            t = None
        if t in ['year', 'day', 'hour', 'minute']:
            getattr(self, '{}_{}_str'.format(e, t)).set(getattr(self, '{}_{}_int'.format(e, t)).get())
        if 'month' in args[0]:
            getattr(self, args[0].replace('int', 'str')).set(month_str(getattr(self, args[0]).get(), 'long'))
        if 'weekday' in args[0]:
            getattr(self, args[0].replace('int', 'str')).set(weekday_str(getattr(self, args[0]).get(), 'long'))

        if self.sort_var.get() == 0:
            if t in ['day', 'month', 'year']:
                num = check_day_against_month(
                    day=getattr(self, '{}_day_int'.format(e)).get(),
                    month=getattr(self, '{}_month_int'.format(e)).get(),
                    year=getattr(self, '{}_year_int'.format(e)).get()
                )
                getattr(self, '{}_day_int'.format(e)).set(num)
                self._set_date_strings(e)
        self._check_order(args[0])

    def _set_date_strings(self, e: str = None):
        if e:
            l_ = [e]
        else:
            l_ = ['high', 'low']
        for s in l_:
            getattr(self, '{}_date_str'.format(s)).set(
                datetime(
                    year=getattr(self, '{}_year_int'.format(s)).get(),
                    month=getattr(self, '{}_month_int'.format(s)).get(),
                    day=getattr(self, '{}_day_int'.format(s)).get(),
                    hour=getattr(self, '{}_hour_int'.format(s)).get(),
                    minute=getattr(self, '{}_minute_int'.format(s)).get()
                ).strftime('%a, %b %d, %Y, %H:%M')
            )

    def set_filters(self):
        keys_ = []
        for e in ['high', 'low']:
            for t in ['year', 'month', 'day', 'hour', 'minute', 'weekday']:
                keys_.append(('{} {}'.format(e, t), '{}_{}_int'.format(e, t)))
        dates = self._reader.dates
        for key in keys_:
            dates[key[0]] = getattr(self, key[1]).get()
        self._reader.date_filter = self.sort_var.get()
        self._reader.dates = dates

    def set_date_int_vars(self):
        dates = self._reader.dates
        for t in ['year', 'month', 'day', 'hour', 'minute', 'weekday']:
            for e in ['low', 'high']:
                getattr(self, '{}_{}_int'.format(e, t)).set(dates['{} {}'.format(e, t)])

    def _check_order(self, var: str):
        if 'high' in var:
            h_ = var
            l_ = var.replace('high', 'low')
        else:
            l_ = var
            h_ = var.replace('low', 'high')
        low = getattr(self, l_)
        high = getattr(self, h_)
        if 'high' in var:
            if high.get() < low.get():
                low.set(high.get())
        else:
            if low.get() > high.get():
                high.set(low.get())

    def reset_int_vars(self):
        for a in [['year', self._reader.oldest_year, self._reader.newest_year], ['month', 1, 12], ['day', 1, 31],
                  ['hour', 0, 23], ['minute', 0, 59], ['weekday', 0, 6]]:
            getattr(self, 'low_{}_int'.format(a[0])).set(a[1])
            getattr(self, 'high_{}_int'.format(a[0])).set(a[2])


class DatesPopup(Toplevel):
    def __init__(self, current_var: IntVar, date_vars: DateVars, old: int, new: int, bind_name: str, **kwargs):
        super(DatesPopup, self).__init__(**kwargs)
        self.title('Filters')

        self._bind_name = bind_name

        add_child_class_to_bindtags(self)

        self.bind('<Escape>', lambda e: self.exit())

        self.protocol('WM_DELETE_WINDOW', self.exit)
        width = 58
        self.set_filters = date_vars.set_filters

        self.style = Style()
        self.style.configure('continuous.Vertical.TScale',
                             troughrelief='raised',
                             troughcolor='light gray',
                             sliderthickness=width + 12,
                             sliderrelief='groove',
                             sliderlength=25,
                             background='#b9b9b9')
        self.style.configure('intervals.continuous.Vertical.TScale',
                             sliderthickness=width)
        self.style.configure('filler.TFrame',
                             background='#c9c9c9',
                             borderwidth=1,
                             relief='sunken')
        self.style.configure('date_sort.TCheckbutton',
                             width=200)
        self.style.configure('reset.TButton',
                             height=10)

        self._current = current_var
        self.sort_var = date_vars.sort_var
        self._initial = date_vars.sort_var.get()

        self._sort_button_holder = Frame(master=self)
        left_frame = Frame(master=self._sort_button_holder, height=30, width=200)
        left_frame.pack_propagate(False)
        self._sort_button = Checkbutton(master=left_frame,
                                        style='date_sort.TCheckbutton',
                                        text='sort by intervals',
                                        variable=self.sort_var,
                                        command=self.set_scales_frame)
        left_frame.pack(side='left')
        right_frame = Frame(master=self._sort_button_holder, height=25)
        right_frame.pack_propagate(False)
        reset_button = Button(master=right_frame, text='Reset', command=date_vars.reset_int_vars)
        reset_button.pack(side='right', anchor='e')
        self._sort_button.pack(side='left', anchor='w')
        right_frame.pack(side='left', fill='x', expand=True)
        self._sort_button_holder.pack(side='top', fill='x')

        self._sort_frame = Frame(master=self)
        self._sort_frame.pack(fill='both', expand=True)

        self._c_frame = Frame(master=self._sort_frame)

        self._scales_c = Frame(master=self._c_frame)
        for a in [[old, new, 'year'], [1, 12, 'month'], [1, 31, 'day'], [0, 23, 'hour'], [0, 59, 'minute']]:
            inner = Labelframe(master=self._scales_c, text=a[2])
            for b in ['low', 'high']:
                Scale(master=inner,
                      style='continuous.Vertical.TScale',
                      orient='vertical',
                      from_=a[0],
                      to=a[1],
                      variable=getattr(date_vars, '{}_{}_int'.format(b, a[2]))
                      ).pack(side='left', fill='y', expand=True, anchor='c')
            inner.pack(side='left', fill='both', expand=True)
        self._scales_c.pack(fill='both', expand=True)
        Separator(master=self._c_frame).pack(fill='x')

        self._labels_c = Frame(master=self._c_frame)
        left_frame = Frame(master=self._labels_c, height=70, width=200)
        left_frame.pack_propagate(False)
        right_frame = Frame(master=self._labels_c, style='filler.TFrame')
        low = Label(master=left_frame, textvariable=date_vars.low_date_str)
        to = Label(master=left_frame, text='to')
        high = Label(master=left_frame, textvariable=date_vars.high_date_str)
        low.pack(fill='y', anchor='w', expand=True)
        to.pack(anchor='w')
        high.pack(fill='y', anchor='w', expand=True)
        left_frame.pack(side='left')
        # right_frame.pack(side='right', fill='both', expand=True)
        self._labels_c.pack(fill='x')

        self._i_frame = Frame(master=self._sort_frame)

        self._scales_i = Frame(master=self._i_frame)
        for a in [[old, new, 'year'], [1, 12, 'month'], [1, 31, 'day'], [0, 23, 'hour'], [0, 59, 'minute'],
                  [0, 6, 'weekday']]:
            inner = Labelframe(master=self._scales_i, text=a[2])
            for b in ['low', 'high']:
                Scale(master=inner,
                      style='intervals.continuous.Vertical.TScale',
                      orient='vertical',
                      from_=a[0],
                      to=a[1],
                      variable=getattr(date_vars, '{}_{}_int'.format(b, a[2]))
                      ).pack(side='left', fill='y', expand=True, anchor='c')
            inner.pack(side='left', fill='both', expand=True, anchor='c')

        self._scales_i.pack(fill='both', expand=True)
        Separator(master=self._i_frame).pack(fill='x')
        self._labels_i = Frame(master=self._i_frame)
        for a in ['year', 'month', 'day', 'hour', 'minute', 'weekday']:
            outer = Frame(master=self._labels_i, borderwidth=1, relief='sunken')
            inner = Frame(master=outer, width=118, height=70)
            inner.pack_propagate(False)
            low = Label(master=inner, textvariable=getattr(date_vars, 'low_{}_str'.format(a)))
            low.pack(anchor='w', fill='x', expand=True)
            to = Label(master=inner, text='to')
            to.pack(anchor='w')
            high = Label(master=inner, textvariable=getattr(date_vars, 'high_{}_str'.format(a)))
            high.pack(anchor='w', fill='x', expand=True)
            inner.pack(side='left')
            outer.pack(side='left', fill='both', expand=True)
        self._labels_i.pack(fill='x')

        # self.bind('<Configure>', self.reconfigure)
        self.set_scales_frame()

    @property
    def bind_name(self):
        return self._bind_name

    def set_scales_frame(self):
        if self.sort_var.get() == 0:
            self._c_frame.pack(fill='both', expand=True)
            self._i_frame.pack_forget()
        else:
            self._i_frame.pack(fill='both', expand=True)
            self._c_frame.pack_forget()

    def exit(self):
        if self._initial != self.sort_var.get():
            self._current.set(0)
        self.set_filters()
        self.event_generate('<<Update Ids>>')
        self.destroy()


def _test():
    from tkinter import Tk
    root = Tk()
    reader = ReaderModule(
        path_to_tempfile='/home/kozmik/Documents/Personal/Education/Projects/Programming/Meta-Jurnl-0.3/.tempfiles'
                         '/Reader/000')
    root.geometry('400x500')
    df = DatesFrame(master=root, reader=reader)
    df.pack(fill='both', expand=True)
    root.bind('<<test>>', lambda x: print('Tested'))
    root.mainloop()


def _test_date_vars():
    def print_vars():
        for x in ['low', 'high']:
            for y in ['year', 'month', 'day', 'hour', 'minute', 'weekday', 'date']:
                print(getattr(a, '{}_{}_str'.format(x, y)).get())

    from tkinter import Tk
    root = Tk()
    a = DateVars(ReaderModule(path_to_tempfile='.tempfiles/Reader/000'))
    print_vars()
    a.sort_var.set(0)
    a.high_month_int.set(10)
    a.low_month_int.set(2)
    a.low_day_int.set(30)
    print_vars()
    root.mainloop()


if __name__ == '__main__':
    _test()
