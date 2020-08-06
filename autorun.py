from copy import deepcopy
from os import listdir, remove, chdir
from os.path import exists, abspath
from database_info import DatabaseManager

from dateutil.parser import parse


class AutoRunModule:

    def __init__(self, database: DatabaseManager = None):
        self.database = DatabaseManager() if not database else database

    def import_remote_entries(self):
        # with open('rsync.conf') as file:
        #     cmd = file.read().splitlines()
        #     file.close()
        # call(cmd)
        chdir(self.storage.settings['imports location'])
        files = listdir()
        entries = [x for x in files if '.mji' in x]
        if len(entries) > 0:
            errors = []
            for file in entries:
                with open(file) as fstream:
                    entry = fstream.read()
                    fstream.close()
                temp = entry.split('<DATE>')
                temp = temp[1].split('<BODY>')
                date = parse(temp[0].strip())
                temp = temp[1].split('<TAGS>')
                body = temp[0].strip()
                temp = temp[1].split('<ATTACHMENTS>')
                tags = temp[0].strip()
                tags = tags.split(',')
                for i in range(len(tags)):
                    tags[i] = tags[i].strip()
                attachments = temp[1].strip()
                attachments = attachments.split(',')
                attachments = list(filter(None, attachments))
                for i in range(len(attachments)):
                    attachments[i] = abspath(attachments[i].strip())
                temp = deepcopy(attachments)
                for att in temp:
                    if not exists(att):
                        attachments.remove(att)
                        errors.append(att)
                self.database.upsert_entry(body=body, date=date, tags=tags, attachments=attachments)
                remove(file)
                for att in attachments:
                    remove(att)


autorun = AutoRunModule()
autorun.import_remote_entries()
