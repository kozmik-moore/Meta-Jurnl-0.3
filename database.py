from os.path import exists, basename
from datetime import datetime
from sqlite3 import Cursor, connect, Error
from typing import Union

from dateutil.parser import parse


def create_database(database: str) -> None:
    file = open(database, 'w+')
    file.close()
    connection = connect(database)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE bodies(entry_id INTEGER PRIMARY KEY, body TEXT)')
    cursor.execute('CREATE TABLE dates(entry_id INTEGER NOT NULL, year INTEGER NOT NULL, month INTEGER NOT NULL, '
                   'day INTEGER NOT NULL, hour INTEGER NOT NULL, minute INTEGER NOT NULL, weekday INTEGER NOT NULL, '
                   'string TEXT NOT NULL, last_edit TEXT, FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE attachments(att_id INTEGER PRIMARY KEY, entry_id INTEGER NOT NULL, '
                   'filename TEXT NOT NULL, file BLOB NOT NULL, added TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, '
                   'FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE relations(rel_id INTEGER PRIMARY KEY, child INTEGER NOT NULL, '
                   'parent INTEGER NOT NULL,FOREIGN KEY(child) REFERENCES bodies(entry_id), '
                   'FOREIGN KEY(parent) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE tags(tag_id INTEGER PRIMARY KEY, entry_id INTEGER NOT NULL, tag TEXT NOT NULL '
                   'DEFAULT \'(UNTAGGED)\', FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    connection.close()


def get_all_tags(cursor: Union[Cursor, str] = 'jurnl.sqlite'):
    try:
        if type(cursor) == Cursor:
            c = cursor
        else:
            c = connect(cursor).cursor()
        c.execute('SELECT tag FROM tags')
        tags = list({tag[0] for tag in c})
        tags.sort()
        return tags
    except TypeError:
        print('Input is not of type Cursor or str')


class DatabaseReader:
    def __init__(self, database: str = None) -> None:
        db_name = 'jurnl.sqlite' if database is None else database
        if exists(db_name):
            try:
                self.__connection = connect(db_name)
                self.__cursor = self.__connection.cursor()
            except Error as detail:
                print('Error connecting to database:', detail)
        else:
            create_database(db_name)
            self.__connection = connect(db_name)
            self.__cursor = self.__connection.cursor()

        self.date_format = '%Y-%m-%d %H:%M'

    """---------------------------------DatabaseReader Methods----------------------------------"""

    def get_number_of_entries(self):
        """Counts the number of entries in the database

        :rtype: int
        :return: an int representing the number of entries in the database
        """
        count = self.__cursor.execute('SELECT COUNT() FROM bodies').fetchone()[0]
        return count

    def get_years(self):
        """Lists, in order, the years in which the database has entries

        :rtype: list
        :return: a list representing the years in which the database has entries
        """
        years = list({x[0] for x in self.__cursor.execute('SELECT year FROM dates')})
        years.sort()
        return years

    def close_connection(self):
        """
        Closes the connection to the database
        """
        self.__connection.close()

    """---------------------------------Date Methods----------------------------------"""

    def get_date(self, entry: int):
        """Gets the date for a given entry

        :rtype: datetime
        :param entry: an int representing the given entry
        :return: the date for the given entry
        """
        self.__cursor.execute('SELECT year,month,day,hour,minute FROM dates WHERE entry_id=?', (entry,))
        temp = self.__cursor.fetchone()
        date = datetime(temp[0], temp[1], temp[2], temp[3], temp[4])
        return date

    def get_all_dates(self):
        """Lists the date as a datetime object for every entry in the database

        :rtype: list
        :return: a list of datetime objects
        """
        ids = self.get_all_entry_ids()
        dates = []
        for entry_id in ids:
            dates.append(self.get_date(entry_id))
        dates.sort()
        return dates

    """---------------------------------Body Methods----------------------------------"""

    def get_body(self, entry: int):
        """Gets the entry content for a given entry

        :rtype: str
        :param entry: an int representing the given entry
        :return: the body of the given entry
        """
        self.__cursor.execute('SELECT body FROM bodies WHERE entry_id=?', (entry,))
        body = self.__cursor.fetchone()[0]
        return body

    """---------------------------------Tags Methods----------------------------------"""

    def get_tags(self, entry: int):
        """Gets either all tags in the entire database or the tags for a specific entry

        :param entry: int representing the id of a given entry
        :return: a list of str representing the tags for all entries or a specific entry
        """
        self.__cursor.execute('SELECT tag FROM tags WHERE entry_id=?', (entry,))
        tags = [tag[0] for tag in self.__cursor]
        tags.sort()
        return tags

    """---------------------------------Attachments Methods----------------------------------"""

    def get_attachment_ids(self, entry_id: int):
        """Gets all attachment ids associated with a given entry

        :param entry_id: the id of the entry for which all attachment ids are desired
        :return: a list of ints representing the ids of the attachments associated with the given entry
        """
        self.__cursor.execute('SELECT att_id FROM attachments WHERE entry_id=?', (entry_id,))
        ids = [x[0] for x in self.__cursor.fetchall()]
        return ids

    def get_attachment_file(self, att_id: int):
        """Gets the file associated with a given attachment

        :param att_id: an int representing the id of a given attachment
        :return: a bytestream representing the attachment file
        """
        self.__cursor.execute('SELECT file FROM attachments WHERE att_id=?', (att_id,))
        attachment = self.__cursor.fetchone()[0]
        return attachment

    def get_attachment_name(self, att_id: int):
        """Gets the name associated with a given attachment

        :param att_id: an int representing the id of a given attachment
        :return: a str representing the filename for the attachment
        """
        self.__cursor.execute('SELECT filename FROM attachments WHERE att_id=?', (att_id,))
        name = self.__cursor.fetchone()[0]
        return name

    def get_attachment_date(self, att_id: int):
        """Gets the date associated with a given attachment

        :param att_id: an int representing the id of a given attachment
        :return: a datetime representing the date that the attachment was added to the database
        """
        self.__cursor.execute('SELECT added FROM attachments WHERE att_id=?', (att_id,))
        name = self.__cursor.fetchone()[0]
        name = parse(name)
        return name

    """---------------------------------Relations Methods----------------------------------"""

    def get_children(self, parent_id: int):
        """Gets the ids of all entries that were generated by the given entry

        :rtype: list
        :param parent_id: an int representing the given entry
        :return: a list of ints representing the child entries of the given entry
        """
        self.__cursor.execute('SELECT child FROM relations WHERE parent=?', (parent_id,))
        children = [x[0] for x in self.__cursor.fetchall()]
        return children

    def get_parent(self, child_id: int):
        """Gets the id of the entry that generated by the given entry

        :rtype: int
        :param child_id: an int representing the given entry
        :return: an int representing the parent of the given entry or None if there is no parent
        """
        self.__cursor.execute('SELECT parent FROM relations WHERE child=?', (child_id,))
        try:
            parent = self.__cursor.fetchone()[0]
        except TypeError:
            parent = None
        return parent

    def get_all_relations(self):
        """Gets all relation pairs from the database

        :rtype: tuple
        :return: a collection of linked pairs, each representing a parent-child relationship
        """
        pairs = self.__cursor.execute('SELECT child,parent FROM relations')
        return pairs

    def get_all_children(self):
        """Gets the ids of all entries that were generated by another entry

        :rtype: list
        :return: a list of ints representing entries
        """
        ids = [x[0] for x in self.__cursor.execute('SELECT child FROM relations ').fetchall()]
        ids.sort(key=self.get_date)
        return ids

    def get_all_parents(self):
        """Gets the ids of all entries that have generated another entry

        :rtype: list
        :return: a list of ints representing entries
        """
        ids = [x[0] for x in self.__cursor.execute('SELECT parent FROM relations ').fetchall()]
        ids.sort(key=self.get_date)
        return ids

    """---------------------------------Entry Methods----------------------------------"""

    def get_entry_id_of_most_recent_entry(self):
        """Gets the id of the most recently edited entry

        :rtype: int
        :return: an int representing a specific entry
        """
        self.__cursor.execute('SELECT entry_id FROM bodies WHERE rowid=(SELECT MAX(rowid) FROM bodies)')
        entry_id = self.__cursor.fetchone()[0]
        return entry_id

    def get_entry_ids_from_year_range(self, year: tuple):
        """Filters the database for entries that were created over a given range of years

        :rtype: list
        :param year: a tuple containing the endpoints of the range
        :return: a list containing the filtered entries
        """
        self.__cursor.execute('SELECT entry_id FROM dates WHERE year BETWEEN ? AND ?', (year[0], year[1]))
        ids = [x[0] for x in self.__cursor.fetchall()]
        ids.sort(key=self.get_date)
        return ids

    def get_entry_ids_from_month_range(self, month: tuple):
        """Filters the database for entries that were created over a given range of months

        :rtype: list
        :param month: a tuple containing the endpoints of the range
        :return: a list containing the filtered entries
        """
        self.__cursor.execute('SELECT entry_id FROM dates WHERE month BETWEEN ? AND ?', (month[0], month[1]))
        ids = [x[0] for x in self.__cursor.fetchall()]
        ids.sort(key=self.get_date)
        return ids

    def get_entry_ids_from_day_range(self, day: tuple):
        """Filters the database for entries that were created over a given range of days

        :rtype: list
        :param day: a tuple containing the endpoints of the range
        :return: a list containing the filtered entries
        """
        self.__cursor.execute('SELECT entry_id FROM dates WHERE day BETWEEN ? AND ?', (day[0], day[1]))
        ids = [x[0] for x in self.__cursor.fetchall()]
        ids.sort(key=self.get_date)
        return ids

    def get_entry_ids_from_hour_range(self, hour: tuple):
        """Filters the database for entries that were created over a given range of hours

        :rtype: list
        :param hour: a tuple containing the endpoints of the range
        :return: a list containing the filtered entries
        """
        self.__cursor.execute('SELECT entry_id FROM dates WHERE hour BETWEEN ? AND ?', (hour[0], hour[1]))
        ids = [x[0] for x in self.__cursor.fetchall()]
        ids.sort(key=self.get_date)
        return ids

    def get_entry_ids_from_minute_range(self, minute: tuple):
        """Filters the database for entries that were created over a given range of minutes

        :rtype: list
        :param minute: a tuple containing the endpoints of the range
        :return: a list containing the filtered entries
        """
        self.__cursor.execute('SELECT entry_id FROM dates WHERE minute BETWEEN ? AND ?', (minute[0], minute[1]))
        ids = [x[0] for x in self.__cursor.fetchall()]
        ids.sort(key=self.get_date)
        return ids

    def get_entry_ids_from_weekday_range(self, weekday: tuple):
        """Filters the database for entries that were created over a given range of weekdays

        :rtype: list
        :param weekday: a tuple containing the endpoints of the range
        :return: a list containing the filtered entries
        """
        self.__cursor.execute('SELECT entry_id FROM dates WHERE weekday BETWEEN ? AND ?', (weekday[0], weekday[1]))
        ids = [x[0] for x in self.__cursor.fetchall()]
        ids.sort(key=self.get_date)
        return ids

    def get_entry_ids_from_range(self, lower: datetime, upper: datetime):
        """Filters the database for entries that were created over a given range of time

        :param lower: a datetime representing the lower limit of the dates to filter for
        :param upper:  a datetime representing the upper limit of the dates to filter for
        :return: a list of ints representing the filtered entries
        :rtype: list
        """
        self.__cursor.execute('SELECT entry_id FROM dates WHERE string BETWEEN ? AND ?',
                              (lower.strftime('%Y-%m-%d %H:%M'), upper.strftime('%Y-%m-%d %H:%M')))
        ids = [x[0] for x in self.__cursor]
        ids.sort(key=self.get_date)
        return ids

    def get_all_entry_ids(self):
        """Gets the id of every entry in the database

        :rtype: list
        :return: a list of ints representing the entry ids
        """
        ids = [x[0] for x in self.__cursor.execute('SELECT entry_id FROM bodies').fetchall()]
        ids.sort(key=self.get_date)
        return ids

    def get_entry_ids_from_tags(self, tags: tuple, op_type: str = 'Contains One Of...'):
        """

        :rtype: list
        :param tags: a tuple of strings representing the tags to be used for filtering entries from the database
        :param op_type: a str representing the type of filter to apply
        :return: a list of ints representing the filtered entries
        """
        ids = []
        if op_type == 'Contains At Least...':
            tags = list(tags)
            tag = tags.pop(0)
            sql = 'SELECT entry_id FROM tags WHERE tag=?'
            temp = set(self.__cursor.execute(sql, (tag,)).fetchall())
            for tag in tags:
                temp = temp.intersection(self.__cursor.execute(sql, (tag,)).fetchall())
            ids = [i[0] for i in temp]
        if op_type == 'Contains Only...':
            for entry in self.get_all_entry_ids():
                if len(self.get_tags(entry)) == len(tags):
                    if set(self.get_tags(entry)).intersection(tags) == set(tags):
                        ids.append(entry)
        if op_type == 'Contains One Of...':
            sql = 'SELECT entry_id FROM tags WHERE tag IN ({})'.format(','.join(['?'] * len(tags)))
            ids = list({x[0] for x in self.__cursor.execute(sql, tags).fetchall()})
        if op_type == 'Untagged':
            cmd = 'SELECT entry_id FROM tags WHERE tag=\'UNTAGGED\''
            ids = [x[0] for x in self.__cursor.execute(cmd).fetchall()]
        return ids

    def get_entry_ids_from_attachments(self):
        """Gets the ids of entries that have attachments

        :rtype: list
        :return: a list of ints representing the filtered entries
        """
        ids = [x[0] for x in self.__cursor.execute('SELECT entry_id FROM attachments').fetchall()]
        return ids

    def get_entry_ids_from_body(self, search_string: str):
        """Gets the ids of entries that contain a given search string

        :rtype: list
        :param search_string: a str which is used to sort the ids
        :return: a list of ints representing the filtered entries
        """
        self.__cursor.execute('SELECT entry_id FROM bodies WHERE body LIKE ?', ('%' + search_string + '%',))
        ids = [x[0] for x in self.__cursor.fetchall()]
        return ids


class DatabaseWriter:
    def __init__(self, database: str = '') -> None:
        db_name = 'jurnl.sqlite' if database == '' else database
        if exists(db_name):
            try:
                self.__connection = connect(db_name)
                self.__cursor = self.__connection.cursor()
            except Error as detail:
                print('Error connecting to database:', detail)
        else:
            create_database(db_name)
            self.__connection = connect(db_name)
            self.__cursor = self.__connection.cursor()

        self.date_format = '%Y-%m-%d %H:%M'

    """---------------------------------DatabaseManager Methods----------------------------------"""

    def close_connection(self):
        """
        Closes the connection to the database
        """
        self.__connection.close()

    """---------------------------------Date Methods----------------------------------"""

    def modify_date(self, entry_id: int, date: datetime):
        """Changes the date of the given entry to the given date

        :param entry_id: an int representing the given entry
        :param date: a datetime representing the new date
        """
        self.__cursor.execute('UPDATE dates SET year=?,month=?,day=?,hour=?,minute=?,weekday=?,string=?'
                              'WHERE entry_id=?',
                              (date.year, date.month, date.day, date.hour, date.minute, date.weekday(),
                               date.strftime(self.date_format), entry_id))
        self.__connection.commit()

    def set_date(self, entry_id: int, date: datetime):
        """Adds a date to the database for the given entry

        :param entry_id: an int representing the given entry
        :param date: a datetime representing the date associated with the given entry
        """
        self.__cursor.execute('INSERT INTO dates(entry_id,year,month,day,hour,minute,weekday,string) '
                              'VALUES(?,?,?,?,?,?,?,?)', (entry_id, date.year, date.month, date.day, date.hour,
                                                          date.minute, date.weekday(),
                                                          date.strftime(self.date_format)))
        self.__connection.commit()

    def change_last_edit(self, entry_id: int):
        """Updates the database to reflect the last time the given entry was changed

        :param entry_id: an int representing the given entry
        """
        now = datetime.now().strftime(self.date_format)
        self.__cursor.execute('UPDATE dates SET last_edit=? WHERE entry_id=?', (now, entry_id))
        self.__connection.commit()

    """---------------------------------Body Methods----------------------------------"""

    def set_body(self, body: str):
        """Adds the given content to the database and returns the id of the newly created entry. This is the only way
        to create a key against which all other information is referenced

        :rtype: int
        :param body: the content of the new entry
        :return: an int representing the id of the new entry
        """
        self.__cursor.execute('INSERT INTO bodies(body) VALUES(?)', (body.strip(),))
        entry = self.__cursor.lastrowid
        return entry

    def modify_body(self, entry_id: int, body: str):
        """Changes the content of the given entry

        :param entry_id: an int representing the entry
        :param body: a str representing the content to replace with
        """
        self.__cursor.execute('UPDATE bodies SET body=? WHERE entry_id=?', (body.strip(), entry_id))
        self.__connection.commit()

    """---------------------------------Tags Methods----------------------------------"""

    def add_tags(self, entry_id: int, tags: tuple):
        for tag in tags:
            self.__cursor.execute('INSERT INTO tags(entry_id,tag) VALUES(?,?)', (entry_id, tag))
        self.__connection.commit()

    def remove_tags(self, entry_id, tags: tuple):
        """Removes the given tags for the given entry

        :param entry_id: an int representing the given int
        :param tags: a tuple representing the tags to be removed from the entry
        """
        for tag in tags:
            self.__cursor.execute('DELETE FROM tags WHERE entry_id=? AND tag=?', (entry_id, tag))
        self.__connection.commit()

    """---------------------------------Attachments Methods----------------------------------"""

    def add_attachments(self, entry_id: int, attachments: tuple):
        """Generates data for a given file and adds the data to the database for the given entry

        :param entry_id: an int representing the entry
        :param attachments: a tuple of path-like objects (preferably of type str)
        """
        for path in attachments:
            name = basename(path)
            with open(path, 'rb') as f:
                bytestream = f.read()
                f.close()
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.__cursor.execute('INSERT INTO attachments(entry_id,filename,file,added) VALUES (?,?,?,?)',
                                  (entry_id, name, bytestream, now))
        self.__connection.commit()

    def remove_attachments(self, ids: tuple):
        """
        Removes from the database all data associated with the given attachments
        :param ids: an int representing the id of a given attachment
        """
        for att_id in ids:
            self.__cursor.execute('DELETE FROM attachments WHERE att_id=?', (att_id,))
        self.__connection.commit()

    """---------------------------------Relations Methods----------------------------------"""

    def add_relation(self, parent: int, child: int):
        """Adds a parent-child relation to the database representing the link between an entry and the one that
        generated it

        :param parent: an int representing the id of the generating entry
        :param child: an int representing the id of the generated entry
        """
        if (child,) not in self.__cursor.execute('SELECT child FROM relations WHERE parent=?', (parent,)).fetchall():
            self.__cursor.execute('INSERT INTO relations(child,parent) VALUES (?,?)', (child, parent))
            self.__connection.commit()

    def remove_relation(self, parent: int, child: int):
        """Removes a parent-child relation from the database, breaking the link between an entry and the one that
        generated it

        :param parent: an int representing the id of the generating entry
        :param child: an int representing the id of the generated entry
        """
        if (child,) in self.__cursor.execute('SELECT child FROM relations WHERE parent=?', (parent,)).fetchall():
            self.__cursor.execute('DELETE FROM relations WHERE child=? AND parent=?', (child, parent))
            self.__connection.commit()

    def set_parent(self, parent: int, entry: int):
        """Directly sets the parent attribute of an entry

        :param parent: an int representing the id of the generating entry
        :param entry: an int representing the id of the given entry
        """
        self.__cursor.execute('UPDATE relations SET parent=? WHERE child=?', (parent, entry))
        self.__connection.commit()

    def set_children(self, entry: int, children: tuple):
        """Directly sets the children attribute of an entry, adding new links and removing discarded ones

        :param entry: an int representing the id of the given entry
        :param children: a tuple of ints representing the ids of the children to be set
        """
        cmd = ('SELECT child FROM relations WHERE parent=?', (entry,))
        current = {x[0] for x in self.__cursor.execute(cmd[0], cmd[1]).fetchall()}
        update = set(children)
        added = tuple((x[0], entry) for x in update.difference(current))
        self.__cursor.executemany('INSERT INTO relations(child,parent) VALUES(?,?)', added)
        removed = tuple((x[0], entry) for x in current.difference(update))
        self.__cursor.executemany('REMOVE FROM relations WHERE child=? AND parent=?', removed)
        self.__connection.commit()

    """---------------------------------Entry Methods----------------------------------"""

    def create_entry(self, body: str, tags: tuple = None, attachments: tuple = None, parent: int = None):
        """Systematically creates a new entry in the database from given information with a minimum of a body and a
        date (the date is automatically generated)

        :param body: a str representing the content of the entry
        :param tags: a tuple representing the tags associated with the entry
        :param attachments: a tuple containing the path-like objects pointing to the entry's attachments
        :param parent: an int representing the entry that generated
        :return: an int identifying the newly created entry
        """
        entry = self.set_body(body)
        self.set_date(entry, datetime.now())
        if tags:
            self.add_tags(entry, tags)
        if attachments:
            self.add_attachments(entry, attachments)
        if parent:
            self.add_relation(parent, entry)
        return entry

    def modify_entry(self, entry_id: int, date: datetime = None, body: str = None, tags: tuple = None,
                     attachments: tuple = None, parent: int = None, children: tuple = None):
        """Systematically modifies the given entry with the information provided

        :param entry_id: an int representing the given entry
        :param date: a datetime representing the date the given entry was created
        :param body: a str representing the content of the entry
        :param tags: a tuple representing the tags associated with the given entry
        :param attachments: a tuple of path-likes and ints representing the location of attachments for the given entry;
        path-likes indicate that the attachment is not yet in the database while ints do
        :param parent: an int representing the entry that generated this entry
        :param children: a tuple representing the entries that are generated from this entry
        """

        if date:
            self.modify_date(entry_id, date)
        if body:
            self.modify_body(entry_id, body)
        if tags is not None:
            temp = self.__cursor.execute('SELECT tag FROM tags WHERE entry_id=?', (entry_id,)).fetchall()
            current = {x[0] for x in temp}
            if set(tags) != current:
                self.remove_tags(entry_id, tuple(current.difference(tags)))
                self.add_tags(entry_id, tuple(set(tags).difference(current)))
        if attachments is not None:
            temp = self.__cursor.execute('SELECT tag FROM tags WHERE entry_id=?', (entry_id,)).fetchall()
            current = {x[0] for x in temp}
            if set(attachments) != current:
                self.remove_attachments(tuple(current.difference(attachments)))
                self.add_attachments(entry_id, tuple(set(attachments).difference(current)))
        if parent:
            self.set_parent(parent, entry_id)
        if children is not None:
            self.set_children(entry_id, children)

    def delete_entry(self, entry_id):
        """Systematically removes the entry from the database

        :param entry_id: an int representing the id of the given entry
        """
        self.__cursor.execute('DELETE FROM bodies WHERE entry_id=?', (entry_id,))
        self.__cursor.execute('DELETE FROM dates WHERE entry_id=?', (entry_id,))
        self.__cursor.execute('DELETE FROM tags WHERE entry_id=?', (entry_id,))
        self.__cursor.execute('DELETE FROM attachments WHERE entry_id=?', (entry_id,))
        self.__cursor.execute('DELETE FROM relations WHERE child=? OR parent=?', (entry_id, entry_id))
        self.__connection.commit()
