"""A test script for the writer module"""

from writer import Writer
from random import randint


def print_entry(w: Writer):
    print('Entry: ', w.id_)
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
    print(w.changes)
    print('--------')


b = Writer()
curs = input('Select an entry or type \'q\' to quit: ')
while curs != 'q':
    print('--------')
    try:
        curs = int(curs)
        if type(curs) == int and curs > 0:
            b.id_ = curs
            print_entry(b)
            # b.body = ''
            # b.tags = ('New Tag',)
            # print_entry(b)
        else:
            print('That is not a valid entry')
            print('--------')
    except ValueError:
        print('That is not a valid entry')
        print('--------')
    curs = input('Select an entry or type \'q\' to quit: ')
salute = [
    'See You Space Cowboy...',
    'You\'re Gonna Carry That Weight.'
]
print('--------')
print(salute[randint(0, len(salute) - 1)])
b.close_database()
