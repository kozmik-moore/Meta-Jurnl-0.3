from ast import literal_eval
from configparser import ConfigParser
from datetime import datetime

from os import makedirs, scandir, remove
from os.path import exists, join, basename
from typing import Union, Tuple

from filter import FilteredReader
from writer import Writer


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
    def __init__(self, path_to_file: str, path_to_database: str = 'jurnl.sqlite'):
        self._path = path_to_file
        self.parser = ConfigParser()
        self.parser.read(path_to_file)
        self._type = self.parser['Meta']['type']
        if self._type == 'Reader':
            self._module = FilteredReader(path_to_database)
            self._module.id_ = int(self.parser['Attributes']['id_'])
        if self._type == 'Writer':
            self._module = Writer(path_to_database)
            if self.parser['Attributes']['id_']:
                self._module.id_ = self.parser['Attributes']['id_']
            self._module.body = self.parser['Attributes']['body']
            self._module.date = datetime.strptime(self.parser['Attributes']['date'], '%Y-%m-%d %H:%M')
            self._module.tags = literal_eval(self.parser['Attributes']['tags'])
            self._module.attachments = literal_eval(self.parser['Attributes']['attachments'])
            self._module.parent = literal_eval(self.parser['Attributes']['parent'])

    @property
    def type_(self):
        return self._type
    
    @property
    def module_(self):
        return self._module

    def delete_tempfile(self):
        remove(self._path)
        
    @property
    def id_(self):
        if self._type == 'Reader':
            return self._module.reader_id
        elif self._type == 'Writer':
            return self._module.id_
    
    @id_.setter
    def id_(self, v: int):
        if self._type == 'Reader':
            self._module.reader_id = v
            self.write_file('id_', v)
        elif self._type == 'Writer':
            self._module.id_ = v
            self.write_file('id_', v)
        
    @property
    def body(self):
        return self._module.body
    
    @body.setter
    def body(self, v: int):
        pass
        
    @property
    def date(self):
        return 0
    
    @date.setter
    def date(self, v: int):
        pass
        
    @property
    def tags(self):
        return 0
    
    @tags.setter
    def tags(self, v: int):
        pass
        
    @property
    def attachments(self):
        return 0
    
    @attachments.setter
    def attachments(self, v: int):
        pass
        
    @property
    def parent(self):
        return 0
    
    @parent.setter
    def parent(self, v: int):
        pass
    
    def write_file(self, attr: str, value: Union[int, str, Tuple[int], Tuple[str]]):
        if attr == 'id_':
            self.parser['Attributes']['id_'] = str(value)
        if attr == 'body':
            self.parser['Attributes']['body'] = str(value)
        if attr == 'date':
            self.parser['Attributes']['date'] = str(value)
        if attr == 'tags':
            self.parser['Attributes']['tags'] = str(value)
        if attr == 'attachments':
            self.parser['Attributes']['attachments'] = str(value)
        if attr == 'parent':
            self.parser['Attributes']['parent'] = str(value)
