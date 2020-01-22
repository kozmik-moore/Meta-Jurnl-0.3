from datetime import datetime
from dateutil.parser import parse, ParserError
from os import mkdir, scandir
from os.path import exists, join, basename

from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from database import DatabaseManager
from base_widgets import GenericInput, GenericButton

Builder.load_file('writer_widgets.kv')


class BodyModule(GenericInput):
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, body: str = None, **kwargs):
        super(BodyModule, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.text = body if body else ''

    # TODO implement "on_text" here rather than in .kv file

    def write_to_temp_file(self):
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        filepath = join(root, 'body')
        with open(filepath, 'w') as file:
            file.write(self.text)
            file.close()


class TagsModule(BoxLayout):
    _filtered_tags = ListProperty()
    _unfiltered_tags = ListProperty()
    filtered_data = ListProperty()
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, filtered: list = None, **kwargs):
        super(TagsModule, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self._unfiltered_tags = self.database.get_all_tags()
        if filtered:
            for tag in filtered:
                self.add_to_filtered_tags(tag)
        else:
            self.update_recycleview()

    def add_to_filtered_tags(self, tag):
        if tag not in self._filtered_tags:
            if tag in self._unfiltered_tags:
                self._unfiltered_tags.remove(tag)
            self._filtered_tags.append(tag)
            self._filtered_tags.sort()
            self.update_recycleview()
            self.write_to_temp_file()

    def add_to_unfiltered_tags(self, tag):
        if tag not in self._unfiltered_tags:
            if tag in self._filtered_tags:
                self._filtered_tags.remove(tag)
            self._unfiltered_tags.append(tag)
            self._unfiltered_tags.sort()
            self.update_recycleview()
            self.write_to_temp_file()

    def update_recycleview(self):
        filtered = [x for x in self._filtered_tags]
        self.filtered_data = [{'text': x, 'category': 'filtered', 'screen': 'writer', 'sorter': self}
                              for x in filtered]

    def write_to_temp_file(self):
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        filepath = join(root, 'tags')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(self._filtered_tags))
            file.close()

    def call_tags_popup(self):
        Factory.TagsPopup(self, self._filtered_tags, self._unfiltered_tags).open()


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
    filtered_attachments = ListProperty()  # list of paths
    unfiltered_attachments = ListProperty()  # list of paths

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
    database = ObjectProperty(None, allownone=True)

    def __init__(self, filtered: list = None, database: DatabaseManager = None, **kwargs):
        super(AttachmentsModuleButton, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        if filtered:
            for path in filtered:
                if exists(path):
                    self.add_to_filtered_attachments(path)


class DateModuleButton(GenericButton):
    string_format = '%A, %B %d, %Y %H:%M'
    datetime_obj = None
    datetime_str = StringProperty('')
    database = ObjectProperty(None, allownone=True)

    def __init__(self, date: datetime = None, string_format: str = None, database: DatabaseManager = None, **kwargs):
        super(DateModuleButton, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
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
        Factory.DatetimePopup(self, date=self.datetime_obj, string_format=self.string_format).open()

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
            self.caller.set_datetime_obj(self.datetime_obj)
        super(DatetimePopup, self).on_dismiss()


class IDModule:
    _parent_id = NumericProperty(-1)
    _entry_id = NumericProperty(-1)
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, parent_id: int = None, entry_id: int = None):
        self._database = database if database else DatabaseManager()
        if parent_id:
            self._parent_id = parent_id
        if entry_id:
            self._entry_id = entry_id

    @property
    def parent_id(self):
        return self._parent_id

    @parent_id.setter
    def parent_id(self, pid):
        self._parent_id = pid
        self.write_to_temp_file()

    @property
    def entry_id(self):
        return self._entry_id

    @entry_id.setter
    def entry_id(self, eid):
        self._entry_id = eid
        self.write_to_temp_file()

    def clear(self):
        self._entry_id = -1
        self._parent_id = -1

    def write_to_temp_file(self):
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        ids = (str(self.entry_id), str(self.parent_id))
        filepath = join(root, 'ids')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join(ids))
            file.close()


class FlagsModule(BoxLayout):
    _link_flag = BooleanProperty(False)
    _edit_flag = BooleanProperty(False)
    _save_flag = BooleanProperty(False)

    def __init__(self, link: bool = None, edit: bool = None, **kwargs):
        if link:
            self._link_flag = link
        if edit:
            self._edit_flag = edit
        super(FlagsModule, self).__init__(**kwargs)

    @property
    def link_flag(self):
        return self._link_flag

    @link_flag.setter
    def link_flag(self, value: bool):
        self._link_flag = value
        self.write_to_temp_file()

    @property
    def edit_flag(self):
        return self._edit_flag

    @edit_flag.setter
    def edit_flag(self, value: bool):
        self._edit_flag = value
        self.write_to_temp_file()

    @property
    def save_flag(self):
        return self._save_flag

    @save_flag.setter
    def save_flag(self, value: bool):
        self._save_flag = value
        self.write_to_temp_file()

    def clear_flags(self):
        self.link_flag = False
        self.edit_flag = False
        self.save_flag = False

    def write_to_temp_file(self):
        root = '.tempfiles'
        if not exists(root):
            mkdir(root)
        filepath = join(root, 'flags')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join([str(self.link_flag), str(self.edit_flag), str(self.save_flag)]))
            file.close()


class WritingModule(BoxLayout):
    id_module = None
    entry_manager = ObjectProperty(None, allownone=True)
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, **kwargs):
        super(WritingModule, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.id_module = IDModule(self.database)
        module = {x: self.ids[x] for x in ['body', 'date', 'tags', 'attachments', 'flags']}
        module['ids'] = self.id_module
        module['database'] = self.database
        self.entry_manager = EntryManager(**module)


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
        self.module_dict = {x: self.__getattribute__(x) for x in
                            ['body', 'date', 'tags', 'attachments', 'ids', 'flags']}

    def save(self):
        pass

    def load(self):
        pass


class ShortMessagePopup(Popup):
    message = StringProperty('')

    def __init__(self, message: str, **kwargs):
        self.message = message
        super(ShortMessagePopup, self).__init__(**kwargs)
