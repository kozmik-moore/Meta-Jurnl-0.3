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


class SpinnerButton(GenericButton):
    pass


class TagFilterModule(BoxLayout):
    database = ObjectProperty()
    filtered_tags = ListProperty()
    unfiltered_tags = list()
    filtered_data = ListProperty()
    unfiltered_data = ListProperty()
    search_text = StringProperty('')

    def __init__(self, filtered: list = None, database: DatabaseManager = None, **kwargs):
        self.database = database if database else DatabaseManager()
        super(TagFilterModule, self).__init__(**kwargs)
        self.unfiltered_tags = self.database.get_all_tags()
        if filtered:
            self.filtered_tags = filtered

    def add_tag_to_filtered(self, tag):
        f = self.filtered_tags.copy()
        f.append(tag)
        f.sort()
        self.filtered_tags = f

    def select_all_tags(self):
        temp = list(set(self.unfiltered_tags).union(self.filtered_tags))
        temp.sort()
        self.filtered_tags = temp

    def deselect_all_tags(self):
        temp = list(set(self.unfiltered_tags).union(self.filtered_tags))
        temp.sort()
        self.unfiltered_tags = temp

    def invert_tags_selection(self):
        f = self.filtered_tags.copy()
        u = self.unfiltered_tags.copy()
        self.filtered_tags = u
        self.unfiltered_tags = f

    def on_filtered_tags(self, instance, value):
        u = self.database.get_all_tags()
        f = self.filtered_tags.copy()
        f.sort()
        for tag in f:
            if tag in u:
                u.remove(tag)
        self.unfiltered_tags = u
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


class TagButton(GenericButton):
    sorter = ObjectProperty(TagFilterModule, allownone=True)

    def __init__(self, **kwargs):
        super(TagButton, self).__init__(**kwargs)


class TagLabel(GenericLabel):
    pass


class DateButton(GenericButton):
    pass


class DateFilterModule(BoxLayout):
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
        super(DateFilterModule, self).__init__(**kwargs)
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
    database = ObjectProperty()
    has_parent = BooleanProperty(False)
    has_children = BooleanProperty(False)
    has_attachments = BooleanProperty(False)
    continuous_range = BooleanProperty(False)
    filter_has_parent = BooleanProperty(False)
    filter_has_children = BooleanProperty(False)
    filter_has_attachments = BooleanProperty(False)
    filter_has_body = StringProperty(False)
    body_search = StringProperty()
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
    filter_screen = StringProperty()
    proportion = StringProperty()
    edit_property = NumericProperty()

    def __init__(self, database: DatabaseManager = None, **kwargs):
        self.database = database if database else DatabaseManager()
        super(ReadingModule, self).__init__(**kwargs)
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
                                                     'Contains One Of...', 'Untagged'] else 'Contains One Of...'
                    temp = file.readline().strip('\n')
                    self.date_sort = literal_eval(temp) if temp and literal_eval(temp) else {
                        'year': [0, len(self.database.get_years()) - 1], 'month': [0, 11], 'day': [0, 30],
                        'hour': [0, 23], 'minute': [0, 59], 'weekday': [0, 6]}
                    temp = file.readline().strip('\n')
                    self.filter_tags = [x for x in literal_eval(temp) if
                                        x in self.database.get_all_tags()] if temp and literal_eval(temp) else []
                    temp = file.readline().strip('\n')
                    self.filtered_entry_ids = literal_eval(temp) if temp and literal_eval(
                        temp) else []
                    file.close()
            else:
                self.continuous_range = False
                self.filter_has_parent = False
                self.filter_has_children = False
                self.filter_has_attachments = False
                self.tag_sort = 'Contains One Of...'
                self.date_sort = {'year': [0, len(self.database.get_years()) - 1], 'month': [0, 11], 'day': [0, 30],
                                  'hour': [0, 23], 'minute': [0, 59], 'weekday': [0, 6]}
                self.filter_tags = []
                self.filtered_entry_ids = []
        else:
            self.entry_id = -1
            makedirs(root)
        if self.database.get_number_of_entries() != 0:
            a = len(self.filtered_entry_ids)
            b = self.database.get_number_of_entries()
            r = a / b
            ratio = 100 * round(r, 3)
            text = '{} | {} ({:.1f}%)'.format(a, b, ratio)
        else:
            text = 'Empty Journal'
        self.proportion = text

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
        if self.database.get_number_of_entries() != 0:
            a = len(self.filtered_entry_ids)
            b = self.database.get_number_of_entries()
            r = a / b
            ratio = 100 * round(r, 3)
            text = '{} | {} ({:.1f}%)'.format(a, b, ratio)
        else:
            text = 'Empty Journal'
        self.proportion = text
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

    def set_edit_property(self):
        self.edit_property = self.entry_id
        self.edit_property = -1

    def call_children_popup(self):
        Factory.ChildrenPopup(self.children_ids, self.date, self, self.database).open()

    def call_attachments_popup(self):
        Factory.AttachmentsPopup(self.att_ids, self.date, self, self.database).open()

    def call_filter_popup(self):
        kwargs = {'has_parent': self.filter_has_parent, 'has_children': self.filter_has_children,
                  'has_attachments': self.filter_has_attachments, 'ranges': self.date_sort, 'caller': self,
                  'continuous_range': self.continuous_range, 'selected_ids': self.filtered_entry_ids,
                  'database': self.database, 'filter_tags': self.filter_tags, 'tag_sort': self.tag_sort,
                  'body_search_text': self.body_search, 'has_body': self.filter_has_body}
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


def parse_date_ranges(month: list, day: list, year: list, hour: list, minute: list,
                      years: list):
    lower = None
    upper = None
    outside_day_range = True
    n = 0
    while outside_day_range:
        try:
            lower = parse('{}-{}-{} {}:{}'.format(month[0] + 1, day[0] + 1 - n, years[year[0]],
                                                  hour[0], minute[0]))
            outside_day_range = False
        except ParserError:
            n += 1
    outside_day_range = True
    n = 0
    while outside_day_range:
        try:
            upper = parse('{}-{}-{} {}:{}'.format(month[1] + 1, day[1] + 1 - n, years[year[1]],
                                                  hour[1], minute[1]))
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
    tags_filter_type = StringProperty('Contains One Of...')
    filtered_tags = ListProperty([])
    database = ObjectProperty()
    body_search_text = StringProperty(None, allownone=True)
    current_screen = StringProperty()
    caller = ObjectProperty()
    selected_ids = ListProperty()
    mass_select = StringProperty('Mass Select')

    def __init__(self, database, has_parent, has_children, has_attachments, has_body, ranges, caller,
                 continuous_range, selected_ids, filter_tags, tag_sort, body_search_text, **kwargs):
        self.database = database
        super(FiltersPopup, self).__init__(**kwargs)
        self.has_parent = has_parent if has_parent else False
        self.has_children = has_children if has_children else False
        self.has_attachments = has_attachments if has_attachments else False
        self.has_body = has_body if has_body else False
        self.body_search_text = body_search_text if body_search_text else ''
        self.years = self.database.get_years()
        self.ranges = ranges if ranges else {
            'year': [0, len(self.years) - 1],
            'month': [0, 11],
            'day': [0, 30],
            'hour': [0, 23],
            'minute': [0, 59],
            'weekday': [0, 6]}
        self.caller = caller if caller else ReadingModule()
        self.continuous_range = continuous_range if continuous_range else False
        self.selected_ids = selected_ids if selected_ids else []
        self.tags_filter_type = tag_sort if tag_sort else 'Contains One Of...'
        self.filtered_tags = filter_tags if filter_tags else []
        self.date_filter_module = self.ids[
            'date_filter_module'] if 'date_filter_module' in self.ids else DateFilterModule()
        self.tags_filter_module = self.ids[
            'tag_filter_module'] if 'tag_filter_module' in self.ids else TagFilterModule()
        self.current_screen = self.caller.filter_screen
        self.date_filter_module.update_ranges(self.ranges)
        self.date_filter_module.bind(year=self.update_year)
        self.date_filter_module.bind(month=self.update_month)
        self.date_filter_module.bind(day=self.update_day)
        self.date_filter_module.bind(hour=self.update_hour)
        self.date_filter_module.bind(minute=self.update_minute)
        self.date_filter_module.bind(weekday=self.update_weekday)
        self.tags_filter_module.bind(filtered_tags=self.update_filtered_tags)

    def on_ranges(self, instance, value):
        if self.caller:
            self.caller.date_sort = value
        self.update_filtered_ids()

    def on_continuous_range(self, instance, value):
        if self.caller:
            self.caller.continuous_range = self.continuous_range
        # self.update_filtered_ids()

    def update_year(self, instance, value):
        self.ranges['year'] = value.copy()
        # self.update_filtered_ids()

    def update_month(self, instance, value):
        self.ranges['month'] = value.copy()
        # self.update_filtered_ids()

    def update_day(self, instance, value):
        self.ranges['day'] = value.copy()
        # self.update_filtered_ids()

    def update_hour(self, instance, value):
        self.ranges['hour'] = value.copy()
        # self.update_filtered_ids()

    def update_minute(self, instance, value):
        self.ranges['minute'] = value.copy()
        # self.update_filtered_ids()

    def update_weekday(self, instance, value):
        self.ranges['weekday'] = value.copy()
        # self.update_filtered_ids()

    def on_has_parent(self, instance, value):
        self.update_filtered_ids()

    def on_has_children(self, instance, value):
        self.update_filtered_ids()

    def on_has_attachments(self, instance, value):
        self.update_filtered_ids()

    def on_has_body(self, instance, value):
        self.update_filtered_ids()

    def on_mass_select(self, instance, value):
        if value in ['All', 'None', 'Invert']:
            if value == 'All':
                self.tags_filter_module.filtered_tags = self.database.get_all_tags()
            elif value == 'None':
                self.tags_filter_module.filtered_tags = []
            else:
                self.tags_filter_module.invert_tags_selection()

    def on_tags_filter_type(self, instance, value):
        if self.filtered_tags and value == 'Untagged':
            self.tags_filter_module.filtered_tags = []
        self.update_filtered_ids()

    def update_filtered_tags(self, instance, value):
        self.filtered_tags = value
        if self.tags_filter_type == 'Untagged' and self.filtered_tags:
            self.tags_filter_type = 'Contains One Of...'
        self.update_filtered_ids()

    def update_filtered_ids(self):
        if self.years:
            temp = self.ranges.copy()
            if self.continuous_range:
                temp['years'] = self.years
                del temp['weekday']
                lower, upper = parse_date_ranges(**temp)
                filtered_ids = self.database.get_entry_ids_from_continuous_range(lower, upper)
            else:
                temp['year'] = [self.years[temp['year'][0]], self.years[temp['year'][1]]]
                temp['month'] = [temp['month'][0] + 1, temp['month'][1] + 1]
                temp['day'] = [temp['day'][0] + 1, temp['day'][1] + 1]
                filtered_ids = self.database.get_entry_ids_from_interval_ranges(**temp)
            if self.has_children:
                filtered_ids = list(set(filtered_ids).intersection(self.database.get_entry_ids_of_all_parents()))
            if self.has_parent:
                filtered_ids = list(set(filtered_ids).intersection(self.database.get_entry_ids_of_all_children()))
            if self.has_attachments:
                filtered_ids = list(set(filtered_ids).intersection(self.database.get_entry_ids_from_attachments()))
            filtered_ids = list(set(filtered_ids).intersection(
                self.database.get_entry_ids_from_tags(self.filtered_tags.copy(), self.tags_filter_type)))
            filtered_ids.sort(key=self.database.get_date_by_entry_id)
            self.selected_ids = filtered_ids

    def on_current_screen(self, instance, value):
        self.caller.filter_screen = self.current_screen

    def clear_filters(self):
        self.has_parent = False
        self.has_children = False
        self.has_attachments = False
        self.has_body = False
        self.ranges = {'year': [0, len(self.years) - 1], 'month': [0, 11], 'day': [0, 30], 'hour': [0, 23],
                       'minute': [0, 59], 'weekday': [0, 6]}
        self.date_filter_module.update_ranges(self.ranges)
        self.continuous_range = False
        self.tags_filter_module.filtered_tags = []
        self.tags_filter_type = 'Contains One Of...'

    def on_dismiss(self):
        self.caller.filtered_entry_ids = self.selected_ids
        self.caller.date_sort = self.ranges
        self.caller.filter_has_parent = self.has_parent
        self.caller.filter_has_children = self.has_children
        self.caller.filter_has_attachments = self.has_attachments
        self.caller.filter_tags = self.filtered_tags
        self.caller.tag_sort = self.tags_filter_type
        if self.caller.entry_id not in self.selected_ids:
            self.caller.clear_ui()
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


class MenuButton(GenericButton):
    pass
