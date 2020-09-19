from datetime import datetime
from json import load, dump
from os import makedirs, scandir, remove
from os.path import exists, join

from configurations import imports_location, default_database
from writer import create_entry


def import_entries():
    """Imports journal entries ('.mjson' files) and their associated attachments and creates a new entry in the db

    """
    loc = imports_location()
    db = default_database()
    if not exists(loc):
        makedirs(loc)
    for file in scandir(loc):
        if '.mjson' in file.path:
            with open(file, 'r') as down:
                j = load(down)
                down.close()
                if not j['imported']:
                    try:
                        date = datetime.strptime(j['date'], '%Y-%m-%d-%H-%M-%S')
                    except ValueError:
                        date = datetime.now()
                    body = j['body']
                    tags = tuple(j['tags'])
                    attachments = j['attachments']
                    tmp = []
                    for att in attachments:
                        path = join(loc, att)
                        if exists(path):
                            tmp.append(path)
                    attachments = tuple(tmp)
                    create_entry(database=db, body=body, tags=tags, date=date, attachments=attachments)
                    j['imported'] = True
                    with open(file, 'w') as up:
                        dump(j, up)
                        up.close()


def delete_imports():
    """Deletes all import files and their associated attachments. Ignores all other files.

    """
    loc = imports_location()
    if not exists(loc):
        makedirs(loc)
    for file in scandir(loc):
        if '.mjson' in file.path:
            with open(file, 'r') as down:
                j = load(down)
                down.close()
                if j['imported']:
                    for att in j['attachments']:
                        try:
                            remove(join(loc, att))
                        except FileNotFoundError:
                            pass
                    remove(file)


def clean_imports_dir():
    """Removes all files in the imports directory

    """
    loc = imports_location()
    if not exists(loc):
        makedirs(loc)
    for file in scandir(loc):
        remove(file)
