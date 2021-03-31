"""Functions for creating and manipulating the journal database"""
from sqlite3 import connect


# TODO add "last_access" to dates
def create_database(database: str) -> None:
    file = open(database, 'w+')
    file.close()
    connection = connect(database=database)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE bodies(entry_id INTEGER PRIMARY KEY, body TEXT)')
    cursor.execute('CREATE TABLE dates(entry_id INTEGER NOT NULL, created TIMESTAMP, last_edit TIMESTAMP, FOREIGN KEY('
                   'entry_id) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE attachments(att_id INTEGER PRIMARY KEY, entry_id INTEGER NOT NULL, '
                   'filename TEXT NOT NULL, file BLOB NOT NULL, added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, '
                   'FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE relations(rel_id INTEGER PRIMARY KEY, child INTEGER NOT NULL, '
                   'parent INTEGER NOT NULL,FOREIGN KEY(child) REFERENCES bodies(entry_id), '
                   'FOREIGN KEY(parent) REFERENCES bodies(entry_id))')
    cursor.execute('CREATE TABLE tags(tag_id INTEGER PRIMARY KEY, entry_id INTEGER NOT NULL, tag TEXT '
                   'DEFAULT \'(UNTAGGED)\', FOREIGN KEY(entry_id) REFERENCES bodies(entry_id))')
    connection.close()
