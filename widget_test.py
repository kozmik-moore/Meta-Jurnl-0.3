from kivy.app import App
from kivy.factory import Factory
from kivy.uix.button import Button

from reader_widgets import FiltersPopup, ReadingModule


class MyApp(App):
    # kwargs = {'has_parent': False, 'has_children': False, 'has_attachments': False, 'has_body': False}
    # widget = Button(text='Test', on_release=Factory.FiltersPopup(**kwargs).open)
    widget = ReadingModule()

    def __init__(self, **kwargs):
        super(MyApp, self).__init__(**kwargs)

    def build(self):
        return self.widget


app = MyApp()
app.run()
