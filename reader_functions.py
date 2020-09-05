"""Classes and functions for reading entries and other information from the database"""
from contextlib import closing
from datetime import datetime
from sqlite3 import connect, PARSE_DECLTYPES, PARSE_COLNAMES
from typing import Union, Tuple

from configurations import default_database
from database_info import get_all_entry_ids


class Reader:
    """Stores the id of the currently selected entry and reports its attributes from the database"""

    _id = None

    def __init__(self, path_to_db: str = None):
        self._path = path_to_db if path_to_db else default_database()

    @property
    def database_location(self):
        return self._path

    @database_location.setter
    def database_location(self, v: str):
        self.id_ = None
        self._path = v

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, entry_id: Union[int, None]):
        """Sets the entry id field and modifies the has_parent, has_children, and has_attachments flags accordingly

        :param entry_id: an int representing an entry from the database or None if the entry is not set
        """
        self._id = entry_id if entry_id in get_all_entry_ids(self.database_location) else None

    @property
    def body(self):
        """Checks whether the entry id field is set and retrieves the content of the entry, if it is

        :return: a str representing the content of the entry or None if the entry is not set
        """
        body = ''
        if self._id:
            body = get_body(database=self.database_location, entry_id=self._id)
        return body

    @property
    def tags(self) -> Tuple[str]:
        """Checks whether the entry id field is set and retrieves the tags of the entry, if it is

        :return: a tuple of str representing the tags of the entry or None if the entry is not set
        """
        tags = ()
        if self._id:
            tags = get_tags(database=self.database_location, entry_id=self._id)
        return tags

    @property
    def date(self):
        """Checks whether the entry id field is set. If it is, retrieves the date of the entry

        :return: a datetime representing the date the entry was created or None if the entry is not set
        """
        date = None
        if self._id:
            date = get_date(database=self.database_location, entry_id=self._id)
        return date

    @property
    def date_last_edited(self):
        date = None
        if self._id:
            date = get_date_last_edited(self._id, self.database_location)
        return date

    @property
    def attachments(self) -> Tuple[int]:
        """Checks whether the entry id field is set. If it is, retrieves the attachment ids associated with the entry

        :return: a tuple of int representing the attachments of the entry or None if the entry is not set
        """
        attachments = ()
        if self._id:
            attachments = get_attachment_ids(database=self.database_location, entry_id=self._id)
        return attachments

    @property
    def parent(self):
        """Passes the parent for the currently selected entry

        :return: an int representing the parent or None if there is no parent or the entry is not set
        """
        parent = None
        if self._id:
            parent = get_parent(database=self.database_location, child_id=self._id)
        return parent

    @property
    def children(self):
        """Passes the children for the currently selected entry

        :return: a list of ints representing the children of the entry
        """
        children = None
        if self._id:
            return tuple(get_children(database=self.database_location, parent_id=self._id))
        return children

    @property
    def has_children(self) -> Union[bool, None]:
        """Checks whether the entry id is set. If it is, checks if it has children and returns a bool

        :return: a bool indicating whether an entry has children or None indicating that the entry id field is not set
        """
        h = None
        if self._id:
            h = True if get_children(self._id, self.database_location) else False
        return h

    @property
    def has_attachments(self) -> Union[bool, None]:
        """Checks whether the entry id is set. If it is, checks if it has attachments and returns a bool

        :return: a bool indicating whether an entry has attachments or None indicating that the entry is not set
        """
        h = None
        if self._id:
            h = True if get_attachment_ids(self._id, self.database_location) else False
        return h

    @property
    def has_parent(self) -> Union[bool, None]:
        """Returns the state of the flag indicating whether the entry has a parent

        :return: a bool indicating whether an entry has a parent or None indicating that the entry id field is not set
        """
        h = None
        if self._id:
            h = True if get_parent(self._id, self.database_location) else False
        return h


# TODO add exception catching to functions which need it


"""---------------------------------Date Methods----------------------------------"""


def get_date(entry_id: int, database: str = None):
    """

    :rtype: datetime
    """
    types = PARSE_DECLTYPES | PARSE_COLNAMES
    db = connect(database, detect_types=types) if database else connect(default_database(), detect_types=types)
    with closing(db) as d:
        return d.execute('SELECT created FROM dates WHERE entry_id=?', (entry_id,)).fetchone()[0]


def get_date_last_edited(entry_id: int, database: str = None):
    types = PARSE_DECLTYPES | PARSE_COLNAMES
    db = connect(database, detect_types=types) if database else connect(default_database(), detect_types=types)
    with closing(db) as d:
        return d.execute('SELECT last_edit FROM dates WHERE entry_id=?', (entry_id,)).fetchone()[0]


"""---------------------------------Body Methods----------------------------------"""


def get_body(entry_id: int, database: str = None):
    """Gets the entry content for a given entry

    :rtype: str
    :param entry_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being queried
    :return: the body of the given entry
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        return d.execute('SELECT body FROM bodies WHERE entry_id=?', (entry_id,)).fetchone()[0]


"""---------------------------------Tags Methods----------------------------------"""


def get_tags(entry_id: int, database: str = None):
    """Gets either all tags in the entire database or the tags for a specific entry

    :param entry_id: int representing the id of a given entry
    :param database: a Connection or str representing the database that is being queried
    :return: a list of str representing the tags for all entries or a specific entry
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        c = d.execute('SELECT tag FROM tags WHERE entry_id=? ORDER BY tag', (entry_id,)).fetchall()
        return tuple([str(tag[0]) for tag in c])


"""---------------------------------Attachments Methods----------------------------------"""


def get_attachment_ids(entry_id: int, database: str = None):
    """Gets all attachment ids associated with a given entry

    :param entry_id: the id of the entry for which all attachment ids are desired
    :param database: a Connection or str representing the database that is being queried
    :return: a tuple of ints representing the ids of the attachments associated with the given entry
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        c = d.execute('SELECT att_id FROM attachments WHERE entry_id=? ORDER BY added', (entry_id,)).fetchall()
        return tuple(int(x[0]) for x in c)


def get_attachment_file(att_id: int, database: str = None):
    """Gets the file associated with a given attachment

    :rtype: int
    :param att_id: an int representing the id of a given attachment
    :param database: a Connection or str representing the database that is being queried
    :return: a bytestream representing the attachment file
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        return d.execute('SELECT file FROM attachments WHERE att_id=?', (att_id,)).fetchone()[0]


def get_attachment_name(att_id: int, database: str = None):
    """Gets the name associated with a given attachment

    :rtype: str
    :param att_id: an int representing the id of a given attachment
    :param database: a Connection or str representing the database that is being queried
    :return: a str representing the filename for the attachment
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        return d.execute('SELECT filename FROM attachments WHERE att_id=?', (att_id,)).fetchone()[0]


def get_attachment_date(att_id: int, database: str = None):
    """Gets the date associated with a given attachment

    :rtype: datetime
    :param att_id: an int representing the id of a given attachment
    :param database: a Connection or str representing the database that is being queried
    :return: a datetime representing the date that the attachment was added to the database
    """
    types = PARSE_DECLTYPES | PARSE_COLNAMES
    db = connect(database, detect_types=types) if database else connect(default_database(), detect_types=types)
    with closing(db) as d:
        return d.execute('SELECT added FROM attachments WHERE att_id=?', (att_id,)).fetchone()[0]


"""---------------------------------Relations Methods----------------------------------"""


def get_children(parent_id: int, database: str = None):
    """Gets the ids of all entries that were generated by the given entry

    :param parent_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing the child entries of the given entry
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        c = d.execute('SELECT child FROM relations WHERE parent=?', (parent_id,)).fetchall()
        return tuple(int(x[0]) for x in c)


def get_parent(child_id: int, database: str = None):
    """Gets the id of the entry that generated by the given entry

    :rtype: int
    :param child_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being queried
    :return: an int representing the parent of the given entry or None if there is no parent
    """
    db = connect(database) if database else connect(default_database())
    with closing(db) as d:
        c = d.execute('SELECT parent FROM relations WHERE child=?', (child_id,))
        t = c.fetchone()
        parent = t[0] if t else None
        return parent
