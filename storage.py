"""Classes and functions for managing the databases and their backups"""
from os import replace, scandir, remove
from os.path import isfile
from shutil import copy
from sqlite3 import connect, DatabaseError

from configurations import *


def move_database(new: str):
    """Checks whether a supplied directory exists and moves the current database to the new location

    :param new: a str representing the new directory
    """
    if exists(new) and isdir(new):
        old = default_database()
        name = basename(old)
        new = join(new, name)
        replace(old, new)
        default_database(new)
    else:
        raise IOError('Provided address is not a valid directory.')


def move_backup(new: str):
    """Checks whether a supplied directory exists and moves the backup directory to the new location

    :param new: a str representing the new directory
    """
    if exists(new) and isdir(new):
        old = backup_location()
        new = join(new, 'Backup')
        replace(old, new)
        backup_location(new)
    else:
        raise IOError('Provided address is not a valid directory.')


def backup_needed():
    """Checks if the current database needs a backup

    :return: a bool indicating whether a backup is needed or None if it is not
    """
    if backup_enabled() == 'yes':
        last = last_backup()
        if not last:
            return True
        else:
            interval = backup_interval()
            now = datetime.now()
            delta = now - last
            if delta.seconds >= interval * 3600:
                return True
            else:
                return False


def backup_database():
    """Performs a database backup and deletes old backups, if necessary

    """
    backup = backup_location()
    name = basename(default_database()).replace('.sqlite', '')
    backups = [x.path for x in scandir(backup) if name in x.name]
    backups.sort()
    now = datetime.now()
    name += '_' + now.strftime('%Y.%m.%d.%H.%M.%S')
    path = join(backup, name)
    copy(default_database(), path)
    last_backup(now)
    num = number_of_backups()
    backups.append(path)
    while len(backups) > num:
        remove(backups.pop(0))


def switch_database(new: str):
    """Checks and sets a database from the configuration file as the current database

    :param new: a str indicating the filename of the database that will be loaded
    """
    d = databases()
    if new in d.keys():
        default_database(d[new])
        backup = backup_location()
        dates = [x.name.replace(new + '_', '') for x in scandir(backup) if new in x.name]
        dates.sort()
        date = datetime.strptime(dates[-1], '%Y.%m.%d.%H.%M.%S')
        last_backup(date)
    else:
        raise KeyError('\'{}\' is not listed as a database'.format(new))


def add_database(location: str):
    """Takes a path, checks whether it is a journal database, and adds it to the application list of databases

    :param location: a str path which is the address of the database
    """
    if is_database(location):
        databases([location])


def remove_database(name: str):
    """Checks whether a database is listed in the configuration file, removes the database if it is, and deletes it

    :param name: a str indicating the filename of the database
    """
    d = databases()
    if name in databases().keys():
        remove(d[name])
        databases(removed=[name])


def is_database(location: str):
    """Checks whether a file is a journal database

    :param location:
    :return:
    :rtype: bool
    """
    is_ = False
    message = 'Not a journal database'
    if not exists(location):
        message = 'File not found'
    elif not isfile(location):
        message = 'Not a file'
    else:
        try:
            database = connect(location)
            names = set(database.execute('SELECT name FROM sqlite_master WHERE type=\'table\''))
            if {('bodies',), ('dates',), ('attachments',), ('relations',), ('tags',)} == names:
                is_ = True
                message = ''
        except DatabaseError:
            message = 'Not a database'
    return is_, message
