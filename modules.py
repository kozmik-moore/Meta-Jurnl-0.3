from datetime import datetime
from tkinter import Event
from typing import Dict, Tuple, List, Any

from database_info import get_oldest_date, get_all_dates, get_all_tags, get_newest_date, get_all_entry_ids
from filter import Filter
from reader_functions import get_date, get_body, get_parent, get_children, get_attachment_ids, get_tags, \
    get_attachment_name, get_attachment_file
from tempfiles import ReaderFileManager, WriterFileManager
from writer import create_entry, set_body, modify_body, modify_date, set_tags, set_attachments


class ReaderModule:
    def __init__(self, path_to_tempfile: str = None):
        self._temp = ReaderFileManager(path_to_tempfile)
        self._filter = Filter(self._temp.database)

        self._filter.dates = self._temp.dates
        self._filter.date_filter = self._temp.date_filter
        self._filter.has_parent = self._temp.has_parent
        self._filter.has_attachments = self._temp.has_attachments
        self._filter.has_children = self._temp.has_children
        self._filter.body = self._temp.body

    @property
    def id_(self):
        return self._temp.id_

    @id_.setter
    def id_(self, v: int):
        self._temp.id_ = v

    @property
    def database(self):
        return self._temp.database

    @property
    def entry_body(self):
        if self.id_:
            return get_body(self.id_, self.database)
        else:
            return ''

    @property
    def entry_date(self):
        if self.id_:
            return get_date(self.id_, self.database)
        else:
            return None

    @property
    def entry_parent(self):
        if self.id_:
            return get_parent(self.id_, self.database)
        else:
            return None

    @property
    def entry_children(self):
        if self.id_:
            return get_children(self.id_, self.database)
        else:
            return ()

    @property
    def entry_attachments(self):
        if self.id_:
            return get_attachment_ids(self.id_, self.database)
        else:
            return ()

    @property
    def entry_tags(self):
        if self.id_:
            return get_tags(self.id_, self.database)
        else:
            return ()

    @property
    def entry_has_children(self):
        if self.entry_children:
            return True
        else:
            return False

    @property
    def entry_has_parent(self):
        if self.entry_parent:
            return True
        else:
            return False

    @property
    def entry_has_attachments(self):
        if self.entry_attachments:
            return True
        else:
            return False

    @property
    def body(self):
        return self._temp.body

    @body.setter
    def body(self, t: Tuple[str]):
        self._filter.body = t
        self._temp.body = t

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
        return self._temp.has_parent

    @has_parent.setter
    def has_parent(self, v: int):
        self._temp.has_parent = v
        self._filter.has_parent = v

    @property
    def has_children(self):
        return self._temp.has_children

    @has_children.setter
    def has_children(self, v: int):
        self._temp.has_children = v
        self._filter.has_children = v

    @property
    def has_attachments(self):
        return self._temp.has_attachments

    @has_attachments.setter
    def has_attachments(self, v: int):
        self._temp.has_attachments = v
        self._filter.has_attachments = v

    @property
    def date_filter(self):
        return self._temp.date_filter

    @date_filter.setter
    def date_filter(self, v: int):
        self._filter.date_filter = v
        self._temp.date_filter = v

    @property
    def tag_filter(self):
        return self._temp.tag_filter

    @tag_filter.setter
    def tag_filter(self, v: int):
        self._temp.tag_filter = v
        self._filter.tag_filter = v

    @property
    def untagged(self):
        return self._filter.is_untagged

    @untagged.setter
    def untagged(self, b: bool):
        self._filter.is_untagged = b

    @property
    def tags_autosort(self):
        return self._temp.tags_sort

    @tags_autosort.setter
    def tags_autosort(self, v: int):
        if type(v) == int:
            self._temp.tags_sort = v

    @property
    def oldest_date(self):
        return get_oldest_date(self._temp.database)

    @property
    def newest_date(self):
        return get_newest_date(self._temp.database)

    @property
    def oldest_year(self):
        return self.oldest_date.year

    @property
    def newest_year(self):
        return self.newest_date.year

    @property
    def all_dates(self):
        return get_all_dates(self._temp.database)

    @property
    def all_tags(self):
        return get_all_tags(self._temp.database)

    @property
    def filtered_ids(self):
        return self._filter.filtered_ids

    @property
    def all_ids(self):
        return get_all_entry_ids(self.database)

    @property
    def path(self):
        return self._temp.path

    def get_date(self, id_: int):
        return get_date(id_, self._temp.database)

    def get_attachment_name(self, id_: int):
        return get_attachment_name(id_, self._temp.database)

    def get_attachment_file(self, id_: int):
        return get_attachment_file(id_, self._temp.database)

    def reset_fields(self):
        self._temp.reset_all_fields()


class WriterModule(WriterFileManager):
    def __init__(self, tempfile: str = None):
        super(WriterModule, self).__init__(file_path=tempfile)

    @property
    def current_year(self):
        return datetime.now().year

    @property
    def current_month(self):
        return datetime.now().month

    @property
    def current_day(self):
        return datetime.now().day

    @property
    def current_hour(self):
        return datetime.now().hour

    @property
    def current_minute(self):
        return datetime.now().minute

    @property
    def all_tags(self):
        return get_all_tags(self.database)

    def add_attachment(self, path: str):
        old: List[Any] = list(self.attachments)
        old.append(path)
        self.attachments = tuple(old)

    def attachment_name(self, id_: int):
        return get_attachment_name(id_, self.database)

    def attachment_file(self, id_: int):
        return get_attachment_file(id_, self.database)

    def check_saved(self, event: Event):
        # TODO Fix this
        if not self.id_ and all([self.body == '',
                                 self.tags == (),
                                 self.attachments == (),
                                 not self.date,
                                 not self.parent]):
            saved = True
        elif self.id_:
            saved = all([self.body == get_body(self.id_, self.database),
                         self.tags == get_tags(self.id_, self.database),
                         self.date == get_date(self.id_, self.database),
                         self.attachments == get_attachment_ids(self.id_, self.database)])
        else:
            saved = False
        return saved

    def save(self):
        if not self.id_:
            if not self.date:
                self.date = datetime.now()
            self.id_ = create_entry(database=self.database, body=self.body, date=self.date, tags=self.tags,
                                    attachments=self.attachments, parent=self.parent)
        else:
            kwargs = {
                'entry_id': self.id_,
                'database': self.database,
                'body': self.body,
                'date': self.date,
                'tags': self.tags,
                'attachments': self.attachments
            }
            modify_body(**kwargs)
            modify_date(**kwargs)
            set_tags(**kwargs)
            set_attachments(**kwargs)
        self.attachments = get_attachment_ids(self.id_, self.database)

    def set_body(self, v: str):
        if type(v) == str:
            self.body = v
        unchanged = True
        if self.id_:
            unchanged = get_body(self.id_, self.database) == self.body
        return unchanged

    def edit_entry(self, entry_id: int):
        self.id_ = entry_id
        self.body = get_body(entry_id, self.database)
        self.tags = get_tags(entry_id, self. database)
        self.attachments = get_attachment_ids(entry_id, self.database)
        self.date = get_date(entry_id, self.database)

    def link_entry(self, entry_id: int):
        self.parent = entry_id
        self.tags = get_tags(entry_id, self. database)


def _test():
    r = ReaderModule(
        path_to_tempfile='/home/kozmik/Documents/Personal/Education/Projects/Programming/Meta-Jurnl-0.3/.tempfiles/'
                         'Reader/000')
    r.id_ = 1
    print(r.all_dates)


if __name__ == '__main__':
    _test()
