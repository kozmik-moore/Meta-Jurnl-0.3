from reader import Reader
from writer import Writer

# a = Reader()
# curs = 0
# while curs != 'q':
#     curs = input('Select and entry or type \'q\' to quit: ')
#     if curs != 'q':
#         a.current_entry = int(curs)
#         print('Entry: ', a.current_entry)
#         print('Body: ', a.body)
#         print('Date: ', a.date)
#         print('Last edited: ', a.date_last_edited)
#         print('Tags: ', a.tags)
#         if a.has_attachments:
#             print('Attachments: ', a.attachments)
#         if a.has_parent:
#             print('Parent: ', a.parent)
#         if a.has_children:
#             print('Children: ', a.children)
# a.close_database()

b = Writer()
curs = 0
while curs != 'q':
    curs = input('Select and entry or type \'q\' to quit: ')
    if curs != 'q':
        b.writer_entry = int(curs)
        print('Entry: ', b.writer_entry)
        print('Body: ', b.body)
        print('Date: ', b.date)
        print('Last edited: ', b.date_last_edited)
        print('Tags: ', b.tags)
        if b.has_attachments:
            print('Attachments: ', b.attachments)
        if b.has_parent:
            print('Parent: ', b.parent)
        if b.has_children:
            print('Children: ', b.children)
        b.body = 'A new test'
        print('Changes: ', b.changes)
        print('Body: ', b.body)
b.close_database()
