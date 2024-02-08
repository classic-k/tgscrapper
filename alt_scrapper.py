from telethon import TelegramClient #, sync
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.channels import InviteToChannelRequest
import getpass
import os
from dotenv import load_dotenv
import time
import asyncio
import json
import re

load_dotenv()


API_ID  = os.getenv("API_ID")#27830331 #1307728
API_HASH = os.getenv("API_HASH") #"4e7e94ade6b47dca634affc4478c3f63" #'0fdacb025cf6bfa8585007b565920454'
PHONE_NUM = os.getenv("PHONE_NUM") #'+2347033637812'
SLEEP_TIME = os.getenv("SLEEP_TIME")
CHAT_LINK ="https://t.me/solana" #"https://t.me/DUROMEDIA2"
New_Channel = "https://t.me/baleers"


async def connect():

    print("Running script")

    client = TelegramClient("anon", API_ID, API_HASH)
    
    if not await client.start(): #and await client.is_user_authorized():

        #tgClient = client
        print("Client is not ready to shoot, try again")
        return #client

    else:

        if not client.is_user_authorized:

            print("Authorizing user")
            if not PHONE_NUM:
                PHONE_NUM = input("Enter your number: ")
            client.sign_in(PHONE_NUM)
            current_user = None

            while not current_user:

                try:
                    code = input("Enter code you juse received")
                    current_user = client.sign_in(code=code)
                    print("Client activated")
                except Exception as error:
                    print("An error occur ",error)
                    pw = getpass.getpass("Enter password received on phone")
                    current_user = client.sign_in(password=pw)
                    print("Client activated")
                    #print("An error occur")
    

    
    return client


async def get_groups(tgClient):


    groups = []
    async for dialog in tgClient.iter_dialogs():

        if dialog.is_group:
            groups.append({"name": dialog.name, "id": dialog.id})
        else: continue

    
    count = 1
    for group in groups:

        print("Enter "+str(count)+" to scrap group "+group["name"])
        count = count + 1

    option = input("Enter your option: ")
   
    try:

        option = int(option)
        print("Options", option)
        group = groups[option - 1]
        print("Selected group is",group["name"])
        return group["id"]
    
    except Exception as err:
        print(err)
        print("Invalid options, program exit")
        return


async def add(tgClient,users, mychannel):

    await tgClient.start()
    channel_entity = await tgClient.get_entity(mychannel)
    usernames = []
    count = 0
    


    for user in users:
        id = user["id"]
        usernames.append(id)
    count  = 0
    l = len(users)
    print("Adding commence")
    while True:
        if count >= l:
            break
        sl = usernames[count:count+10]
        count+=10
        try:
            await tgClient(InviteToChannelRequest(channel_entity, sl))
            time.sleep(60)
        except Exception as err:
                print(err)
           
async def get_member_using_search(client, channel):

    queryKey = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    all_participants = []
    result = []
    
    print("Scrapping begins")
    for key in queryKey:
        offset = 0
        limit = 100
        while True:
            participants = await client(GetParticipantsRequest(
            channel, ChannelParticipantsSearch(key), offset, limit,
            hash=0
        ))
            if not participants.users:
                break
            for user in participants.users:
                try:
                    if re.findall(r"\b[a-zA-Z]", user.first_name)[0].lower() == key:
                     all_participants.append(user)

    
                except Exception as err:
                    pass
                    #print(err)
                   

            offset += len(participants.users)

    for user in all_participants:
        if user.bot:
            continue
        member = {"id": user.id,"username": user.username, "firstname":user.first_name, "lastname": user.last_name}
        
        result.append(member)
    print("Total number scrapped:",len(result))
    writeToFile(result)
        

   

def writeToFile(lists, filename="users.json"):

    content = []
    
    try:
        with open(filename, "r") as f:
            con = json.load(f)
            content.extend(list(con))
    except Exception as err:
        print("File empty")
        
    print("initial length",len(content))
    content.extend(lists)
    print("Content after:", len(content))
    with open(filename, "w") as f:
        json.dump(content, f)


def getOffset():
    l = 0
    try:

        with open("users.json", "r") as f:
            contents = json.load(f)
            l = len(list(contents))
    except Exception as err:
        
        l = 0
    return l

async def isMember(tgClient,channel, username):
    limit = 100
    offset = 0
    entity = await tgClient.get_entity(channel)
    while True:
        members = await tgClient(GetParticipantsRequest(channel=entity,filter=ChannelParticipantsSearch(username), offset=offset, limit=limit, hash=0))
        if not members.users:
            break
        if members:
            return True
        
    return False

async def main():
    client = await connect()

    while True:
        print("ENter 1 to scrapp members from groups")
        print("Enter 2 to add scrapped member to your group")
        print("any other input to exit")
        action = input("Enter 1 or 2: ")

        if action == "1":

            CHAT_LINK = await get_groups(client)
            
            group = CHAT_LINK #if CHAT_LINK != "y" else os.getenv("GROUP")
            #print("group is ",group)
            await get_member_using_search(client, group)#getChannelMembers(client,group)
            print("Done adding members")

        elif action == "2":
            lst = []
            mychannel = os.getenv("MY_CHANNEL")
            with open("users.json", "r") as f:
                lst = list(json.load(f))
            await add(client, lst, mychannel)

        else:
            print("Good bye")
            break
            
    

if __name__ == "__main__":
	asyncio.run(main())
