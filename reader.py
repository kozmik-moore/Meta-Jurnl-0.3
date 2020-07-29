"""Classes and functions for reading entries and other information from the database"""
from contextlib import closing
from datetime import datetime
from os import makedirs
from os.path import exists
from sqlite3 import connect, Connection, DatabaseError
from typing import Union, Tuple

from database import get_all_entry_ids, create_database


class Reader:
    """Stores the id of the currently selected entry and reports its attributes from the database"""

    def __init__(self, path_to_db: str = 'jurnl.sqlite'):
        if not exists(path_to_db):
            create_database(path_to_db)
        self._database_path = path_to_db
        self._database = connect(path_to_db)
        self._id_ = None

    @property
    def database_location(self):
        return self._database_path

    @property
    def connection(self):
        return self._database

    @connection.setter
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
    def id_(self):
        return self._id_

    @id_.setter
    def id_(self, entry_id: Union[int, None]):
        """Sets the entry id field and modifies the has_parent, has_children, and has_attachments flags accordingly

        :param entry_id: an int representing an entry from the database or None if the entry is not set
        """
        if self.connection:
            self._id_ = entry_id if entry_id in get_all_entry_ids(self.connection) else None

    @property
    def body(self):
        """Checks whether the entry id field is set and retrieves the content of the entry, if it is

        :return: a str representing the content of the entry or None if the entry is not set
        """
        body = ''
        if self._id_:
            body = get_body(database=self.connection, entry_id=self._id_)
        return body

    @property
    def tags(self) -> Tuple[str]:
        """Checks whether the entry id field is set and retrieves the tags of the entry, if it is

        :return: a tuple of str representing the tags of the entry or None if the entry is not set
        """
        tags = ()
        if self._id_:
            tags = get_tags(database=self.connection, entry_id=self._id_)
        return tags

    @property
    def date(self):
        """Checks whether the entry id field is set. If it is, retrieves the date of the entry

        :return: a datetime representing the date the entry was created or None if the entry is not set
        """
        date = None
        if self._id_:
            date = get_date(database=self.connection, entry_id=self._id_)
        return date

    @property
    def date_last_edited(self):
        date = None
        if self._id_:
            date = get_date_last_edited(self._id_, self.connection)
        return date

    @property
    def attachments(self) -> Tuple[int]:
        """Checks whether the entry id field is set. If it is, retrieves the attachment ids associated with the entry

        :return: a tuple of int representing the attachments of the entry or None if the entry is not set
        """
        attachments = ()
        if self._id_:
            attachments = get_attachment_ids(database=self.connection, entry_id=self._id_)
        return attachments

    @property
    def parent(self):
        """Passes the parent for the currently selected entry

        :return: an int representing the parent or None if there is no parent or the entry is not set
        """
        parent = None
        if self._id_:
            parent = get_parent(database=self.connection, child_id=self._id_)
        return parent

    @property
    def children(self):
        """Passes the children for the currently selected entry

        :return: a list of ints representing the children of the entry
        """
        children = None
        if self._id_:
            children = tuple(get_children(database=self.connection, parent_id=self._id_))
        return children

    @property
    def has_children(self) -> Union[bool, None]:
        """Checks whether the entry id is set. If it is, checks if it has children and returns a bool

        :return: a bool indicating whether an entry has children or None indicating that the entry id field is not set
        """
        h = None
        if self._id_:
            h = True if get_children(self._id_, self.connection) else False
        return h

    @property
    def has_attachments(self) -> Union[bool, None]:
        """Checks whether the entry id is set. If it is, checks if it has attachments and returns a bool

        :return: a bool indicating whether an entry has attachments or None indicating that the entry is not set
        """
        h = None
        if self._id_:
            h = True if get_attachment_ids(self._id_, self.connection) else False
        return h

    @property
    def has_parent(self) -> Union[bool, None]:
        """Returns the state of the flag indicating whether the entry has a parent

        :return: a bool indicating whether an entry has a parent or None indicating that the entry id field is not set
        """
        h = None
        if self._id_:
            h = True if get_parent(self._id_, self.connection) else False
        return h

    def close_database(self):
        self.connection = None


# TODO add exception catching to functions which need it


"""---------------------------------Date Methods----------------------------------"""


def get_date(entry_id: int, database: Union[Connection, str]):
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


def get_date_last_edited(entry_id: int, database: Union[Connection, str]):
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT last_edit FROM dates WHERE entry_id=?', (entry_id,))
        date = datetime.strptime(c.fetchone()[0], '%Y-%m-%d %H:%M')
    return date


"""---------------------------------Body Methods----------------------------------"""


def get_body(entry_id: int, database: Union[Connection, str]):
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


def get_tags(entry_id: int, database: Union[Connection, str]) -> Tuple[str]:
    """Gets either all tags in the entire database or the tags for a specific entry

    :param entry_id: int representing the id of a given entry
    :param database: a Connection or str representing the database that is being queried
    :return: a list of str representing the tags for all entries or a specific entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT tag FROM tags WHERE entry_id=? ORDER BY tag', (entry_id,))
        tags = tuple([str(tag[0]) for tag in c])
    return tags


"""---------------------------------Attachments Methods----------------------------------"""


def get_attachment_ids(entry_id: int, database: Union[Connection, str]) -> Tuple[int]:
    """Gets all attachment ids associated with a given entry

    :param entry_id: the id of the entry for which all attachment ids are desired
    :param database: a Connection or str representing the database that is being queried
    :return: a tuple of ints representing the ids of the attachments associated with the given entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT att_id FROM attachments WHERE entry_id=? ORDER BY added', (entry_id,))
        ids = tuple([int(x[0]) for x in c.fetchall()])
    return ids


def get_attachment_file(att_id: int, database: Union[Connection, str]):
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


def get_attachment_name(att_id: int, database: Union[Connection, str]):
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


def get_attachment_date(att_id: int, database: Union[Connection, str]):
    """Gets the date associated with a given attachment

    :param att_id: an int representing the id of a given attachment
    :param database: a Connection or str representing the database that is being queried
    :return: a datetime representing the date that the attachment was added to the database
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('SELECT added FROM attachments WHERE att_id=?', (att_id,))
        date = c.fetchone()[0]
        date = datetime.strptime(date, '%Y-%m-%d %H:%M')
    return date


"""---------------------------------Relations Methods----------------------------------"""


def get_children(parent_id: int, database: Union[Connection, str]):
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


def get_parent(child_id: int, database: Union[Connection, str]):
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
