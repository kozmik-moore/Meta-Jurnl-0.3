from reader import Reader
from writer import Writer

# a = Reader()
# a.current_entry = 2
# print(a.attachments)
# print(a.has_attachments)
# a.current_entry = 6
# print(a.attachments)
# print(a.has_attachments)
# a.current_entry = 2
# print(a.attachments)
# print(a.has_attachments)
# a.current_entry = 6
# print(a.attachments)
# print(a.has_attachments)

b = Writer()
b.current_entry = 6
print(b.current_entry)
print(b.tags)
print(b.attachments)
print(b.date)
print(b.changes)
b.body = 'A new test'
c = super(Writer, b)
c.has_attachments = False
print(c.has_attachments)



# a.close_database()
