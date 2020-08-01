"""Classes and functions for managing the tempfile, which tracks open Readers and Writers after the application is
closed """
from ast import literal_eval
from configparser import ConfigParser
from datetime import datetime

from os import makedirs, remove, scandir
from os.path import exists, join
from typing import Tuple, Union


def get_file_id():
    """Searches for and returns the next available tempfile filename

    :return: a str representing the next available tempfile filename
    """
    ids = [int(x.name) for x in scandir('.tempfiles')]
    ids.sort()
    diff = False
    i = 0
    while not diff and i < len(ids):
        if i != ids[i]:
            diff = True
        i += 1
    if i == 0:
        id_ = 0
    elif diff:
        id_ = i - 1
    else:
        id_ = i
    id_ = '{:03d}'.format(id_)
    return id_


def check_attachments(_attachments):
    """Checks whether all supplied attachments still exist. Edits the list, if any do not

    :param _attachments: a collection of str representing paths
    :return: a tuple representing the (edited) collection and a str representing whether any changes were required
    """
    l_ = list()
    status = 'Good'
    for a in _attachments:
        if exists(_attachments):
            l_.append(a)
        else:
            status = 'Bad'
    l_ = tuple(l_)
    return l_, status


class TempfileManager:
    """Manages a single tempfile containing all fields of an entry"""

    def __init__(self, file_id: str = None, module: str = None):
        if not exists('.tempfiles'):
            makedirs('.tempfiles')
        self._file_path = join('.tempfiles', get_file_id()) if file_id is None else join('.tempfiles', file_id)
        self._parser = ConfigParser()

        self._type: str = module if module else 'Reader'
        self._id: Union[int, None] = None
        self._body: str = ''
        self._date: Union[datetime, None] = None
        self._tags: Tuple = ()
        self._attachments: Tuple = ()
        self._parent: Union[int, None] = None

        self._errors = {'attachments': 'Good'}

        if file_id:
            self._parser.read(self._file_path)
            self._type = self._parser['Meta']['type']
            id_ = literal_eval(self._parser['Attributes']['id'])
            self._id = int(id_) if id_ else None
            self._body = self._parser['Attributes']['body']
            self._tags = literal_eval(self._parser['Attributes']['tags'])
            date = self._parser['Attributes']['date']
            self._date = datetime.strptime(date, '%Y-%m-%d %H:%M') if date != 'None' else None
            self._attachments = literal_eval(self._parser['Attributes']['attachments'])
            if self._attachments:
                self._attachments, self._errors['attachments'] = check_attachments(self._attachments)
            parent = literal_eval(self._parser['Attributes']['parent'])
            self._parent = int(parent) if parent else None
        else:
            self._parser['Meta'] = {'type': self._type}
            self._parser['Attributes'] = {
                'id': 'None',
                'body': '',
                'date': 'None',
                'tags': '()',
                'attachments': '()',
                'parent': 'None'
            }
            self.write_file()

    @property
    def errors(self):
        return self._errors

    @property
    def type_(self):
        return self._type

    @type_.setter
    def type_(self, v: str):
        if v in ['Reader', 'Writer']:
            self._type = v
            self._parser['Meta']['type'] = v
            self.write_file()
        else:
            raise KeyError('Allowed arguments include \'Reader\' and \'Writer\'.')

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, v: int):
        if type(v) == int:
            self._id = v
            self._parser['Attributes']['id'] = str(v)
            self.write_file()
        else:
            raise TypeError('Argument is not of type int.')

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, v: str):
        if type(v) == str:
            self._body = v
            self._parser['Attributes']['body'] = v
            self.write_file()
        else:
            raise TypeError('Argument is not of type str.')

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, v: datetime):
        if type(v) == datetime:
            self._date = v
            self._parser['Attributes']['date'] = v.strftime('%Y-%m-%d %H:%M')
            self.write_file()
        else:
            raise TypeError('Argument is not of type datetime.')

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, v: Tuple[str]):
        if type(v) == tuple and all(isinstance(x, str) for x in v):
            self._tags = v
            self._parser['Attributes']['tags'] = str(v)
            self.write_file()
        else:
            raise TypeError('Argument should be a tuple of str.')

    @property
    def attachments(self):
        return self._attachments

    @attachments.setter
    def attachments(self, v: Tuple[str]):
        if type(v) == tuple and all(isinstance(x, str) for x in v):
            self._attachments = v
            self._parser['Attributes']['attachments'] = str(v)
            self.write_file()
        else:
            raise TypeError('Argument should be a tuple of str.')

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, v: int):
        if type(v) == int:
            self._parent = v
            self._parser['Attributes']['parent'] = str(v)
            self.write_file()
        else:
            raise TypeError('Argument is not of type int.')

    def delete_tempfile(self):
        if exists(self._file_path):
            remove(self._file_path)

    def write_file(self):
        with open(self._file_path, 'w') as file:
            self._parser.write(file)
            file.close()
