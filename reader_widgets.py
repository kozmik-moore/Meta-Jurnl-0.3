from ast import literal_eval
from datetime import datetime
from dateutil.parser import parse, ParserError
from os import makedirs
from os.path import exists, join

from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

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


class DatetimeSortModule(BoxLayout):
    years = ListProperty()
    ranges = DictProperty()
    continuous_range = BooleanProperty()
    year = ListProperty([0, 0])
    month = ListProperty([0, 0])
    day = ListProperty([0, 0])
    hour = ListProperty([0, 0])
    minute = ListProperty([0, 0])
    weekday = ListProperty([0, 0])

    def __init__(self, years: list = None, continuous: bool = False, ranges: dict = None, **kwargs):
        super(DatetimeSortModule, self).__init__(**kwargs)
        self.years = years if years else [datetime.now().year]
        self.continuous_range = continuous
        self.year = [ranges['year'][0], ranges['year'][1]] if ranges else [0, len(self.years) - 1]
        self.month = [ranges['month'][0], ranges['month'][1]] if ranges else [0, 11]
        self.day = [ranges['day'][0], ranges['day'][1]] if ranges else [0, 30]
        self.hour = [ranges['hour'][0], ranges['hour'][1]] if ranges else [0, 23]
        self.minute = [ranges['minute'][0], ranges['minute'][1]] if ranges else [0, 59]
        self.weekday = [ranges['weekday'][0], ranges['weekday'][1]] if ranges else [0, 6]

    def update_ranges(self, ranges):
        self.year = [ranges['year'][0], ranges['year'][1]] if ranges else [0, len(self.years) - 1]
        self.month = [ranges['month'][0], ranges['month'][1]] if ranges else [0, 11]
        self.day = [ranges['day'][0], ranges['day'][1]] if ranges else [0, 30]
        self.hour = [ranges['hour'][0], ranges['hour'][1]] if ranges else [0, 23]
        self.minute = [ranges['minute'][0], ranges['minute'][1]] if ranges else [0, 59]
        self.weekday = [ranges['weekday'][0], ranges['weekday'][1]] if ranges else [0, 6]


class ReadingModule(BoxLayout):
    database = ObjectProperty(None, allownone=True)
    has_parent = BooleanProperty(False)
    has_children = BooleanProperty(False)
    has_attachments = BooleanProperty(False)
    continuous_range = BooleanProperty(False)
    filter_has_parent = BooleanProperty(False)
    filter_has_children = BooleanProperty(False)
    filter_has_attachments = BooleanProperty(False)
    filter_has_body = StringProperty(False)
    tag_sort = StringProperty()
    date_sort = DictProperty()
    filter_tags = ListProperty()
    entry_id = NumericProperty(-1)
    parent_id = NumericProperty(-1)
    body = StringProperty()
    entry_tags = ListProperty()
    entry_tags_data = ListProperty()
    children_ids = ListProperty()
    att_ids = ListProperty()
    date = StringProperty()
    filtered_entry_ids = ListProperty()
    filtered_dates_data = ListProperty()
    date_label_format = StringProperty('%A, %B %d, %Y %H:%M')
    date_button_format = StringProperty('%Y-%m-%d %H:%M')

    def __init__(self, database: DatabaseManager = None, **kwargs):
        super(ReadingModule, self).__init__(**kwargs)
        self.database = database if database else DatabaseManager()
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
                    self.continuous_range = True if temp == 'True' else False
                    temp = file.readline().strip('\n')
                    self.filter_has_parent = True if temp == 'True' else False
                    temp = file.readline().strip('\n')
                    self.filter_has_children = True if temp == 'True' else False
                    temp = file.readline().strip('\n')
                    self.filter_has_attachments = True if temp == 'True' else False
                    temp = file.readline().strip('\n')
                    self.tag_sort = temp if temp in ['Contains At Least...', 'Contains Only...',
                                                     'Contains...'] else 'Contains...'
                    temp = file.readline().strip('\n')
                    self.date_sort = literal_eval(temp) if temp and literal_eval(temp) else {
                        'year': [0, len(self.database.get_years()) - 1], 'month': [0, 11], 'day': [0, 30],
                        'hour': [0, 23], 'minute': [0, 59], 'weekday': [0, 6]}
                    temp = file.readline().strip('\n')
                    self.filter_tags = [x for x in literal_eval(temp) if
                                        x in self.database.get_all_tags()] if temp and literal_eval(temp) else []
                    temp = file.readline().strip('\n')
                    self.filtered_entry_ids = literal_eval(temp) if temp and literal_eval(
                        temp) else self.database.get_all_entry_ids()
                    file.close()
            else:
                self.continuous_range = False
                self.filter_has_parent = False
                self.filter_has_children = False
                self.filter_has_attachments = False
                self.tag_sort = 'Contains...'
                self.date_sort = {'year': [0, len(self.database.get_years()) - 1], 'month': [0, 11], 'day': [0, 30],
                                  'hour': [0, 23], 'minute': [0, 59], 'weekday': [0, 6]}
                self.filter_tags = []
                self.filtered_entry_ids = self.database.get_all_entry_ids()
        else:
            self.entry_id = -1
            makedirs(root)
        self.date_sort_module = self.ids['date_sort_module'] if 'date_sort_module' in self.ids else DatetimeSortModule()

    def on_entry_id(self, instance, value):
        self.body = self.database.get_body_by_entry_id(value) if value != -1 else ''
        self.entry_tags = self.database.get_tags_by_entry_id(value) if value != -1 else []
        self.att_ids = self.database.get_att_ids_from_entry_id(value) if value != -1 else []
        self.has_attachments = True if self.att_ids and value != -1 else False
        self.parent_id = self.database.get_parent_by_entry_id(value) if value != -1 else -1
        self.has_parent = True if self.parent_id != -1 else False
        self.date = self.database.get_date_by_entry_id(value).strftime(self.date_label_format) if value != -1 else ''
        self.children_ids = self.database.get_children_by_entry_id(value) if value != -1 else []
        self.has_children = True if self.children_ids and value != -1 else False
        root = join('.tempfiles', 'reader')
        if not exists(root):
            makedirs(root)
        location = join(root, 'entry_id')
        with open(location, 'w') as file:
            file.write(str(value))
            file.close()

    def on_entry_tags(self, instance, value):
        self.entry_tags_data = [{'text': x, 'screen': 'writer'} for x in value]

    def on_filtered_entry_ids(self, instance, value):
        self.filtered_dates_data = [
            {'text': self.database.get_date_by_entry_id(entry_id, self.date_button_format), 'entry_id': entry_id,
             'caller': self} for entry_id in value]
        self.write_filters_to_temp_file()

    def on_continuous_range(self, instance, value):
        self.write_filters_to_temp_file()

    def on_filter_has_parent(self, instance, value):
        self.write_filters_to_temp_file()

    def on_filter_has_children(self, instance, value):
        self.write_filters_to_temp_file()

    def on_filter_has_attachments(self, instance, value):
        self.write_filters_to_temp_file()

    def on_tag_sort(self, instance, value):
        self.write_filters_to_temp_file()

    def on_date_sort(self, instance, value):
        self.write_filters_to_temp_file()

    def on_filter_tags(self, instance, value):
        self.write_filters_to_temp_file()

    def call_children_popup(self):
        Factory.ChildrenPopup(self.children_ids, self.date, self, self.database).open()

    def call_attachments_popup(self):
        Factory.AttachmentsPopup(self.att_ids, self.date, self, self.database).open()

    def call_filter_popup(self):
        kwargs = {'has_parent': self.filter_has_parent, 'has_children': self.filter_has_children,
                  'has_attachments': self.filter_has_attachments, 'ranges': self.date_sort, 'caller': self,
                  'continuous_range': self.continuous_range, 'selected_ids': self.filtered_entry_ids}
        Factory.FiltersPopup(**kwargs).open()

    def clear_ui(self):
        self.entry_id = -1

    def write_filters_to_temp_file(self):
        filters = [str(self.continuous_range), str(self.filter_has_parent), str(self.filter_has_children),
                   str(self.filter_has_attachments), self.tag_sort, str(self.date_sort), str(self.filter_tags),
                   str(self.filtered_entry_ids)]
        root = join('.tempfiles', 'reader')
        if not exists(root):
            makedirs(root)
        location = join(root, 'filters')
        with open(location, 'w') as file:
            file.write('\n'.join(filters))
            file.close()


def parse_date_ranges(month_index: list, day_index: list, year_index: list, hour_index: list, minute_index: list,
                      years: list):
    lower = None
    upper = None
    outside_day_range = True
    n = 0
    while outside_day_range:
        try:
            lower = parse('{}-{}-{} {}:{}'.format(month_index[0] + 1, day_index[0] + 1 - n, years[year_index[0]],
                                                  hour_index[0], minute_index[0]))
            outside_day_range = False
        except ParserError:
            n += 1
    outside_day_range = True
    n = 0
    while outside_day_range:
        try:
            upper = parse('{}-{}-{} {}:{}'.format(month_index[1] + 1, day_index[1] + 1 - n, years[year_index[1]],
                                                  hour_index[1], minute_index[1]))
            outside_day_range = False
        except ParserError:
            n += 1
    return lower, upper


class FiltersPopup(Popup):
    has_parent = BooleanProperty(False)
    has_children = BooleanProperty(False)
    has_attachments = BooleanProperty(False)
    has_body = BooleanProperty(False)
    ranges = DictProperty({
        'year': [0, 0],
        'month': [0, 11],
        'day': [0, 30],
        'hour': [0, 23],
        'minute': [0, 59],
        'weekday': [0, 6]})
    years = ListProperty()
    continuous_range = BooleanProperty()
    filtered_tags = ListProperty([])
    database = ObjectProperty(DatabaseManager)
    body_search_text = StringProperty()
    current_screen = StringProperty()
    caller = ObjectProperty()
    selected_ids = ListProperty()

    def __init__(self, **kwargs):
        super(FiltersPopup, self).__init__(**kwargs)
        self.has_parent = kwargs['has_parent'] if 'has_parent' in kwargs.keys() else False
        self.has_children = kwargs['has_children'] if 'has_children' in kwargs.keys() else False
        self.has_attachments = kwargs['has_attachments'] if 'has_attachments' in kwargs.keys() else False
        self.has_body = kwargs['has_body'] if 'has_body' in kwargs.keys() else False
        self.database = kwargs['database'] if 'database' in kwargs.keys() else DatabaseManager()
        self.years = self.database.get_years()
        self.ranges = kwargs['ranges'] if 'ranges' in kwargs.keys() else {
            'year': [0, len(self.years) - 1],
            'month': [0, 11],
            'day': [0, 30],
            'hour': [0, 23],
            'minute': [0, 59],
            'weekday': [0, 6]}
        self.caller = kwargs['caller'] if 'caller' in kwargs.keys() else ReadingModule()
        self.continuous_range = kwargs['continuous_range'] if 'continuous_range' in kwargs.keys() else False
        self.selected_ids = kwargs['selected_ids'] if 'selected_ids' in kwargs.keys() else []
        self.date_sort_module = self.ids['date_sort_module'] if 'date_sort_module' in self.ids else DatetimeSortModule
        self.date_sort_module.update_ranges(self.ranges)
        self.date_sort_module.bind(year=self.update_year)
        self.date_sort_module.bind(month=self.update_month)
        self.date_sort_module.bind(day=self.update_day)
        self.date_sort_module.bind(hour=self.update_hour)
        self.date_sort_module.bind(minute=self.update_minute)

    def on_ranges(self, instance, value):
        if self.caller:
            self.caller.date_sort = value

    def on_continuous_range(self, instance, value):
        if self.caller:
            self.caller.continuous_range = self.continuous_range

    def update_year(self, instance, value):
        if self.continuous_range:
            temp = self.ranges.copy()
            new_lower, new_upper = parse_date_ranges(temp['month'], temp['day'], value, temp['hour'], temp['minute'],
                                                     self.years)
            old_lower, old_upper = parse_date_ranges(temp['month'], temp['day'], temp['year'], temp['hour'],
                                                     temp['minute'], self.years)
            ids = self.database.get_entry_ids_from_continuous_range(new_lower, new_upper)
            if new_lower < old_lower or new_upper > old_upper:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if new_lower > old_lower or new_upper < old_upper:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        else:
            ids = self.database.get_entry_ids_from_year_range([self.years[value[0]], self.years[value[1]]])
            if value[0] < self.ranges['year'][0] or value[1] > self.ranges['year'][1]:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if value[0] > self.ranges['year'][0] or value[1] < self.ranges['year'][1]:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        self.ranges['year'] = value.copy()

    def update_month(self, instance, value):
        if self.continuous_range:
            temp = self.ranges.copy()
            new_lower, new_upper = parse_date_ranges(value, temp['day'], temp['year'], temp['hour'], temp['minute'],
                                                     self.years)
            old_lower, old_upper = parse_date_ranges(temp['month'], temp['day'], temp['year'], temp['hour'],
                                                     temp['minute'], self.years)
            ids = self.database.get_entry_ids_from_continuous_range(new_lower, new_upper)
            if new_lower < old_lower or new_upper > old_upper:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if new_lower > old_lower or new_upper < old_upper:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        else:
            ids = self.database.get_entry_ids_from_month_range([value[0] + 1, value[1] + 1])
            if value[0] < self.ranges['month'][0] or value[1] > self.ranges['month'][1]:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if value[0] > self.ranges['month'][0] or value[1] < self.ranges['month'][1]:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        self.ranges['month'] = value.copy()

    def update_day(self, instance, value):
        if self.continuous_range:
            temp = self.ranges.copy()
            new_lower, new_upper = parse_date_ranges(temp['month'], value, temp['year'], temp['hour'], temp['minute'],
                                                     self.years)
            old_lower, old_upper = parse_date_ranges(temp['month'], temp['day'], temp['year'], temp['hour'],
                                                     temp['minute'], self.years)
            ids = self.database.get_entry_ids_from_continuous_range(new_lower, new_upper)
            if new_lower < old_lower or new_upper > old_upper:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if new_lower > old_lower or new_upper < old_upper:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        else:
            ids = self.database.get_entry_ids_from_day_range([value[0] + 1, value[1] + 1])
            if value[0] < self.ranges['day'][0] or value[1] > self.ranges['day'][1]:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if value[0] > self.ranges['day'][0] or value[1] < self.ranges['day'][1]:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        self.ranges['day'] = value.copy()

    def update_hour(self, instance, value):
        if self.continuous_range:
            temp = self.ranges.copy()
            new_lower, new_upper = parse_date_ranges(temp['month'], temp['day'], temp['year'], value, temp['minute'],
                                                     self.years)
            old_lower, old_upper = parse_date_ranges(temp['month'], temp['day'], temp['year'], temp['hour'],
                                                     temp['minute'], self.years)
            ids = self.database.get_entry_ids_from_continuous_range(new_lower, new_upper)
            if new_lower < old_lower or new_upper > old_upper:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if new_lower > old_lower or new_upper < old_upper:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        else:
            ids = self.database.get_entry_ids_from_hour_range(value)
            if value[0] < self.ranges['hour'][0] or value[1] > self.ranges['hour'][1]:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if value[0] > self.ranges['hour'][0] or value[1] < self.ranges['hour'][1]:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        self.ranges['hour'] = value.copy()

    def update_minute(self, instance, value):
        if self.continuous_range:
            temp = self.ranges.copy()
            new_lower, new_upper = parse_date_ranges(temp['month'], temp['day'], temp['year'], temp['hour'], value,
                                                     self.years)
            old_lower, old_upper = parse_date_ranges(temp['month'], temp['day'], temp['year'], temp['hour'],
                                                     temp['minute'], self.years)
            ids = self.database.get_entry_ids_from_continuous_range(new_lower, new_upper)
            if new_lower < old_lower or new_upper > old_upper:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if new_lower > old_lower or new_upper < old_upper:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        else:
            ids = self.database.get_entry_ids_from_minute_range(value)
            if value[0] < self.ranges['minute'][0] or value[1] > self.ranges['minute'][1]:
                self.selected_ids = list(set(self.selected_ids).union(ids))
            if value[0] > self.ranges['minute'][0] or value[1] < self.ranges['minute'][1]:
                self.selected_ids = list(set(self.selected_ids).intersection(ids))
        self.ranges['minute'] = value.copy()

    def clear_filters(self):
        self.has_parent = False
        self.has_children = False
        self.has_attachments = False
        self.has_body = False
        self.ranges = {'year': [0, len(self.years) - 1], 'month': [0, 11], 'day': [0, 30], 'hour': [0, 23],
                       'minute': [0, 59], 'weekday': [0, 6]}
        self.date_sort_module.update_ranges(self.ranges)
        self.continuous_range = False

    def on_dismiss(self):
        self.caller.filtered_entry_ids = self.selected_ids
        self.caller.date_sort = self.ranges
        super(FiltersPopup, self).on_dismiss()


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
        super(SlideBox, self).__init__(**kwargs)
        self.decoupled_values = kwargs['decoupled_values'] if 'decoupled_values' in kwargs.keys() else False
        self.disable_on_decouple = kwargs['disable_on_decouple'] if 'disable_on_decouple' in kwargs.keys() else False
        self.label_list = kwargs['label_list'] if 'label_list' in kwargs.keys() else []
        self.label = kwargs['label'] if 'label' in kwargs.keys() else ''
        self.min_range = 0
        self.max_range = len(self.label_list) - 1 if self.label_list else 0
        self.min_value = kwargs['min_value'] if 'min_value' in kwargs.keys() else 0
        self.max_value = kwargs['max_value'] if 'max_value' in kwargs.keys() else self.max_range

    def on_label_list(self, instance, value):
        self.max_range = len(self.label_list) - 1
        self.max_value = self.max_range

    def on_decoupled_values(self, instance, value):
        if value is False and self.max_value < self.min_value:
            self.max_value = self.min_value
