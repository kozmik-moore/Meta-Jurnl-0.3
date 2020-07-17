"""Functions for creating and querying the database for general information"""
from contextlib import closing
from sqlite3 import connect, Connection
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
    cursor.execute('CREATE TABLE tags(tag_id INTEGER PRIMARY KEY, entry_id INTEGER NOT NULL, tag TEXT '
                   'DEFAULT \'(UNTAGGED)\', FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    connection.close()


def get_all_entry_ids(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the id of every entry in the database

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing the entry ids
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        ids = [x[0] for x in c.execute('SELECT entry_id FROM dates ORDER BY string').fetchall()]
    return ids


def get_all_tags(database: Union[Connection, str] = 'jurnl.sqlite'):
    try:
        d = database if type(database) == Connection else connect(database)
        with closing(d.cursor()) as c:
            c.execute('SELECT tag FROM tags ORDER BY tag')
            tags = list({tag[0] for tag in c})
            return tags
    except TypeError:
        print('Input is not of type Cursor or str')


def get_all_dates(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Lists the date as a datetime object for every entry in the database

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list of datetime objects
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        dates = c.execute('SELECT string FROM dates').fetchall()
        dates = [parse(x[0]) for x in dates]
        return dates


def get_all_children(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the ids of all entries that were generated by another entry

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        sql = 'SELECT entry_id FROM dates WHERE entry_id=(SELECT child FROM relations) ORDER BY string'
        ids = [x[0] for x in c.execute(sql).fetchall()]
        return ids


def get_all_parents(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets the ids of all entries that have generated another entry

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list of ints representing entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        sql = 'SELECT entry_id FROM dates WHERE entry_id=(SELECT parent FROM relations) ORDER BY string'
        ids = [x[0] for x in c.execute(sql).fetchall()]
    return ids


def get_all_relations(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Gets all relation pairs from the database

    :rtype: tuple
    :param database: a Connection or str representing the database that is being queried
    :return: a collection of linked pairs, each representing a parent-child relationship
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        pairs = c.execute('SELECT child,parent FROM relations')
    return pairs


def get_number_of_entries(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Counts the number of entries in the database.

    :rtype: int
    :param database: a Connection or str representing the database that is being queried
    :return: an int representing the number of entries in the database
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        count = c.execute('SELECT COUNT() FROM bodies').fetchone()[0]
    return count


def get_years(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Lists, in order, the years in which the database has entries

    :rtype: list
    :param database: a Connection or str representing the database that is being queried
    :return: a list representing the years in which the database has entries
    """
    d = database if type(database) == Connection else connect(database)
    with closing(d.cursor()) as c:
        years = list({x[0] for x in c.execute('SELECT year FROM dates')})
        years.sort()
    return years


def close_connection(database: Union[Connection, str] = 'jurnl.sqlite'):
    """Closes the connection to the database

    :param database: a Connection or str representing the database that is being queried
    """
    database.close()
