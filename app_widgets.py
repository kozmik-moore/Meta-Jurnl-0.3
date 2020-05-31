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
        self.writer_module.bind(save_property=self.update_reader_module)
        self.reader_module.bind(link_property=self.link_stored_entry)

    def edit_stored_entry(self, instance, entry_id):
        if entry_id > 0:
            self.writer_module.entry_manager.clear_ui()
            self.writer_module.entry_manager.load(entry_id)
            self.screen = 'writer'

    def link_stored_entry(self, instance, entry_id):
        if entry_id > 0:
            tags = self.database.get_tags_by_entry_id(entry_id)
            self.writer_module.entry_manager.create_linked_entry(entry_id, tags)
            self.screen = 'writer'

    def update_reader_module(self, instance, entry_id):
        if entry_id > 0:
            reader_id = self.reader_module.entry_id
            if entry_id == reader_id:
                self.reader_module.clear_ui()
                self.reader_module.entry_id = entry_id


class JournalApp(App):
    database = ObjectProperty(allownone=True)
    ui = ObjectProperty()

    def __init__(self, **kwargs):
        self.database = DatabaseManager()
        self.ui = JournalInterface(database=self.database, **kwargs)
        super(JournalApp, self).__init__(**kwargs)

    def build(self):
        return self.ui
