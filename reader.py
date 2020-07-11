"""Classes and functions for reading entries and other information from the database"""
from contextlib import closing
from datetime import datetime
from os import makedirs
from os.path import exists, join, basename
from sqlite3 import connect, Connection
from typing import Union

from dateutil.parser import parse

from database import get_all_tags, get_all_entry_ids
from err import ErrorManager


# TODO Rewrite temp file functions to write all information for each Reader and Writer class instance (support tabs)


def read_temp_file():
    p = join('.tempfiles', 'reader')
    if not exists(p):
        makedirs(p)
    f = join(p, 'entry_id')
    entry_id = -1
    if exists(f):
        with open(f, 'r') as s:
            entry_id = int(s.read())
            s.close()
    return entry_id


def write_temp_file(entry_id: int = None):
    p = join('.tempfiles', 'reader')
    if not exists(p):
        makedirs(p)
    f = join(p, 'entry_id')
    with open(f, 'w') as s:
        s.write(str(entry_id))
        s.close()


class Reader:
    def __init__(self, path_to_db: str, error_mngr: ErrorManager):
        self.__database_path = path_to_db
        self.__database = connect(path_to_db)
        self.__current_entry = read_temp_file()
        self.__error_manager = error_mngr
        self.__attachments_flag = False
        self.__parent_flag = False
        self.__children_flag = False

    @property
    def database(self):
        return basename(self.__database_path)

    @property
    def current_entry(self):
        return self.__current_entry

    @current_entry.setter
    def current_entry(self, entry_id: Union[int, None]):
        self.__current_entry = entry_id
        if type(entry_id) == int:
            if entry_id in get_all_entry_ids():
                self.has_parent = True if get_parent(database=self.__database, child_id=self.__current_entry) else False
                self.has_children = True if get_children(database=self.__database,
                                                         parent_id=self.__current_entry) else False
                self.has_attachments = True if get_attachment_ids(database=self.__database,
                                                                  entry_id=self.__current_entry) else False
                write_temp_file(entry_id)
            else:
                self.__error_manager.message = 'Entry id is not in database'
        elif entry_id is None:
            self.has_parent = False
            self.has_children = False
            self.has_attachments = False
        else:
            raise TypeError('Value is not an int or None')

    @property
    def body(self):
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            body = get_body(database=self.__database, entry_id=self.__current_entry)
            return body

    @property
    def tags(self):
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            tags = get_tags(database=self.__database, entry_id=self.__current_entry)
            return tags

    @property
    def all_tags(self):
        tags = get_all_tags(database=self.__database)
        return tags

    @property
    def date(self):
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            date = get_date(database=self.__database, entry_id=self.__current_entry)
            return date

    @property
    def attachments(self):
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            attachments = {att_id: get_attachment_name(att_id=att_id) for att_id in
                           get_attachment_ids(database=self.__database, entry_id=self.__current_entry)}
            return attachments

    @property
    def parent(self):
        """Passes the parent for the currently selected entry

        :return: an int representing the parent or None if there is no parent
        """
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            parent = get_parent(database=self.__database, child_id=self.__current_entry)
            return parent

    @property
    def children(self):
        """Passes the children for the currently selected entry

        :return: a list of ints representing the children of the entry
        """
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            children = get_children(database=self.__database, parent_id=self.__current_entry)
            return children

    @property
    def has_children(self):
        return self.__children_flag

    @has_children.setter
    def has_children(self, v: bool):
        self.__children_flag = v

    @property
    def has_attachments(self):
        return self.__attachments_flag

    @has_attachments.setter
    def has_attachments(self, v: bool):
        self.__attachments_flag = v

    @property
    def has_parent(self):
        return self.__children_flag

    @has_parent.setter
    def has_parent(self, v: bool):
        self.__parent_flag = v


# TODO add exception catching to functions which need it


"""---------------------------------Date Methods----------------------------------"""


def get_date(entry_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the date for a given entry

    :rtype: datetime
    :param entry_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being queried
    :return: the date for the given entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT year,month,day,hour,minute FROM dates WHERE entry_id=?', (entry_id,))
        temp = c.fetchone()
        date = datetime(temp[0], temp[1], temp[2], temp[3], temp[4])
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return date


"""---------------------------------Body Methods----------------------------------"""


def get_body(entry_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the entry content for a given entry

    :rtype: str
    :param entry_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being queried
    :return: the body of the given entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT body FROM bodies WHERE entry_id=?', (entry_id,))
        body = c.fetchone()[0]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return body


"""---------------------------------Tags Methods----------------------------------"""


def get_tags(entry_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets either all tags in the entire database or the tags for a specific entry

    :param entry_id: int representing the id of a given entry
    :param database: a Connection or str representing the database that is being queried
    :return: a list of str representing the tags for all entries or a specific entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT tag FROM tags WHERE entry_id=?', (entry_id,))
        tags = [tag[0] for tag in c]
        tags.sort()
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return tags


"""---------------------------------Attachments Methods----------------------------------"""


def get_attachment_ids(entry_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets all attachment ids associated with a given entry

    :param entry_id: the id of the entry for which all attachment ids are desired
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing the ids of the attachments associated with the given entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT att_id FROM attachments WHERE entry_id=?', (entry_id,))
        ids = [x[0] for x in c.fetchall()]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_attachment_file(att_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the file associated with a given attachment

    :param att_id: an int representing the id of a given attachment
    :param database: a Connection or str representing the database that is being queried
    :return: a bytestream representing the attachment file
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT file FROM attachments WHERE att_id=?', (att_id,))
        attachment = c.fetchone()[0]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return attachment


def get_attachment_name(att_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the name associated with a given attachment

    :param att_id: an int representing the id of a given attachment
    :param database: a Connection or str representing the database that is being queried
    :return: a str representing the filename for the attachment
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT filename FROM attachments WHERE att_id=?', (att_id,))
        name = c.fetchone()[0]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return name


def get_attachment_date(att_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the date associated with a given attachment

    :param att_id: an int representing the id of a given attachment
    :param database: a Connection or str representing the database that is being queried
    :return: a datetime representing the date that the attachment was added to the database
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT added FROM attachments WHERE att_id=?', (att_id,))
        name = c.fetchone()[0]
        name = parse(name)
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return name


"""---------------------------------Relations Methods----------------------------------"""


def get_children(parent_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the ids of all entries that were generated by the given entry

    :rtype: list
    :param parent_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing the child entries of the given entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT child FROM relations WHERE parent=?', (parent_id,))
        children = [x[0] for x in c.fetchall()]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return children


def get_parent(child_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the id of the entry that generated by the given entry

    :rtype: int
    :param child_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being queried
    :return: an int representing the parent of the given entry or None if there is no parent
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT parent FROM relations WHERE child=?', (child_id,))
        try:
            parent = c.fetchone()[0]
        except TypeError:  # will return None if there is no parent (Nonetype not subscriptable)
            parent = None
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return parent


"""---------------------------------Entry Methods----------------------------------"""

# TODO Consider removing this function (no permanent cursor, I think)


def get_entry_id_of_most_recent_entry(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the id of the most recently edited entry

    :rtype: int
    :param database: a Connection or str representing the database that is being queried
    :return: an int representing a specific entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM bodies WHERE rowid=(SELECT MAX(rowid) FROM bodies)')
        entry_id = c.fetchone()[0]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return entry_id


def get_entry_ids_from_year_range(database: Union[Connection, str] = 'jurnl.sqlite',
                                  year: tuple = (1970, datetime.now().year)):
    """Filters the database for entries that were created over a given range of years

    :rtype: list
    :param year: a tuple containing the endpoints of the range
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE year BETWEEN ? AND ?', (year[0], year[1]))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_month_range(database: Union[Connection, str] = 'jurnl.sqlite', month: tuple = (1, 12)):
    """Filters the database for entries that were created over a given range of months

    :rtype: list
    :param month: a tuple containing the endpoints of the range
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE month BETWEEN ? AND ?', (month[0], month[1]))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_day_range(database: Union[Connection, str] = 'jurnl.sqlite', day: tuple = (1, 31)):
    """Filters the database for entries that were created over a given range of days

    :rtype: list
    :param day: a tuple containing the endpoints of the range
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE day BETWEEN ? AND ?', (day[0], day[1]))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_hour_range(database: Union[Connection, str] = 'jurnl.sqlite', hour: tuple = (0, 23)):
    """Filters the database for entries that were created over a given range of hours

    :rtype: list
    :param hour: a tuple containing the endpoints of the range
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE hour BETWEEN ? AND ?', (hour[0], hour[1]))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_minute_range(database: Union[Connection, str] = 'jurnl.sqlite', minute: tuple = (0, 59)):
    """Filters the database for entries that were created over a given range of minutes

    :rtype: list
    :param minute: a tuple containing the endpoints of the range
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE minute BETWEEN ? AND ?', (minute[0], minute[1]))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_weekday_range(database: Union[Connection, str] = 'jurnl.sqlite', weekday: tuple = (0, 6)):
    """Filters the database for entries that were created over a given range of weekdays

    :rtype: list
    :param weekday: a tuple containing the endpoints of the range
    :param database: a Connection or str representing the database that is being queried
    :return: a list containing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE weekday BETWEEN ? AND ?', (weekday[0], weekday[1]))
        ids = [x[0] for x in c.fetchall()]
        ids.sort(key=get_date)
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_range(lower: datetime, upper: datetime, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Filters the database for entries that were created over a given range of time

    :param database: a Connection or str representing the database that is being queried
    :param lower: a datetime representing the lower limit of the dates to filter for
    :param upper:  a datetime representing the upper limit of the dates to filter for
    :return: a list of ints representing the filtered entries
    :rtype: list
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM dates WHERE string BETWEEN ? AND ?',
                  (lower.strftime('%Y-%m-%d %H:%M'), upper.strftime('%Y-%m-%d %H:%M')))
        ids = [x[0] for x in c]
        ids.sort(key=get_date)
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_tags(tags: tuple, database: Union[Connection, str] = 'jurnl.sqlite',
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
            for entry in get_all_entry_ids():
                if len(get_tags(entry)) == len(tags):
                    if set(get_tags(entry)).intersection(tags) == set(tags):
                        ids.append(entry)
        if op_type == 'Contains One Of...':
            sql = 'SELECT entry_id FROM tags WHERE tag IN ({})'.format(','.join(['?'] * len(tags)))
            ids = list({x[0] for x in c.execute(sql, tags).fetchall()})
        if op_type == 'Untagged':
            cmd = 'SELECT entry_id FROM tags WHERE tag=\'UNTAGGED\''
            ids = [x[0] for x in c.execute(cmd).fetchall()]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_attachments(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the ids of entries that have attachments

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        ids = [x[0] for x in c.execute('SELECT entry_id FROM attachments').fetchall()]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids


def get_entry_ids_from_body(search_string: str, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the ids of entries that contain a given search string

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :param search_string: a str which is used to sort the ids
    :return: a list of ints representing the filtered entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT entry_id FROM bodies WHERE body LIKE ?', ('%' + search_string + '%',))
        ids = [x[0] for x in c.fetchall()]
    if type(database) == str:  # database is not being managed by caller
        d.close()
    return ids
