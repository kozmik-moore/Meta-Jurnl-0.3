from datetime import datetime
from os import scandir, rmdir, mkdir, makedirs, remove
from os.path import join, exists
from shutil import copy

from configurations import last_backup, backup_location, backup_interval, number_of_backups, databases


def check_backup():
    """Checks if a backup is required and calls run_backup, if necessary

    :return: either a 1 indicating successful backup or an error code
    """
    last = last_backup()
    loc = backup_location()
    if not exists(loc):
        makedirs(loc)
    backups = list(scandir(loc))
    if not last or len(backups) == 0:
        return run_backup()
    else:
        now = datetime.now().replace(second=59, microsecond=999999)
        try:
            delta = (now - last).seconds / 3600
            if delta > backup_interval():
                return run_backup()
        except ValueError as err:
            return err


def run_backup():
    """Creates a new backup for each database in the config file

    :return: either a 1 indicating successful backup or an error code
    """
    dbs = databases()
    loc = backup_location()
    if not exists(loc):
        makedirs(loc)
    try:
        for name in dbs.keys():
            d = join(loc, name)
            if not exists(d):
                mkdir(d)
        backups = list(scandir(loc))
        num = number_of_backups()
        for directory in backups:
            dirs = list(scandir(directory))
            dirs.sort(key=lambda x: x.name)
            while len(dirs) >= num:
                d = dirs.pop(0)
                for file in scandir(d):
                    remove(file)
                rmdir(d)
            now = datetime.now().strftime('%Y-%m-%d-%-H-%-M')
            destination = join(join(loc, directory), now)
            mkdir(destination)
            copy(dbs[directory.name], destination)
        last_backup(datetime.now())
        return 1
    except PermissionError as err:
        return err
    except FileNotFoundError as err:
        return err
