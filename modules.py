from typing import Dict, Tuple

from configurations import tags_autosort, dates_sort
from database_info import get_oldest_date, get_all_dates, get_all_tags, get_newest_date
from filter import Filter
from reader import Reader, get_date
from tempfiles import ReaderFileManager


class ReaderModule:
    def __init__(self, path_to_db: str = None, path_to_tempfile: str = None):
        self._filter = Filter(path_to_db)
        self._reader = Reader(path_to_db)
        self._temp = ReaderFileManager(path_to_tempfile)

        self._database = path_to_db

        self._filter.dates = self._temp.dates
        self._filter.date_filter = dates_sort()

    @property
    def id_(self):
        return self._reader.id_

    @id_.setter
    def id_(self, v: int):
        self._reader.id_ = v
        self._temp.id_ = self._reader.id_

    @property
    def entry_body(self):
        body = self._reader.body
        return body

    @property
    def entry_date(self):
        return self._reader.date

    @property
    def entry_parent(self):
        return self._reader.parent

    @property
    def entry_children(self):
        return self._reader.children

    @property
    def entry_attachments(self):
        return self._reader.attachments

    @property
    def entry_tags(self):
        return self._reader.tags

    @property
    def entry_has_children(self):
        return self._reader.has_children

    @property
    def entry_has_parent(self):
        return self._reader.has_parent

    @property
    def entry_has_attachments(self):
        return self._reader.has_attachments

    @property
    def body(self):
        return self._filter.body

    @body.setter
    def body(self, t: Tuple[str]):
        self._filter.tags = t
        self._temp.tags = t

    @property
    def tags(self):
        return self._temp.tags

    @tags.setter
    def tags(self, t: Tuple[str]):
        self._filter.tags = t
        self._temp.tags = t

    @property
    def dates(self):
        return self._temp.dates.copy()

    @dates.setter
    def dates(self, d: Dict[str, int]):
        self._temp.dates = d
        self._filter.dates = d

    @property
    def has_parent(self):
        return self._filter.has_parent

    @has_parent.setter
    def has_parent(self, d: Dict[str, int]):
        self._temp.has_parent = d
        self._filter.has_parent = d

    @property
    def has_children(self):
        return self._filter.has_children

    @has_children.setter
    def has_children(self, d: Dict[str, int]):
        self._temp.has_children = d
        self._filter.has_children = d

    @property
    def has_attachments(self):
        return self._filter.has_attachments

    @has_attachments.setter
    def has_attachments(self, d: Dict[str, int]):
        self._temp.has_attachments = d
        self._filter.has_attachments = d
        
    @property
    def date_filter(self):
        return dates_sort()
    
    @date_filter.setter
    def date_filter(self, v: int):
        self._filter.date_filter = v
        dates_sort(v)
        
    @property
    def tag_filter(self):
        return self._filter.tag_filter
    
    @tag_filter.setter
    def tag_filter(self, s: str):
        self._filter.tag_filter = s
        
    @property
    def untagged(self):
        return self._filter.is_untagged
    
    @untagged.setter
    def untagged(self, b: bool):
        self._filter.is_untagged = b

    @property
    def tags_autosort(self):
        return tags_autosort()

    @tags_autosort.setter
    def tags_autosort(self, b: int):
        tags_autosort(b)

    @property
    def oldest_date(self):
        return get_oldest_date(self._database)

    @property
    def newest_date(self):
        return get_newest_date(self._database)

    @property
    def oldest_year(self):
        return self.oldest_date.year

    @property
    def newest_year(self):
        return self.newest_date.year

    @property
    def all_dates(self):
        return get_all_dates(self._database)

    @property
    def all_tags(self):
        return get_all_tags(self._database)

    @property
    def filtered_ids(self):
        return self._filter.filtered_ids

    def get_date(self, id_: int):
        return get_date(id_, self._database)


def _test():
    r = ReaderModule(
        path_to_tempfile='/home/kozmik/Documents/Personal/Education/Projects/Programming/Meta-Jurnl-0.3/.tempfiles/'
                         'Reader/000')
    r.id_ = 1
    print(r.all_dates)


if __name__ == '__main__':
    _test()
