"""Classes and functions for writing entries to the database"""
from contextlib import closing
from datetime import datetime
from os.path import basename
from sqlite3 import Connection, connect
from typing import Union, Tuple

from reader import Reader, get_tags, get_attachment_ids


class Writer(Reader):
    def __init__(self, path_to_db: str = 'jurnl.sqlite'):
        self.__body = ''
        self.__tags = tuple()
        self.__date = None
        self.__attachments = tuple()
        self.__parent = None
        self.__changes = False
        self.__body_changed = False
        self.__tags_changed = False
        self.__attachments_changed = False
        self.__date_changed = False
        super(Writer, self).__init__(path_to_db=path_to_db)

    @property
    def writer_id(self):
        return self.reader_id

    @writer_id.setter
    def writer_id(self, entry_id: Union[int, None]):
        """Updates all fields with information from the database

        :param entry_id: either an int (representing an entry from the database) or None (indicating a new entry)
        """
        self.reader_id = entry_id
        self.body = self.get_body
        self.attachments = self.get_attachments
        self.date = self.get_date
        self.tags = self.get_tags
        self.parent = self.get_parent

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, v: str):
        """Changes the Writer's content field and checks to see whether the changes flag needs to be updated

        :param v: a str representing content for the entry
        """
        if type(v) is str:
            self.__body = v
            self.__body_changed = self.body != self.get_body
            self.check_for_changes()

    @property
    def tags(self):
        return self.__tags

    @tags.setter
    def tags(self, v: Tuple[str]):
        """Changes the Writer's tags field and checks to see whether the changes flag needs to be updated

        :param v: a list of str representing tags for the entry
        """
        if type(v) == tuple and all(isinstance(s, str) for s in v):
            self.__tags = v
            self.__tags_changed = self.tags != self.get_tags
            self.check_for_changes()

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, v: Union[None, datetime]):
        """Changes the Writer's date field and checks to see whether the changes flag needs to be updated

        :param v: a datetime representing the date the entry was created
        """
        if type(v) is datetime or v is None:
            self.__date = v
            self.__date_changed = self.date != self.get_date
            self.check_for_changes()

    @property
    def attachments(self):
        return self.__attachments

    @attachments.setter
    def attachments(self, v: Tuple[Union[int, str]]):
        """Changes the Writer's list of attachments and checks to see whether the changes flag needs to be updated

        :param v: a tuple of int and str representing attachment locations; an int indicates the attachment is in the
        database and a str indicates it is in the filesystem and represents an absolute path to the file
        """
        if type(v) is tuple and all(isinstance(x, (int, str)) for x in v):
            self.__attachments = v
            self.__attachments_changed = self.attachments != self.get_attachments
            self.check_for_changes()

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, v: int):
        if v is None or type(v) == int and v > 0:
            self.__parent = v

    @property
    def has_attachments(self) -> Union[bool, None]:
        has_att = False if not self.__attachments else True
        return has_att

    @property
    def changes(self):
        return self.__changes

    @changes.setter
    def changes(self, v: bool):
        if type(v) == bool:
            self.__changes = v

    def check_for_changes(self):
        """If the entry exists in the database, compares the Writer's entry fields to the entry fields in the
        database. If it does not, checks the fields empty. Afterwards, updates the changes flag
        """
        changed = False
        if self.writer_id:
            if any([
                self.__body_changed,
                self.__tags_changed,
                self.__attachments_changed,
                self.__date_changed
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
            if not self.writer_id:
                self.writer_id = create_entry(self.body, self.tags, self.date, self.attachments, self.parent,
                                              self.connection)
            else:
                if self.__body_changed:
                    modify_body(self.writer_id, self.body, self.connection)
                if self.__date_changed:
                    modify_date(self.writer_id, self.date, self.connection)
                if self.__tags_changed:
                    tags = ('UNTAGGED',)
                    if self.tags:
                        tags = self.tags
                    set_tags(self.writer_id, tags, self.connection)
                if self.__attachments_changed:
                    set_attachments(self.writer_id, self.attachments, self.connection)
                modify_last_edit(self.writer_id, self.connection)
            self.writer_id = self.reader_id

    def clear_fields(self):
        """Clears all entry fields if there have been no changes to the body, date, tags, or attachments.

        """
        if not self.changes:
            self.writer_id = None
            self.body = ''
            self.date = None
            self.tags = tuple()
            self.parent = None
            self.attachments = tuple()
            self.changes = False

    def reset(self):
        """Clears all entry fields regardless of changes to fields

        """
        self.writer_id = None
        self.body = ''
        self.tags = tuple()
        self.parent = None
        self.attachments = tuple()
        self.changes = False

    def remove_from_database(self):
        """Removes entry from the database and clears entry fields

        """
        if self.writer_id:
            delete_entry(self.writer_id, self.connection)
            self.reset()


"""---------------------------------Date Methods----------------------------------"""


# TODO Does this need to be modified for when the new date is after the latest edit?
def modify_date(entry_id: int, date: datetime, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Changes the date of the given entry to the given date

    :param entry_id: an int representing the given entry
    :param date: a datetime representing the new date
    :param database: a Connection or str representing the database that is being modified
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('UPDATE dates SET year=?,month=?,day=?,hour=?,minute=?,weekday=?,string=?'
                  'WHERE entry_id=?',
                  (date.year, date.month, date.day, date.hour, date.minute, date.weekday(),
                   date.strftime('%Y-%m-%d %H:%M'), entry_id))
    d.commit()


def set_date(entry_id: int, date: datetime, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Adds a date to the database for the given entry

    :param entry_id: an int representing the given entry
    :param date: a datetime representing the date associated with the given entry
    :param database: a Connection or str representing the database that is being modified
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        date_string = date.strftime('%Y-%m-%d %H:%M')
        c.execute('INSERT INTO dates(entry_id,year,month,day,hour,minute,weekday,string,last_edit) '
                  'VALUES(?,?,?,?,?,?,?,?,?)', (entry_id, date.year, date.month, date.day, date.hour, date.minute,
                                                date.weekday(), date_string, date_string))
    d.commit()


def modify_last_edit(entry_id: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Updates the database to reflect the last time the given entry was changed

    :param entry_id: an int representing the given entry
    :param database: a Connection or str representing the database that is being modified
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        c.execute('UPDATE dates SET last_edit=? WHERE entry_id=?', (now, entry_id))
    d.commit()


"""---------------------------------Body Methods----------------------------------"""


def set_body(body: str, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Adds the given content to the database and returns the id of the newly created entry. This is the only way
    to create a key against which all other information is referenced

    :rtype: int
    :param body: the content of the new entry
    :param database: a Connection or str representing the database that is being modified
    :return: an int representing the id of the new entry
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('INSERT INTO bodies(body) VALUES(?)', (body.strip(),))
        entry = c.lastrowid
    d.commit()
    return entry


def modify_body(entry_id: int, body: str, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Changes the content of the given entry

    :param entry_id: an int representing the entry
    :param body: a str representing the content to replace with
    :param database: a Connection or str representing the database that is being modified
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('UPDATE bodies SET body=? WHERE entry_id=?', (body.strip(), entry_id))
    d.commit()


"""---------------------------------Tags Methods----------------------------------"""


def set_tags(entry_id: int, tags: Tuple[str], database: Union[Connection, str] = 'jurnl.sqlite'):
    """Updates the tags for the given entry

    :param entry_id: an int representing the given int
    :param tags: a tuple representing the tags to be removed from the entry
    :param database: a Connection or str representing the database that is being modified
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        if not tags:
            c.execute('INSERT INTO tags(entry_id) VALUES(?)', (entry_id,))
        else:
            old = get_tags(entry_id, database)
            added = set(tags).difference(old)
            added = [(entry_id, tag) for tag in added]
            c.executemany('INSERT INTO tags(entry_id,tag) VALUES(?,?)', added)
            removed = set(old).difference(tags)
            removed = [(entry_id, tag) for tag in removed]
            c.executemany('DELETE FROM tags WHERE entry_id=? AND tag=?', removed)
    d.commit()


"""---------------------------------Attachments Methods----------------------------------"""


def set_attachments(entry_id: int, attachments: Tuple[str], database: Union[Connection, str] = 'jurnl.sqlite'):
    """Generates data for a given file and adds the data to the database for the given entry

    :param entry_id: an int representing the entry
    :param attachments: a tuple of int (indicating an attachment in the database) or path-like (indicating a location in
        the filesystem)
    :param database: a Connection or str representing the database that is being modified
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        old = get_attachment_ids(entry_id, database)
        added = tuple(set(attachments).difference(old))
        for path in added:
            name = basename(path)
            with open(path, 'rb') as f:
                bytestream = f.read()
                f.close()
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            c.execute('INSERT INTO attachments(entry_id,filename,file,added) VALUES (?,?,?,?)',
                      (entry_id, name, bytestream, now))

        removed = set(old).difference(attachments)
        removed = [(att_id,) for att_id in removed]
        c.executemany('DELETE FROM attachments WHERE att_id=?', removed)


"""---------------------------------Relations Methods----------------------------------"""


def set_relation(parent: int, child: int, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Adds a parent-child relation to the database representing the link between an entry and the one that
    generated it

    :param parent: an int representing the id of the generating entry
    :param child: an int representing the id of the generated entry
    :param database: a Connection or str representing the database that is being modified
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        if (child,) not in c.execute('SELECT child FROM relations WHERE parent=?', (parent,)).fetchall():
            c.execute('INSERT INTO relations(child,parent) VALUES (?,?)', (child, parent))
    d.commit()


"""---------------------------------Entry Methods----------------------------------"""


def create_entry(body: str = '', tags: tuple = (), date: datetime = None, attachments: tuple = None, parent: int = None,
                 database: Union[Connection, str] = 'jurnl.sqlite'):
    """Systematically adds a new entry to the database. This is the preferred method for making new entries.

    :param body: a str representing the content of the entry
    :param tags: a tuple representing the tags associated with the entry
    :param date: a datetime representing when the date the entry was created
    :param attachments: a tuple of path-likes representing the attachments associated with the entry
    :param parent: an int representing the parent of the entry
    :param database: a Connection or str representing the database that is being modified
    :return: an int identifying the entry in the database
    """
    d = database if type(database) == Connection else connect(database)
    id_ = set_body(body, d)
    set_tags(id_, tags, d)
    set_attachments(id_, attachments, d)
    set_date(id_, date if date else datetime.now(), d)
    if parent:
        set_relation(parent, id_)
    return id_


def delete_entry(entry_id, database: Union[Connection, str] = 'jurnl.sqlite'):
    """Systematically removes the entry from the database

    :param entry_id: an int representing the id of the given entry
    :param database: a Connection or str representing the database that is being modified
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        c.execute('DELETE FROM bodies WHERE entry_id=?', (entry_id,))
        c.execute('DELETE FROM dates WHERE entry_id=?', (entry_id,))
        c.execute('DELETE FROM tags WHERE entry_id=?', (entry_id,))
        c.execute('DELETE FROM attachments WHERE entry_id=?', (entry_id,))
        c.execute('DELETE FROM relations WHERE child=? OR parent=?', (entry_id, entry_id))
    d.commit()
