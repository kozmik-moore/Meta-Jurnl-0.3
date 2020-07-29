"""Contains the classes and functions that support a a reader which can also filter entries"""
from contextlib import closing
from datetime import datetime
from os import makedirs
from os.path import exists
from sqlite3 import Connection, connect, DatabaseError
from typing import Union, Tuple

from database import get_all_entry_ids, create_database
from reader import Reader


def get_entry_ids_from_year_range(database: Union[Connection, str],
                                  lower: int = 1970, upper: int = datetime.now().year):
    """Filters the database for entries that were created over a given range of years

    :param upper:
    :param lower:
    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE year BETWEEN ? AND ?', (lower, upper))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    return ids


def get_entry_ids_from_month_range(database: Union[Connection, str], lower: int = 1, upper: int = 12):
    """Filters the database for entries that were created over a given range of months

    :param upper:
    :param lower:
    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE month BETWEEN ? AND ?', (lower, upper))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    return ids


def get_entry_ids_from_day_range(database: Union[Connection, str], lower: int = 1, upper: int = 31):
    """Filters the database for entries that were created over a given range of days

    :param upper:
    :param lower:
    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE day BETWEEN ? AND ?', (lower, upper))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    return ids


def get_entry_ids_from_hour_range(database: Union[Connection, str], lower: int = 0, upper: int = 23):
    """Filters the database for entries that were created over a given range of hours

    :param upper:
    :param lower:
    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE hour BETWEEN ? AND ?', (lower, upper))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    return ids


def get_entry_ids_from_minute_range(database: Union[Connection, str], lower: int = 0, upper: int = 59):
    """Filters the database for entries that were created over a given range of minutes

    :param upper:
    :param lower:
    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE minute BETWEEN ? AND ?', (lower, upper))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    return ids


def get_entry_ids_from_weekday_range(database: Union[Connection, str], lower: int = 0, upper: int = 6):
    """Filters the database for entries that were created over a given range of weekdays

    :param upper:
    :param lower:
    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE weekday BETWEEN ? AND ?', (lower, upper))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    return ids


def get_entry_ids_from_range(lower: Tuple[int], upper: Tuple[int], database: Union[Connection, str]):
    """Filters the database for entries that were created over a given range of time

    :param database: a Connection or str representing the database that is being queried
    :param lower: a datetime representing the lower limit of the dates to filter for
    :param upper:  a datetime representing the upper limit of the dates to filter for
    :return: a list of ints representing the filtered entries
    :rtype: list
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        l_str = '{}-{:02}-{:02} {:02}:{:02}'.format(lower[0], lower[1], lower[2], lower[3], lower[4])
        u_str = '{}-{:02}-{:02} {:02}:{:02}'.format(upper[0], upper[1], upper[2], upper[3], upper[4])
        c.execute('SELECT entry_id FROM dates WHERE string BETWEEN ? AND ?',
                  (l_str, u_str))
        ids = [x[0] for x in c.fetchall()]
    return ids


def get_entry_ids_from_intervals(lower: Tuple[int], upper: Tuple[int],
                                 database: Union[Connection, str]):
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute("SELECT entry_id FROM dates WHERE (year BETWEEN ? AND ?) AND (month BETWEEN ? AND ?) AND (day "
                  "BETWEEN ? AND ?) AND (hour BETWEEN ? AND ?) AND (minute BETWEEN ? AND ?) AND (weekday BETWEEN ? AND "
                  "?)", (lower[0], upper[0], lower[1], upper[1], lower[2], upper[2], lower[3], upper[3],
                         lower[4], upper[4], lower[5], upper[5]))
        ids = [x[0] for x in c.fetchall()]
        return ids


def get_entry_ids_from_tags(tags: tuple, database: Union[Connection, str],
                            op_type: str = 'Contains One Of...'):
    """

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :param tags: a tuple of strings representing the tags to be used for filtering entries from the database
    :param op_type: a str representing the type of filter to apply
    :return: a list of ints representing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        ids = []
        if op_type == 'Contains At Least...':
            tags = list(tags)
            tag = tags.pop(0)
            sql = 'SELECT entry_id FROM tags WHERE tag=?'
            temp = set(c.execute(sql, (tag,)).fetchall())
            for tag in tags:
                temp = temp.intersection(c.execute(sql, (tag,)).fetchall())
            ids = [i[0] for i in temp]
        if op_type == 'Contains Only...':
            for entry in get_all_entry_ids(d):
                if len(get_tags(entry, d)) == len(tags):
                    if set(get_tags(entry, d)).intersection(tags) == set(tags):
                        ids.append(entry)
        if op_type == 'Contains One Of...':
            sql = 'SELECT entry_id FROM tags WHERE tag IN ({})'.format(','.join(['?'] * len(tags)))
            ids = list({x[0] for x in c.execute(sql, tags).fetchall()})
        if op_type == 'Untagged':
            cmd = 'SELECT entry_id FROM tags WHERE tag=\'(UNTAGGED)\''
            ids = [x[0] for x in c.execute(cmd).fetchall()]
    return tuple(ids)


def get_entry_ids_from_untagged(database: Union[Connection, str]):
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        ids = (x[0] for x in c.execute('SELECT entry_id FROM tags WHERE tag=(UNTAGGED)').fetchall())
        return ids


def get_entry_ids_from_attachments(database: Union[Connection, str]):
    """Gets the ids of entries that have attachments

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        ids = [x[0] for x in c.execute('SELECT entry_id FROM attachments').fetchall()]
        return ids


def get_entry_ids_from_body(search_string: str, database: Union[Connection, str]):
    """Gets the ids of entries that contain a given search string

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :param search_string: a str which is used to sort the ids
    :return: a list of ints representing the filtered entries
    """
    # TODO allow regex for more useful searches
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM bodies WHERE body LIKE ?', ('%' + search_string.lower() + '%',))
        ids = [x[0] for x in c.fetchall()]
        return ids


class Filter:
    """Provides methods for filtering-in entries based on their attributes"""
    def __init__(self, path_to_db: str = 'jurnl.sqlite'):
        self._database_path = path_to_db
        self._database = connect(self._database_path)
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
        return self._database_path

    @property
    def connection(self):
        return self._database

    @connection.setter
    # TODO create function to handle this for all relevant classes
    def connection(self, path: Union[str, None]):
        if path is not None:
            if exists(path):
                try:
                    self._database.close()
                    self._database = connect(path)
                    self._database_path = path
                except DatabaseError as err:
                    raise err
            else:
                makedirs(path)
                create_database(path)
        else:
            self._database.close()
            self._database = None

    @property
    def filtered_ids(self):
        return self._filtered

    @property
    def attachments(self):
        return self._by_attachments

    @attachments.setter
    def attachments(self, v: bool):
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
    def date(self):
        return self._by_date

    @date.setter
    def date(self, t: Tuple[Tuple[int]]):
        if all([type(t) == tuple, (isinstance(x, tuple) for x in t), len(t) in [0, 2], (len(x) == 6 for x in t)]):
            if not t:
                self._by_date = ()
            else:
                f = t[0]
                s = t[1]
                if not f:
                    d: datetime = get_oldest_date(self._database)
                    f = (d.year, d.month, d.day, d.hour, d.minute, d.weekday())
                if not s:
                    d: datetime = get_newest_date(self._database)
                    s = (d.year, d.month, d.day, d.hour, d.minute, d.weekday())
                self._by_date = (f, s)
            self._filter()

    @property
    def date_filter(self):
        return self.date_filter()

    @date_filter.setter
    def date_filter(self, v: str):
        if v in ['Continuous', 'Intervals']:
            self._date_type = v
            if self.date:
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
                self._by_tags = tuple(get_all_tags(self._database))
                self._by_is_untagged = True
                self._filter()
            elif v == 'none':
                self._by_tags = ()
                self._by_is_untagged = False
                self._filter()
            elif v == 'invert':
                a = set(get_all_tags(self._database))
                self._by_tags = tuple(a.difference(self._by_tags))
                self._by_is_untagged = False if True else True
                self._filter()

    @property
    def untagged(self):
        return self._by_is_untagged

    @untagged.setter
    def untagged(self, v: bool):
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
        filtered = set(get_all_entry_ids(self._database))
        if self._by_attachments:
            filtered = filtered.intersection(get_entry_ids_from_attachments(self._database))
        if self._by_body:
            filtered = filtered.intersection(get_entry_ids_from_body(self._by_body, self._database))
        if any([self._by_tags, self._by_is_untagged]):
            l_ = ()
            if self._by_tags and self._by_is_untagged:
                l_ = tuple(list(self._by_tags) + ['(UNTAGGED)'])
            elif not self._by_tags and self._by_is_untagged:
                l_ = ('(UNTAGGED)',)
            elif self._by_tags and not self._by_is_untagged:
                l_ = self._by_tags
            filtered = filtered.intersection(get_entry_ids_from_tags(l_, self._database, self._tags_type))
        if self._by_date:
            l_ = set()
            f = self._by_date[0]
            s = self._by_date[1]
            if self._date_type == 'Continuous':
                l_ = tuple(get_entry_ids_from_range(f, s, self._database))
            elif self._date_type == 'Intervals':
                l_ = get_entry_ids_from_intervals(f, s, self._database)
            filtered = filtered.intersection(l_)
        if self._by_is_child:
            filtered = filtered.intersection(get_all_children(self._database))
        if self._by_is_parent:
            filtered = filtered.intersection(get_all_parents(self._database))
        filtered = list(filtered)
        filtered.sort(key=lambda i: get_date(entry_id=i, database=self._database))
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

    def refresh(self):
        self._filter()

    def close(self):
        self._database.close()
        self._database = None



class FilteredReader(Reader):
    def __init__(self, path_to_database: str = 'jurnl.sqlite'):
        super(FilteredReader, self).__init__(path_to_database)
