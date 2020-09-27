from os.path import join, exists
from tkinter.ttk import Style

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
        *app*background: {}
        *background: {}
        *foreground: {}
        *highlightThickness: {}
        *Text*background: {}
        *Text*insertBackground: {}
        *Menubutton*background: {}
        *Menubutton*activeBackground: {}
        """.format(frame_bg, frame_bg, fg, 0, interactive_bg, listbutton_bg, interactive_bg, listbutton_bg).encode())
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
            s.configure('unselected.TCheckbutton', background=frame_bg, foreground=fg, indicatorcolor=unselected_fg)
            s.map('TCheckbutton',
                  indicatorcolor=[
                      ('pressed', '#ececec'),
                      ('!disabled', 'alternate', '#9fbdd8'),
                      ('disabled', 'alternate', '#c0c0c0'),
                      ('!disabled', 'selected', fg),
                      ('disabled', 'selected', '#a3a3a3')],
                  background=[
                      ('active', listbutton_bg)])

            s.configure('TRadiobutton', background=interactive_bg, foreground=fg)

            s.configure('TEntry', fieldbackground=interactive_bg, foreground=fg, insertcolor=listbutton_bg)

            s.configure('TCombobox', fieldbackground=interactive_bg, foreground=fg)
