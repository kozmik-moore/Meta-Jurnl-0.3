"""A test script for the writer module"""
from datetime import datetime

from dateutil.parser import parse

from database import get_all_entry_ids
from writer import Writer
from random import randint


def print_break(message: str = ''):
    print('\n', end='')
    if message:
        print(message)
    print('\n', end='')


def read_entry(w: Writer):
    print_break()
    print('Entry: ', w.writer_id)
    print('Body: ', w.body)
    print('Date: ', w.date)
    print('Last edited: ', w.get_date_last_edited)
    print('Tags: ', w.tags)
    if w.has_attachments:
        print('Attachments: ', w.attachments)
    if w.has_parent:
        print('Parent: ', w.parent)
    if w.has_children:
        print('Children: ', w.get_children)
    choice = input('\nPress \'c\' to continue or \'l\' to create a link\t')
    if choice == 'l':
        id_ = w.reader_id
        w.reset()
        w.parent = id_
        edit_entry(w)
    print_break()


def edit_entry(w: Writer):
    p = 'Select from the following:\n' \
        '  (b)ody\n' \
        '  (d)ate\n' \
        '  (t)ags\n' \
        '  (a)ttachments\n' \
        '  (s)ave changes\n' \
        '  (f)inish editing\t'
    choice = input(p)
    while choice not in ['f']:
        if choice in ['b', 'd', 't', 'a', 's']:
            if choice == 'b':
                w.body = input('Enter some text for the body: ')
                print_break()
            if choice == 'd':
                date = input('Enter the date (format: \'YYYY-MM-DD HH:MM\' or \'n\' for now: ')
                date = datetime.now() if date in ['n', ''] else parse(date)
                w.date = date
                print_break()
            if choice == 't':
                tags = input('Enter tags, separated by commas: ')
                tags = tuple(x.strip() for x in tags.split(',')) if tags else ()
                w.tags = tags
                print_break()
            if choice == 'a':
                attachments = input('Enter attachments as path-strings, separated by commas: ')
                attachments = tuple(x.strip() for x in attachments.split(',')) if attachments else ()
                w.attachments = attachments
                print_break()
            if choice == 's':
                if w.changes:
                    w.write_to_database()
                    print_break('Saved')
                else:
                    print_break('Nothing to save')
        else:
            print_break('Invalid option')
        choice = input(p)
    if w.changes:
        choice = input('There are unsaved changes. Do you want to save them? ')
        if choice in ['y', 'yes', 'Y', 'Yes']:
            w.write_to_database()
            print_break('Saved')
    print_break()


def delete_entry(w: Writer):
    choice = input('Are you sure you want to delete this entry? ')
    if choice in ['yes', 'y', 'Yes', 'Y', 'YES']:
        w.remove_from_database()
        print_break('Entry removed')
    else:
        print_break()


def exit_(w: Writer):
    salute = [
        'See You Space Cowboy...',
        'You\'re Gonna Carry That Weight.'
    ]
    print_break(salute[randint(0, len(salute) - 1)])
    w.close_database()


def run():
    b = Writer()
    print('\n')
    p1 = 'Select an option:\n' \
         '  (a)ll entries\n' \
         '  (r)ead\n' \
         '  (c)reate\n' \
         '  (e)dit\n' \
         '  (d)elete\n' \
         '  (q)uit\t'
    choice = input(p1)
    while choice != 'q':
        print_break()
        if choice in ['a', 'r', 'c', 'e', 'd']:
            if choice == 'a':
                print(get_all_entry_ids())
                print_break()
            if choice == 'c':
                b.reset()
                edit_entry(b)
                print_break()
            if choice in ['e', 'r', 'd']:
                p2 = 'Select an entry to {}\n' \
                     '(Type \'cancel\' to return to previous menu):\t'.format(
                        {'r': 'read', 'e': 'edit', 'd': 'delete'}[choice])
                c = input(p2)
                print_break()
                while c != 'cancel':
                    try:
                        id_ = int(c)
                        if id_ in get_all_entry_ids(b.connection):
                            b.writer_id = id_
                            if choice == 'r':
                                read_entry(b)
                            elif choice == 'e':
                                edit_entry(b)
                            else:
                                delete_entry(b)
                            c = 'cancel'
                        else:
                            print_break('Entry does not exist')
                    except ValueError:
                        print_break('Not a valid entry')
                    if c != 'cancel':
                        c = input('Select an entry to view:\n'
                                  '(Type \'cancel\' to return to previous menu): ')
        choice = input(p1)
    exit_(b)


run()
