"""Classes and functions for manipulating and maintaining the application's configuration file(s)"""
from configparser import ConfigParser
from datetime import datetime
from os.path import exists, isdir, abspath


def create_file():
    """Creates the config file for the journal application

    """
    parser = ConfigParser()
    parser['Backup'] = {
        'enabled': 'yes',
        'last backup': 'Never',
        'backup interval': '72'
    }
    parser['Filesystem'] = {
        'database location': '.',
        'backup location': 'Backup'
    }
    with open('settings.config', 'w') as f:
        parser.write(f)
        f.close()
    

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
        if 'database location' in keys:
            database_location(options["database location"])
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
        p['Backup']['last backup'] = date.strftime('%Y-%m-%d %H:%M')
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    elif date is None:
        v = p['Backup']['last backup']
        if v == 'Never':
            return None
        else:
            return datetime.strptime(v, '%Y-%m-%d %H:%M')


def backup_interval(interval: int = None):
    """If interval is supplied, edits the 'backup interval' field in the config file. Otherwise, returns the field

    :param interval: an int indicating the number of hours between backups
    :return: an int indicating the number of hours between backups
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')
    if type(interval) == int:
        p['Backup']['backup interval'] = str(interval)
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    elif interval is None:
        v = int(p['Backup']['backup interval'])
        return v


def database_location(path: str = None):
    """If path is supplied, edits the 'database location' field in the config file. Otherwise, returns the field

    :param path: a str indicating the location of the database
    :return: a str indicating the location of the database
    """
    if not exists('settings.config'):
        create_file()
    p = ConfigParser()
    p.read('settings.config')
    if path is None:
        v = p['Filesystem']['database location']
        return abspath(v)
    elif exists(path) and isdir(path):
        p['Filesystem']['database location'] = path
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
        p['Filesystem']['backup location'] = path
        with open('settings.config', 'w') as f:
            p.write(f)
            f.close()
    else:
        raise IOError('Not a valid path to a directory')
