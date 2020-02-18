from datetime import datetime
from dateutil.parser import parse, ParserError
from os import mkdir, scandir, remove, makedirs
from os.path import exists, join, basename

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from database import DatabaseManager
from base_widgets import GenericInput, GenericButton

Builder.load_file('writer_widgets.kv')


class BodyModule(GenericInput):
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, body: str = None, **kwargs):
        super(BodyModule, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.text = body if body else ''

    def on_text(self, instance, value):
        self.write_to_temp_file()

    def write_to_temp_file(self):
        root = join('.tempfiles', 'writer')
        if not exists(root):
            makedirs(root)
        filepath = join(root, 'body')
        with open(filepath, 'w') as file:
            file.write(self.text)
            file.close()


class TagsModule(BoxLayout):
    filtered_tags = ListProperty()
    unfiltered_tags = ListProperty()
    filtered_data = ListProperty()
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, filtered: list = None, **kwargs):
        super(TagsModule, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.unfiltered_tags = self.database.get_all_tags()
        if filtered:
            for tag in filtered:
                self.add_to_filtered_tags(tag)
        else:
            self.update_recycleview()

    def add_to_filtered_tags(self, tag):
        if tag not in self.filtered_tags:
            if tag in self.unfiltered_tags:
                self.unfiltered_tags.remove(tag)
            self.filtered_tags.append(tag)
            self.filtered_tags.sort()
            self.update_recycleview()
            self.write_to_temp_file()

    def add_to_unfiltered_tags(self, tag):
        if tag not in self.unfiltered_tags:
            if tag in self.filtered_tags:
                self.filtered_tags.remove(tag)
            self.unfiltered_tags.append(tag)
            self.unfiltered_tags.sort()
            self.update_recycleview()
            self.write_to_temp_file()

    def update_recycleview(self):
        filtered = [x for x in self.filtered_tags]
        self.filtered_data = [{'text': x, 'category': 'filtered', 'screen': 'writer', 'sorter': self}
                              for x in filtered]

    def write_to_temp_file(self):
        root = join('.tempfiles', 'writer')
        if not exists(root):
            makedirs(root)
        filepath = join(root, 'tags')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(self.filtered_tags))
            file.close()

    def clear_filtered_tags(self):
        self.unfiltered_tags = self.unfiltered_tags + self.filtered_tags
        self.filtered_tags = []
        self.update_recycleview()
        self.write_to_temp_file()

    def call_tags_popup(self):
        Factory.TagsPopup(self, self.filtered_tags, self.unfiltered_tags).open()


class TagsPopup(Popup):
    filtered_tags = list()
    unfiltered_tags = list()
    filtered_data = ListProperty()
    unfiltered_data = ListProperty()
    search_text = StringProperty('')
    sorter = None

    def __init__(self, sorter: TagsModule, filtered, unfiltered):
        super(TagsPopup, self).__init__()
        self.sorter = sorter if sorter else TagsModule()
        for tag in filtered:
            self.add_to_filtered_tags(tag)
        for tag in unfiltered:
            self.add_to_unfiltered_tags(tag)

    def add_to_filtered_tags(self, tag):
        if tag not in self.filtered_tags:
            if tag in self.unfiltered_tags:
                self.unfiltered_tags.remove(tag)
            self.filtered_tags.append(tag)
            self.filtered_tags.sort()
            self.update_recycleviews()
            self.write_to_temp_file()

    def add_to_unfiltered_tags(self, tag):
        if tag not in self.unfiltered_tags:
            if tag in self.filtered_tags:
                self.filtered_tags.remove(tag)
            self.unfiltered_tags.append(tag)
            self.unfiltered_tags.sort()
            self.update_recycleviews()
            self.write_to_temp_file()

    def update_recycleviews(self):
        filtered = [x for x in self.filtered_tags if self.search_text.lower() in x.lower()]
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
        root = join('.tempfiles', 'writer')
        if not exists(root):
            makedirs(root)
        filepath = join(root, 'tags')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(self.filtered_tags))
            file.close()

    def on_dismiss(self):
        for tag in self.filtered_tags:
            self.sorter.add_to_filtered_tags(tag)
        for tag in self.unfiltered_tags:
            self.sorter.add_to_unfiltered_tags(tag)
        super(TagsPopup, self).on_dismiss()


class WriterTagButton(GenericButton):
    sorter = ObjectProperty(TagsModule, allownone=True)

    def __init__(self, **kwargs):
        super(WriterTagButton, self).__init__(**kwargs)


class AttachmentsModule:
    filtered_attachments = ListProperty()  # list of paths
    unfiltered_attachments = ListProperty()  # list of paths
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, **kwargs):
        super(AttachmentsModule, self).__init__(**kwargs)
        if not exists('Imports'):
            mkdir('Imports')
        self.database = database if database else DatabaseManager()

    def on_filtered_attachments(self, instance, value):  # used for mass loading paths
        self.write_to_temp_file()

    def on_unfiltered_attachments(self, instance, value):  # used for mass loading paths
        self.write_to_temp_file()

    # def add_to_filtered_attachments(self, path):            # used for singly loading paths
    #     if path not in self.filtered_attachments:
    #         if path in self.unfiltered_attachments:
    #             self.unfiltered_attachments.remove(path)
    #         self.filtered_attachments.append(path)
    #         self.write_to_temp_file()
    #
    # def add_to_unfiltered_attachments(self, path):          # used for singly loading paths
    #     if path not in self.unfiltered_attachments:
    #         if path in self.filtered_attachments:
    #             self.filtered_attachments.remove(path)
    #         self.unfiltered_attachments.append(path)
    #         self.write_to_temp_file()

    def clear_filtered_attachments(self):
        self.filtered_attachments = []
        self.unfiltered_attachments = []
        if not exists('Imports'):
            mkdir('Imports')
        self.unfiltered_attachments = [x.path for x in scandir('Imports')]

    def write_to_database(self, entry_id):
        f_paths = [x for x in self.filtered_attachments if 'database att_id: ' not in x]
        d_paths = [x for x in self.unfiltered_attachments if
                   'database att_id: ' in x]
        d_ids = [x.strip('database att_id: ') for x in d_paths]
        for path in d_ids:
            self.database.delete_attachments_from_att_id(path)
        self.database.update_attachments(entry_id, f_paths)
        for path in f_paths:
            remove(path)
        for path in d_paths:
            self.unfiltered_attachments.remove(path)
        self.clear_filtered_attachments()
        self.filtered_attachments = ['database att_id: {}'.format(att_id) for att_id in
                                     self.database.get_att_ids_from_entry_id(entry_id)]

    def write_to_temp_file(self):
        root = join('.tempfiles', 'writer')
        if not exists(root):
            makedirs(root)
        filepath = join(root, 'attachments_master')
        temp = self.filtered_attachments + ['---'] + self.unfiltered_attachments
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(temp))
            file.close()

    def call_attachments_popup(self):
        Factory.AttachmentsPopup(self, self.filtered_attachments, self.unfiltered_attachments, self.database).open()


class AttachmentsPopup(Popup):
    filtered_attachments = list()  # list of paths
    unfiltered_attachments = list()  # list of paths
    filtered_data = ListProperty()
    unfiltered_data = ListProperty()
    search_text = StringProperty('')
    sorter = None

    def __init__(self, sorter: AttachmentsModule, filtered: list, unfiltered: list, database: DatabaseManager):
        super(AttachmentsPopup, self).__init__()
        self.database = database
        self.sorter = sorter if sorter else AttachmentsModule()
        # for item in list(scandir('Imports')):
        #     self.add_to_unfiltered_attachments(item.path)
        self.filtered_attachments = list(filtered)
        self.filtered_attachments.sort(key=self.get_sort_key)
        self.unfiltered_attachments = list(set([x.path for x in scandir('Imports') if x.path not in filtered]).union(unfiltered))
        self.unfiltered_attachments.sort(key=self.get_sort_key)
        self.check_paths_exist()
        self.update_recycleviews()
        self.write_to_temp_file()

    def add_to_filtered_attachments(self, attachment):
        if attachment not in self.filtered_attachments:
            if exists(attachment) or 'database att_id: ' in attachment:
                if attachment in self.unfiltered_attachments:
                    self.unfiltered_attachments.remove(attachment)
                self.filtered_attachments.append(attachment)
                self.filtered_attachments.sort(key=self.get_sort_key)
                self.update_recycleviews()
                self.write_to_temp_file()

    def add_to_unfiltered_attachments(self, attachment):
        if attachment not in self.unfiltered_attachments:
            if exists(attachment) or 'database att_id: ' in attachment:
                if attachment in self.filtered_attachments:
                    self.filtered_attachments.remove(attachment)
                self.unfiltered_attachments.append(attachment)
                self.unfiltered_attachments.sort(key=self.get_sort_key)
                self.update_recycleviews()
                self.write_to_temp_file()

    def update_recycleviews(self):
        f_temp = list()
        u_temp = list()
        filtered = [x for x in self.filtered_attachments if self.search_text.lower() in basename(x).lower()]
        unfiltered = [x for x in self.unfiltered_attachments if self.search_text.lower() in basename(x).lower()]
        for x in filtered:
            n = str(basename(x)) if 'database att_id: ' not in x else self.database.get_attachment_name_from_att_id(
                x.strip('database att_id: '))
            t = n if len(n) < 30 else n[:20] + ' ... .' + n.split('.')[-1]
            d = {'path': x, 'category': 'filtered', 'screen': 'writer', 'sorter': self, 'name': n, 'text': t}
            f_temp.append(d)
        for x in unfiltered:
            n = str(basename(x)) if 'database att_id: ' not in x else self.database.get_attachment_name_from_att_id(
                x.strip('database att_id: '))
            t = n if len(n) < 30 else n[:20] + ' ... .' + n.split('.')[-1]
            d = {'path': x, 'category': 'unfiltered', 'screen': 'writer', 'sorter': self, 'name': n, 'text': t}
            u_temp.append(d)
        self.filtered_data = f_temp
        self.unfiltered_data = u_temp

    def search(self, text: str):
        self.search_text = text
        self.update_recycleviews()

    def clear_search_bar(self):
        self.update_recycleviews()

    def get_sort_key(self, path):
        if 'database att_id: ' in path:
            key = self.database.get_attachment_name_from_att_id(path.strip('database att_id: '))
        else:
            key = basename(path)
        return key

    def check_paths_exist(self):
        temp = self.filtered_attachments
        for path in temp:
            if not exists(path) and 'database att_id: ' not in path:
                self.filtered_attachments.remove(path)
        temp = self.unfiltered_attachments
        for path in temp:
            if not exists(path) and 'database att_id: ' not in path:
                self.unfiltered_attachments.remove(path)

    def write_to_temp_file(self):
        root = join('.tempfiles', 'writer')
        if not exists(root):
            makedirs(root)
        filepath = join(root, 'attachments_master')
        temp = self.filtered_attachments + ['---'] + self.unfiltered_attachments
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(temp))

    def on_dismiss(self):
        self.sorter.filtered_attachments = self.filtered_attachments
        self.sorter.unfiltered_attachments = self.unfiltered_attachments
        super(AttachmentsPopup, self).on_dismiss()


class AttachmentButton(GenericButton):
    sorter = ObjectProperty(TagsModule, allownone=True)

    def __init__(self, **kwargs):
        super(AttachmentButton, self).__init__(**kwargs)


class AttachmentsModuleButton(GenericButton, AttachmentsModule):
    database = ObjectProperty(None, allownone=True)

    def __init__(self, filtered: list = None, database: DatabaseManager = None, **kwargs):
        super(AttachmentsModuleButton, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        if filtered:
            for path in filtered:
                if exists(path):
                    self.add_to_filtered_attachments(path)


class DateModuleButton(GenericButton):
    string_format = StringProperty('%A, %B %d, %Y %H:%M')
    datetime_obj = ObjectProperty(None, allownone=True)
    datetime_str = StringProperty('No Date')
    database = ObjectProperty(None, allownone=True)

    def __init__(self, date: datetime = None, string_format: str = None, database: DatabaseManager = None, **kwargs):
        super(DateModuleButton, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        if date:
            self.datetime_obj = date
        if string_format:
            self.string_format = string_format

    def on_datetime_obj(self, instance, value):
        self.datetime_str = self.datetime_obj.strftime(self.string_format) if self.datetime_obj else 'No Date'
        self.write_to_temp_file()

    def call_datetime_popup(self):
        Factory.DatetimePopup(self, date=self.datetime_obj, string_format=self.string_format).open()

    def write_to_temp_file(self):
        root = join('.tempfiles', 'writer')
        if not exists(root):
            makedirs(root)
        filepath = join(root, 'date')
        with open(filepath, 'w') as file:
            file.write(self.datetime_str)
            file.close()

    def clear_date(self):
        pass

    def on_release(self):
        self.call_datetime_popup()
        super(DateModuleButton, self).on_release()


class DatetimePopup(Popup):
    string_format = ''
    datetime_obj = None
    datetime_str = StringProperty('')
    caller = None

    def __init__(self, caller: DateModuleButton, string_format: str, date: datetime = None, **kwargs):
        self.string_format = string_format
        if date:
            self.datetime_obj = date
            self.datetime_str = self.datetime_obj.strftime(self.string_format)
        self.caller = caller
        super(DatetimePopup, self).__init__(**kwargs)

    def set_date(self, date: str):
        try:
            self.datetime_obj = parse(date)
            self.datetime_str = self.datetime_obj.strftime(self.string_format)
        except ParserError:
            Factory.ShortMessagePopup(
                message='Unrecognized date format. Try entering the date in the form MM-DD-YY or YYYY-MM-DD '
                        'HH:MM.', title='Invalid Format').open()
        except OverflowError:
            Factory.ShortMessagePopup(
                message='Unrecognized date format. Try entering the date in the form MM-DD-YY or YYYY-MM-DD '
                        'HH:MM.', title='Invalid Format').open()

    def on_dismiss(self):
        if self.datetime_obj:
            self.caller.datetime_obj = self.datetime_obj
        super(DatetimePopup, self).on_dismiss()


class IDModule(Widget):
    parent_id = NumericProperty(-1)
    entry_id = NumericProperty(-1)
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, parent_id: int = None, entry_id: int = None, **kwargs):
        self._database = database if database else DatabaseManager()
        if parent_id:
            self.parent_id = parent_id
        if entry_id:
            self.entry_id = entry_id
        super(IDModule, self).__init__(**kwargs)

    def on_parent_id(self, instance, value):
        self.write_to_temp_file()

    def on_entry_id(self, instance, value):
        self.write_to_temp_file()

    def reset_ids(self):
        self.entry_id = -1
        self.parent_id = -1

    def write_to_temp_file(self):
        root = join('.tempfiles', 'writer')
        if not exists(root):
            makedirs(root)
        ids = (str(self.entry_id), str(self.parent_id))
        filepath = join(root, 'ids')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(ids))
            file.close()


class FlagsModule(BoxLayout):
    is_saved = BooleanProperty(None, allownone=True)
    is_linked = BooleanProperty(False)
    is_being_edited = BooleanProperty(False)

    def __init__(self, save: bool = None, link: bool = None, edit: bool = None, **kwargs):
        if save:
            self.is_saved = save
        if link:
            self.is_linked = link
        if edit:
            self.is_being_edited = edit
        super(FlagsModule, self).__init__(**kwargs)

    def on_is_saved(self, instance, value):
        self.write_to_temp_file()

    def on_is_linked(self, instance, value):
        self.write_to_temp_file()

    def on_is_being_edited(self, instance, value):
        self.write_to_temp_file()

    def clear_flags(self):
        self.is_saved = False
        self.is_linked = False
        self.is_being_edited = False

    def write_to_temp_file(self):
        root = join('.tempfiles', 'writer')
        if not exists(root):
            makedirs(root)
        filepath = join(root, 'flags')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join([str(self.is_saved if self.is_saved else 'No Entry'), str(self.is_linked),
                                       str(self.is_being_edited)]))
            file.close()


class WritingModule(BoxLayout):
    entry_manager = ObjectProperty(None, allownone=True)
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, **kwargs):
        self.database = database if database else DatabaseManager()
        super(WritingModule, self).__init__(**kwargs)
        try:
            self.get_ids()
        except KeyError:
            Clock.schedule_once(self.get_ids)

    def get_ids(self, value=None):
        modules = {x: self.ids[x] for x in ['body', 'date', 'tags', 'attachments', 'flags', 'ids']}
        modules['database'] = self.database
        self.entry_manager = EntryManager(**modules)


class EntryManager:
    body = None
    date = None
    tags = None
    attachments = None
    ids = None
    flags = None
    database = None

    def __init__(self, body: BodyModule, date: DateModuleButton, tags: TagsModule, attachments: AttachmentsModuleButton,
                 ids: IDModule, flags: FlagsModule, database: DatabaseManager):
        self.body = body
        self.date = date
        self.tags = tags
        self.attachments = attachments
        self.ids = ids
        self.flags = flags
        self.database = database
        self.body.bind(text=self.check_entry_saved)
        self.tags.bind(filtered_tags=self.check_entry_saved)
        self.date.bind(datetime_obj=self.check_entry_saved)
        self.ids.bind(parent_id=self.check_entry_linked)
        self.attachments.bind(filtered_attachments=self.check_entry_saved)
        self.attachments.bind(unfiltered_attachments=self.check_entry_saved)
        root = join('.tempfiles', 'writer')
        location = join(root, 'ids')
        if exists(location):
            with open(location, 'r') as file:
                ids = [x.strip('\n') for x in file.readlines()]
                self.ids.entry_id = ids[0]
                self.ids.parent_id = ids[1]
                file.close()
        location = join(root, 'date')
        if exists(location):
            with open(location, 'r') as file:
                date = file.read()
                self.date.datetime_obj = parse(date) if date != 'No Date' else None
                file.close()
        location = join(root, 'body')
        if exists(location):
            with open(location, 'r') as file:
                self.body.text = file.read()
                file.close()
        location = join(root, 'tags')
        if exists(location):
            with open(location, 'r') as file:
                for tag in [x.strip('\n') for x in file.readlines()]:
                    self.tags.add_to_filtered_tags(tag)
                file.close()
        location = join(root, 'attachments_master')
        temp = list()
        i = 0
        f = set()
        u = set()
        if exists(location):
            with open(location, 'r') as file:
                temp = [x.strip('\n') for x in file.readlines()]
                if temp:
                    i = temp.index('---')
                f = set(temp[:i])
                u = set(temp[i + 1:])
                file.close()
        s = set([x.path for x in scandir('Imports')])
        self.attachments.unfiltered_attachments = list(u.union(s.difference(f.union(u))))
        self.attachments.filtered_attachments = list(f)
        location = join(root, 'flags')
        if exists(location):
            with open(location, 'r') as file:
                flags = [x.strip('\n') for x in file.readlines()]
                self.flags.is_saved = {'True': True, 'False': False, 'No Entry': None}[flags[0]]
                self.flags.is_linked = True if flags[1] == 'True' else False
                self.flags.is_being_edited = True if flags[2] == 'True' else False
                file.close()

    def save(self):
        self.ids.entry_id = self.database.upsert_entry(body=self.body.text, tags=self.tags.filtered_tags,
                                                       date=self.date.datetime_obj, entry_id=self.ids.entry_id,
                                                       parent_id=self.ids.parent_id)
        self.attachments.write_to_database(self.ids.entry_id)
        self.date.datetime_obj = self.database.get_date_by_entry_id(self.ids.entry_id)
        self.flags.is_saved = True
        self.flags.is_being_edited = False

    def load(self, entry_id: int = -1, parent_id: int = -1, body: str = '', date: datetime = None,
             attachments: list = None, tags: list = None):
        if entry_id != -1:
            self.ids.entry_id = entry_id
            entry = self.database.get_entry_from_entry_id(entry_id)
            self.body.text = entry['body']
            for tag in entry['tags']:
                self.tags.add_to_filtered_tags(tag)
            self.ids.parent_id = entry['parent_id']
            self.date.datetime_obj = entry['date']
            for attachment in entry['attachments']:
                self.attachments.add_to_filtered_attachments('database att_id: {}'.format(str(attachment['att_id'])))

    def create_linked_entry(self, parent_id: int = None, tags: list = None):
        if not parent_id:
            parent_id = self.ids.entry_id
            tags = self.tags.filtered_tags
        self.clear_ui()
        self.ids.parent_id = parent_id
        for tag in tags:
            self.tags.add_to_filtered_tags(tag)

    def check_entry_saved(self, instance, value):
        is_saved = True
        if self.ids.entry_id != -1:
            if self.body.text != self.database.get_body_by_entry_id(self.ids.entry_id):
                is_saved = False
            if is_saved and self.tags.filtered_tags != self.database.get_tags_by_entry_id(self.ids.entry_id):
                is_saved = False
            if is_saved and self.date.datetime_obj != self.database.get_date_by_entry_id(self.ids.entry_id):
                is_saved = False
            if is_saved and ([x for x in self.attachments.filtered_attachments if 'database att_id: ' not in x] or
                             [x for x in self.attachments.unfiltered_attachments if 'database att_id: ' in x]):
                is_saved = False
        elif not self.body.text and not self.tags.filtered_tags and not self.date.datetime_obj and self.ids.parent_id \
                == -1 and not self.attachments.filtered_attachments:
            is_saved = None
        else:
            is_saved = False
        self.flags.is_saved = is_saved

    def check_entry_linked(self, instance, value):
        self.flags.is_linked = True if self.ids.parent_id != -1 else False

    def clear_ui(self):
        self.date.datetime_obj = None
        self.body.text = ''
        self.ids.reset_ids()
        self.tags.clear_filtered_tags()
        self.attachments.clear_filtered_attachments()
        self.flags.is_being_edited = False


class ShortMessagePopup(Popup):
    message = StringProperty('')

    def __init__(self, message: str, **kwargs):
        self.message = message
        super(ShortMessagePopup, self).__init__(**kwargs)
