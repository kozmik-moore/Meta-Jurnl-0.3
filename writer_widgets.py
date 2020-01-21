from datetime import datetime
from dateutil.parser import parse, ParserError
from os import mkdir, scandir
from os.path import exists, join, basename

from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

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


class TagsModule(BoxLayout):
    filtered_tags = list()
    unfiltered_tags = list()
    filtered_data = ListProperty()
    database = None

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
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        filepath = join(root, 'tags')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(self.filtered_tags))
            file.close()

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
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
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


class TagButton(GenericButton):
    sorter = ObjectProperty(TagsModule, allownone=True)

    def __init__(self, **kwargs):
        super(TagButton, self).__init__(**kwargs)


class AttachmentsModule:
    filtered_attachments = list()  # list of paths
    unfiltered_attachments = list()  # list of paths

    def __init__(self, filtered: list = None, **kwargs):
        super(AttachmentsModule, self).__init__(**kwargs)
        if filtered:
            for path in filtered:
                self.add_to_filtered_attachments(path)
        if not exists('Imports'):
            mkdir('Imports')
        for item in list(scandir('Imports')):
            self.add_to_unfiltered_attachments(item.path)

    def add_to_filtered_attachments(self, attachment):
        if attachment not in self.filtered_attachments:
            if attachment in self.unfiltered_attachments:
                self.unfiltered_attachments.remove(attachment)
            self.filtered_attachments.append(attachment)
            self.write_to_temp_file()

    def add_to_unfiltered_attachments(self, attachment):
        if attachment not in self.unfiltered_attachments:
            if attachment in self.filtered_attachments:
                self.filtered_attachments.remove(attachment)
            self.unfiltered_attachments.append(attachment)
            self.write_to_temp_file()

    def write_to_temp_file(self):
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        filepath = join(root, 'attachments')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(self.filtered_attachments))
            file.close()

    def call_attachments_popup(self):
        Factory.AttachmentsPopup(self, self.filtered_attachments, self.unfiltered_attachments).open()


class AttachmentsPopup(Popup):
    filtered_attachments = list()  # list of paths
    unfiltered_attachments = list()  # list of paths
    filtered_data = ListProperty()
    unfiltered_data = ListProperty()
    search_text = StringProperty('')
    sorter = None

    def __init__(self, sorter: AttachmentsModule, filtered, unfiltered):
        super(AttachmentsPopup, self).__init__()
        self.sorter = sorter if sorter else AttachmentsModule()
        for attachment in filtered:
            self.add_to_filtered_attachments(attachment)
        for attachment in unfiltered:
            self.add_to_unfiltered_attachments(attachment)

    def add_to_filtered_attachments(self, attachment):
        if exists(attachment) and attachment not in self.filtered_attachments:
            if attachment in self.unfiltered_attachments:
                self.unfiltered_attachments.remove(attachment)
            self.filtered_attachments.append(attachment)
            self.filtered_attachments.sort(key=basename)
            self.update_recycleviews()
            self.write_to_temp_file()

    def add_to_unfiltered_attachments(self, attachment):
        if exists(attachment) and attachment not in self.unfiltered_attachments:
            if attachment in self.filtered_attachments:
                self.filtered_attachments.remove(attachment)
            self.unfiltered_attachments.append(attachment)
            self.unfiltered_attachments.sort(key=basename)
            self.update_recycleviews()
            self.write_to_temp_file()

    def update_recycleviews(self):
        f_temp = list()
        u_temp = list()
        filtered = [x for x in self.filtered_attachments if self.search_text.lower() in basename(x).lower()]
        unfiltered = [x for x in self.unfiltered_attachments if self.search_text.lower() in basename(x).lower()]
        for x in filtered:
            b = str(basename(x))
            t = b if len(b) < 30 else b[:20] + ' ... .' + b.split(',')[-1]
            d = {'path': x, 'category': 'filtered', 'screen': 'writer', 'sorter': self, 'name': b, 'text': t}
            f_temp.append(d)
        for x in unfiltered:
            b = str(basename(x))
            t = b if len(b) < 30 else b[:20] + ' ... .' + b.split(',')[-1]
            d = {'path': x, 'category': 'unfiltered', 'screen': 'writer', 'sorter': self, 'name': b, 'text': t}
            u_temp.append(d)
        self.filtered_data = f_temp
        self.unfiltered_data = u_temp

    def search(self, text: str):
        self.search_text = text
        self.update_recycleviews()

    def clear_search_bar(self):
        self.update_recycleviews()

    def write_to_temp_file(self):
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        filepath = join(root, 'attachments')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(self.filtered_attachments))
            file.close()

    def on_dismiss(self):
        for attachment in self.filtered_attachments:
            self.sorter.add_to_filtered_attachments(attachment)
        for attachment in self.unfiltered_attachments:
            self.sorter.add_to_unfiltered_attachments(attachment)
        super(AttachmentsPopup, self).on_dismiss()


class AttachmentButton(GenericButton):
    sorter = ObjectProperty(TagsModule, allownone=True)

    def __init__(self, **kwargs):
        super(AttachmentButton, self).__init__(**kwargs)


class AttachmentsModuleButton(GenericButton, AttachmentsModule):
    def __init__(self, filtered: list = None, **kwargs):
        super(AttachmentsModuleButton, self).__init__(**kwargs)
        for path in filtered:
            if exists(path):
                self.add_to_filtered_attachments(path)


class DateModuleButton(GenericButton):
    string_format = '%A, %B %d, %Y %H:%M'
    datetime_obj = None
    datetime_str = StringProperty('')

    def __init__(self, date: datetime = None, string_format: str = None, **kwargs):
        super(DateModuleButton, self).__init__(**kwargs)
        if date:
            self.datetime_obj = date
            self.datetime_str = self.datetime_obj.strftime(self.string_format)
        if string_format:
            self.string_format = string_format

    def set_datetime_obj(self, date: datetime):
        self.datetime_obj = date
        self.datetime_str = self.datetime_obj.strftime(self.string_format)

    def set_string_format(self, string_format: str):
        self.string_format = string_format

    def get_datetime_obj(self):
        return self.datetime_obj

    def get_string_format(self):
        return self.string_format

    def call_datetime_popup(self):
        Factory.DatetimePopup(self, self.datetime_obj, self.string_format).open()
        
    def on_release(self):
        self.call_datetime_popup()
        super(DateModuleButton, self).on_release()
        
    @property
    def dt_obj(self):
        return self.datetime_obj

    @property
    def dt_str(self):
        return self.datetime_str


class DatetimePopup(Popup):
    string_format = ''
    datetime_obj = None
    datetime_str = StringProperty('')
    caller = None

    def __init__(self, caller: DateModuleButton, date: datetime, string_format: str, **kwargs):
        self.string_format = string_format
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
        self.caller.set_datetime_obj(self.datetime_obj)
        super(DatetimePopup, self).on_dismiss()


class ParentModule:
    pass


class ShortMessagePopup(Popup):
    message = StringProperty('')

    def __init__(self, message: str, **kwargs):
        self.message = message
        super(ShortMessagePopup, self).__init__(**kwargs)
