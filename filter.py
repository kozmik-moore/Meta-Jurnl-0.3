"""Contains the classes and functions that allow for switch-type manipulation of filters"""
from contextlib import closing
from datetime import datetime
from os.path import abspath
from sqlite3 import connect
from typing import Union, Tuple

from configurations import current_database
from database_info import get_all_entry_ids, get_oldest_date, get_newest_date, get_all_tags, \
    get_all_children, get_all_parents
from reader import Reader, get_tags, get_date


def from_continuous_range(lower: datetime = None, upper: datetime = None, database: str = None):
    """Filters the database for entries that were created over a given range of time

    :param database: a str representing the location of the database that is being queried
    :param lower: a datetime representing the lower limit of the dates to filter for
    :param upper:  a datetime representing the upper limit of the dates to filter for
    :return: a list of ints representing the filtered entries
    :rtype: list
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        lower = get_oldest_date(database) if not lower else lower
        upper - get_newest_date(database) if not upper else upper
        lower = lower.replace(second=0, microsecond=0)
        upper = upper.replace(second=59, microsecond=999999)
        c = d.execute('SELECT entry_id FROM dates WHERE created BETWEEN ? AND ?', (lower, upper)).fetchall()
        return [x[0] for x in c]


def from_intervals(lower: Tuple[int, int, int, int, int, int] = None, upper: Tuple[int, int, int, int, int, int] = None,
                   database: str = None):
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        if not lower:
            lower = (get_oldest_date(database).year, 1, 1, 0, 0, 0)
        if not upper:
            upper = (get_newest_date(database).year, 12, 31, 23, 59, 6)
        t = '{:02d}'
        c = d.execute('SELECT entry_id FROM dates WHERE (strftime("%Y", created) BETWEEN ? AND ?) AND '
                      '(strftime("%m", created) BETWEEN ? AND ?) AND (strftime("%d", created) BETWEEN ? AND ?) AND '
                      '(strftime("%H", created) BETWEEN ? AND ?) AND (strftime("%M", created) BETWEEN ? AND ?) AND '
                      '(strftime("%w", created) BETWEEN ? AND ?)',
                      (str(lower[0]), str(upper[0]), t.format(lower[1]), t.format(upper[1]),
                       t.format(lower[2]), t.format(upper[2]), t.format(lower[3]), t.format(upper[3]),
                       t.format(lower[4]), t.format(upper[4]), str(lower[5]), str(upper[5])
                       )
                      )
        return [x[0] for x in c]


def from_tags(tags: tuple, database: str = None,
              op_type: str = 'Contains One Of...'):
    """

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :param tags: a tuple of strings representing the tags to be used for filtering entries from the database
    :param op_type: a str representing the type of filter to apply
    :return: a list of ints representing the filtered entries
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        ids = []
        if op_type == 'Contains At Least...':
            tags = list(tags)
            tag = tags.pop(0)
            sql = 'SELECT entry_id FROM tags WHERE tag=?'
            temp = set(d.execute(sql, (tag,)).fetchall())
            for tag in tags:
                temp = temp.intersection(d.execute(sql, (tag,)).fetchall())
            ids = [i[0] for i in temp]
        if op_type == 'Contains Only...':
            for entry in get_all_entry_ids(database):
                if len(get_tags(entry, database)) == len(tags):
                    if set(get_tags(entry, database)).intersection(tags) == set(tags):
                        ids.append(entry)
        if op_type == 'Contains One Of...':
            sql = 'SELECT entry_id FROM tags WHERE tag IN ({})'.format(','.join(['?'] * len(tags)))
            ids = list({x[0] for x in d.execute(sql, tags).fetchall()})
        if op_type == 'Untagged':
            cmd = 'SELECT entry_id FROM tags WHERE tag=\'(UNTAGGED)\''
            ids = [x[0] for x in d.execute(cmd).fetchall()]
        return tuple(ids)


def from_attachments(database: str = None):
    """Gets the ids of entries that have attachments

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing the filtered entries
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        ids = [x[0] for x in d.execute('SELECT entry_id FROM attachments').fetchall()]
        return ids


def from_body(search_string: str, database: str = None):
    """Gets the ids of entries that contain a given search string

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :param search_string: a str which is used to sort the ids
    :return: a list of ints representing the filtered entries
    """
    # TODO allow regex for more useful searches
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        c = d.execute('SELECT entry_id FROM bodies WHERE body LIKE ?', ('%' + search_string.lower() + '%',)).fetchall()
        return [x[0] for x in c]


class Filter:
    """Provides methods for filtering entries in based on their attributes"""

    def __init__(self, path_to_db: str = None):
        self._path = abspath(path_to_db) if path_to_db else current_database()
        self._by_attachments = False
        self._by_is_child = False
        self._by_is_parent = False
        self._by_body = ''
        self._by_date = ()
        self._date_type = 'Continuous'
        self._by_tags = tuple()
        self._by_is_untagged = False
        self._tags_type = 'Contains One Of...'
        self._filtered = tuple()

    @property
    def database_location(self):
        return self._path

    @property
    def filtered_ids(self):
        return self._filtered

    @property
    def has_attachments(self):
        return self._by_attachments

    @has_attachments.setter
    def has_attachments(self, v: bool):
        """Sets the attachments flag for the filter and calls the filter

        :param v: a bool indicating whether the entries are partitioned by having attachments
        """
        if type(v) == bool:
            self._by_attachments = bool
            self._filter()

    @property
    def is_parent(self):
        return self._by_is_parent

    @is_parent.setter
    def is_parent(self, v: bool):
        """Sets the parent flag for the filter and calls the filter

        :param v: a bool indicating whether the entries are partitioned by having attachments
        """
        if type(v) == bool:
            self._by_is_parent = bool
            self._filter()

    @property
    def is_child(self):
        return self._by_is_child

    @is_child.setter
    def is_child(self, v: bool):
        if type(v) == bool:
            self._by_is_child = bool
            self._filter()

    @property
    def date_range(self):
        return self._by_date

    @date_range.setter
    def date_range(self, t: Tuple[Union[Tuple[int, int, int, int, int, int], datetime]]):
        if t and len(t) == 2:
            if all(isinstance(x, datetime) for x in t):
                self._date_type = 'Continuous'
            elif all(isinstance(x, tuple) for x in t):
                self._date_type = 'Intervals'
            self._by_date = (t[0], t[1])
        elif not t:
            self._by_date = (None, None)
        self._filter()

    @property
    def date_filter(self):
        return self.date_filter()

    @date_filter.setter
    def date_filter(self, v: str):
        if v in ['Continuous', 'Intervals']:
            self._date_type = v
            if self.date_range:
                self._filter()

    @property
    def body_has(self):
        return self._by_body

    @body_has.setter
    def body_has(self, v: str):
        if type(v) == str:
            self._by_body = v
            self._filter()

    @property
    def tags_has(self):
        return self._by_tags

    @tags_has.setter
    def tags_has(self, v: Union[Tuple[str], str]):
        if type(v) == tuple and all(isinstance(x, str) for x in v):
            self._by_tags = v
            self._filter()
        elif type(v) == str:
            if v == 'all':
                self._by_tags = tuple(get_all_tags(self.database_location))
                self._by_is_untagged = True
                self._filter()
            elif v == 'none':
                self._by_tags = ()
                self._by_is_untagged = False
                self._filter()
            elif v == 'invert':
                a = set(get_all_tags(self.database_location))
                self._by_tags = tuple(a.difference(self._by_tags))
                self._by_is_untagged = False if True else True
                self._filter()

    @property
    def is_untagged(self):
        return self._by_is_untagged

    @is_untagged.setter
    def is_untagged(self, v: bool):
        if type(v) == bool:
            self._by_is_untagged = v
            self._filter()

    @property
    def tag_filter(self):
        return self._tags_type

    @tag_filter.setter
    def tag_filter(self, v: str):
        if v in [
            'Contains One Of...',
            'Contains At Least...',
            'Contains Only...'
        ]:
            self._tags_type = v
            self._filter()

    def _filter(self):
        filtered = set(get_all_entry_ids(self.database_location))
        if self._by_attachments:
            filtered = filtered.intersection(from_attachments(self.database_location))
        if self._by_body:
            filtered = filtered.intersection(from_body(self._by_body, self.database_location))
        if any([self._by_tags, self._by_is_untagged]):
            l_ = ()
            if self._by_tags and self._by_is_untagged:
                l_ = tuple(list(self._by_tags) + ['(UNTAGGED)'])
            elif not self._by_tags and self._by_is_untagged:
                l_ = ('(UNTAGGED)',)
            elif self._by_tags and not self._by_is_untagged:
                l_ = self._by_tags
            filtered = filtered.intersection(from_tags(l_, self.database_location, self._tags_type))
        if self._by_date:
            l_ = set()
            f = self._by_date[0]
            s = self._by_date[1]
            if self._date_type == 'Continuous':
                l_ = tuple(from_continuous_range(f, s, self.database_location))
            elif self._date_type == 'Intervals':
                l_ = from_intervals(f, s, self.database_location)
            filtered = filtered.intersection(l_)
        if self._by_is_child:
            filtered = filtered.intersection(get_all_children(self.database_location))
        if self._by_is_parent:
            filtered = filtered.intersection(get_all_parents(self.database_location))
        filtered = list(filtered)
        filtered.sort(key=lambda i: get_date(entry_id=i, database=self.database_location))
        self._filtered = tuple(filtered)

    def reset_filters(self):
        self._by_attachments = False
        self._by_is_child = False
        self._by_is_parent = False
        self._by_body = ''
        self._by_date = ()
        self._date_type = 'Continuous'
        self._by_tags = tuple()
        self._by_is_untagged = False
        self._tags_type = 'Contains One Of...'
        self._filtered = tuple()

    def refresh_ids(self):
        self._filter()


class FilteredReader(Filter, Reader):
    def __init__(self, path_to_db: str = None):
        super(FilteredReader, self).__init__(path_to_db)
