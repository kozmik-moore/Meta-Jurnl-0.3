from os import makedirs
from os.path import join, exists

from err import ErrorManager


def get_entry_id_from_temp_file()
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

class WriterManager:
    def __init__(self, path_to_db: str, error_mngr: ErrorManager):
        self.__database_path = path_to_db

