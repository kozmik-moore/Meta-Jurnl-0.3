from datetime import datetime
from dateutil.parser import parse, ParserError
from os import mkdir, scandir, remove, makedirs
from os.path import exists, join, basename

from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from database import DatabaseManager
from base_widgets import GenericInput, GenericButton, GenericLabel

Builder.load_file('reader_widgets.kv')


class BodyModule(GenericInput):
    database = ObjectProperty(None, allownone=True)

    def __init__(self, database: DatabaseManager = None, body: str = None, **kwargs):
        super(BodyModule, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.text = body if body else ''


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

    def add_to_unfiltered_tags(self, tag):
        if tag not in self.unfiltered_tags:
            if tag in self.filtered_tags:
                self.filtered_tags.remove(tag)
            self.unfiltered_tags.append(tag)
            self.unfiltered_tags.sort()
            self.update_recycleview()

    def update_recycleview(self):
        filtered = [x for x in self.filtered_tags]
        self.filtered_data = [{'text': x, 'category': 'filtered', 'screen': 'writer', 'sorter': self}
                              for x in filtered]

    def clear_filtered_tags(self):
        self.unfiltered_tags = self.unfiltered_tags + self.filtered_tags
        self.filtered_tags = []
        self.update_recycleview()

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

    def add_to_unfiltered_tags(self, tag):
        if tag not in self.unfiltered_tags:
            if tag in self.filtered_tags:
                self.filtered_tags.remove(tag)
            self.unfiltered_tags.append(tag)
            self.unfiltered_tags.sort()
            self.update_recycleviews()

    def update_recycleviews(self):
        filtered = [x for x in self.filtered_tags if self.search_text.lower() in x.lower()]
        unfiltered = [x for x in self.unfiltered_tags if self.search_text.lower() in x.lower()]
        self.filtered_data = [{'text': x, 'category': 'filtered', 'screen': 'reader', 'sorter': self}
                              for x in filtered]
        self.unfiltered_data = [{'text': x, 'category': 'unfiltered', 'screen': 'reader', 'sorter': self}
                                for x in unfiltered]

    def search(self, text: str):
        self.search_text = text
        self.update_recycleviews()

    def clear_search_bar(self):
        self.update_recycleviews()

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


class TagLabel(GenericLabel):
    pass


class DateLabel(GenericLabel):
    pass


class DateButton(GenericButton):
    pass


class DateModule(BoxLayout):
    string_format = StringProperty('%Y-%m-%d %H:%M')
    database = ObjectProperty(None, allownone=True)
    entry_ids = ListProperty()
    date_data = ListProperty()
    selected_id = NumericProperty(-1)
    selected_ranges = DictProperty()
    continuous_range = BooleanProperty()

    def __init__(self, entry_ids: list = None, database: DatabaseManager = None, continuous: bool = False, **kwargs):
        self.database = database if database else DatabaseManager()
        self.entry_ids = entry_ids if entry_ids else self.database.get_all_entry_ids()
        self.continuous_range = continuous
        self.date_data = [
            {'text': self.database.get_date_by_entry_id(entry_id, self.string_format), 'entry_id': entry_id,
             'caller': self} for entry_id in self.entry_ids]
        self.selected_ranges = {'years': {'min': 0, 'max': self.database.get_years()[-1]},
                                'months': {'min': 0, 'max': 11}, 'days': {'min': 0, 'max': 30},
                                'hours': {'min': 0, 'max': 23}, 'minutes': {'min': 0, 'max': 59},
                                'weekdays': {'min': 0, 'max': 6}}
        super(DateModule, self).__init__(**kwargs)

    def call_dates_popup(self):
        years = self.database.get_years()
        if self.selected_ranges['years']['max'] > len(years) - 1:
            self.selected_ranges['years']['max'] = len(years) - 1
        if self.database.get_number_of_entries() > 1:
            Factory.DatetimePopup(self.selected_ranges, years, self.continuous_range, self).open()

    def update(self, entry_ids: list = None):
        self.entry_ids = self.database.get_all_entry_ids() if entry_ids is None else entry_ids
        self.date_data = [
            {'text': self.database.get_date_by_entry_id(entry_id, self.string_format), 'entry_id': entry_id,
             'caller': self} for
            entry_id in self.entry_ids]

    def on_entry_ids(self, instance, value):
        self.date_data = [
            {'text': self.database.get_date_by_entry_id(entry_id, self.string_format), 'entry_id': entry_id,
             'caller': self} for entry_id in self.entry_ids]


class DatetimePopup(Popup):
    years = ListProperty()
    ranges = DictProperty()
    continuous_range = BooleanProperty()
    caller = None

    def __init__(self, ranges: dict, years: list, continuous: bool, caller: DateModule, **kwargs):
        self.years = years
        self.ranges = ranges
        self.continuous_range = continuous
        self.caller = caller
        super(DatetimePopup, self).__init__(**kwargs)

    def on_dismiss(self):
        self.caller.selected_ranges = self.ranges
        self.caller.continuous_range = self.continuous_range
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
        root = join('.tempfiles', 'reader')
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
        root = join('.tempfiles', 'reader')
        if not exists(root):
            makedirs(root)
        filepath = join(root, 'flags')
        with open(filepath, 'w') as file:
            file.writelines('\n'.join([str(self.is_saved if self.is_saved else 'No Entry'), str(self.is_linked),
                                       str(self.is_being_edited)]))
            file.close()


class ReadingModule(BoxLayout):
    database = ObjectProperty(None, allownone=True)
    has_parent = BooleanProperty()
    has_children = BooleanProperty()
    has_attachments = BooleanProperty()
    filter_has_parent = BooleanProperty()
    filter_has_children = BooleanProperty()
    filter_has_attachments = BooleanProperty()
    filter_has_body = StringProperty()
    tag_sort = StringProperty()
    filter_date_sort = DictProperty()
    entry_id = NumericProperty(-1)
    parent_id = NumericProperty(-1)
    body = StringProperty()
    filtered_tags = ListProperty()
    filtered_tags_data = ListProperty()
    children_ids = ListProperty()
    att_ids = ListProperty()
    date = StringProperty()
    filtered_entry_ids = ListProperty()
    filtered_dates_data = ListProperty()
    continuous_range = BooleanProperty()
    date_label_format = StringProperty('%A, %B %d, %Y %H:%M')
    date_button_format = StringProperty('%Y-%m-%d %H:%M')

    def __init__(self, database: DatabaseManager = None, **kwargs):
        super(ReadingModule, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.filtered_entry_ids = self.database.get_all_entry_ids()
        root = join('.tempfiles', 'reader')
        if exists(root):
            location = join(root, 'entry_id')
            if exists(location):
                with open(location, 'r') as file:
                    try:
                        temp = int(file.read())
                    except ValueError:
                        temp = -1
                    self.entry_id = temp
                    file.close()
            location = join(root, 'filters')
            if exists(location):
                with open(location, 'r') as file:
                    temp = file.readline().strip('\n')
                    self.continuous_range = True if temp is True else False
                    temp = file.readline().strip('\n')
                    self.filter_has_parent = True if temp is True else False
                    temp = file.readline().strip('\n')
                    self.filter_has_children = True if temp is True else False
                    temp = file.readline().strip('\n')
                    self.filter_has_attachments = True if temp is True else False
                    temp = file.readline().strip('\n')
                    self.tag_sort = temp if temp in ['Contains At Least...', 'Contains Only...',
                                                     'Contains...'] else 'Contains...'
                    file.close()
            location = join(root, 'tags')
            if exists(location):
                with open(location, 'r') as file:
                    master = self.database.get_all_tags()
                    temp = file.readlines()
                    self.filtered_tags = [x.strip('\n') for x in temp if x.strip('\n') in master]
                    file.close()

        else:
            self.entry_id = -1
            makedirs(root)
            self.tag_sort = 'Contains...'
            self.continuous_range = False

    def on_entry_id(self, instance, value):
        self.body = self.database.get_body_by_entry_id(value) if value != -1 else ''
        self.filtered_tags = self.database.get_tags_by_entry_id(value) if value != -1 else []
        self.att_ids = self.database.get_att_ids_from_entry_id(value) if value != -1 else []
        self.has_attachments = True if self.att_ids else False
        self.parent_id = self.database.get_parent_by_entry_id(value) if value != -1 else -1
        self.has_parent = True if self.parent_id != -1 else False
        self.date = self.database.get_date_by_entry_id(value).strftime(self.date_label_format) if value != -1 else ''
        self.children_ids = self.database.get_children_by_entry_id(value) if value != -1 else []
        self.has_children = True if self.children_ids else False
        root = join('.tempfiles', 'reader')
        if not exists(root):
            makedirs(root)
        location = join(root, 'entry_id')
        with open(location, 'w') as file:
            file.write(str(value))
            file.close()

    def on_filtered_tags(self, instance, value):
        self.filtered_tags_data = [{'text': x, 'screen': 'writer'} for x in value]

    def on_filtered_entry_ids(self, instance, value):
        self.filtered_dates_data = [
            {'text': self.database.get_date_by_entry_id(entry_id, self.date_button_format), 'entry_id': entry_id,
             'caller': self} for entry_id in value]

    def on_continuous_range(self):
        self.write_filters_to_temp_file()

    def on_filter_has_parent(self):
        self.write_filters_to_temp_file()

    def on_filter_has_children(self):
        self.write_filters_to_temp_file()

    def on_filter_has_attachment(self):
        self.write_filters_to_temp_file()

    def on_filter_tag_sort(self):
        self.write_filters_to_temp_file()

    def call_children_popup(self):
        Factory.ChildrenPopup(self.children_ids, self.date, self, self.database).open()

    def call_attachments_popup(self):
        Factory.AttachmentsPopup(self.att_ids, self.date, self, self.database).open()

    def call_filter_popup(self):
        Factory.FiltersPopup(self, self.filtered_entry_ids, self.continuous_range, self.filter_has_parent,
                             self.filter_has_children, self.filter_has_attachments, self.tag_sort, self.database).open()

    def clear_ui(self):
        self.entry_id = -1

    def write_filters_to_temp_file(self):
        filters = [str(self.continuous_range), str(self.filter_has_parent), str(self.filter_has_children),
                   str(self.filter_has_attachments), self.tag_sort]
        root = join('.tempfiles', 'reader')
        if not exists(root):
            makedirs(root)
        location = join(root, 'filters')
        with open(location, 'w') as file:
            file.write('\n'.join(filters))
            file.close()


class FiltersPopup(Popup):
    database = ObjectProperty()
    caller = ObjectProperty()
    continuous_range = BooleanProperty()
    has_parent = BooleanProperty()
    has_children = BooleanProperty()
    has_attachments = BooleanProperty()
    tag_sort = StringProperty()
    entry_ids = ListProperty()
    filtered_tags = ListProperty()
    unfiltered_tags = ListProperty()

    def __init__(self, caller: ReadingModule, entry_ids: list, continuous_range_setting: bool, has_parent_setting: bool,
                 has_children_setting: bool, has_attachments_setting: bool, tag_sort_setting: str,
                 database: DatabaseManager = None, **kwargs):
        super(FiltersPopup, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
        self.entry_ids = entry_ids
        self.caller = caller
        self.continuous_range = continuous_range_setting
        self.has_parent = has_parent_setting
        self.has_children = has_children_setting
        self.has_attachments = has_attachments_setting
        self.tag_sort = tag_sort_setting

    def on_has_parent(self, instance, value):
        pass

    def on_has_children(self, instance, value):
        pass

    def on_has_attachments(self, instance, value):
        pass


class ChildrenPopup(Popup):
    database = ObjectProperty()
    caller = ObjectProperty()
    children_master = ObjectProperty()
    children_data = ListProperty()
    date = StringProperty()
    selected_id = NumericProperty(None, allownone=True)
    datebutton_format = StringProperty('%a, %b %d, %Y %H:%M')
    search_text = StringProperty()

    def __init__(self, children_ids: list, date: str, caller: ReadingModule = None, database: DatabaseManager = None,
                 **kwargs):
        super(ChildrenPopup, self).__init__(**kwargs)
        self.date = date
        self.caller = caller
        self.database = database if database else DatabaseManager()
        self.children_master = [
            {'text': self.database.get_date_by_entry_id(entry_id, self.datebutton_format), 'caller': self,
             'entry_id': entry_id} for entry_id in children_ids]
        self.children_data = self.children_master

    def on_search_text(self, instance, value):
        if value:
            self.children_data = [x for x in self.children_master if value.lower() in x['text'].lower()]
        else:
            self.children_data = [x for x in self.children_master]

    def on_dismiss(self):
        if self.caller and self.selected_id:
            self.caller.entry_id = self.selected_id
        elif self.selected_id:
            print(self.selected_id)
        super(ChildrenPopup, self).on_dismiss()


class ChildButton(GenericButton):
    pass


class AttachmentsPopup(Popup):
    database = ObjectProperty()
    caller = ObjectProperty()
    attachments_master = list()
    attachments_data = ListProperty()
    date = StringProperty()
    search_text = StringProperty()
    announcement = StringProperty()

    def __init__(self, att_ids: list, date: str, caller: ReadingModule = None, database: DatabaseManager = None,
                 **kwargs):
        super(AttachmentsPopup, self).__init__(**kwargs)
        self.date = date
        self.caller = caller
        self.database = database if database else DatabaseManager()
        for x in att_ids:
            n = self.database.get_attachment_name_from_att_id(x)
            t = n if len(n) < 35 else n[:20] + ' ... .' + n.split('.')[-1]
            d = {'att_id': x, 'caller': self, 'name': n, 'text': t}
            self.attachments_data.append(d)
            self.attachments_master.append(d)

    def on_search_text(self, instance, value):
        if value:
            self.attachments_data = [x for x in self.attachments_master if value.lower() in x['name'].lower()]
        else:
            self.attachments_data = [x for x in self.attachments_master]

    def export_file(self, att_id, name):
        stream = self.database.get_attachment_from_att_id(att_id)
        if not exists('Exports'):
            makedirs('Exports')
        location = join('Exports', name)
        with open(location, 'wb') as file:
            file.write(stream)
            file.close()
        self.announcement = name + ' exported to \'Exports\' folder.'


class AttachmentButton(GenericButton):
    pass


class ShortMessagePopup(Popup):
    message = StringProperty('')

    def __init__(self, message: str, **kwargs):
        self.message = message
        super(ShortMessagePopup, self).__init__(**kwargs)


class SlideBox(BoxLayout):
    decoupled_values = BooleanProperty()
    disable_on_decouple = BooleanProperty
    label_list = ListProperty()
    label = StringProperty('')
    min_range = NumericProperty()
    max_range = NumericProperty()
    min_value = NumericProperty()
    max_value = NumericProperty()

    def __init__(self, **kwargs):
        self.decoupled_values = kwargs['decoupled_values'] if 'decoupled_values' in kwargs.keys() else False
        self.disable_on_decouple = kwargs['disable_on_decouple'] if 'disable_on_decouple' in kwargs.keys() else False
        self.label_list = kwargs['label_list'] if 'label_list' in kwargs.keys() else []
        self.label = kwargs['label'] if 'label' in kwargs.keys() else ''
        self.min_range = 0
        self.max_range = len(self.label_list) - 1 if self.label_list else 0
        self.min_value = kwargs['min_value'] if 'min_value' in kwargs.keys() else 0
        self.max_value = kwargs['max_value'] if 'max_value' in kwargs.keys() else self.max_range
        super(SlideBox, self).__init__(**kwargs)

    def on_label_list(self, instance, value):
        self.max_range = len(self.label_list) - 1
        self.max_value = self.max_range

    def on_decoupled_values(self, instance, value):
        if value is False and self.max_value < self.min_value:
            self.max_value = self.min_value
