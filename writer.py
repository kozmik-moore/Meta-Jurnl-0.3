"""Classes and functions for writing entries to the database"""
from contextlib import closing
from datetime import datetime
from os.path import basename
from sqlite3 import connect
from typing import Union, Tuple

from configurations import current_database
from reader import Reader, get_tags, get_attachment_ids


class Writer:
    def __init__(self, path_to_db: str = None):
        self._path = path_to_db if path_to_db else current_database()
        self._reader = Reader(path_to_db)

        self._id = None
        self._body = ''
        self._tags = tuple()
        self._date = None
        self._attachments = tuple()
        self._parent = None

        self._changes = False
        self._body_changed = False
        self._tags_changed = False
        self._attachments_changed = False
        self._date_changed = False

    @property
    def database_location(self):
        return self._path

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, entry_id: Union[int, None]):
        """Updates all fields with information from the database

        :param entry_id: either an int (representing an entry from the database) or None (indicating a new entry)
        """
        self._reader.id_ = entry_id
        self._id = entry_id
        if self._reader.id_:
            self.body = self._reader.body
            self.attachments = self._reader.attachments
            self.date = self._reader.date
            self.tags = self._reader.tags
            self.parent = self._reader.parent

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, v: str):
        """Changes the Writer's content field and checks to see whether the changes flag needs to be updated

        :param v: a str representing content for the entry
        """
        if type(v) is str:
            self._body = v
            self._body_changed = self.body != self._reader.body
            self.check_for_changes()

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, v: Tuple[str]):
        """Changes the Writer's tags field and checks to see whether the changes flag needs to be updated

        :param v: a list of str representing tags for the entry
        """
        if type(v) == tuple and all(isinstance(s, str) for s in v):
            self._tags = v
            self._tags_changed = self.tags != self._reader.tags
            self.check_for_changes()

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, v: Union[None, datetime]):
        """Changes the Writer's date field and checks to see whether the changes flag needs to be updated

        :param v: a datetime representing the date the entry was created
        """
        if type(v) is datetime or v is None:
            self._date = v
            self._date_changed = self.date != self._reader.date
            self.check_for_changes()

    @property
    def attachments(self):
        return self._attachments

    @attachments.setter
    def attachments(self, v: Tuple[Union[int, str]]):
        """Changes the Writer's list of attachments and checks to see whether the changes flag needs to be updated

        :param v: a tuple of int and str representing attachment locations; an int indicates the attachment is in the
        database and a str indicates it is in the filesystem and represents an absolute path to the file
        """
        if type(v) is tuple and all(isinstance(x, (int, str)) for x in v):
            self._attachments = v
            self._attachments_changed = self.attachments != self._reader.attachments
            self.check_for_changes()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, v: int):
        if v is None or type(v) == int and v > 0:
            self._parent = v

    @property
    def has_attachments(self) -> Union[bool, None]:
        has_att = False if not self._attachments else True
        return has_att

    @property
    def changes(self):
        return self._changes

    @changes.setter
    def changes(self, v: bool):
        if type(v) == bool:
            self._changes = v

    def check_for_changes(self):
        """If the entry exists in the database, compares the Writer's entry fields to the entry fields in the
        database. If it does not, checks the fields empty. Afterwards, updates the changes flag
        """
        changed = False
        if self.id_:
            if any([
                self._body_changed,
                self._tags_changed,
                self._attachments_changed,
                self._date_changed
            ]):
                changed = True
        elif any([
            self.body,
            self.tags,
            self.date,
            self.attachments,
            self.parent]
        ):
            changed = True
        self.changes = changed

    def write_to_database(self):
        if self.changes:
            if not self.id_:
                self.id_ = create_entry(self._path, self.body, self.tags, self.date, self.attachments,
                                        self.parent)
            else:
                if self._body_changed:
                    modify_body(self.id_, self.body, self._path)
                if self._date_changed:
                    modify_date(self.id_, self.date, self._path)
                if self._tags_changed:
                    tags = ('UNTAGGED',)
                    if self.tags:
                        tags = self.tags
                    set_tags(self.id_, tags, self._path)
                if self._attachments_changed:
                    set_attachments(self.id_, self.attachments, self._path)
                modify_last_edit(self.id_, self._path)
            self.id_ = self.id_

    # TODO remove
    def clear_fields(self):
        """Clears all entry fields if there have been no changes to the body, date, tags, or attachments.

        """
        if not self.changes:
            self.id_ = None
            self.body = ''
            self.date = None
            self.tags = tuple()
            self.parent = None
            self.attachments = tuple()
            self.changes = False

    def reset(self):
        """Clears all entry fields regardless of changes to fields

        """
        self.id_ = None
        self.body = ''
        self.tags = tuple()
        self.parent = None
        self.attachments = tuple()
        self.changes = False

    def remove_from_database(self):
        """Removes entry from the database and clears entry fields

        """
        if self.id_:
            delete_entry(self.id_, self._path)
            self.reset()


"""---------------------------------Date Methods----------------------------------"""


# TODO Does this need to be modified for when the new date is after the latest edit?
def modify_date(entry_id: int, date: datetime, database: str = None):
    """Changes the date of the given entry to the given date

    :param entry_id: an int representing the given entry
    :param date: a datetime representing the new date
    :param database: a Connection or str representing the database that is being modified
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        d.execute('UPDATE dates SET created=? WHERE entry_id=?',
                  (date, entry_id))
        d.commit()


def set_date(entry_id: int, date: datetime, database: str = None):
    """Adds a date to the database for the given entry

    :param entry_id: an int representing the given entry
    :param date: a datetime representing the date associated with the given entry
    :param database: a Connection or str representing the database that is being modified
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        d.execute('INSERT INTO dates(entry_id,created,last_edit) VALUES(?,?,?)', (entry_id, date, date))
        d.commit()


def modify_last_edit(entry_id: int, database: str = None):
    """Updates the database to reflect the last time the given entry was changed

    :param entry_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being modified
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        now = datetime.now()
        d.execute('UPDATE dates SET last_edit=? WHERE entry_id=?', (now, entry_id))
        d.commit()


"""---------------------------------Body Methods----------------------------------"""


def set_body(body: str, database: str = None):
    """Adds the given content to the database and returns the id of the newly created entry. This is the only way
    to create a key against which all other information is referenced

    :rtype: int
    :param body: the content of the new entry
    :param database: a Connection or str representing the database that is being modified
    :return: an int representing the id of the new entry
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        c = d.execute('INSERT INTO bodies(body) VALUES(?)', (body.strip(),))
        entry = c.lastrowid
        d.commit()
    return entry


def modify_body(entry_id: int, body: str, database: str = None):
    """Changes the content of the given entry

    :param entry_id: an int representing the entry
    :param body: a str representing the content to replace with
    :param database: a Connection or str representing the database that is being modified
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        d.execute('UPDATE bodies SET body=? WHERE entry_id=?', (body.strip(), entry_id))
        d.commit()


"""---------------------------------Tags Methods----------------------------------"""


def set_tags(entry_id: int, tags: Tuple[str], database: str = None):
    """Updates the tags for the given entry

    :param entry_id: an int representing the given int
    :param tags: a tuple representing the tags to be removed from the entry
    :param database: a Connection or str representing the database that is being modified
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        if not tags:
            d.execute('INSERT INTO tags(entry_id) VALUES(?)', (entry_id,))
        else:
            old = get_tags(entry_id, database)
            added = set(tags).difference(old)
            added = [(entry_id, tag) for tag in added]
            d.executemany('INSERT INTO tags(entry_id,tag) VALUES(?,?)', added)
            removed = set(old).difference(tags)
            removed = [(entry_id, tag) for tag in removed]
            d.executemany('DELETE FROM tags WHERE entry_id=? AND tag=?', removed)
        d.commit()


"""---------------------------------Attachments Methods----------------------------------"""


def set_attachments(entry_id: int, attachments: Tuple[str], database: str = None):
    """Generates data for a given file and adds the data to the database for the given entry

    :param entry_id: an int representing the entry
    :param attachments: a tuple of int (indicating an attachment in the database) or path-like (indicating a location in
        the filesystem)
    :param database: a Connection or str representing the database that is being modified
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        old = get_attachment_ids(entry_id, database)
        added = tuple(set(attachments).difference(old))
        for path in added:
            name = basename(path)
            with open(path, 'rb') as f:
                bytestream = f.read()
                f.close()
            # TODO get this to appropriately add the timestamp (UTC issue?)
            d.execute('INSERT INTO attachments(entry_id,filename,file,added) VALUES (?,?,?,?)',
                      (entry_id, name, bytestream, datetime.now()))

        removed = set(old).difference(attachments)
        removed = [(att_id,) for att_id in removed]
        d.executemany('DELETE FROM attachments WHERE att_id=?', removed)
        d.commit()


"""---------------------------------Relations Methods----------------------------------"""


def set_relation(parent: int, child: int, database: str = None):
    """Adds a parent-child relation to the database representing the link between an entry and the one that
    generated it

    :param parent: an int representing the id of the generating entry
    :param child: an int representing the id of the generated entry
    :param database: a Connection or str representing the database that is being modified
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        if (child,) not in d.execute('SELECT child FROM relations WHERE parent=?', (parent,)).fetchall():
            d.execute('INSERT INTO relations(child,parent) VALUES (?,?)', (child, parent))
        d.commit()


"""---------------------------------Entry Methods----------------------------------"""


def create_entry(database: str = None, body: str = '', tags: tuple = (), date: datetime = None,
                 attachments: tuple = None, parent: int = None):
    """Systematically adds a new entry to the database. This is the preferred method for making new entries.

    :param body: a str representing the content of the entry
    :param tags: a tuple representing the tags associated with the entry
    :param date: a datetime representing when the date the entry was created
    :param attachments: a tuple of path-likes representing the attachments associated with the entry
    :param parent: an int representing the parent of the entry
    :param database: a Connection or str representing the database that is being modified
    :return: an int identifying the entry in the database
    """
    d = database if database else current_database()
    id_ = set_body(body, d)
    set_tags(id_, tags, d)
    set_attachments(id_, attachments, d)
    set_date(id_, date if date else datetime.now(), d)
    if parent:
        set_relation(parent, id_, d)
    return id_


def delete_entry(entry_id, database: str = None):
    """Systematically removes the entry from the database

    :param entry_id: an int representing the id of the given entry
    :param database: a Connection or str representing the database that is being modified
    """
    db = connect(database) if database else connect(current_database())
    with closing(db) as d:
        d.execute('DELETE FROM bodies WHERE entry_id=?', (entry_id,))
        d.execute('DELETE FROM dates WHERE entry_id=?', (entry_id,))
        d.execute('DELETE FROM tags WHERE entry_id=?', (entry_id,))
        d.execute('DELETE FROM attachments WHERE entry_id=?', (entry_id,))
        d.execute('DELETE FROM relations WHERE child=? OR parent=?', (entry_id, entry_id))
        d.commit()
