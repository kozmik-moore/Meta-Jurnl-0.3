from reader import Reader
from writer import Writer

a = Reader()
curs = 0
while curs != 'q':
    curs = input('Select and entry or type \'q\' to quit: ')
    if curs != 'q':
        a.current_entry = int(curs)
        print('Entry: ', a.current_entry)
        print('Body: ', a.body)
        print('Date: ', a.date)
        print('Last edited: ', a.date_last_edited)
        print('Tags: ', a.tags)
        if a.has_attachments:
            print('Attachments: ', a.attachments)
        if a.has_parent:
            print('Parent: ', a.parent)
        if a.has_children:
            print('Children: ', a.children)


# b = Writer()
# b.current_entry = 6
# print(b.current_entry)
# print(b.tags)
# print(b.attachments)
# print(b.date)
# print(b.changes)
# b.body = 'A new test'
# c = super(Writer, b)
# c.has_attachments = False
# print(c.has_attachments)


a.close_database()
# b.close_database()
