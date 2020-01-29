from kivy.app import App
from kivy.factory import Factory
from kivy.uix.button import Button

from reader_widgets import ReadingModule


class MyApp(App):
    widget = ReadingModule()

    def __init__(self, **kwargs):
        super(MyApp, self).__init__(**kwargs)

    def build(self):
        return self.widget


app = MyApp()
app.run()
