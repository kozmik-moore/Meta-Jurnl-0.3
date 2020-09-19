"""Contains the classes and functions that allow for switch-type manipulation of filters"""
from contextlib import closing
from datetime import datetime
from os.path import abspath
from sqlite3 import connect
from typing import Union, Tuple, Dict

from configurations import default_database
from database_info import get_all_entry_ids, get_oldest_date, get_newest_date, get_all_tags, \
    get_all_children, get_all_parents
from reader_functions import get_tags, get_date


def _leap_year(year: int):
    leap = False
    if (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0):
        leap = True
    return leap


def check_day_against_month(day: int, month: int, year: int = None):
    if month in [4, 6, 9, 11] and day > 30:
        day = 30
    if month == 2 and day >= 29:
        day = 29
        if not _leap_year(year):
            day = 28
    return day


def from_continuous_range(intervals: Dict[str, int], database: str = None):
    """Filters the database for entries that were created over a given range of time

    :param intervals:
    :param database: a str representing the location of the database that is being queried
    :return: a list of ints representing the filtered entries
    :rtype: list
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        l_year = intervals.get('low year', get_oldest_date(database))
        h_year = intervals.get('high year', get_newest_date(database))
        l_month = intervals.get('low month', 1)
        h_month = intervals.get('high month', 12)
        l_day = intervals.get('low day', 1)
        h_day = intervals.get('high day', 31)
        l_hour = intervals.get('low hour', 0)
        h_hour = intervals.get('high hour', 23)
        l_minute = intervals.get('low minute', 0)
        h_minute = intervals.get('high minute', 59)
        l_second = 0
        h_second = 59
        l_microsecond = 0
        h_microsecond = 999999
        lower = datetime(l_year, l_month, l_day, l_hour, l_minute, l_second, l_microsecond)
        upper = datetime(h_year, h_month, h_day, h_hour, h_minute, h_second, h_microsecond)
        c = d.execute('SELECT entry_id FROM dates WHERE created BETWEEN ? AND ?', (lower, upper)).fetchall()
        return [x[0] for x in c]


def from_intervals(intervals: Dict[str, int], database: str = None):
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        l_year = intervals.get('low year', get_oldest_date(database).year)
        h_year = intervals.get('high year', get_newest_date(database).year)
        l_month = intervals.get('low month', 1)
        h_month = intervals.get('high month', 12)
        l_day = intervals.get('low day', 1)
        h_day = intervals.get('high day', 31)
        l_hour = intervals.get('low hour', 0)
        h_hour = intervals.get('high hour', 23)
        l_minute = intervals.get('low minute', 0)
        h_minute = intervals.get('high minute', 59) + 0.999999
        l_weekday = intervals.get('low weekday', 0)
        h_weekday = intervals.get('high weekday', 6)
        t = '{:02d}'
        f = '{:09.6f}'
        c = d.execute('SELECT entry_id FROM dates WHERE (strftime("%Y", created) BETWEEN ? AND ?) AND '
                      '(strftime("%m", created) BETWEEN ? AND ?) AND (strftime("%d", created) BETWEEN ? AND ?) AND '
                      '(strftime("%H", created) BETWEEN ? AND ?) AND (strftime("%f", created) BETWEEN ? AND ?) AND '
                      '(strftime("%w", created) BETWEEN ? AND ?)',
                      (str(l_year), str(h_year), t.format(l_month), t.format(h_month), t.format(l_day), t.format(h_day),
                       t.format(l_hour), t.format(h_hour), f.format(l_minute), f.format(h_minute), str(l_weekday),
                       str(h_weekday)
                       )
                      )
        return [x[0] for x in c]


def from_tags(tags: tuple, database: str = None, op_type: int = 0):
    """Given a set of tags and a filter type, returns the ids of entries that satisfy the criteria

    :rtype: tuple
    :param database: a Connection or str representing the database that is being queried
    :param tags: a tuple of strings representing the tags to be used for filtering entries from the database
    :param op_type: an int: '0' for 'Contains One Of', '1' for 'Contains At Least, '2' for 'Contains Only'
    :return: a tuple of ints representing the filtered entries
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        ids = []
        if op_type == 1:
            if tags:
                tags = list(tags)
                tag = tags.pop(0)
                sql = 'SELECT entry_id FROM tags WHERE tag=?'
                temp = set(d.execute(sql, (tag,)).fetchall())
                for tag in tags:
                    temp = temp.intersection(d.execute(sql, (tag,)).fetchall())
                ids = [i[0] for i in temp]
        if op_type == 2:
            for entry in get_all_entry_ids(database):
                if len(get_tags(entry, database)) == len(tags):
                    if set(get_tags(entry, database)).intersection(tags) == set(tags):
                        ids.append(entry)
        if op_type == 0:
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
    db = connect(database) if database else connect(default_database())
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
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        c = d.execute('SELECT entry_id FROM bodies WHERE body LIKE ?', ('%' + search_string.lower() + '%',)).fetchall()
        return [x[0] for x in c]


class Filter:
    """Provides methods for filtering entries in based on their attributes"""

    def __init__(self, path_to_db: str = None):
        self._path = abspath(path_to_db) if path_to_db else default_database()
        self._by_attachments = 0
        self._by_child = 0
        self._by_parent = 0
        self._by_body = ''
        self._by_date = None
        self._date_type = 0  # 0 for Continuous, 1 for Intervals
        self._by_tags = tuple()
        self._by_is_untagged = False
        self._tags_type = 0
        self._filtered = tuple()
        self._filter()

    @property
    def database_location(self):
        return self._path

    @property
    def filtered_ids(self):
        """

        :rtype: Tuple[int]
        :return: a tuple of int representing the entry ids which have been filtered in
        """
        self._filter()
        return self._filtered

    @property
    def has_attachments(self):
        return self._by_attachments

    @has_attachments.setter
    def has_attachments(self, v: int):
        """Sets the attachments flag for the filter and calls the filter

        :param v: a int indicating whether the entries are partitioned by having attachments
        """
        if type(v) == int:
            self._by_attachments = v
            self._filter()

    @property
    def has_parent(self):
        return self._by_parent

    @has_parent.setter
    def has_parent(self, v: int):
        """Sets the parent flag for the filter and calls the filter

        :param v: a int indicating whether the entries are partitioned by having attachments
        """
        if type(v) == int:
            self._by_parent = v
            self._filter()

    @property
    def has_children(self):
        return self._by_child

    @has_children.setter
    def has_children(self, v: int):
        if type(v) == int:
            self._by_child = v
            self._filter()

    @property
    def dates(self):
        return self._by_date

    @dates.setter
    def dates(self, t: Dict[str, int]):
        if t:
            if self._date_type == 0:
                t['low day'] = check_day_against_month(t['low day'], t['low month'], t['low year'])
                t['high day'] = check_day_against_month(t['high day'], t['high month'], t['high year'])
            self._by_date = t
        elif not t:
            self._by_date = None
        self._filter()

    @property
    def date_filter(self):
        return self._date_type

    @date_filter.setter
    def date_filter(self, v: str):
        if v in [1, 0]:
            self._date_type = v
            if self.dates:
                self._filter()

    @property
    def body(self):
        return self._by_body

    @body.setter
    def body(self, v: str):
        if type(v) == str:
            self._by_body = v
            self._filter()

    @property
    def tags(self):
        return self._by_tags

    @tags.setter
    def tags(self, v: Union[Tuple[str], str]):
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
    def tag_filter(self, v: int):
        """Sets tags filter to one of three modes

        :param v: an int, '0' for 'Contains One Of', '1' for 'Contains At Least, '2' for 'Contains Only'
        """
        if v in [0, 1, 2]:
            self._tags_type = v
            self._filter()

    def _filter(self):
        filtered = set(get_all_entry_ids(self.database_location))
        l_ = ()

        if self._by_tags:
            l_ = list(self._by_tags)
        if self._by_is_untagged:
            l_ += ['(UNTAGGED)']
        filtered = filtered.intersection(from_tags(tuple(l_), self.database_location, self._tags_type))

        if self._by_attachments:
            filtered = filtered.intersection(from_attachments(self.database_location))
        if self._by_body:
            filtered = filtered.intersection(from_body(self._by_body, self.database_location))

        if self._by_date:
            if self._date_type == 0:
                l_ = tuple(from_continuous_range(self._by_date, self.database_location))
            else:
                l_ = tuple(from_intervals(self._by_date, self.database_location))
            filtered = filtered.intersection(l_)

        if self._by_child:
            filtered = filtered.intersection(get_all_parents(self.database_location))

        if self._by_parent:
            filtered = filtered.intersection(get_all_children(self.database_location))

        filtered = list(filtered)
        filtered.sort(key=lambda i: get_date(entry_id=i, database=self.database_location))
        self._filtered = tuple(filtered)

    def reset_filters(self):
        self._by_attachments = False
        self._by_child = False
        self._by_parent = False
        self._by_body = ''
        self._by_date = ()
        self._date_type = 0
        self._by_tags = tuple()
        self._by_is_untagged = False
        self._tags_type = 0
        self._filtered = tuple()

    def refresh_ids(self):
        self._filter()


def _test_filter():
    f = Filter()
    print(f.filtered_ids)
    # f.has_child = True
    print(f.filtered_ids)


if __name__ == '__main__':
    _test_filter()
