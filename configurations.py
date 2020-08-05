"""Classes and functions for manipulating and maintaining the application's configuration file(s)"""
from configparser import ConfigParser
from datetime import datetime
from os import getcwd
from os.path import exists, isdir, abspath, join, basename
from typing import List, Union

from database import create_database


def create_file(database: str = None):
    """Creates the config file for the application. Creates a database named 'jurnl.sqlite', if it does not exist

    :param database: a str path pointing to the database that the config file is initially built for
    """
    if not database:
        database = join(getcwd(), 'jurnl.sqlite')
        if not exists(database):
            create_database(database)
    else:
        database = abspath(database)
    name = basename(database)
    if exists(abspath(database)):
        parser = ConfigParser()
        parser['Backup'] = {
            'enabled': 'yes',
            'last backup': 'Never',
            'backup interval': '72',
            'number of backups': '3'
        }
        parser['Filesystem'] = {
            'current database': database,
            'backup location': join(getcwd(), 'Backup')
        }
        parser['Databases'] = {
            name.replace('.sqlite', ''): database
        }
        with open('settings.config', 'w') as f:
            parser.write(f)
            f.close()
    else:
        raise FileNotFoundError('The provided database \'{}\' does not exist.'.format(name))
    

def config(**options):
    """If options are supplied, attempts to edit those options in the file. Otherwise, gets and returns the options

    :param options: various str representing keys in the config file
    :return: a ConfigParser containing all the options in the config file
    """
    if options:
        keys = options.keys()
        if 'enabled' in keys:
            enabled(options['enabled'])
        if 'last backup' in keys:
            last_backup(options['last backup'])
        if 'backup interval' in keys:
            backup_interval(options['backup interval'])
        if 'number of backups' in keys:
            number_of_backups(options['number of backups'])
        if 'current database' in keys:
            current_database(options['current database'])
        if 'backup location' in keys:
            backup_location(options['backup location'])
    else:
        if not exists('settings.config'):
            create_file()
    p = ConfigParser()
    p.read('settings.config')
    return p
            
            
def enabled(option: str = None):
    """If option is supplied, edits the 'backup enabled' switch in the config file. Otherwise, returns its status

    :param option: a str: 'yes' indicates that backups are enabled, 'no' indicates disabled
    :return: a str indicating whether backups are enabled
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')  
    if option in ['yes', 'no']:
        p['Backup']['enabled'] = option
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    elif option is None:
        v = p['Backup']['enabled']
        return v


def last_backup(date: datetime = None):
    """If date is supplied, edits the 'last backup' field in the config file. Otherwise, returns the field

    :param date: a datetime indicating the last time a backup was performed
    :return: a str or datetime indicating the last time a backup was performed
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')
    if type(date) == datetime:
        p['Backup']['last backup'] = date.strftime('%Y-%m-%d %H:%M:%S')
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    elif date is None:
        v = p['Backup']['last backup']
        if v == 'Never':
            return None
        else:
            return datetime.strptime(v, '%Y-%m-%d %H:%M:%S')


def backup_interval(interval: Union[float, int] = None):
    """If interval is supplied, edits the 'backup interval' field in the config file. Otherwise, returns the field

    :param interval: an int indicating the number of hours between backups
    :return: an int indicating the number of hours between backups
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')
    if type(interval) in [float, int]:
        p['Backup']['backup interval'] = str(interval)
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    elif interval is None:
        v = float(p['Backup']['backup interval'])
        return v


def number_of_backups(number: int = None):
    """If interval is supplied, edits the 'backup interval' field in the config file. Otherwise, returns the field

    :param number: an int indicating the number of hours between backups
    :return: an int indicating the number of hours between backups
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')
    if type(number) == int:
        p['Backup']['number of backups'] = str(number)
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    elif number is None:
        v = int(p['Backup']['number of backups'])
        return v


def current_database(path: str = None):
    """If path is supplied, edits the 'current database' field in the config file. Otherwise, returns the field

    :param path: a str indicating the location of the database
    :return: a str indicating the location of the database
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')
    if path is None:
        v = p['Filesystem']['current database']
        return abspath(v)
    elif exists(path):
        databases([path])
        p.read('settings.config')
        p['Filesystem']['current database'] = abspath(path)
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    else:
        raise IOError('Not a valid path to a directory')


def backup_location(path: str = None):
    # TODO create dir if passed a bool indicating permission
    """If path is supplied, edits the 'backup location' field in the config file. Otherwise, returns the field

    :param path: a str indicating the location of the database backups
    :return: a str indicating the location of the database backups
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')
    if path is None:
        v = p['Filesystem']['backup location']
        return abspath(v)
    elif exists(path) and isdir(path):
        p['Filesystem']['backup location'] = abspath(path)
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    else:
        raise IOError('Not a valid path to a directory')


def databases(added: List[str] = None, removed: List[str] = None):
    """If path is supplied, edits the 'Databases' section in the config file. Otherwise, returns the section

    :param added: a list of str paths indicating databases to be added
    :param removed: a list of str indicating databases to be removed
    :return: a dict of databases and their paths
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')
    if not added and not removed:
        v = {x: p['Databases'][x] for x in p.options('Databases')}
        return v
    else:
        if added:
            for a in added:
                if exists(a):
                    p.set('Databases', basename(a).replace('.sqlite', ''), a)
                else:
                    raise IOError('Not a valid path to a database')
        if removed:
            for r in removed:
                p.remove_option('Databases', basename(r).replace('.sqlite', ''))
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
