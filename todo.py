import sqlite3
import argparse
from colorama import init, deinit, Fore, Back, Style
import re
import datetime

init()

parser = argparse.ArgumentParser(description = "To-do list")
parser.add_argument('-m', '--method', dest = "method", help = "Method to be performed")
parser.add_argument('-n', '--name', dest = "topic", help = "The name of the tasks")
parser.add_argument('-s', '--subject', dest = "subject", help = "Subject to which Topic belong to")
parser.add_argument('-st', '--status', dest = "status", help = "Completed(1) or Not Complemted(0) For Code")
parser.add_argument('-o', '--open', dest = "Filename", help = "To open a new file if present, if not present create new file")
arg = parser.parse_args()

if '.' in arg.Filename:
    arg.Filename = Filename.split(".")[0]

flag = 0
fh = open("toDoListNames.txt")
for line in fh:
    if arg.Filename in line :
        flag = 1
        break
fh.close()

if (flag == 0):
    fh = open("toDoListNames.txt", 'a')
    fh.write(arg.Filename)
    fh.close()

conn = sqlite3.connect(arg.Filename + '.sqlite')
cur = conn.cursor()


cur.executescript('''
CREATE TABLE IF NOT EXISTS todo
(
    Topic TEXT,
    status_id INTEGER,
    subject_id INTEGER,
    assigned_date INTEGER,
    submission_date INTEGER,
    UNIQUE(Topic, subject_id)
);

CREATE TABLE IF NOT EXISTS Subjects
(   id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    subject TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Status
(
    id INTEGER NOT NULL PRIMARY KEY UNIQUE,
    txt TEXT UNIQUE
);

INSERT OR IGNORE INTO Status(id, txt) VALUES(0, "InCompleted");
INSERT OR IGNORE INTO Status(id, txt) VALUES(1, "Completed Practical");
INSERT OR IGNORE INTO Status(id, txt) VALUES(2, "Completed Writeup");
INSERT OR IGNORE INTO Status(id, txt) VALUES(3, "Completed");
INSERT OR IGNORE INTO Status(id, txt) VALUES(4, "Submitted")
''')

def getDate():
    pattern = '^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}'
    while True:
        date = input("Enter submission date details(or 'quit' to quit): ")
        if date =="quit":
            quit()
        m = re.fullmatch(pattern, date)
        if m is None:
            print("Wrong pattern..Please try Again")
        else:
            year, month, day = map(int, date.split("-"))
            x = datetime.date(year, month, day)
            return x

def noOfDays(month):
    if month == 2:
        return 28
    elif month%2==1:
        return 31
    else:
        return 30

def check(submissionDate, status = 0):
    dateToday = datetime.date.today()
    submissionDate = submissionDate.split("-")
    if status != 'Submitted':
        daysLeft = (int(submissionDate[2]) - dateToday.day) + ((int(submissionDate[1])-dateToday.month)*noOfDays(dateToday.month))
        if daysLeft <= 5 and daysLeft > 2:
            return 1
        elif daysLeft <=2:
            return 0
        else:
            return 3
    else:
        return 2

def getId(subject):
    cur.execute('SELECT id FROM Subjects WHERE subject = ?', (subject, ))
    subject_id = cur.fetchone()[0]
    return subject_id

def add(topic, subject, status):
    cur.execute('INSERT OR IGNORE INTO Subjects(subject) VALUES (?)', (subject, ))
    subject_id = getId(subject)
    print(subject_id)
    assignedDate = datetime.date.today()
    submissiondate = getDate()
    cur.execute('INSERT OR IGNORE INTO todo (Topic, status_id, subject_id, assigned_date, submission_date) VALUES (?, ?, ?, ?, ?)', (topic, status, subject_id, assignedDate, submissiondate))
    conn.commit()

def change_status(topic, subject, status):
    subject_id = getId(subject)
    cur.execute('UPDATE todo SET status_id = ? WHERE Topic = ? AND subject_id = ?', (status, topic, subject_id))

def remove(topic, subject):
    subject_id = getId(subject)
    cur.execute('DELETE FROM todo WHERE Topic = ? AND subject_id = ?', (topic, subject_id))

def printTable(result):
    dash = '-' * 65
    print(dash)
    print('{:^15s} {:<7s} {:^22s} {:>14s}'.format('TOPIC',  'SUBJECT', 'STATUS', 'SUBMISSION DATE'))
    print(dash)
    for row in result:
        # print(row)
        if check(row[3], row[2])==0:
            print(Fore.RED, end='')
        elif check(row[3], row[2])==1:
            print(Fore.YELLOW, end='')
        elif check(row[3], row[2])==2:
            print(Fore.GREEN, end='')
        print('{:^15s} {:^7s} {:^22s} {:^14s}'.format(row[0], row[1], row[2], row[3]))
        print(Style.RESET_ALL, end='')

def display(topic, subject, status):
    print(end='\n\n')
    mainStatement = """SELECT todo.Topic, Subjects.subject, Status.txt, todo.submission_date
                FROM todo JOIN Subjects JOIN Status
                ON todo.subject_id = Subjects.id AND todo.status_id = Status.id """
    if subject and status:
        subject_id = getId(subject)
        cur.execute(mainStatement + """WHERE todo.subject_id=? AND todo.status_id=?""", (subject_id, status))
    elif subject:
        subject_id = getId(subject)
        cur.execute(mainStatement + """WHERE todo.subject_id=?""", (subject_id, ))
    elif status:
        cur.execute(mainStatement + """WHERE todo.status_id=?""", (status, ))
    else:
        cur.execute(mainStatement);
    result = cur.fetchall()
    if result:
        printTable(result)
    else:
        print("No Tasks left")


def displayFiles():
    fh = open("filename.txt")
    for line in fh:
        print(line, end='')
    fh.close()

method, topic, subject, status = arg.method, arg.topic, arg.subject, arg.status

# Calling the appropiate functions based on the method passed
if method == "add": add(topic, subject, status)
elif method == "change_status": change_status(topic, subject, status)
elif method == "rem" : remove(topic, subject)
elif method == "display" : display(topic, subject, status)
elif method == "displayFile" : displayFiles()
else: print("Wrong method argument")
conn.commit()
deinit()
