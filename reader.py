"""The tab which contains all of the methods for displaying data from a journal entry"""
from os import makedirs
from os.path import exists, join, basename
from typing import Union

from database import DatabaseReader, get_all_tags


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


class ErrorManager:
    __message = ''

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, m):
        try:
            self.__message = m
            print(m)
        except TypeError:
            print('Message is not of type str')

    def clear_message(self):
        self.message = ''


class ReaderManager:
    def __init__(self, path_to_db: str, error_mngr: ErrorManager):
        self.__database_path = path_to_db
        self.__database = DatabaseReader(path_to_db)
        self.__current_entry = read_temp_file()
        self.__error_manager = error_mngr

    @property
    def database(self):
        return basename(self.__database_path)

    @database.setter
    def database(self, path_to_db: str):
        self.__database = DatabaseReader(path_to_db)
        self.current_entry = None

    @property
    def current_entry(self):
        return self.__current_entry

    @current_entry.setter
    def current_entry(self, entry_id: Union[int, None]):
        if type(entry_id) == int:
            if entry_id in self.__database.get_all_entry_ids():
                self.__current_entry = entry_id
                write_temp_file(entry_id)
            else:
                self.__error_manager.message = 'Entry id is not in database'
        else:
            raise TypeError('Value is not an int')

    @property
    def body(self):
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            body = self.__database.get_body(self.__current_entry)
            return body

    @property
    def tags(self):
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            tags = self.__database.get_tags(self.__current_entry)
            return tags

    @property
    def all_tags(self):
        tags = get_all_tags(self.__database_path)
        return tags

    @property
    def date(self):
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            date = self.__database.get_date(self.__current_entry)
            return date

    @property
    def attachments(self):
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            attachments = {att_id: self.__database.get_attachment_name(att_id=att_id) for att_id in
                           self.__database.get_attachment_ids(self.__current_entry)}
            return attachments

    @property
    def parent(self):
        """Passes the parent for the currently selected entry

        :return: an int representing the parent or None if there is no parent
        """
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            parent = self.__database.get_parent(self.__current_entry)
            return parent

    @property
    def children(self):
        """Passes the parent for the currently selected entry

        :return: a list representing the children of the entry
        """
        if self.current_entry is None:
            self.__error_manager.message = 'No entry is selected'
        else:
            children = self.__database.get_children(self.__current_entry)
            return children
