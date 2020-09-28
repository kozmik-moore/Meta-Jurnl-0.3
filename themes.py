from os.path import join, exists, abspath
from tkinter.ttk import Style

from PIL import ImageTk, Image

from configurations import color_scheme

frame_bg = '#222222'
fg = '#00cb00'
interactive_bg = '#333333'
selected_bg = '#0000dc'
unselected_bg = '#550000'
unselected_fg = '#000'
listbutton_bg = '#006600'


class ThemeEngine:
    def __init__(self):
        self._optionsfile = join('.resources', 'options')

    def create_options_files(self):
        options = bytes("""
        theme: dark
        color: green
        
        *app*background: {}
        *background: {}
        *foreground: {}
        *highlightThickness: {}
        *Text*background: {}
        *Text*insertBackground: {}
        *Menubutton*background: {}
        *Menubutton*activeBackground: {}
        *Menu*activeBackground: {}
        """.format(frame_bg, frame_bg, fg, 0, interactive_bg, listbutton_bg, interactive_bg, listbutton_bg,
                   listbutton_bg).encode())
        with open(self._optionsfile, 'wb') as file:
            file.write(options)
            file.close()

    @property
    def theme(self):
        return 0

    @theme.setter
    def theme(self, v):
        pass

    @property
    def options_file(self):
        if not exists(self._optionsfile):
            self.create_options_files()
        return self._optionsfile

    def set_options(self, **kwargs):
        pass

    @staticmethod
    def set_ttk_style(style: str = 'dark'):

        if style == 'dark':
            s = Style()

            s.configure('TButton', background=interactive_bg, foreground=fg)
            s.map('TButton',
                  foreground=[('disabled', listbutton_bg)],
                  background=[('disabled', frame_bg),
                              ('pressed', '!focus', 'cyan'),
                              ('active', listbutton_bg)],
                  highlightcolor=[('focus', fg),
                                  ('!focus', 'red')])

            s.configure('TFrame', background=frame_bg)

            s.configure('TLabel', background=frame_bg, foreground=fg)

            s.configure('Vertical.TScrollbar', background=frame_bg, troughcolor=interactive_bg)
            s.map('Vertical.TScrollbar',
                  arrowcolor=[('disabled', unselected_fg),
                              ('pressed', 'red'),
                              ('!disabled', fg)],
                  background=[('disabled', frame_bg),
                              ('pressed', '!focus', 'cyan'),
                              ('active', interactive_bg)])

            s.configure('TNotebook', background=frame_bg)
            s.configure('TNotebook.Tab', background=interactive_bg, foreground=fg)
            s.map('TNotebook.Tab', background=[('selected', frame_bg)])

            s.configure('TPanedwindow', background=frame_bg)

            s.configure('TCheckbutton', background=interactive_bg, foreground=fg)
            s.configure('selected.TCheckbutton', background=frame_bg, foreground=fg)
            s.configure('unselected.TCheckbutton', background=frame_bg, foreground=fg, indicatorcolor=frame_bg)
            s.map('TCheckbutton',
                  indicatorcolor=[
                      ('pressed', '#ececec'),
                      ('!disabled', 'alternate', '#9fbdd8'),
                      ('disabled', 'alternate', '#c0c0c0'),
                      ('!disabled', 'selected', fg),
                      ('disabled', 'selected', '#a3a3a3')],
                  background=[
                      ('active', listbutton_bg)])

            s.configure('TRadiobutton', background=interactive_bg, foreground=fg, indicatorcolor=frame_bg)
            s.map('TRadiobutton',
                  indicatorcolor=[
                      ('pressed', '#ececec'),
                      ('!disabled', 'alternate', '#9fbdd8'),
                      ('disabled', 'alternate', '#c0c0c0'),
                      ('!disabled', 'selected', fg),
                      ('disabled', 'selected', '#a3a3a3')],
                  background=[
                      ('active', listbutton_bg)])

            s.configure('TEntry', fieldbackground=interactive_bg, foreground=fg, insertcolor=listbutton_bg)

            s.configure('TCombobox', fieldbackground=interactive_bg, foreground=fg)


def get_icon(name: str):
    colors = color_scheme()
    icon_path = abspath(join('.resources', join(colors[0], join(colors[1], '{}.png'.format(name)))))
    img = Image.open(icon_path)
    img = img.resize((16, 16))
    return ImageTk.PhotoImage(image=img)
