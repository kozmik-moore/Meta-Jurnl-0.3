"""Classes and functions for managing the tempfile, which tracks open Readers and Writers after the application is
closed """
from ast import literal_eval
from configparser import ConfigParser
from datetime import datetime

from os import makedirs, remove, scandir
from os.path import exists, join, isfile
from typing import Tuple, Union


def _parse_datestring(date: str):
    if date == 'None':
        return None
    else:
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')


def _get_file_id(directory: str):
    """Searches for and returns the next available tempfile filename

    :return: a str representing the next available tempfile filename
    """
    ids = [int(x.name) for x in scandir(join('.tempfiles', directory))]
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


def _check_attachments(_attachments):
    """Checks whether all supplied attachments still exist. Edits the collection, if any do not

    :param _attachments: a collection of str representing paths
    :return: a tuple representing the (edited) collection and a str representing whether any changes were required
    """
    l_ = list()
    status = 'Good'
    for a in _attachments:
        if exists(a):
            l_.append(a)
        else:
            status = 'Bad'
    l_ = tuple(l_)
    return l_, status


class _TempFileManager:
    """Manages a single tempfile containing all fields of an entry"""

    def __init__(self, module: str, file_path: str = None):
        d = join('.tempfiles', module)
        if not exists(d):
            makedirs(d)
        self._file_path = join(d, _get_file_id(module)) if file_path is None else file_path
        self._parser = ConfigParser(
            converters={'date': _parse_datestring,
                        'tuple': literal_eval,
                        'literal': literal_eval
                        })

        self._type = module
        self._id: Union[int, None] = None
        if file_path:
            self._parser.read(self._file_path)
            self.id_ = self._parser.getliteral('Attributes', 'id')
        else:
            self._parser['Meta'] = {
                'type': module
            }
            self._parser['Attributes'] = {
                'id': 'None'
            }
            self.write_file()

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
    def path(self):
        return self._file_path

    @path.setter
    def path(self, v: str):
        if exists(v) and isfile(v):
            self._file_path = v

    @property
    def parser(self):
        return self._parser

    @parser.setter
    def parser(self, v: ConfigParser):
        if type(v) == ConfigParser:
            self._parser = v

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, v: int = None):
        if type(v) == int or v is None:
            self._id = v
            self._parser['Attributes']['id'] = str(v)
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


class ReaderFileManager(_TempFileManager):
    """Manages a single tempfile containing all fields of a reading module"""

    def __init__(self, file_path: str = None):
        super(ReaderFileManager, self).__init__(file_path=file_path, module='Reader')

        self._tags = ()
        self._has_children = False
        self._has_parent = False
        self._has_attachments = False

        if file_path:
            self.tags = self.parser.gettuple('Filters', 'tags')
            self._has_children = self.parser.getboolean('Filters', 'has children')
            self._has_parent = self.parser.getboolean('Filters', 'has parent')
            self._has_attachments = self.parser.getboolean('Filters', 'has attachments')
        else:
            self.parser['Filters'] = {
                'tags': '()',
                'has children': 'False',
                'has parent': 'False',
                'has attachments': 'False'
            }
            self.write_file()

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, v: tuple):
        if type(v) == tuple and all([isinstance(x, str) for x in v]):
            self._tags = v
            self.parser['Filters']['tags'] = str(v)
            self.write_file()

    @property
    def children(self):
        return self._has_children

    @children.setter
    def children(self, v: bool):
        if type(v) == bool:
            self._has_children = v
            self.parser['Filters']['has children'] = str(v)
            self.write_file()

    @property
    def parent(self):
        return self._has_parent

    @parent.setter
    def parent(self, v: bool):
        if type(v) == bool:
            self._has_parent = v
            self.parser['Filters']['has parent'] = str(v)
            self.write_file()

    @property
    def attachments(self):
        return self._has_attachments

    @attachments.setter
    def attachments(self, v: bool):
        if type(v) == bool:
            self._has_attachments = v
            self.parser['Filters']['has attachments'] = str(v)
            self.write_file()


class WriterFileManager(_TempFileManager):
    """Manages a single tempfile containing all fields of a writing module"""

    def __init__(self, file_path: str = None):
        super(WriterFileManager, self).__init__(file_path=file_path, module='Writer')

        self._body: str = ''
        self._date: Union[datetime, None] = None
        self._tags: Tuple = ()
        self._attachments: Tuple = ()
        self._parent: Union[int, None] = None

        self._errors = {'attachments': 'Good'}

        if file_path:
            self._body = self._parser['Attributes']['body']
            self._tags = self.parser.gettuple('Attributes', 'tags')
            self._date = self.parser.getdate('Attributes', 'date')
            self._attachments = self.parser.gettuple('Attributes', 'attachments')
            if self._attachments:
                self._attachments, self._errors['attachments'] = _check_attachments(self._attachments)
            self._parent = self.parser.getliteral('Attributes', 'parent')
        else:
            self.parser.set('Attributes', 'body', '')
            self.parser.set('Attributes', 'date', 'None')
            self.parser.set('Attributes', 'tags', '()')
            self.parser.set('Attributes', 'attachments', '()')
            self.parser.set('Attributes', 'parent', 'None')
            self.write_file()

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, v: dict):
        if type(v) == dict:
            if 'attachments' in v.keys():
                self._errors['attachments'] = v['attachments']

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
            self._parser['Attributes']['date'] = str(v)
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
            v, m = _check_attachments(v)
            self._attachments = v
            self.errors = {'attachments': m}
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
