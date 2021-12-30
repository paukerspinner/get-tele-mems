import re
import csv
import os

def saveMemberList(members, group):
    with open("data/members/" + re.sub("-+","-",re.sub("[^a-zA-Z]","-",str.lower(group.title))) + ".csv","w",encoding='UTF-8') as f:
        writer = csv.writer(f,delimiter=",",lineterminator="\n")
        writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
        for user in members:
            username = user.username or ''
            firstname = user.first_name or ''
            lastname = user.last_name or ''
            name = (firstname + ' ' + lastname).strip()
            writer.writerow([username,user.id,user.access_hash,name,group.title, group.id])      
    print('Members scraped successfully.')

def deleteFromCsvFile(dir, filename, numberDelete, deleteFrom=1):
    with open(dir + '/' + filename, "r", encoding='UTF-8') as fread:
        rows = list(csv.reader(fread))
        seletedRows = rows[:deleteFrom] + rows[deleteFrom+numberDelete:]
    
        with open(dir + '/' + 'new-' + filename, "w", encoding='UTF-8') as fwrite:
            writer = csv.writer(fwrite)
            for row in seletedRows:
                writer.writerow(row)
    
    os.remove(dir + '/' + filename)
    os.rename(dir + '/' + 'new-' + filename, dir + '/' + filename)