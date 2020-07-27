from configparser import ConfigParser

from os import makedirs, scandir
from os.path import exists, join, basename


def get_entry_id_from_temp_file():
    p = join('.tempfiles', 'writer')
    if not exists(p):
        makedirs(p)
    f = join(p, 'entry_id')
    entry_id = -1
    if exists(f):
        with open(f, 'r') as s:
            entry_id = int(s.read())
            s.close()
    return entry_id


def write_entry_id_to_temp_file(entry_id: int = None):
    p = join('.tempfiles', 'writer')
    if not exists(p):
        makedirs(p)
    f = join(p, 'entry_id')
    with open(f, 'w') as s:
        s.write(str(entry_id))
        s.close()


def read_temp_file():
    p = join('.tempfiles', 'reader')
    if not exists(p):
        makedirs(p)
    f = join(p, 'entry_id')
    entry_id = -1
    if exists(f):
        with open(f, 'r') as s:
            entry_id = int(s.read())
            s.close()
    return entry_id


def write_temp_file(entry_id: int = None):
    p = join('.tempfiles', 'reader')
    if not exists(p):
        makedirs(p)
    f = join(p, 'entry_id')
    with open(f, 'w') as s:
        s.write(str(entry_id))
        s.close()


class TempfileManager:
    def __init__(self, file_location: str):
        if 'reader' in file_location:
            self._type = 'Reader'
        elif 'writer' in file_location:
            self._type = 'Writer'
        else:
            raise TypeError('Unable to determine object type from file name.')


    @property
    def type_(self):
        return self._type
