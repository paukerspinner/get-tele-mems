from telebot import *
from tkinter import *
from env import *

apiId = API_ID
apiHash = API_HASH
phoneNum = PHONE_NUMBER

def getMembers():
    fromGroup = telebot.selectGroup('Choose one of the following groups to scrape members:')
    exceptFirstUsers = int(input('How many first members you want to except: '))
    members = telebot.fetchMembersFromGroup(fromGroup, exceptFirstUsers)
    telebot.saveMemberList(members, fromGroup)

def addUsers():
    fileImport = utils.selectFileImport('Choose file to import users', './data/members', 'csv')
    toGroup = telebot.selectGroup('Choose a group to add members: ')
    limit = int(input('Enter number of users to add from import-file: '))
    telebot.addUsersToGroup(fileImport, toGroup, limit)

telebot = Telebot(phoneNum, apiId, apiHash)


parser = argparse.ArgumentParser()
parser.add_argument('-g', action='store_true', help='Get members from group and save to database')
parser.add_argument('-a', action='store_true', help='Add users from import-file to a group')
args = parser.parse_args()

if args.g:
    getMembers()
if args.a:
    addUsers()


def doSomething():
    print(a)

root = Tk()
a = StringVar()
Label(root, text='Choose a group to scrape members from:').pack()
Entry(root, textvariabl=a).pack()
Button(root, text='Enter', command=doSomething).pack()
