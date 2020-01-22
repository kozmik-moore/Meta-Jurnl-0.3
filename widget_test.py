from datetime import datetime

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from writer_widgets import WritingModule
from database import DatabaseManager
import base_widgets


class MyApp(App):
    widget = WritingModule()

    def __init__(self, **kwargs):
        super(MyApp, self).__init__(**kwargs)

    def build(self):
        return self.widget


app = MyApp()
app.run()
