import sqlite3
from os.path import exists, basename
from datetime import datetime


def create_database(database: str) -> None:
    file = open(database, 'w+')
    file.close()
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE bodies(entry_id INTEGER PRIMARY KEY, body TEXT)')
    cursor.execute('CREATE TABLE dates(entry_id INTEGER NOT NULL, year INTEGER NOT NULL, month INTEGER NOT NULL, '
                   'day INTEGER NOT NULL, hour INTEGER NOT NULL, minute INTEGER NOT NULL, weekday INTEGER NOT NULL, '
                   'string TEXT NOT NULL, last_edit TEXT, FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE attachments(att_id INTEGER PRIMARY KEY, entry_id INTEGER NOT NULL, '
                   'filename TEXT NOT NULL, file BLOB NOT NULL, added TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, '
                   'FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE relations(rel_id INTEGER PRIMARY KEY, child INTEGER NOT NULL, '
                   'parent INTEGER NOT NULL,FOREIGN KEY(child) REFERENCES bodies(entry_id), '
                   'FOREIGN KEY(parent) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE tags(tag_id INTEGER PRIMARY KEY, entry_id INTEGER NOT NULL, tag TEXT NOT NULL, '
                   'FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    connection.close()


def get_date(entry):
    return entry['date']


class DatabaseManager:
    def __init__(self, database: str = '') -> None:
        if database == '':
            database = 'jurnl.sqlite'
        if exists(database):
            try:
                self.connection = sqlite3.connect(database)
                self.cursor = self.connection.cursor()
            except sqlite3.Error as detail:
                print('Error connecting to database:', detail)
        else:
            create_database(database)
            self.connection = sqlite3.connect(database)
            self.cursor = self.connection.cursor()

        self._default_format_ = '%Y-%m-%d %H:%M'

    def set_date_format(self, f_str: str):
        self._default_format_ = f_str

    def close_connection(self):
        self.connection.close()

    """---------------------------------Update Methods----------------------------------"""

    def update_date(self, entry_id: int, date: datetime = None):
        if not date:
            date = datetime.now()
        self.cursor.execute('UPDATE dates SET year=?,month=?,day=?,hour=?,minute=?,weekday=?,string=?'
                            'WHERE entry_id=?',
                            (date.year, date.month, date.day, date.hour, date.minute, date.weekday(),
                             date.strftime(self._default_format_), entry_id))
        self.connection.commit()
        return entry_id

    def update_body(self, entry_id, body):
        self.cursor.execute('UPDATE bodies SET body=? WHERE entry_id=?', (body, entry_id))
        self.connection.commit()
        return entry_id

    def update_tags(self, entry_id: int, tags: list = None):
        entry_tags = set(self.get_tags_by_entry_id(entry_id))
        if not tags:
            tags = set()
        else:
            tags = set(tags)
        if len(tags) > len(entry_tags):
            temp = tags.difference(entry_tags)
            for tag in temp:
                self.cursor.execute('INSERT INTO tags(entry_id,tag) VALUES(?,?)', (entry_id, tag))
        elif len(tags) < len(entry_tags):
            temp = entry_tags.difference(tags)
            for tag in temp:
                self.cursor.execute('DELETE FROM tags WHERE entry_id=? AND tag=?', (entry_id, tag))
        else:
            temp = tags.symmetric_difference(entry_tags)
            for tag in temp:
                if tag in tags:
                    self.cursor.execute('INSERT INTO tags(entry_id,tag) VALUES(?,?)', (entry_id, tag))
                else:
                    self.cursor.execute('DELETE FROM tags WHERE entry_id=? AND tag=?', (entry_id, tag))
        self.connection.commit()
        return entry_id

    def update_attachments(self, entry_id: int, attachments: list = None):
        """
        Takes a list of paths
        @param entry_id: int
        @param attachments: list
        @return: entry_id
        """
        if attachments:
            for path in attachments:
                name = basename(path)
                with open(path, 'rb') as f:
                    bytestream = f.read()
                now = datetime.now()
                self.cursor.execute('INSERT INTO attachments(entry_id,filename,file,added) VALUES (?,?,?,?)',
                                    (entry_id, name, bytestream, now.strftime('%Y-%m-%d %H:%M')))
                self.connection.commit()
            return entry_id

    def update_relations(self, child: int, parent: int):
        pairs = self.cursor.execute('SELECT child,parent FROM relations')
        if (child, parent) not in pairs and child != parent:
            self.cursor.execute('INSERT INTO relations(child,parent) VALUES (?,?)', (child, parent))
            self.connection.commit()
        return child, parent

    def upsert_entry(self, entry_id: int = -1, body: str = '', date: datetime = None, tags: list = None,
                     attachments: list = None, parent_id: int = -1, **kwargs):
        """attachments is a list of path objects"""
        if entry_id == -1:
            self.cursor.execute('INSERT INTO bodies(body) VALUES(?)', (body,))
            entry_id = self.cursor.lastrowid
            if not date:
                date = datetime.now()
            self.cursor.execute('INSERT INTO dates(entry_id,year,month,day,hour,minute,weekday,string) '
                                'VALUES(?,?,?,?,?,?,?,?)', (entry_id, date.year, date.month, date.day, date.hour,
                                                            date.minute, date.weekday(),
                                                            date.strftime(self._default_format_)))
            if tags:
                for tag in tags:
                    self.cursor.execute('INSERT INTO tags(entry_id,tag) VALUES(?,?)', (entry_id, tag))
            if attachments:
                self.update_attachments(entry_id, attachments)
            if parent_id != -1:
                self.update_relations(entry_id, parent_id)
        else:
            self.update_date(entry_id, date)
            self.update_body(entry_id, body)
            self.update_tags(entry_id, tags)
            self.update_attachments(entry_id, attachments)
        self.update_last_edit(entry_id, datetime.now())
        self.connection.commit()
        return entry_id

    def update_last_edit(self, entry_id, date: datetime = None):
        if not date:
            date = datetime.now()
        self.cursor.execute('UPDATE dates SET last_edit=? WHERE entry_id=?', (date.strftime(self._default_format_),
                                                                              entry_id))
        self.connection.commit()

    """---------------------------------Delete Methods----------------------------------"""

    def delete_entry_by_id(self, entry_id):
        self.cursor.execute('DELETE FROM bodies WHERE entry_id=?', (entry_id,))
        self.cursor.execute('DELETE FROM dates WHERE entry_id=?', (entry_id,))
        self.cursor.execute('DELETE FROM tags WHERE entry_id=?', (entry_id,))
        self.cursor.execute('DELETE FROM attachments WHERE entry_id=?', (entry_id,))
        self.cursor.execute('DELETE FROM relations WHERE child=? OR parent=?', (entry_id, entry_id))
        self.connection.commit()

    def delete_tag_by_id(self, entry_id, tag=None):
        if tag:
            self.cursor.execute('DELETE FROM tags WHERE entry_id=? AND path=?', (entry_id, tag))
        else:
            self.cursor.execute('DELETE FROM tags WHERE entry_id=?', (entry_id,))
        self.connection.commit()

    def delete_attachments_from_att_id(self, att_id):
        self.cursor.execute('DELETE FROM attachments WHERE att_id=?', (att_id,))
        self.connection.commit()

    def delete_relation_by_id_and_position(self, entry_id: int, position: str):
        if position is 'child':
            self.cursor.execute('DELETE FROM relations WHERE child=?', (entry_id,))
        elif position is 'parent':
            self.cursor.execute('DELETE FROM relations WHERE parent=?', (entry_id,))
        self.connection.commit()

    """---------------------------------Get entry_id Methods----------------------------------"""

    def get_entry_id_of_most_recent_entry(self):
        self.cursor.execute('SELECT entry_id FROM bodies WHERE rowid=(SELECT MAX(rowid) FROM bodies)')
        entry_id = self.cursor.fetchone()[0]
        return entry_id

    # TODO improve computation time
    def get_entry_ids_from_tags(self, tags: list, op_type: str = 'Contains One Of...', **kwargs):
        ids = []
        if tags:
            if op_type == 'Contains At Least...':
                tag = tags.pop(0)
                sql = 'SELECT entry_id FROM tags WHERE path=?'
                self.cursor.execute(sql, (tag,))
                temp = set(self.cursor.fetchall())
                for tag in tags:
                    self.cursor.execute(sql, (tag,))
                    temp = temp.intersection(self.cursor.fetchall())
                ids = [i[0] for i in temp]
            if op_type == 'Contains Only...':
                t1 = self.get_all_entry_ids()
                for item in t1:
                    if len(self.get_tags_by_entry_id(item)) == len(tags):
                        if set(self.get_tags_by_entry_id(item)).intersection(set(tags)) == set(tags):
                            ids.append(item)
            if op_type == 'Contains One Of...':
                sql = 'SELECT entry_id FROM tags WHERE path IN ({})'.format(','.join(['?'] * len(tags)))
                self.cursor.execute(sql, tags)
                temp = set()
                for item in self.cursor.fetchall():
                    temp.add(item[0])
                ids = list(temp)
        return ids

    def get_entry_id_of_untagged_entries(self):
        all_entries = set(self.get_all_entry_ids())
        all_tagged_entries = set([i[0] for i in self.cursor.execute('SELECT entry_id FROM tags')])
        ids = list(all_entries.difference(all_tagged_entries))
        return ids

    def get_entry_ids_from_attachments(self):
        ids = []
        self.cursor.execute('SELECT entry_id FROM attachments')
        for entry_id in self.cursor:
            ids.append(entry_id[0])
        return ids

    def get_entry_ids_from_body(self, search_string: str):
        ids = []
        if search_string == '':
            self.cursor.execute('SELECT entry_id FROM bodies WHERE body=?', (search_string,))
        else:
            self.cursor.execute('SELECT entry_id FROM bodies WHERE body LIKE ?', ('%' + search_string + '%',))
        for i in self.cursor:
            ids.append(i[0])
        return ids

    def get_entry_ids_from_date(self, **kwargs):
        if kwargs['date_sort_method'] == 'continuous':
            return self.get_entry_ids_from_continuous_range(**kwargs)
        else:
            return self.get_entry_ids_from_interval_ranges(**kwargs)

    def get_entry_ids_from_continuous_range(self, lower: datetime, upper: datetime):
        """lower and upper are datetime objects representing dates, where lower is earlier than upper"""
        ids = []
        self.cursor.execute('SELECT entry_id FROM dates WHERE string BETWEEN ? AND ?',
                            (lower.strftime('%Y-%m-%d %H:%M'), upper.strftime('%Y-%m-%d %H:%M')))
        for item in self.cursor:
            ids.append(item[0])
        return ids

    def get_entry_ids_from_interval_ranges(self, year: tuple = None, month: tuple = None, day: tuple = None,
                                           hour: tuple = None, minute: tuple = None, weekday: tuple = None, **kwargs):
        ids = []
        year_range = self.get_year_range() if not year else year
        month_range = [1, 12] if not month else month
        day_range = [1, 31] if not day else day
        hour_range = [0, 23] if not hour else hour
        minute_range = [0, 59] if not minute else minute
        weekday_range = [0, 6] if not weekday else weekday
        self.cursor.execute('SELECT entry_id from dates WHERE (year BETWEEN ? AND ?) AND (month BETWEEN ? AND ?) AND '
                            '(day BETWEEN ? AND ?) AND (hour BETWEEN ? AND ?) AND (minute BETWEEN ? AND ?) AND '
                            '(weekday BETWEEN ? AND ?)',
                            (year_range[0], year_range[1], month_range[0], month_range[1], day_range[0], day_range[1],
                             hour_range[0], hour_range[1], minute_range[0], minute_range[1], weekday_range[0],
                             weekday_range[1]))
        for entry_id in self.cursor:
            ids.append(entry_id[0])
        return ids

    def get_entry_ids_from_filtered_attributes(self, **kwargs):
        def get_datetime(entry_id):
            return self.get_date_by_entry_id(entry_id)

        filtered_ids = set(self.get_all_entry_ids())
        if 'parent' in kwargs and kwargs['parent']:
            has_parent_ids = set(self.get_entry_ids_of_all_children())
            filtered_ids = filtered_ids.intersection(has_parent_ids)
        if 'child' in kwargs and kwargs['child']:
            has_child_ids = set(self.get_entry_ids_of_all_parents())
            filtered_ids = filtered_ids.intersection(has_child_ids)
        if 'attachments' in kwargs and kwargs['attachments']:
            has_attachments_ids = set(self.get_entry_ids_from_attachments())
            filtered_ids = filtered_ids.intersection(has_attachments_ids)
        if 'body' in kwargs and kwargs['body'] is not None:
            has_attachments_ids = set(self.get_entry_ids_from_body(kwargs['body']))
            filtered_ids = filtered_ids.intersection(has_attachments_ids)
        filtered_ids = list(filtered_ids.intersection(set(self.get_entry_ids_from_tags(**kwargs))).intersection(
            set(self.get_entry_ids_from_date(**kwargs))))
        filtered_ids.sort(key=get_datetime)
        return filtered_ids

    def get_all_entry_ids(self, ordered=True):
        def get_datetime(item):
            return item[1]

        ids = []
        self.cursor.execute('SELECT entry_id FROM bodies')
        for i in self.cursor:
            ids.append(i[0])
        if ordered:
            temp = list()
            for i in ids:
                temp.append([i, self.get_date_by_entry_id(i)])
            temp.sort(key=get_datetime)
            ids.clear()
            for i in temp:
                ids.append(i[0])
        return ids

    """---------------------------------Get Field Methods----------------------------------"""

    def get_body_by_entry_id(self, entry_id):
        self.cursor.execute('SELECT body FROM bodies WHERE entry_id=?', (entry_id,))
        body = self.cursor.fetchone()[0]
        return body

    def get_date_by_entry_id(self, entry_id, format_str=None):
        """if provided with a format, returns a string; else returns a datetime object"""
        self.cursor.execute('SELECT year,month,day,hour,minute FROM dates WHERE entry_id=?', (entry_id,))
        temp = self.cursor.fetchone()
        date = datetime(temp[0], temp[1], temp[2], temp[3], temp[4])
        if format_str:
            date = date.strftime(format_str)
        return date

    def get_all_datetimes(self):
        ids = self.get_all_entry_ids()
        dates = []
        for entry_id in ids:
            dates.append(self.get_date_by_entry_id(entry_id))
        dates.sort()
        return dates

    def get_tags_by_entry_id(self, entry_id):
        tags = list()
        self.cursor.execute('SELECT tag FROM tags WHERE entry_id=?', (entry_id,))
        for item in self.cursor:
            tags.append(item[0])
        tags.sort()
        return tags

    def get_all_tags(self):
        tags = set()
        self.cursor.execute('SELECT tag FROM tags')
        for tag in self.cursor:
            tags.add(tag[0])
        tags = list(tags)
        tags.sort()
        return tags

    def get_tags_by_date_range(self, range_type='continuous', **kwargs):
        tags = set()
        if range_type == 'interval':
            ids = self.get_entry_ids_from_interval_ranges(**kwargs)
        else:
            ids = self.get_entry_ids_from_continuous_range(**kwargs)
        for entry_id in ids:
            for tag in self.get_tags_by_entry_id(entry_id):
                tags.add(tag)
        tags = list(tags)
        tags.sort()
        return tags

    def get_attachment_from_att_id(self, att_id):
        self.cursor.execute('SELECT file FROM attachments WHERE att_id=?', (att_id,))
        attachment = self.cursor.fetchone()[0]
        return attachment

    def get_attachment_name_from_att_id(self, att_id):
        self.cursor.execute('SELECT filename FROM attachments WHERE att_id=?', (att_id,))
        name = self.cursor.fetchone()[0]
        return name

    def get_att_ids_from_entry_id(self, entry_id):
        self.cursor.execute('SELECT att_id FROM attachments WHERE entry_id=?', (entry_id,))
        ids = [x[0] for x in self.cursor.fetchall()]
        return ids

    def get_all_attachment_data_from_entry_id(self, entry_id):
        def sort_by_added(a):
            return a['added']

        self.cursor.execute('SELECT att_id, filename, added FROM attachments WHERE entry_id=?', (entry_id,))
        attachments = [{'att_id': tup[0], 'filename': tup[1], 'added': tup[2]} for tup in self.cursor.fetchall()]
        attachments.sort(key=sort_by_added)
        return attachments

    def get_children_by_entry_id(self, parent_id, reverse=False):
        temp = dict()
        self.cursor.execute('SELECT child FROM relations WHERE parent=?', (parent_id,))
        for i in self.cursor.fetchall():
            temp[i[0]] = self.get_date_by_entry_id(i[0])
        sorted_values = sorted(temp.items(), key=lambda kv: kv[1], reverse=reverse)
        children = [x[0] for x in sorted_values]
        return children

    def get_parent_by_entry_id(self, child_id):
        self.cursor.execute('SELECT parent FROM relations WHERE child=?', (child_id,))
        parent = -1
        temp = self.cursor.fetchone()
        if temp:
            parent = temp[0]
        return parent

    def get_entry_ids_of_all_children(self, reverse=False):
        self.cursor.execute('SELECT child FROM relations ')
        temp = dict()
        for tup in self.cursor.fetchall():
            temp[tup[0]] = self.get_date_by_entry_id(tup[0])
        sorted_values = sorted(temp.items(), key=lambda kv: kv[1], reverse=reverse)
        ids = [x[0] for x in sorted_values]
        return ids

    def get_entry_ids_of_all_parents(self, reverse=False):
        self.cursor.execute('SELECT parent FROM relations ')
        temp = dict()
        for tup in self.cursor.fetchall():
            temp[tup[0]] = self.get_date_by_entry_id(tup[0])
        sorted_values = sorted(temp.items(), key=lambda kv: kv[1], reverse=reverse)
        ids = [x[0] for x in sorted_values]
        return ids

    def get_entry_from_entry_id(self, entry_id):
        entry = dict()
        entry['entry_id'] = entry_id
        entry['body'] = self.get_body_by_entry_id(entry_id)
        entry['date'] = self.get_date_by_entry_id(entry_id)
        entry['tags'] = self.get_tags_by_entry_id(entry_id)
        entry['attachments'] = self.get_all_attachment_data_from_entry_id(entry_id)
        entry['parent_id'] = self.get_parent_by_entry_id(entry_id)
        entry['children'] = self.get_children_by_entry_id(entry_id)
        return entry

    def get_entries_from_continuous_range(self, lower, upper, reverse=False):
        """lower and upper are datetime objects, where lower is earlier than upper"""
        ids = self.get_entry_ids_from_continuous_range(lower, upper)
        entries = []
        for eid in ids:
            entries.append(self.get_entry_from_entry_id(eid))
        entries.sort(reverse=reverse, key=get_date)
        return entries

    def get_entries_from_interval_ranges(self, year: list = None, month: list = None, day: list = None,
                                         hour: list = None, minute: list = None, reverse=False):
        ids = self.get_entry_ids_from_interval_ranges(year, month, day, hour, minute)
        entries = []
        for entry_id in ids:
            entries.append(self.get_entry_from_entry_id(entry_id))
        entries.sort(reverse=reverse, key=get_date)
        return entries

    def get_entries_from_filtered_attributes(self, **kwargs):
        filtered_ids = self.get_entry_ids_from_filtered_attributes(**kwargs)
        entries = self.get_multiple_entries(filtered_ids)
        return entries

    def get_multiple_entries(self, ids: list = None, reverse=False):
        if not ids:
            ids = list()
        entries = []
        for entry_id in ids:
            entries.append(self.get_entry_from_entry_id(entry_id))
        entries.sort(reverse=reverse, key=get_date)
        return entries

    """---------------------------------Stats Methods----------------------------------"""

    def get_number_of_entries(self) -> int:
        self.cursor.execute('SELECT COUNT() FROM bodies')
        number = self.cursor.fetchone()[0]
        return number

    def get_year_range(self):
        self.cursor.execute('SELECT MAX(year),MIN(year) FROM dates')
        (high, low) = self.cursor.fetchone()
        return [low, high]

    def get_years(self):
        years = set()
        self.cursor.execute('SELECT year FROM dates')
        for item in self.cursor:
            years.add(item[0])
        years = list(years)
        years.sort()
        return years

    def get_stats_and_entry_ids_from_filters(self, **kwargs):
        ids = self.get_entry_ids_from_filtered_attributes(**kwargs)
        tags = [{i: self.get_tags_by_entry_id(i)} for i in ids]
        dates = [self.get_date_by_entry_id(i) for i in ids]
        stats = {'tagged_ids': tags, 'dates': dates, 'filters': kwargs}
        return ids, stats
