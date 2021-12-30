from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, UserChannelsTooMuchError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import UserStatusOnline, UserStatusOffline, ContactStatus, UserStatusLastMonth
import sys
import csv
import traceback
import time
import random
import re
import db
import utils
import argparse
import datetime
from config import *

class Telebot():
    def __init__(self, phoneNum, apiId, apiHash):
        self.__setAccount(phoneNum, apiId, apiHash)
    
    def __setAccount(self, phoneNum, apiId, apiHash):
        try:
            self.client = TelegramClient( './sessions/' + phoneNum, apiId, apiHash)
            self.client.connect()
            if not self.client.is_user_authorized():
                self.client.send_code_request(phoneNum)
                self.client.sign_in(phoneNum, input('Enter verifiy code: '))
        except Exception as err:
            print(err)

    def selectGroup(self, title):
        chats = []
        last_date = None
        chunk_size = 10
        groups=[]

        result = self.client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash = 0
        ))
        chats.extend(result.chats)

        for chat in chats:
            try:
                if chat.megagroup== True: # CONDITION TO ONLY LIST MEGA GROUPS.
                    groups.append(chat)
            except:
                continue

        print(title)
        i=0
        for g in groups:
            print(str(i) + '- ' + g.title)
            i+=1
        
        selectedGroupIdx = int(input('Enter a number: '))
        return groups[selectedGroupIdx]

    # verifiedTime = contract[2] # datetime.datetime.strptime(contract[2],'%Y-%m-%d %H:%M:%S')
    # now = datetime.datetime.utcnow()
    # difftime = (now - verifiedTime).total_seconds()

    def fetchMembersFromGroup(self, group, exceptFirstUsers):
        members = self.client.get_participants(group, aggressive=True)
        # print(members[0].status.was_online)
        print(len(members))
        inactiveMembers = []
        for member in members:
            if isinstance(member.status, UserStatusOffline):
                wasOnlineTime = member.status.was_online
                now = datetime.datetime.now(datetime.timezone.utc)
                difftime = (now - wasOnlineTime).total_seconds()
                if difftime >= LIMIT_TIME * 24 * 60 * 60:
                    if member.username:
                        inactiveMembers.append(member)
                    print(member.status.was_online)
            if isinstance(member.status, UserStatusLastMonth):
                if member.username:
                    inactiveMembers.append(member)
            # print(time.ctime())
        return inactiveMembers

    def addUserToGroup(self, user, group):
        try:
            userEntity = InputPeerUser(user['id'], user['access_hash'])
            groupEntity = InputPeerChannel(group.id, group.access_hash)
            self.client(InviteToChannelRequest(groupEntity, [userEntity]))
            print('Successfully added', user['id'], user['username'])
            time.sleep(60)
            return True
        except PeerFloodError:
            print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
            print("Next account, please!")
        except UserPrivacyRestrictedError:
            print("The user's privacy settings do not allow you to do this. Skipping.")
        except UserChannelsTooMuchError:
            print("This user is already in too many channels/groups.")
        except Exception as error:
            print(error)
        return False

    def saveMemberList(self, members, fromGroup):
        db.saveMemberList(members, fromGroup)

    def addUsersToGroup(self, fileImport, toGroup, limit):
        users = []
        with open('./data/members/' + fileImport, encoding='UTF-8') as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user['username'] = row[0]
                try:
                    user['id'] = int(row[1])
                    user['access_hash'] = int(row[2])
                except IndexError:
                    print('Users without id or access_hash')
                users.append(user)

        addedCount = 0
        idxUser = 0
        while addedCount < limit and idxUser < len(users):
            user = users[idxUser]
            try:
                userEntity = InputPeerUser(user['id'], user['access_hash'])
                groupEntity = InputPeerChannel(toGroup.id, toGroup.access_hash)
                self.client(InviteToChannelRequest(groupEntity, [userEntity]))
                print('Successfully added', user['id'], user['username'])
                addedCount += 1
                time.sleep(60)
            # except PeerFloodError:
            #     print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.", user['id'], user['username'])
            #     print("Next account, please!")
            #     break
            except UserPrivacyRestrictedError:
                print("The user's privacy settings do not allow you to do this. Skipping.", user['id'], user['username'])
            except UserChannelsTooMuchError:
                print("This user is already in too many channels/groups.", user['id'], user['username'])
            # except Exception as error:
            #     print(error, user['id'], user['username'])
            idxUser += 1
        db.deleteFromCsvFile('data/members', fileImport, idxUser)
        print('Success added %d/%d' % (addedCount, idxUser))