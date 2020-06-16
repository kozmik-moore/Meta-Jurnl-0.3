from datetime import datetime
from json import dumps, loads
from os import makedirs, listdir, remove
from os.path import exists, join
from shutil import copyfile

from dateutil.parser import parse
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
        self.storage = StorageModule()
        self.database = DatabaseManager()
        self.ui = JournalInterface(database=self.database, **kwargs)
        self.title = 'Meta-Jurnl'
        super(JournalApp, self).__init__(**kwargs)

    def build(self):
        return self.ui


class StorageModule:

    def __init__(self):
        self.settings = None
        self.database = DatabaseManager()
        self.read_settings_from_file()
        self.check_dirs()
        if self.settings['last backup'] == 'None' or (
                datetime.now() - parse(self.settings['last backup'])).total_seconds() >= self.settings[
                'backup freq'] * 3600:
            self.backup_database()

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, d):
        self._settings = d

    def read_settings_from_file(self):
        if exists('settings.json'):
            with open('settings.json') as file:
                data = file.read()
                self._settings = loads(data)
                file.close()
        else:
            self.write_settings_to_file()

    def write_settings_to_file(self):
        if not exists('settings.json'):
            self._settings = {'last backup': 'None', 'backup freq': 72, 'backup location': 'Backups',
                              'imports location': 'Imports', 'date format': '%Y-%m-%d %H:%M', 'number of backups': 3}
        json = dumps(self.settings, indent=4)
        with open('settings.json', 'w') as file:
            file.write(json)
            file.close()

    def backup_database(self):
        location = self.settings['backup location']
        dbs = listdir(location)
        if len(dbs) == int(self.settings['number of backups']):
            sorted_dbs = sorted(dbs, reverse=True)
            remove(join(location, sorted_dbs[-1]))
        now = datetime.now()
        filename = 'backup_' + now.strftime('%Y%m%d%H%M') + '.sqlite'
        copyfile('jurnl.sqlite', join(location, filename))
        self.settings['last backup'] = now.strftime('%A, %b %d, %Y, %H:%M')
        self.write_settings_to_file()

    def check_dirs(self):
        for s in self.settings:
            if 'location' in s:
                location = self.settings[s]
                if not exists(location):
                    makedirs(location)
