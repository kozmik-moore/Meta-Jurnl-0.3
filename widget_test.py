from datetime import datetime

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from writer_widgets import DateModuleButton
from database import DatabaseManager
import base_widgets


class MyApp(App):
    date = datetime.now()
    button = DateModuleButton(date=date, text='Test')
    widget = BoxLayout()
    widget.add_widget(button)

    def __init__(self, **kwargs):
        super(MyApp, self).__init__(**kwargs)

    def build(self):
        return self.widget

# class MyApp(App):
#     widget = BoxLayout()
#     widget.add_widget(base_widgets.GenericButton(text='Test'))
#
#     def __init__(self):
#         super(MyApp, self).__init__()
#
#     def build(self):
#         return self.widget


app = MyApp()
app.run()
