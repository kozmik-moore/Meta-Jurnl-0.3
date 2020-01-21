from os import mkdir
from os.path import exists, join

from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from database import DatabaseManager
from base_widgets import GenericInput, GenericButton


Builder.load_file('writer_widgets.kv')


class Body(GenericInput):
    database = None

    def __init__(self, database: DatabaseManager = None, body: str = None, **kwargs):
        super(Body, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.text = body if body else ''

    def write_to_temp_file(self):
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        filepath = join(root, 'body')
        with open(filepath, 'w') as file:
            file.write(self.text)
            file.close()


class TagSorter(BoxLayout):
    filtered_tags = list()
    unfiltered_tags = list()
    filtered_data = ListProperty()
    unfiltered_data = ListProperty()
    search_text = StringProperty()
    database = None

    def __init__(self, database: DatabaseManager = None, filtered: list = None, **kwargs):
        super(TagSorter, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.unfiltered_tags = self.database.get_all_tags()
        if filtered:
            for tag in filtered:
                self.add_to_filtered_tags(tag)
        else:
            self.update_recycleviews()

    def add_to_filtered_tags(self, tag):
        if tag not in self.filtered_tags:
            if tag in self.unfiltered_tags:
                self.unfiltered_tags.remove(tag)
            self.filtered_tags.append(tag)
            self.filtered_tags.sort()
            self.update_recycleviews()
            self.write_to_temp_file()

    def add_to_unfiltered_tags(self, tag):
        if tag in self.filtered_tags:
            self.filtered_tags.remove(tag)
        self.unfiltered_tags.append(tag)
        self.unfiltered_tags.sort()
        self.update_recycleviews()
        self.write_to_temp_file()

    def update_recycleviews(self, filtered: list = None, unfiltered: list = None):
        if filtered is None:
            filtered = [x for x in self.filtered_tags if self.search_text.lower() in x.lower()]
        if unfiltered is None:
            unfiltered = [x for x in self.unfiltered_tags if self.search_text.lower() in x.lower()]
        self.filtered_data = [{'text': x, 'category': 'filtered', 'screen': 'writer', 'sorter': self}
                              for x in filtered]
        self.unfiltered_data = [{'text': x, 'category': 'unfiltered', 'screen': 'writer', 'sorter': self}
                                for x in unfiltered]

    def search(self, text: str):
        self.search_text = text
        self.update_recycleviews()

    def clear_search_bar(self):
        self.update_recycleviews()

    def write_to_temp_file(self):
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        filepath = join(root, 'tags')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(self.filtered_tags))
            file.close()


class TagButton(GenericButton):
    sorter = ObjectProperty(TagSorter, allownone=True)

    def __init__(self, **kwargs):
        super(TagButton, self).__init__(**kwargs)
