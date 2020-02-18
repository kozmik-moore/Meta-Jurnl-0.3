from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from database import DatabaseManager
from writer_widgets import WritingModule
from reader_widgets import ReadingModule


Builder.load_file('app_widgets.kv')


class JournalInterface(BoxLayout):
    database = ObjectProperty()
    screen = StringProperty()

    def __init__(self, database: DatabaseManager = None, **kwargs):
        self.database = database if database else DatabaseManager()
        super(JournalInterface, self).__init__(**kwargs)
        self.writer_module = self.ids['writer_module'] if 'writer_module' in self.ids else WritingModule()
        self.reader_module = self.ids['reader_module'] if 'reader_module' in self.ids else ReadingModule()
        self.reader_module.bind(edit_property=self.edit_stored_entry)

    def edit_stored_entry(self, instance, entry_id):
        if entry_id > 0:
            self.writer_module.entry_manager.clear_ui()
            self.writer_module.entry_manager.load(entry_id)
            self.screen = 'writer'


class JournalApp(App):
    database = ObjectProperty(allownone=True)
    ui = ObjectProperty()

    def __init__(self, **kwargs):
        self.database = DatabaseManager()
        self.ui = JournalInterface(database=self.database, **kwargs)
        super(JournalApp, self).__init__(**kwargs)

    def build(self):
        return self.ui
