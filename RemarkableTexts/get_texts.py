from imessage_reader import fetch_data
from datetime import datetime
from os.path import expanduser, getmtime
import time

# The path to the iMessage database
DB_PATH = expanduser("~") + "/Library/Messages/chat.db-wal"
mtime_last = 0

def print_new_texts():
    #grab texts (user id, message, date, service, account, is_from_me)
    fd = fetch_data.FetchData()
    messages = fd.get_messages()

    #sort by converted timestamp strings to datetime
    messages = sorted(messages, key=lambda tup: datetime.strptime(tup[2], '%Y-%m-%d %H:%M:%S'))
    print('---')
    for m in messages[-10:]:
        if m[5]:
            print(m[2] + ':' + m[1] + ' (TO ' + m[0] + ')')
        else:
            print(m[2] + ':' + m[1] + ' (FROM ' + m[0] + ')')

#check if database has changed
while True:
    time.sleep(5)
    mtime_cur = getmtime(DB_PATH)
    if mtime_cur != mtime_last:
        print_new_texts()
    else:
        print('no update')
    mtime_last = mtime_cur

