"""Classes and functions for reading entries and other information from the database"""
from contextlib import closing
from datetime import datetime
from os.path import exists
from sqlite3 import connect, Connection, DatabaseError
from typing import Union, List, Tuple

from dateutil.parser import parse

from database import get_all_entry_ids


class Reader:
    def __init__(self, path_to_db: str = 'jurnl.sqlite'):
        self.__database_path = path_to_db
        self.__database = connect(path_to_db)
        self.__current_entry = None
        self.__attachments_flag = False
        self.__parent_flag = False
        self.__children_flag = False

    @property
    def database_location(self):
        return self.__database_path

    @property
    def database_connection(self):
        return self.__database

    @database_connection.setter
    def database_connection(self, d: Union[str, None]):
        if d is not None and exists(d):
            try:
                self.__database = connect(d)
            except DatabaseError as err:
                raise err
        else:
            self.__database = None

    @property
    def current_entry(self):
        return self.__current_entry

    @current_entry.setter
    def current_entry(self, entry_id: Union[int, None]):
        """Sets the entry id field and modifies the has_parent, has_children, and has_attachments flags accordingly

        :param entry_id: an int representing an entry from the database or None if the entry is not set
        """
        # TODO check for database or create if none exists prior to assigning entry_id
        if self.database_connection:
            self.__current_entry = entry_id if entry_id in get_all_entry_ids(self.database_connection) else None
            if type(entry_id) == int and entry_id > 0:
                if entry_id in get_all_entry_ids():
                    self.has_parent = True if get_parent(
                        database=self.database_connection, child_id=self.__current_entry) else False
                    self.has_children = True if get_children(database=self.database_connection,
                                                             parent_id=self.__current_entry) else False
                    self.has_attachments = True if get_attachment_ids(database=self.database_connection,
                                                                      entry_id=self.__current_entry) else False
            elif entry_id is None:
                self.has_parent = None
                self.has_children = None
                self.has_attachments = None

    @property
    def body(self):
        """Checks whether the entry id field is set and retrieves the content of the entry, if it is

        :return: a str representing the content of the entry or None if the entry is not set
        """
        body = None
        if self.current_entry:
            body = get_body(database=self.database_connection, entry_id=self.current_entry)
        return body

    @property
    def tags(self) -> Tuple[str]:
        """Checks whether the entry id field is set and retrieves the tags of the entry, if it is

        :return: a tuple of str representing the tags of the entry or None if the entry is not set
        """
        tags = None
        if self.current_entry:
            tags = get_tags(database=self.database_connection, entry_id=self.current_entry)
        return tags

    @property
    def date(self):
        """Checks whether the entry id field is set. If it is, retrieves the date of the entry

        :return: a datetime representing the date the entry was created or None if the entry is not set
        """
        date = None
        if self.current_entry:
            date = get_date(database=self.database_connection, entry_id=self.current_entry)
        return date

    @property
    def date_last_edited(self):
        date = None
        if self.current_entry:
            date = date_last_edited(self.current_entry, self.database_connection)
        return date

    @property
    def attachments(self) -> Tuple[int]:
        """Checks whether the entry id field is set. If it is, retrieves the attachment ids associated with the entry

        :return: a tuple of int representing the attachments of the entry or None if the entry is not set
        """
        attachments = None
        if self.current_entry:
            attachments = [att_id for att_id in
                           get_attachment_ids(database=self.database_connection, entry_id=self.current_entry)]
            attachments.sort(key=get_attachment_date)
            attachments = tuple(attachments)
        return attachments

    @property
    def parent(self):
        """Passes the parent for the currently selected entry

        :return: an int representing the parent or None if there is no parent or the entry is not set
        """
        parent = None
        if self.current_entry:
            parent = get_parent(database=self.database_connection, child_id=self.current_entry)
        return parent

    @property
    def children(self):
        """Passes the children for the currently selected entry

        :return: a list of ints representing the children of the entry
        """
        children = None
        if self.current_entry:
            children = tuple(get_children(database=self.database_connection, parent_id=self.current_entry))
        return children

    @property
    def has_children(self) -> Union[bool, None]:
        """Returns the state of the flag indicating whether the entry has children

        :return: a bool indicating whether an entry has children or None indicating that the entry id field is not set
        """
        return self.__children_flag

    @has_children.setter
    def has_children(self, v: Union[bool, None]):
        """Sets the has_children flag

        :param v: a bool or None, indicating whether an entry has children or None indicating that the entry is not set
        """
        if type(v) == bool:
            self.__children_flag = v

    @property
    def has_attachments(self) -> Union[bool, None]:
        """Returns the state of the flag indicating whether the entry has attachments

        :return: a bool indicating whether an entry has attachments or None indicating that the entry is not set
        """
        return self.__attachments_flag

    @has_attachments.setter
    def has_attachments(self, v: Union[bool, None]):
        """Sets the has_attachments flag

        :param v: a bool indicating whether an entry has attachments or None indicating that the entry is not set
        """
        if type(v) == bool:
            self.__attachments_flag = v

    @property
    def has_parent(self) -> Union[bool, None]:
        """Returns the state of the flag indicating whether the entry has a parent

        :return: a bool indicating whether an entry has a parent or None indicating that the entry id field is not set
        """
        return self.__children_flag

    @has_parent.setter
    def has_parent(self, v: Union[bool, None]):
        """Sets the has_parent flag

        :param v: a bool, indicating whether an entry has a parent or None indicating that the entry id field is not set
        """
        if type(v) == bool:
            self.__parent_flag = v

    def close_database(self):
        self.database_connection.close()
        self.database_connection = None


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
    return date


def date_last_edited(entry_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT last_edit FROM dates WHERE entry_id=?', (entry_id,))
        date = parse(c.fetchone()[0])
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
    return body


"""---------------------------------Tags Methods----------------------------------"""


def get_tags(entry_id: int, database: Union[Connection, str] = 'jurnl.sqlite') -> Tuple[str]:
    """Gets either all tags in the entire database or the tags for a specific entry

    :param entry_id: int representing the id of a given entry
    :param database: a Connection or str representing the database that is being queried
    :return: a list of str representing the tags for all entries or a specific entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT tag FROM tags WHERE entry_id=?', (entry_id,))
        tags = [str(tag[0]) for tag in c]
        tags.sort()
        tags = tuple(tags)
    return tags


"""---------------------------------Attachments Methods----------------------------------"""


def get_attachment_ids(entry_id: int, database: Union[Connection, str] = 'jurnl.sqlite') -> List[int]:
    """Gets all attachment ids associated with a given entry

    :param entry_id: the id of the entry for which all attachment ids are desired
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing the ids of the attachments associated with the given entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT att_id FROM attachments WHERE entry_id=?', (entry_id,))
        ids = [x[0] for x in c.fetchall()]
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
    return parent


"""---------------------------------Entry Methods----------------------------------"""


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
    return ids
