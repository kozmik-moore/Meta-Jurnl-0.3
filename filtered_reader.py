"""Contains the classes and functions that support a a reader which can also filter entries"""

from reader import Filter, Reader


class FilteredReader(Filter, Reader):
    def __init__(self, path_to_database: str = 'jurnl.sqlite'):
        super(FilteredReader, self).__init__(path_to_database)
