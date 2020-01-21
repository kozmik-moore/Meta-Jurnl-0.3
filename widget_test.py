from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from writer_widgets import TagSorter
from database import DatabaseManager
import base_widgets


class MyApp(App):
    database = DatabaseManager()
    widget = TagSorter(database, ['Art', 'Philosophy', 'Art'])

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
