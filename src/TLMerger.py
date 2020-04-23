#!/usr/bin/python3
import logging, shutil, sqlite3, os, time, io
import progressbar  # progressbar2 module
try:
    import cryptg
    from cryptg import *
except:
    pass

from datetime import date, timedelta
from sys import exit
from getpass import getpass
from telethon.sync import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.crypto import AuthKey
from telethon.tl.functions.messages import *
from telethon.tl.types import *
from telethon.utils import *
from telethon.sessions import *
import pyAesCrypt

api_id = YOUR_API_ID_HERE
api_hash = 'YOUR_API_HASH_HERE'
TLdevice_model = 'Desktop device'
TLsystem_version = 'Console'
TLapp_version = '- TLMerger 1.1'
TLlang_code = 'en'
TLsystem_lang_code = 'en'
found_media = {}
User1IDs = []
User2IDs = []
FetchableMsgIDs = []
FetchableMsgIDsUser2 = []
SelfUser1 = None
SelfUser2 = None
ChosenChat = None
dialogs = None
DestinationChat = None
AgressiveTimestamps = False
SoloImporting = False
AddFwdHeader = True
AddSender = True
NoTimestamps = False
SendAllLinkPreviews = False
DeleteOriginalMessages = False
AppendHashtag = False
SendDatabase = True
Warnings = False
Errors = False
peer = None
YYYYMMDD = True
DateSeconds = True
DateEnd = False
ReversedDate = False
ExceptionReached = False
client2 = None
timezonediff = None
count = None
#SecretModeVariables
SecretMessage = None
SecretChosenChat = None
SecretMode = False
password = "YOUR_PASSWORD_FOR_SECRET_MODE_HERE"
bufferSize = 64 * 4096
secretdbstream = None

client1 = TelegramClient('User1', api_id, api_hash, device_model=TLdevice_model, system_version=TLsystem_version, app_version=TLapp_version, lang_code=TLlang_code, system_lang_code=TLsystem_lang_code)

def StartClient1():
    global SelfUser1, client1
    try:
        client1.connect()
        if not client1.is_user_authorized():
            client1.start(force_sms=False)
        SelfUser1 = client1.get_entity(client1.get_me())
    except:
        if not client1.is_connected():
            getpass("You are not connected to the internet or the phone was given in the incorrect format. Check your connection and press ENTER to try again: ")
        StartClient1()
    return

def StartClient2():
    global SelfUser2, client2
    try:
        client2.connect()
        if not client2.is_user_authorized():
            client2.start(force_sms=False)
        SelfUser2 = client2.get_entity(client2.get_me())
    except:
        if not client2.is_connected():
            getpass(
            "You are not connected to the internet or the phone was given in the incorrect format. Check your connection and press ENTER to try again: ")
        StartClient1()
    return

async def EventHandler(event):
    global SecretMessage, secretdbstream, SecretChosenChat
    if getattr(event.message, 'media', None):
        if isinstance(event.message.media, (MessageMediaDocument, Document)):
            for attr in event.message.media.document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    if attr.file_name == "DB.aes":
                        print("\nResponse received! Processing...")
                        secretdbstream = await client1.download_media(event.message, file=bytes)
                        SecretMessage = await client1.send_message(SecretChosenChat, "WooHoo!")
                        await client1.disconnect()
    return

def AskSoloMode():
    while True:
        answer = None
        answer = input(
            "Do you want to import a conversation using two users, in a 1:1 format? Otherwise, the chat will be imported inside your 'Saved Messages'.\n\nWARNING: Importing into Saved Messages hasn't been tested extensively, but should work. Use at your own risk.\nEnter your answer [y/n]: ")
        answer = answer.replace(" ", "")
        answer = answer.upper()
        if not (answer == 'Y' or answer == 'N'):
            while True:
                print()
                answer = input("The command you entered was not valid. Please, enter a valid one: ")
                answer = answer.replace(" ", "")
                answer = answer.upper()
                if (answer == "Y") or (answer == "N"):
                    break
        if answer == "Y":
            SoloImporting = False
            print("\nYou have chosen to merge the conversation using two accounts\n")
            break
        if answer == "N":
            SoloImporting = True
            print("\nYou have chosen to merge the conversation within your own account. This is known as 'Solo Mode'")
            break

def ChangeSenderSettings():
    global AddSender
    answer = None
    print()
    print(
        "You have chosen to merge conversations within your own account. Do you want to add the original sender's name to every message?")
    print()
    if AddSender is True:
        print("> Your current setting: The sender's name will be added.")
    else:
        print("> Your current setting: The sender's name won't be added")
    print()
    print("> Available commands: ")
    print(" > !1: Change the settings to add the sender's name to each message")
    print(" > !2: Change the settings and don't add the sender's name to each message")
    print(" > !C: Cancel and go back.")
    print()
    answer = input("Enter a command: ")
    answer = answer.replace(" ", "")
    answer = answer.upper()
    if not (answer == '!C' or answer == '!1' or answer == '!2'):
        while True:
            print()
            answer = input("The command you entered was invalid. Please, enter a valid command: ")
            answer = answer.replace(" ", "")
            answer = answer.upper()
            if (answer == "!C") or (answer == "!1") or (answer == "!2"):
                break
    if (answer == "!C"):
        return
    if (answer == "!1"):
        AddSender = True
        return
    if (answer == "!2"):
        AddSender = False
        return

def ChangeFwdHeaderSettings():
    global AddFwdHeader
    answer = None
    print()
    print("When you forward a message through Telegram, a 'Forwarded from' tag will be added to the messages. You can choose between adding that tag or not in the new copy of the messages")
    print()
    if AddFwdHeader is True:
        print("> Your current setting: The 'Forwarded from' tag will be added.")
    else:
        print("> Your current setting: The 'Forwarded from' tag won't be added")
    print()
    print("> Available commands: ")
    print(" > !1: Change the settings to add the 'Forwarded from' tag")
    print(" > !2: Change the settings and don't add the 'Forwarded from' tag")
    print(" > !C: Cancel and go back.")
    print()
    answer = input("Enter a command: ")
    answer = answer.replace(" ", "")
    answer = answer.upper()
    if not (answer == '!C' or answer == '!1' or answer == '!2'):
        while True:
            print()
            answer = input("The command you entered was invalid. Please, enter a valid command: ")
            answer = answer.replace(" ", "")
            answer = answer.upper()
            if (answer == "!C") or (answer == "!1") or (answer == "!2"):
                break
    if (answer == "!C"):
        return
    if (answer == "!1"):
        AddFwdHeader = True
        return
    if (answer == "!2"):
        AddFwdHeader = False
        return

def ChangeTimestampSettings():
    global AgressiveTimestamps, NoTimestamps, DateSeconds, YYYYMMDD, DateEnd, ReversedDate
    answer = None
    answer1 = None
    answer2 = None
    while True:
        print()
        print("TLMerger needs to resend the messages to the conversation as if they were new,\nso they will be sent with the current time and not with their original one.\nBy default, TLMerger adds the original date and time of a message in a [DD:MM:YYYY HH:MM] format, except for those photos, videos, stickers, files and forwarded messages.")
        print("\n--TIMESTAMP MODES--")
        print("> Agressive: Adds the timestamp to every message, including forwarded messages, stickers, GIFs and all kind of media.")
        print("> Default: Adds only the timestamp to text messages.")
        print("> No Timestamps: Doesn't add any timestamp to the messages.")
        print("\n--OTHER SETTINGS--")
        print("> Format: You can choose between [DD/MM/YYYY HH:MM], [YYYY/MM/DD HH:MM], [HH:MM DD/MM/YYYY], [HH:MM YYYY/MM/DD] timestamp formats")
        print("> Seconds: You can also opt to add the seconds like this: HH:MM:SS")
        print("> Position: You can choose if you want timestamps at the beginning of each message or at the end.")
        print()
        if AgressiveTimestamps is True:
            print("> Your current mode: Agressive")
        elif NoTimestamps is True:
            print("> Your current mode: No Timestamps")
        else:
            print("> Your current mode: Default")
        if NoTimestamps is False:
            if YYYYMMDD is False:
                if ReversedDate is False:
                    print("> Format: DD/MM/YYYY HH:MM")
                else:
                    print("> Format: HH:MM DD/MM/YYYY")
            else:
                if ReversedDate is False:
                    print("> Format: YYYY/MM/DD HH:MM")
                else:
                    print("> Format: HH:MM YYYY/MM/DD")
            if DateSeconds is True:
                print("> Seconds: Seconds will be added to timestamps, like this: HH:MM:SS")
            else:
                print("> Seconds: Seconds won't be added to timestamps. Timestamp will appear like this: HH:MM")
            if DateEnd is True:
                print("> Position: The timestamp will be added to the end of each message")
            else:
                print("> Position: The timestamp will be added to the beginning of each message")
        else:
            print("> **Other settings here are hidden because you have chosen to not use timestamps for messages. Enable\nthem to change this settings**")
        print()
        print("Here is an example based on your current settings:\n")
        print("----------------------------------------")
        if YYYYMMDD is True:
            if DateSeconds is True:
                if DateEnd is True:
                    if ReversedDate is True:
                        print("|Hello John! Let's meet this afternoon!|\n|[14:23:07 2018/5/24]                   |")
                    else:
                        print("|Hello John! Let's meet this afternoon!|\n|[2018/5/24 14:23:07]                   |")
                else:
                    if ReversedDate is True:
                        print("|[14:23:07 2018/5/24]                   \n|Hello John! Let's meet this afternoon!|")
                    else:
                        print("|[2018/5/24 14:23:07]                   \n|Hello John! Let's meet this afternoon!|")
            else:
                if DateEnd is True:
                    if ReversedDate is True:
                        print("|Hello John! Let's meet this afternoon!|\n|[14:23 2018/5/24]                      |")
                    else:
                        print("|Hello John! Let's meet this afternoon!|\n|[2018/5/24 14:23]                      |")
                else:
                    if ReversedDate is True:
                        print("|[14:23 2018/5/24]                      \n|Hello John! Let's meet this afternoon!|")
                    else:
                        print("|[2018/5/24 14:23]                      \n|Hello John! Let's meet this afternoon!|")
        else:
            if DateSeconds is True:
                if DateEnd is True:
                    if ReversedDate is True:
                        print("|Hello John! Let's meet this afternoon!|\n|[14:23:07 24/5/2018]                   |")
                    else:
                        print("|Hello John! Let's meet this afternoon!|\n|[24/5/2018 14:23:07]                   |")
                else:
                    if ReversedDate is True:
                        print("|[14:23:07 24/5/2018]                   \n|Hello John! Let's meet this afternoon!|")
                    else:
                        print("|[24/5/2018 14:23:07]                   \n|Hello John! Let's meet this afternoon!|")
            else:
                if DateEnd is True:
                    if ReversedDate is True:
                        print("|Hello John! Let's meet this afternoon!|\n|[14:23 24/5/2018]                      |")
                    else:
                        print("|Hello John! Let's meet this afternoon!|\n|[24/5/2018 14:23]                      |")
                else:
                    if ReversedDate is True:
                        print("|[14:23 24/5/2018]                      \n|Hello John! Let's meet this afternoon!|")
                    else:
                        print("|[24/5/2018 14:23]                      \n|Hello John! Let's meet this afternoon!|")
        print("----------------------------------------")
        print("\n> Available commands:")
        print(" > !1: Change the timestamps mode")
        print(" > !2: Change the timestamps format")
        if DateSeconds is False:
            print(" > !3: Change your setting to add seconds to the timestamps")
        else:
            print(" > !3: Change your settings and don't add the seconds to the timestamps")
        if DateEnd is True:
            print(" > !4: Change the position of the timestamp to the beginning of the message")
        else:
            print(" > !4: Change the position of the timestamps to the end of the message")
        print(" > !C: Confirm these settings and go back.")
        answer = input("\nEnter your command: ")
        answer = answer.replace(" ", "")
        answer = answer.upper()
        if not (answer == '!C' or answer == '!1' or answer == '!2' or answer == '!3'):
            while True:
                print()
                answer = input("The command you entered was invalid. Please, enter a valid command: ")
                answer = answer.replace(" ", "")
                if (answer == "!1") or (answer == "!2") or (answer == "!3") or (answer == "!C"):
                    break
        if answer == "!C":
            break
            return
        elif answer == "!1":
            print("\nNow, choose a timestamp mode. Available commands:\n")
            print(" > !1: Change the timestamp mode to 'Agressive'")
            print(" > !2: Change the timestamp settings to 'Default'")
            print(" > !3: Change the timestamp settings to 'No timestamps'")
            answer1 = input("\nEnter your command: ")
            answer1 = answer1.replace(" ", "")
            answer1 = answer1.upper()
            if not (answer1 == '!1' or answer1 == '!2' or answer1 == '!3'):
                while True:
                    print()
                    answer1 = input("The command you entered was invalid. Please, enter a valid command: ")
                    answer1 = answer1.replace(" ", "")
                    if (answer1 == "!1") or (answer1 == "!2") or (answer1 == "!3"):
                        break
            if answer1 == "!1":
                AgressiveTimestamps = True
                NoTimestamps = False
            if answer1 == "!2":
                AgressiveTimestamps = False
                NoTimestamps = False
            if answer1 == "!3":
                AgressiveTimestamps = False
                NoTimestamps = True
        elif answer == "!2":
            print("\nNow, choose a timestamp format. Available commands:\n")
            print(" > !1: Use [DD/MM/YYYY HH:MM] format")
            print(" > !2: Use [YYYY/MM/DD HH:MM] format")
            print(" > !3: Use [HH:MM DD/MM/YYYY] format")
            print(" > !4: Use [HH:MM YYYY/MM/DD] format")
            answer2 = input("\nEnter your command: ")
            answer2 = answer2.replace(" ", "")
            answer2 = answer2.upper()
            if not (answer2 == '!1' or answer2 == '!2' or answer2 == '!3' or answer2 == "!4"):
                while True:
                    print()
                    answer2 = input("The command you entered was invalid. Please, enter a valid command: ")
                    answer2 = answer2.replace(" ", "")
                    if (answer2 == "!1") or (answer2 == "!2") or (answer2 == "!3") or (answer2 == "!4"):
                        break
            if answer2 == "!1":
                YYYYMMDD = False
                ReversedDate = False
            elif answer2 == "!2":
                YYYYMMDD = True
                ReversedDate = False
            elif answer2 == "!3":
                ReversedDate = True
                YYYYMMDD = False
            elif answer2 == "!4":
                ReversedDate = True
                YYYYMMDD = True
        elif answer == "!3":
            if DateSeconds is True:
                DateSeconds = False
            else:
                DateSeconds = True
        elif answer == "!4":
            if DateEnd is True:
                DateEnd = False
            else:
                DateEnd = True

def ChangeLinkPreviewSettings():
    global SendAllLinkPreviews
    answer = None
    print()
    print("When you send a link through Telegram, a link preview will be generated, so you can see the photos, documents and videos that the webpage contains\ninside Telegram, without opening the webpage. If the webpage changes or gets deleted, those previews will be still available in your Telegram Chat.\nThat means that you might lose some link previews which you might care about while merging the chat if the webpage has been changed since you sent the original message.")
    print()
    print("> Add Link Previews: We will attach the original Link Preview of the link to the new chat. A new link preview will be generated as well, but the message containing the link will be replied with the original link preview.\nWe will add a #LinkPreview hashtag so you can track them easily using search.")
    print("> Don't Add Link Previews: New Link Previews will be generated based on the actual webpage, and the old ones will be discarded")
    print()
    if SendAllLinkPreviews is True:
        print("> Your current setting: The original Link Previews will be replied to the original message.")
    else:
        print("> Your current setting: Original Link Previews won't be added and new ones will be generated")
    print()
    print("> Available commands: ")
    print(" > !1: Change the settings and add the Link Preview")
    print(" > !2: Change the settings and don't add the original Link Previews")
    print(" > !C: Cancel and go back.")
    print()
    answer = input("Enter a command: ")
    answer = answer.replace(" ", "")
    answer = answer.upper()
    if not (answer == '!C' or answer == '!1' or answer == '!2'):
        while True:
            print()
            answer = input("The command you entered was invalid. Please, enter a valid command: ")
            answer = answer.replace(" ", "")
            answer = answer.upper()
            if (answer == "!C") or (answer == "!1") or (answer == "!2"):
                break
    if (answer == "!C"):
        return
    if (answer == "!1"):
        SendAllLinkPreviews = True
        return
    if (answer == "!2"):
        SendAllLinkPreviews = False
        return

def ChangeHashtagsSettings():
    global AppendHashtag
    answer = None
    print()
    print("You can choose between adding the hashtag '#TLMerger' to every message (not photos, stickers, files...), so they can be easily searchable.\nThis setting depends on what's convenient for you, but you don't need it strictly: TLMerger will always keep a list of all the messages sent in the database, so you can later undo the changes using TLRevert.")
    print()
    if AppendHashtag is True:
        print("> Your current setting: Add Hashtags.")
    else:
        print("> Your current setting: Don't Add Hashtags")
    print()
    print(">Available commands: ")
    print(">  !C: Cancel and go back.")
    print(">  !1: Change your settings and add hashtags to messages.")
    print(">  !2: Change your settings and don't add hashtags to messages.")
    print()
    answer = input("Enter your command: ")
    answer = answer.replace(" ", "")
    answer = answer.upper()
    if not (answer == '!C' or answer == '!1' or answer == '!2'):
        while True:
            print()
            answer = input("You entered an invalid command. Please, enter a valid one: ")
            answer = answer.replace(" ", "")
            answer = answer.upper()
            if (answer == "!C") or (answer == "!1") or (answer == "!2"):
                break
    if (answer == "!C"):
        return
    if (answer == "!1"):
        AppendHashtag = True
        return
    if (answer == "!2"):
        AppendHashtag = False
        return

def ChangeDatabaseSettings():
    global SendDatabase
    answer = None
    print()
    print("The database of TLMerger contains a lot of useful information which you can later check using applications like https://github.com/sqlitebrowser/sqlitebrowser. It will be also necessary if you want to undo all the changes made by TLMerger in the future, using TLRevert.")
    print("\nYou can choose between making a backup of the database on your Telegram's 'Saved Messages' (the chat with yourself) or don't do it.")
    print()
    if SendDatabase is True:
        print("> Your current setting: Make a Backup of the Database inside your 'Saved Messages'.")
    else:
        print("> Your current setting: Don't make a backup of the Database and keep it only in the disk.")
    print()
    print("> Available commands: ")
    print(">   !C: Cancel and go back.")
    print(">   !1: Make a backup in your 'Saved Messages'")
    print(">   !2: Don't make a backup in 'Saved Messages'")
    print()
    answer = input("Enter a command: ")
    answer = answer.replace(" ", "")
    answer = answer.upper()
    if not (answer == '!C' or answer == '!1' or answer == '!2'):
        while True:
            print()
            answer = input("The command you entered was invalid. Please, enter a valid one: ")
            answer = answer.replace(" ", "")
            answer = answer.upper()
            if (answer == "!C") or (answer == "!1") or (answer == "!2"):
                break
    if (answer == "!C"):
        return
    if (answer == "!1"):
        SendDatabase = True
        return
    if (answer == "!2"):
        SendDatabase = False
        return

def ChangeDeleteSettings():
    global DeleteOriginalMessages
    print()
    answer = None
    print("After merging the conversation in the new chat, TLMerger can delete the original messages.")
    print()
    if DeleteOriginalMessages is True:
        print("> Your current setting: Delete the original messages")
    else:
        print("> Your current setting: Keep the original messages")
    print()
    print("> Available commands:")
    print(" > !1: Change the settings and delete the original messages")
    print(" > !2: Change the settings and don't delete original messages")
    print(" > !C: Cancel and go back.")
    print()
    answer = input("Enter your command: ")
    answer = answer.replace(" ", "")
    answer = answer.upper()
    if not (answer == '!C' or answer == '!1' or answer == '!2'):
        while True:
            print()
            answer = input("The command you entered was invalid. Please, enter a valid command: ")
            answer = answer.replace(" ", "")
            if (answer == "!1") or (answer == "!2") or (answer == "!C"):
                break
    if (answer == "!C"):
        return
    if (answer == "!1"):
        DeleteOriginalMessages = True
        return
    if (answer == "!2"):
        DeleteOriginalMessages = False
        return

def sprint(string, *args, **kwargs):
    #Safe Print (handle UnicodeEncodeErrors on some terminals)
    try:
        print(string, *args, **kwargs)
    except UnicodeEncodeError:
        string = string.encode('utf-8', errors='ignore')\
                       .decode('ascii', errors='ignore')
        print(string, *args, **kwargs)

def PrintChatList():
    global dialogs
    while True:
        if dialogs is None:
            dialogs = client1.get_dialogs(limit=None)
        i = None
        while i is None:
            print("This is the chat list:\n\n")
            for i, dialog in enumerate(dialogs, start=1):
                if get_display_name(dialog.entity) == "":
                    name = "Deleted Account"
                elif isinstance(dialog.entity, InputPeerSelf):
                    name = "Chat with yourself (Saved Messages)"
                else:
                    name = get_display_name(dialog.entity)
                sprint('{}. {}'.format(i, name))

            print()
            if not SecretMode:
                print('> Which is the chat do you want to merge?')
            else:
                print('> Who is your partner?')
            print('> Available commands:')
            print('  !q: Quits the dialogs window and exits.')
            print('  !l: Logs out, terminating this session.')
            print()
            i = input('Enter dialog ID or a command to continue: ')
            if i is None:
                continue
            if i == '!q':
                exit()
            if i == '!l':
                client1.log_out()
                exit()
        try:
            i = int(i if i else 0) - 1
            # Ensure it is inside the bounds, otherwise retry
            dialog_count = dialogs.total
            if not 0 <= i < dialog_count:
                i = None
        except:
            i = None
            print("That's not a valid Chat. Please, try again.")
            continue

            # Retrieve the selected user (or chat, or channel)
        return dialogs[i].entity

def StartSecretMode():
    global dialogs, SecretChosenChat, password, bufferSize, client2, SecretMessage, secretdbstream
    getpass("\n\nYou have chosen to use the Telegram Tool's secret mode for logging your partner in Telegram.\nNow, it's time to choose your partner in your chat list. Press ENTER to continue: ")
    print("\nGathering your chat list...")
    SecretChosenChat = PrintChatList()
    print("\n\nWaiting for a response from your partner...")
    client1.add_event_handler(EventHandler, events.NewMessage(chats=SecretChosenChat, incoming=True))
    client1.run_until_disconnected()
    client1.connect()
    client1.remove_event_handler(EventHandler, events.NewMessage(chats=SecretChosenChat, incoming=True))
    byteDec = io.BytesIO()
    byteIn = io.BytesIO(secretdbstream)
    pyAesCrypt.decryptStream(byteIn, byteDec, password, bufferSize, len(byteIn.getvalue()))
    byteDec.seek(0)
    client2 = TelegramClient(StringSession(byteDec.read().decode()), api_id, api_hash, device_model=TLdevice_model,
                             system_version=TLsystem_version, app_version=TLapp_version, lang_code=TLlang_code,
                             system_lang_code=TLsystem_lang_code)
    StartClient2()
    print("Secret Mode's Authentication done successfully!")

def HandleExceptions():
    global SelfUser1, peer, SendDatabase, SelfUser2, FetchableMsgIDs, SoloImporting
    answer = None
    print("\n\n")
    print("It seems that you have already reached some problems before. You can keep retrying again, or exit TLMerger and report this error in\nhttps://github.com/TelegramTools/TLMerger/issues.")
    print("\n\n> Available commands: ")
    print(" > !1: Try again")
    print(" > !2: Save Changes in the database and exit TLMerger")
    answer = input("\nEnter you command: ")
    answer.replace(" ", "")
    answer = answer.upper()
    if not (answer == '!1' or answer == '!2'):
        while True:
            print()
            answer = input("The command you entered was invalid. Please, enter a valid command: ")
            answer = answer.replace(" ", "")
            if (answer == "!1") or (answer == "!2"):
                break
    if (answer == "!1"):
        return
    if (answer == "!2"):
        CommitMessages(None, True)
        if not SoloImporting:
            DeleteMessageClient1(SelfUser2, message_ids=FetchableMsgIDs, revoke=True)
        print(
            "Changes saved! You can use TLRevert in case you want to revert the changes made by TLMerger in the future.\nYou will need to start from scratch if you want to continue the merging process later.")
        if SendDatabase is True:
            print(
                "You have chosen to make a copy of your database in your 'Saved Messages' inside Telegram.\nBacking up database...")
            databasecopy = SendFileClient1(SelfUser1, file="data\TLMerger-Database.db",
                                           caption="This is the TLMerger's database with " + peer)
            SendMessageClient1(SelfUser1,
                               "💾 You can read this database using programs like https://github.com/sqlitebrowser/sqlitebrowser/releases. This database is **mandatory** if you want to use [TLRevert](https://github.com/TelegramTools/TLRevert) in order to revert all the changes made by TLMerger. Read the manuals of both programs if you have any doubt about them. **Thank you very much for using** [TLMerger](https://github.com/TelegramTools/TLMerger)**!**\n\n**--ferferga**", reply_to=databasecopy.id)
        getpass("\n\nYou can close TLMerger by pressing ENTER: ")
        exit(0)
    return

def countdown(t):
    print("\n\n")
    while t:
        timeformat = '--> We have reached a flood limitation. Waiting for: ' + str(timedelta(seconds=t))
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1

def SendMessageClient1(*args, **kwargs):
    global ExceptionReached
    try:
        return client1.send_message(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN SendFileClient1: " + str(e))
        countdown(e.seconds)
        return SendMessageClient1(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN SendFileClient1: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))        
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return SendMessageClient1(*args, **kwargs)

def SendFileClient2(*args, **kwargs):
    global ExceptionReached
    try:
        return client2.send_file(*args, allow_cache=False, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN SendFileClient2: " + str(e))
        countdown(e.seconds)
        return SendFileClient2(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN SendFileClient2: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        ExceptionReached = True
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return SendFileClient2(*args, **kwargs)

def SendFileClient1(*args, **kwargs):
    global ExceptionReached
    try:
        return client1.send_file(*args, allow_cache=False, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN SendFileClient1: " + str(e))
        countdown(e.seconds)
        return SendFileClient1(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN SendFileClient1: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        ExceptionReached = True
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return SendFileClient1(*args, **kwargs)

def SendMessageClient2(*args, **kwargs):
    global ExceptionReached
    try:
        return client2.send_message(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN SendMessageClient2: " + str(e))
        countdown(e.seconds)
        return SendMessageClient2(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN SendMessageClient2: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return SendMessageClient2(*args, **kwargs)

def ForwardMessageClient1(*args, **kwargs):
    global ExceptionReached
    try:
        return client1.forward_messages(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN ForwardMessageClient1: " + str(e))
        countdown(e.seconds)
        return ForwardMessageClient1(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN ForwardMessageClient1: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return ForwardMessageClient1(*args, **kwargs)

def ForwardMessageClient2(*args, **kwargs):
    global ExceptionReached
    try:
        return client2.forward_messages(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN ForwardMessageClient2: " + str(e))
        countdown(e.seconds)
        return ForwardMessageClient2(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN ForwardMessageClient2: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return ForwardMessageClient2(*args, **kwargs)

def DeleteMessageClient1(*args, **kwargs):
    global ExceptionReached
    try:
        return client1.delete_messages(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN DeleteMessageClient1: " + str(e))
        countdown(e.seconds)
        return DeleteMessageClient1(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN DeleteMessageClient1: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return DeleteMessageClient1(*args, **kwargs)

def DeleteMessageClient2(*args, **kwargs):
    global ExceptionReached
    try:
        return client2.delete_messages(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN DeleteMessageClient2: " + str(e))
        countdown(e.seconds)
        return DeleteMessageClient2(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN DeleteMessageClient2: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return DeleteMessageClient2(*args, **kwargs)

def SendRequestClient1(*args, **kwargs):
    global ExceptionReached
    try:
        return client1(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN SendRequestClient1: " + str(e))
        countdown(e.seconds)
        return SendRequestClient1(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN SendRequestClient1: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return SendRequestClient1(*args, **kwargs)

def SendRequestClient2(*args, **kwargs):
    global ExceptionReached
    try:
        return client2(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN SendRequestClient2: " + str(e))
        countdown(e.seconds)
        return SendRequestClient2(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN SendRequestClient2: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return SendRequestClient2(*args, **kwargs)

def GetIncomingIdOfUser1(u):
    global ExceptionReached
    try:
        return client2.get_messages(u, limit=1)[0].id
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN GETINCOMINGIDOFUSER1: " + str(e))
        countdown(e.seconds)
        return GetIncomingIdOfUser1(u)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN GETINCOMINGIDOFUSER1: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return GetIncomingIdOfUser1(u)

def GetIncomingIdOfUser2(u):
    global ExceptionReached
    try:
        return client1.get_messages(u, limit=1)[0].id
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN GETINCOMINGIDOFUSER2: " + str(e))
        countdown(e.seconds)
        return GetIncomingIdOfUser2(u)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN GETINCOMINGIDOFUSER2: " + str(e))
        print("Something went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return GetIncomingIdOfUser2(u)

def DownloadMedia(*args, **kwargs):
    global ExceptionReached
    try:
        return client1.download_media(*args, **kwargs)
    except FloodWaitError as e:
        logging.exception("TLMERGER FLOODEXCEPTION IN DownloadMedia: " + str(e))
        countdown(e.seconds)
        return DownloadMedia(*args, **kwargs)
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN DownloadMedia: " + str(e))
        print("Something went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        if ExceptionReached is False:
            getpass("Press ENTER to try again: ")
            ExceptionReached = True
        else:
            HandleExceptions()
        return DownloadMedia(*args, **kwargs)

def CreateTables(db):
    cursor = db.cursor()
    cursor.execute("PRAGMA journal_mode = wal")
    cursor.execute("PRAGMA read_uncommitted = true;")
    db.commit()
    cursor.execute('''
    CREATE TABLE OriginalChat(sender TEXT, from_id INTEGER, message_id INTEGER PRIMARY KEY, message TEXT, out BOOLEAN, system_message BOOLEAN, reply_to_msg_id INTEGER, via_bot_username TEXT, fwd_from_id INTEGER, fwd_from_channel BOOLEAN, has_media BOOLEAN, DocType BOOLEAN, mediaType TEXT, mimeType TEXT, UnknownType BOOLEAN, UnknownClass TEXT, Day TEXT, Month TEXT, Year TEXT, Hour TEXT, Minute TEXT, Second TEXT)''')
    cursor.execute('''
    CREATE TABLE NewChat(OldId INTEGER, User1ID INTEGER, User2ID INTEGER)''')
    cursor.execute('''
    CREATE TABLE SentMessagesIDs(User1 INTEGER, User2 INTEGER)''')
    cursor.execute('''
    CREATE TABLE OldChatStatistics(count INTEGER, chat_id INTEGER, media_count INTEGER, chatName TEXT)''')
    cursor.execute('''
    CREATE TABLE Statistics(User1ID INTEGER, User2ID INTEGER, NameUser1 TEXT, NameUser2 TEXT, TotalCountUser1 INTEGER, TotalCountUser2 INTEGER, AffectedMessages INTEGER, SoloMode BOOLEAN)''')
    cursor.execute('''
    CREATE TABLE MediaPaths(message_id INTEGER PRIMARY KEY, FileName TEXT, hint_path TEXT)''')
    cursor.execute('''
    CREATE TABLE ContactMediaInfo(message_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, phone TEXT, vcard TEXT)''')
    cursor.execute('''
    CREATE TABLE PhotoMediaInfo(message_id INTEGER PRIMARY KEY, DocumentID LONG, AccessHash LONG, AccessHashUser2 LONG, FileReferenceUser1 BLOB, FileReferenceUser2 BLOB)''')
    cursor.execute('''
    CREATE TABLE GeoMediaInfo(message_id INTEGER PRIMARY KEY, long DOUBLE, lat DOUBLE)''')
    cursor.execute('''
    CREATE TABLE VenueMediaInfo(message_id INTEGER PRIMARY KEY, long DOUBLE, lat DOUBLE, title TEXT, address TEXT, provider TEXT, venue_id TEXT, venue_type TEXT)''')
    cursor.execute('''
    CREATE TABLE DocumentMediaInfo(message_id INTEGER PRIMARY KEY, DocumentID LONG, AccessHash LONG, AccessHashUser2 LONG, FileReferenceUser1 BLOB, FileReferenceUser2 BLOB)''')
    cursor.execute('''
    CREATE TABLE Version(AppName TEXT, AppVersion TEXT, CreationDate TEXT)''')
    db.commit()
    current_date = str(date.today())
    reg = ("TLMerger", "1.1", current_date)
    cursor.execute("INSERT INTO Version VALUES(?,?,?)", reg)
    db.commit()
    cursor.close()

def CommitMessages(database, stats):
    global User1IDs, User2IDs, SelfUser1, SelfUser2, SoloImporting, client1, client2, count
    if database is None:
        database = DBConnection(False, False)
    try:
        database.commit()
    except:
        database.close()
        database = DBConnection(False, False)
    cursor = database.cursor()
    if stats:
        if not SoloImporting:
            reg8 = (SelfUser1.id, SelfUser2.id, SelfUser1.first_name + " (+" + SelfUser1.phone + ")", SelfUser2.first_name + " (+" + SelfUser2.phone + ")", client1.get_messages(SelfUser2, limit=0).total, client2.get_messages(SelfUser1, limit=0).total, count, 1)
        else:
            reg8 = (SelfUser1.id, None, SelfUser1.first_name + " (+" + SelfUser1.phone + ")",
                    None, client1.get_messages(SelfUser1, limit=0).total,
                    None, count, 1)
        cursor.execute("INSERT INTO Statistics VALUES(?,?,?,?,?,?,?,?)", reg8)
    for id1 in User1IDs:
        reg5 = (id1, None)
        cursor.execute("INSERT INTO SentMessagesIDs VALUES(?,?)", reg5)
    database.commit()
    LoopingCount = 0
    for id1 in User1IDs:
        if len(User2IDs) != 0:
            cursor.execute("UPDATE SentMessagesIDs SET User2={id} WHERE User1={user1id}". \
                             format(user1id=id1, id=User2IDs.pop(0)))
            LoopingCount = LoopingCount + 1
        else:
            break
    if len(User2IDs) != 0:
        for id2 in User2IDs:
            reg5 = (None, id2)
            cursor.execute("INSERT INTO SentMessagesIDs VALUES(?,?)", reg5)
    database.commit()
    cursor.close()
    return

def GatherAllMessages(chat):
    global peer, timezonediff, count
    chatname = get_display_name(chat)
    if chatname == "":
        peer = input("\nThe chosen chat is with a Deleted Account. Please, define the name of your peer, which will be used for mentioning him correctly: ")
    else:
        peer = chatname
    count = client1.get_messages(chat, limit=0).total
    print("Gathering ", count, " messages from the chosen chat.\nThis can take a lot of time, but it's going as fast as possible.\n\nPlease, be patient...")
    try:
        db = DBConnection(False, False)
        chatID = get_peer_id(chat)        
        messages = client1.get_messages(chat, limit=None)
        while len(messages) > count:
            print("There was an error while getting the messages. Make sure that you don't send/receive any message in the chosen chat while we are getting messages.\nRetrying...")
            count = client1.get_messages(chat, limit=0).total
            messages = client1.get_messages(chat, limit=None)
            if len(messages) == count:
                break
        print("\nAll the messages were retrieved. Backing up data into the database...\n")
        completed = 0
        bar = progressbar.ProgressBar(max_value=count)
        bar.update(completed)
        for msg in reversed(messages):
            year = str(msg.date.year)
            if (msg.date.month < 10):
                month = "0" + str(msg.date.month)
            else:
                month = str(msg.date.month)
            if (msg.date.day < 10):
                day = "0" + str(msg.date.day)
            else:
                day = str(msg.date.day)
            hour = str(msg.date.hour+timezonediff)
            if (msg.date.minute < 10):
                minute = "0" + str(msg.date.minute)
            else:
                minute = str(msg.date.minute)
            if (msg.date.second < 10):
                second = "0" + str(msg.date.second)
            else:
                second = str(msg.date.second)
            if getattr(msg, "sender", None):
                if get_display_name(msg.sender) == "" or chatname == "":
                    sender = peer
                else:
                    sender = get_display_name(msg.sender)
            else:
                sender = get_display_name(chat)
            mediaType = None
            mimeType = None
            system_message = False
            UnknownType = False
            has_media = False
            UnknownClass = None
            via_bot_username = None
            fwd_from_id = None
            fwd_from_channel = False
            DocType = False
            if getattr(msg, 'media', None):
                FileName = None
                found_media[msg.id] = msg
                has_media = True
                message = msg.message
                system_message = False
                UnknownType = False
                UnknownClass = None
                if isinstance(msg.media, (MessageMediaWebPage, WebPageEmpty, WebPage)):
                    mediaType = "WebPage Preview"
                elif isinstance(msg.media, (MessageMediaGeo, GeoPoint, MessageMediaGeoLive)):
                    mediaType = "Geo"
                    reg = (msg.id, msg.media.geo.long, msg.media.geo.lat)
                    db.execute("INSERT INTO GeoMediaInfo VALUES(?,?,?)", reg)
                elif isinstance(msg.media, MessageMediaVenue):
                    mediaType = "Venue"
                    reg8 = (msg.id, msg.media.geo.long, msg.media.geo.lat, msg.media.title, msg.media.address, msg.media.provider, msg.media.venue_id, msg.media.venue_type)
                    db.execute("INSERT INTO VenueMediaInfo VALUES(?,?,?,?,?,?,?,?)", reg8)
                elif isinstance(msg.media, (MessageMediaContact, Contact)):
                    mediaType = "Contact"
                    reg1 = (msg.id, msg.media.first_name, msg.media.last_name, msg.media.phone_number, msg.media.vcard)
                    db.execute("INSERT INTO ContactMediaInfo VALUES(?,?,?,?,?)", reg1)
                    mimeType = None
                elif isinstance(msg.media, (Game, MessageMediaGame)):
                    mediaType = "Game"
                    mimeType = None
                elif isinstance(msg.media, (MessageMediaPhoto, Photo, PhotoSize, PhotoCachedSize)):
                    mediaType = "Photo"
                    if msg.out:
                        reg1 = (msg.id, msg.media.photo.id, msg.media.photo.access_hash, msg.media.photo.access_hash,
                            msg.media.photo.file_reference, msg.media.photo.file_reference)
                    else:
                        reg1 = (msg.id, msg.media.photo.id, msg.media.photo.access_hash, None, msg.media.photo.file_reference, None)
                    db.execute("INSERT INTO PhotoMediaInfo VALUES(?,?,?,?,?,?)", reg1)
                elif isinstance(msg.media, MessageMediaUnsupported):
                    mediaType = "Unsupported"                    
                    mimeType = None
                    UnknownClass = type(msg).__name__
                    logging.warning("TLMERGER EXCEPTION: Unsupported media found: " + UnknownClass)
                elif isinstance(msg.media, (MessageMediaDocument, Document)):
                    mimeType = msg.media.document.mime_type
                    mediaType = "Document"
                    DocType = True
                    for attr in msg.media.document.attributes:
                        if isinstance(attr, DocumentAttributeAudio):
                            if attr.voice:
                                mediaType = "VoiceNote"
                            elif not attr.voice:
                                mediaType = "Audio"
                        elif isinstance(attr, DocumentAttributeHasStickers):
                            mediaType = "HasSticker"
                        elif isinstance(attr, DocumentAttributeVideo):
                            if attr.round_message:
                                mediaType = "VideoNote"
                            elif not attr.round_message:
                                mediaType = "Video"
                        elif isinstance(attr, DocumentAttributeFilename):
                            FileName = attr.file_name
                        elif isinstance(attr, DocumentAttributeAnimated):
                            mediaType = "Animated GIF"
                        elif isinstance(attr, DocumentAttributeImageSize):
                            mediaType = "Uncompressed Image"
                        elif isinstance(attr, DocumentAttributeSticker):
                            mediaType = "StickerPack"
                        else:
                            logging.warning("TLMERGER EXCEPTION IN GATHERINGCHATS: DocumentAttribute Conditions weren't met.")
                    if msg.out:
                        reg21 = (msg.id, msg.media.document.id, msg.media.document.access_hash, msg.media.document.access_hash,
                            msg.media.document.file_reference, msg.media.document.file_reference)
                    else:
                        reg21 = (
                        msg.id, msg.media.document.id, msg.media.document.access_hash, None, msg.media.document.file_reference, None)
                    db.execute("INSERT INTO DocumentMediaInfo VALUES(?,?,?,?,?,?)", reg21)
                else:
                    logging.warning("TLMERGER EXCEPTION IN GATHERINGCHATS: Media Conditions weren't met.")
                    mediaType = "Unknown"
                    UnknownClass = type(msg.media).__name__
                if (mediaType == "WebPage Preview" or (mediaType == "Animated GIF" and mimeType == "image/gif")):
                    os.makedirs('data/Media/' + str(msg.id), exist_ok=True)
                    path = ("data/Media/" + str(msg.id))
                    output = DownloadMedia(msg.media, path)
                    if (mediaType == "WebPage Preview" and output is None):
                        mediaType = "WebPage"
                    elif output is None:
                        mediaType = "Expired Media"
                    try:
                        finaloutput = output.replace("\\", "/")
                    except:
                        finaloutput = output
                    reg4 = (msg.id, FileName, finaloutput)
                    db.execute("INSERT INTO MediaPaths VALUES(?,?,?)", reg4)
            elif hasattr(msg, 'message'):
                message = msg.message
            else:
                UnknownClass = type(msg).__name__
                UnknownType = True
                logging.warning("TLMERGER EXCEPTION IN GATHERINGCHATS: Message conditions weren't met.")

            if msg.action:
                system_message = True
                if isinstance(msg.action, MessageActionHistoryClear):
                    completed = completed + 1
                    bar.update(completed)
                    continue
                if isinstance(msg.action, MessageActionPhoneCall):
                    if isinstance(msg.action, MessageActionPhoneCall):
                        if msg.action.duration is not None:
                            message = "📞 **Phone call from " + sender + "**\n`" + str(
                                timedelta(seconds=msg.action.duration)) + "` in call. 📞"
                        elif getattr(msg.action, "reason", None):
                            if isinstance(msg.action.reason, (PhoneCallDiscardReasonMissed, PhoneCallDiscardReasonBusy, PhoneCallDiscardReasonDisconnect)):
                                message = "📞 **Missed phone call from " + sender + "** 📞"
                            elif isinstance(msg.action.reason, PhoneCallDiscardReasonHangup):
                                message = "📞 **Rejected phone call from " + sender + "** 📞"

                elif isinstance(msg.action, MessageActionGameScore):
                    message = "`" + sender + " achieved an score of " + str(msg.action.score) + " points`"
                else:
                    message = "`Unknown System Message: " + str(msg.action) + "`"               
            reply_to_msg_id = msg.reply_to_msg_id
            if getattr(msg, 'from_id', None):
                from_id = msg.from_id
            else:
                from_id = None
            if hasattr(msg, "via_bot_id"):
                if msg.via_bot_id is not None:
                    botusername = client1.get_entity(client1.get_input_entity(msg.via_bot_id)).username
                    if botusername is not None:
                        via_bot_username = "via @" + botusername
            if getattr(msg, 'fwd_from', None):
                if isinstance(msg.fwd_from, MessageFwdHeader):
                    fwd_from_sender = msg.fwd_from.from_id
                    fwd_channel_id = msg.fwd_from.channel_id
                    if fwd_from_sender:
                        fwd_from_id = get_peer_id(fwd_from_sender)
                        fwd_from_channel = False
                    elif fwd_channel_id:
                        fwd_from_id = get_peer_id(fwd_channel_id)
                        fwd_from_channel = True

            reg5 = (sender, from_id, msg.id, message, msg.out, system_message, reply_to_msg_id, via_bot_username, fwd_from_id, fwd_from_channel, has_media, DocType, mediaType, mimeType, UnknownType, UnknownClass, day, month, year, hour, minute, second)
            db.execute("INSERT INTO OriginalChat VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", reg5)
            completed = (completed + 1)
            bar.update(completed)        
        reg6 = (count, chatID, len(found_media), peer)
        db.execute("INSERT INTO OldChatStatistics VALUES(?,?,?,?)", reg6)
        db.commit()
        DBConnection(False, True)
        bar.finish()
        messages.clear()
        print("\nDone! Backed up", count, "messages and", len(found_media), "files.")
    except Exception as e:
        logging.exception("TLMERGER TELEGRAMEXCEPTION IN GATHERALLMESSAGES: " + str(e))
        print("\nSomething went wrong in Telegram's side. This is the full exception:\n\n"  + str(e))
        getpass("This part of the process can't be recovered. You must start from scratch.\n\nYou can report this issue at https://github.com/TelegramTools/TLMerger/issues/new. Please, give as much details as possible of the error message and attach the 'TLMerger-log.log' file, as all the detailed information about the bug has been written there.\n\nPress ENTER to close the app...")
        exit(0)
    return

def RefreshFileRefs(user1, user2):
    global FetchableMsgIDs, FetchableMsgIDsUser2, SelfUser2, SelfUser1, database
    database.commit()
    if not SoloImporting:
        cur1 = database.cursor()
        docmsg = client2.get_messages(user1, ids=FetchableMsgIDsUser2)
        for msg in docmsg:
            if getattr(msg, 'media', None):
                if isinstance(msg.media, (MessageMediaDocument, Document)):
                    access_hash = msg.media.document.access_hash
                    file_reference = msg.media.document.file_reference
                    document_id = msg.media.document.id

                    cur1.execute("UPDATE DocumentMediaInfo SET AccessHashUser2=?, FileReferenceUser2=? WHERE DocumentID=?",
                        (access_hash, file_reference, document_id))
                            
                elif isinstance(msg.media, (MessageMediaPhoto, Photo, PhotoSize, PhotoCachedSize)):
                    access_hash = msg.media.photo.access_hash
                    file_reference = msg.media.photo.file_reference
                    document_id = msg.media.photo.id

                    cur1.execute("UPDATE PhotoMediaInfo SET AccessHashUser2=?, FileReferenceUser2=? WHERE DocumentID=?",
                        (access_hash, file_reference, document_id))

        database.commit()
        cur1.close()
    originalIds = []
    cur = database.cursor()
    cur.execute("SELECT message_id FROM DocumentMediaInfo GROUP BY DocumentID")
    for row in cur:
        originalIds.append(row[0])
    cur.execute("SELECT message_id FROM PhotoMediaInfo GROUP BY DocumentID")
    for row in cur:
        originalIds.append(row[0])
    cur.close()
    cur2 = database.cursor()
    docmsg = client1.get_messages(ChosenChat, ids=originalIds)
    for msg in docmsg:
        if getattr(msg, 'media', None):
            if isinstance(msg.media, (MessageMediaDocument, Document)):
                access_hash = msg.media.document.access_hash
                file_reference = msg.media.document.file_reference
                document_id = msg.media.document.id

                cur2.execute("UPDATE DocumentMediaInfo SET AccessHash=?, FileReferenceUser1=? WHERE DocumentID=?",
                        (access_hash, file_reference, document_id))

            elif isinstance(msg.media, (MessageMediaPhoto, Photo, PhotoSize, PhotoCachedSize)):
                access_hash = msg.media.photo.access_hash
                file_reference = msg.media.photo.file_reference
                document_id = msg.media.photo.id

                cur2.execute("UPDATE PhotoMediaInfo SET AccessHash=?, FileReferenceUser1=? WHERE DocumentID=?",
                    (access_hash, file_reference, document_id))
    database.commit()
    cur2.close()
    del originalIds
    return

def ExportMessages():
    global Errors, SendAllLinkPreviews, SendDatabase, AgressiveTimestamps, YYYYMMDD, ReversedDate, DateSeconds, DateEnd, NoTimestamps, \
        client1, client2, AppendHashtag, SelfUser1, SelfUser2, ChosenChat, DestinationChat, DeleteOriginalMessages, \
        User1IDs, User2IDs, peer, SoloImporting, FetchableMsgIDs, database
    print("\nProcessing...")
    client2.get_dialogs(limit=None)
    if not SoloImporting:
        try:
            user1 = client2.get_input_entity(SelfUser1.phone)
            user2 = client1.get_input_entity(SelfUser2.phone)
        except:
            user1 = client2.get_input_entity(SelfUser1.id)
            user2 = client1.get_input_entity(SelfUser2.id)
    else:
        user1 = client1.get_input_entity(DestinationChat)

    database = DBConnection(False, False)
    if not SoloImporting:
        AccessHash = []
        DocID = []
        PhotoID = []
        PhotoAccHash = []
        PhotoFileRef = []
        DocFileRef = []
        print("\nWe need to get some data from Telegram before starting. Preparing, this might take a while...")
        db = database.cursor()
        db.execute('SELECT * FROM DocumentMediaInfo WHERE AccessHashUser2 IS NULL GROUP BY DocumentID')
        for row in db:
            if row[1] not in DocID:
                DocID.append(row[1])
                AccessHash.append(row[2])
                DocFileRef.append(row[4])
        db2 = database.cursor()
        db2.execute('SELECT * FROM PhotoMediaInfo WHERE AccessHashUser2 IS NULL GROUP BY DocumentID')
        for row in db2:
            if row[1] not in PhotoID:
                PhotoID.append(row[1])
                PhotoAccHash.append(row[2])
                PhotoFileRef.append(row[4])
        length = len(DocID) + len(PhotoID)
        b = progressbar.ProgressBar(max_value=length)
        b.start()
        complete = 0
        Placeholder = []
        msg2placeholder = []
        for docid in DocID:
            Placeholder.append(0)
            if len(Placeholder) == 25:
                placeholder = SendMessageClient2(user1, "**This is just a placeholder message for avoiding flood limits.**")
                msg2placeholder.append(placeholder.id)
                Placeholder.clear()
            index = DocID.index(docid)
            request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=docid, access_hash=AccessHash[index], file_reference=DocFileRef[index])), message="")
            result = SendRequestClient1(request)
            msg = client1._get_response_message(request, result, user2)
            FetchableMsgIDs.append(msg.id)
            complete = complete + 1
            b.update(complete)
        for photoid in PhotoID:
            Placeholder.append(0)
            if len(Placeholder) == 25:
                placeholder = SendMessageClient2(user1, "**This is just a placeholder message for avoiding flood limits.**")
                msg2placeholder.append(placeholder.id)
                Placeholder.clear()
            index = PhotoID.index(photoid)
            request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=photoid, access_hash=PhotoAccHash[index], file_reference=PhotoFileRef[index])), message="")
            result = SendRequestClient1(request)
            msg = client1._get_response_message(request, result, user2)
            FetchableMsgIDs.append(msg.id)
            complete = complete + 1
            b.update(complete)
        Placeholder.clear()
        DeleteMessageClient2(user1, message_ids=msg2placeholder, revoke=True)
        b.finish()
        print("\nFetching media metadata from the receiver account...\nPlease wait, this can take a while...")
        cursor = database.cursor()
        docmsg = client2.get_messages(user1, limit=length)
        for msg in docmsg:
            if getattr(msg, 'media', None):
                if isinstance(msg.media, (MessageMediaDocument, Document)):
                    access_hash = msg.media.document.access_hash
                    file_reference = msg.media.document.file_reference
                    document_id = msg.media.document.id
                    cursor.execute("UPDATE DocumentMediaInfo SET AccessHashUser2=?, FileReferenceUser2=? WHERE DocumentID=?",
                        (access_hash, file_reference, document_id))

                elif isinstance(msg.media, (MessageMediaPhoto, Photo, PhotoSize, PhotoCachedSize)):
                    access_hash = msg.media.photo.access_hash
                    file_reference = msg.media.photo.file_reference
                    document_id = msg.media.photo.id
                    cursor.execute("UPDATE PhotoMediaInfo SET AccessHashUser2=?, FileReferenceUser2=? WHERE DocumentID=?",
                        (access_hash, file_reference, document_id))

            FetchableMsgIDsUser2.append(msg.id)
        database.commit()
        cursor.close()
        AccessHash.clear()
        DocID.clear()
        PhotoID.clear()
        PhotoAccHash.clear()
        PhotoFileRef.clear()
        DocFileRef.clear()
        del cursor, AccessHash, DocID, PhotoID, PhotoAccHash, PhotoFileRef, DocFileRef
        print("\n\nEverything is prepared and ready. Copying messages to the new chat...")
    print("\nINFORMATION: Each 1000 messages, a pause will happen because TLMerger needs to refresh metadata due to Telegram's restrictions.")
    print("Although the process might look like it's stuck, don't close or cancel it because you think it's stuck. Whenever an error happens, you will be informed.")
    completed = 0
    RawLoopCount = 0
    hashtag = ("\n#TLMerger")
    print("\n\nYou can cancel at any time using CTRL+C keyboard combination.")
    try:
        db = database.cursor()
        db.execute('SELECT * FROM OldChatStatistics')
        count = None
        chatId = None
        media_count = None
        chat_name = None
        for row in db:
            count = row[0]
            chatId = row[1]
            media_count = row[2]
            chat_name = row[3]
        if chat_name == "":
            chat_name = "Deleted account"
        if not SoloImporting:
            Welcmsg = SendMessageClient1(user2, "📲`MERGING THE CHAT WITH` __" + chat_name + "__. __'" + chat_name + "'__ is **" + SelfUser2.first_name + "** now.")
        else:
            Welcmsg = SendMessageClient1(user2,
                                         "📲`MERGING THE CHAT WITH` __" + chat_name + "__. __'" + chat_name + "'__ is **" + get_display_name(DestinationChat.entity) + "** now.")
        User1IDs.append(Welcmsg.id)
        if not SoloImporting:
            User2IDs.append(GetIncomingIdOfUser1(user1))
        bar = progressbar.ProgressBar(max_value=count)
        db.execute('SELECT * FROM OriginalChat')
        for row in db:            
            NewReplyId = None
            NewUser2ID = None
            NewUser1ID = None
            Sender = row[0]
            id = row[2] #int
            from_id = row[1] #int
            if not SoloImporting:
                message = row[3]
            else:
                message = "`" + row[0] + "`\n" + row[3]
            if not SoloImporting:
                if row[4] == 1:
                    out = True #bool
                elif row[4] == 0:
                    out = False
            else:
                out = True
            if row[5] == 1:
                system_message = True #bool
            elif row[5] == 0:
                system_message = False
            reply_to_msg_id = row[6] #int
            if row[7] is not None:
                via_bot_username = "**" + row[7] + "**"
            else:
                via_bot_username = None
            fwd_from_id = row[8] #int
            if row[9] == 1:
                fwd_from_channel = True #bool
            elif row[9] == 0:
                fwd_from_channel = False
            if row[10] == 1:
                has_media = True #bool
            elif row[10] == 0:
                has_media = False
            if row[11] == 0:
                DocType = False
            elif row[11] == 1:
                DocType = True
            mediaType = row[12] #string
            UnknownClass = row[15] #string
            mimeType = row[13] #string

            Day = row[16]
            Month = row[17]
            Year = row[18]
            Hour = row[19]
            Minute = row[20]
            Second = row[21]

            if YYYYMMDD is True:
                if DateSeconds is True:
                    if DateEnd is True:
                        if ReversedDate is True:
                            date = ("\n`[" + Hour + ":" + Minute + ":" + Second + " " + Year + "/" + Month + "/" + Day + "]`")
                        else:
                            date = ("\n`[" + Year + "/" + Month + "/" + Day + " " + Hour + ":" + Minute + ":" + Second + "]`")
                    else:
                        if ReversedDate is True:
                            date = ("`[" + Hour + ":" + Minute + ":" + Second + " " + Year + "/" + Month + "/" + Day + "]`\n")
                        else:
                            date = ("`[" + Year + "/" + Month + "/" + Day + " " + Hour + ":" + Minute + ":" + Second + "]`\n")
                else:
                    if DateEnd is True:
                        if ReversedDate is True:
                            date = ("\n`[" + Hour + ":" + Minute + " " + Year + "/" + Month + "/" + Day + "]`")
                        else:
                            date = ("\n`[" + Year + "/" + Month + "/" + Day + " " + Hour + ":" + Minute + "]`")
                    else:
                        if ReversedDate is True:
                            date = ("`[" + Hour + ":" + Minute + " " + Year + "/" + Month + "/" + Day + "]`\n")
                        else:
                            date = ("`[" + Year + "/" + Month + "/" + Day + " " + Hour + ":" + Minute + "]`\n")
            else:
                if DateSeconds is True:
                    if DateEnd is True:
                        if ReversedDate is True:
                            date = ("\n`[" + Hour + ":" + Minute + ":" + Second + " " + Day + "/" + Month + "/" + Year + "]`")
                        else:
                            date = ("\n`[" + Day + "/" + Month + "/" + Year + " " + Hour + ":" + Minute + ":" + Second + "]`")
                    else:
                        if ReversedDate is True:
                            date = ("`[" + Hour + ":" + Minute + ":" + Second + " " + Day + "/" + Month + "/" + Year + "]`\n")
                        else:
                            date = ("`[" + Day + "/" + Month + "/" + Year + " " + Hour + ":" + Minute + ":" + Second + "]`\n")
                else:
                    if DateEnd is True:
                        if ReversedDate is True:
                            date = ("\n`[" + Hour + ":" + Minute + " " + Day + "/" + Month + "/" + Year + "]`")
                        else:
                            date = ("\n`[" + Day + "/" + Month + "/" + Year + " " + Hour + ":" + Minute + "]`")
                    else:
                        if ReversedDate is True:
                            date = ("`[" + Hour + ":" + Minute + " " + Day + "/" + Month + "/" + Year + "]`\n")
                        else:
                            date = ("`[" + Day + "/" + Month + "/" + Year + " " + Hour + ":" + Minute + "]`\n")
            if AddFwdHeader:
                if fwd_from_id is not None:
                    if fwd_from_id == from_id:
                        FwdName = Sender
                    else:
                        ent = client1.get_entity(fwd_from_id)
                        if get_display_name(ent) == "":
                            FwdName = "Deleted Account"
                        else:
                            FwdName = get_display_name(ent)
                    if via_bot_username is None:
                        ForwardedHeader = ("➡️ **Forwarded from " + FwdName + "**\n")
                    else:
                        via_bot_username = row[7]
                        ForwardedHeader = ("➡️ **Forwarded from " + FwdName + via_bot_username + "**\n")

                if fwd_from_id is None and via_bot_username is not None:
                    message = via_bot_username + "\n" + message
            else:
                ForwardedHeader = ""

            if reply_to_msg_id is not None:
                db1 = database.cursor()
                db1.execute('SELECT * FROM NewChat WHERE OldId={id}'.\
                    format(id=reply_to_msg_id))
                for row in db1:
                    if from_id is get_peer_id(SelfUser1):
                        NewReplyId = row[1]
                    else:
                        NewReplyId = row[2]
                db1.close()

            if system_message is True:
                message = "__System Message:__ " + message

            if has_media is False or (mediaType == "WebPage Preview" and SendAllLinkPreviews is False) or mediaType == "WebPage":
                if out is True:
                    if fwd_from_id is None:
                        if reply_to_msg_id is None:
                            if NoTimestamps is False:
                                if AppendHashtag is True:
                                    if ReversedDate is True:
                                        if len(message + hashtag + date) > 4096:
                                            msg = SendMessageClient1(user2, message)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, hashtag + date, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, message + hashtag + date)
                                    else:
                                        if len(message + hashtag + date) > 4096:
                                            msg = SendMessageClient1(user2, message)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, date + hashtag, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, date + message + hashtag)
                                else:
                                    if ReversedDate is True:
                                        if len(message + date) > 4096:
                                            msg = SendMessageClient1(user2, message)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, message + date)
                                    else:
                                        if len(message + date) > 4096:
                                            msg = SendMessageClient1(user2, message)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, date + message)
                            else:
                                if AppendHashtag is True:
                                    if len(message + hashtag) > 4096:
                                        msg = SendMessageClient1(user2, message)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, hashtag, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        msg = SendMessageClient1(user2, message + hashtag)
                                else:
                                    msg = SendMessageClient1(user2, message)
                        else:
                            if NoTimestamps is True:
                                if AppendHashtag is True:
                                    if len(message + hashtag) > 4096:
                                        msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, hashtag, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        msg = SendMessageClient1(user2, message + hashtag, reply_to=NewReplyId)
                                else:
                                    msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                            else:
                                if AppendHashtag is True:
                                    if DateEnd is False:
                                        if len(date + message + hashtag) > 4096:
                                            msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, date + hashtag, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, date + message + hashtag,
                                                                     reply_to=NewReplyId)
                                    else:
                                        if len(date + message + hashtag) > 4096:
                                            msg = SendMessageClient1(user2, message,
                                                                     reply_to=NewReplyId)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, hashtag + date, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, message + hashtag + date, reply_to=NewReplyId)
                                else:
                                    if DateEnd is False:
                                        if len(date + message) > 4096:
                                            msg = SendMessageClient1(user2, message,
                                                                     reply_to=NewReplyId)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, date + message, reply_to=NewReplyId)
                                    else:
                                        if len(date + message) > 4096:
                                            msg = SendMessageClient1(user2, message,
                                                                     reply_to=NewReplyId)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, message + date, reply_to=NewReplyId)
                    else:
                        if AgressiveTimestamps is True:
                            if AppendHashtag is True:
                                if DateEnd is False:
                                    if len(date+ForwardedHeader+message+hashtag) > 4096:
                                        msg = SendMessageClient1(user2, message)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date + ForwardedHeader + hashtag, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        msg = SendMessageClient1(user2, date + ForwardedHeader + message + hashtag)
                                else:
                                    if len(ForwardedHeader+message+hashtag+date) > 4096:
                                        msg = SendMessageClient1(user2, message)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, ForwardedHeader + hashtag + date,
                                                                  reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        msg = SendMessageClient1(user2, ForwardedHeader + message + hashtag + date)
                            else:
                                if DateEnd is False:
                                    if len(date+ForwardedHeader+message) > 4096:
                                        msg = SendMessageClient1(user2, message)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date + ForwardedHeader,
                                                                  reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        msg = SendMessageClient1(user2, date + ForwardedHeader + message)
                                else:
                                    if len(ForwardedHeader+message+date) > 4096:
                                        msg = SendMessageClient1(user2, message)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, ForwardedHeader + date,
                                                                  reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        msg = SendMessageClient1(user2, ForwardedHeader + message + date)
                        else:
                            if AppendHashtag is True:
                                if len(ForwardedHeader+message+hashtag) > 4096:
                                    msg = SendMessageClient1(user2, message)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, ForwardedHeader + hashtag,
                                                              reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    msg = SendMessageClient1(user2, ForwardedHeader + message + hashtag)
                            else:
                                if len(ForwardedHeader + message) > 4096:
                                    msg = SendMessageClient1(user2, message)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, ForwardedHeader,
                                                              reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    msg = SendMessageClient1(user2, ForwardedHeader + message)
                else:
                    if fwd_from_id is None:
                        if reply_to_msg_id is None:
                            if NoTimestamps is True:
                                if AppendHashtag is True:
                                    if len(message+hashtag) > 4096:
                                        msg = SendMessageClient2(user1, message)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, hashtag,
                                                                  reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        msg = SendMessageClient2(user1, message + hashtag)
                                else:
                                    msg = SendMessageClient2(user1, message)
                            else:
                                if AppendHashtag is True:
                                    if DateEnd is False:
                                        if len(date+message+hashtag) > 4096:
                                            msg = SendMessageClient2(user1, message)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, date + hashtag,
                                                                      reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, date + message + hashtag)
                                    else:
                                        if len(message+hashtag+date) > 4096:
                                            msg = SendMessageClient2(user1, message)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, hashtag + date,
                                                                      reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, message + hashtag + date)
                                else:
                                    if DateEnd is False:
                                        if len(date+message) > 4096:
                                            msg = SendMessageClient2(user1, message)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, date,
                                                                      reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, date + message)
                                    else:
                                        if len(date+message) > 4096:
                                            msg = SendMessageClient2(user1, message)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, date,
                                                                      reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, message + date)
                        else:
                            if NoTimestamps is True:
                                if AppendHashtag is True:
                                    if len(message + hashtag) > 4096:
                                        msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, hashtag,
                                                                  reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        msg = SendMessageClient2(user1, message + hashtag, reply_to=NewReplyId)
                                else:
                                    msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                            else:
                                if AppendHashtag is True:
                                    if DateEnd is False:
                                        if len(date+message+hashtag) > 4096:
                                            msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, date + hashtag,
                                                                      reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, date + message + hashtag, reply_to=NewReplyId)
                                    else:
                                        if len(message+hashtag+date) > 4096:
                                            msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, hashtag + date,
                                                                      reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, message + hashtag + date, reply_to=NewReplyId)
                                else:
                                    if DateEnd is False:
                                        if len(date + message) > 4096:
                                            msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, date,
                                                                      reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, date + message, reply_to=NewReplyId)
                                    else:
                                        if len(message+date) > 4096:
                                            msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, date,
                                                                      reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, message + date, reply_to=NewReplyId)
                    else:
                        if AgressiveTimestamps is True:
                            if AppendHashtag is True:
                                if DateEnd is False:
                                    if len(date+ForwardedHeader+message+hashtag) > 4096:
                                        msg = SendMessageClient2(user1, message)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date + ForwardedHeader + hashtag,
                                                                  reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        msg = SendMessageClient2(user1, date + ForwardedHeader + message + hashtag)
                                else:
                                    if len(ForwardedHeader+message+hashtag+date) > 4096:
                                        msg = SendMessageClient2(user1, message)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, ForwardedHeader + hashtag + date,
                                                                  reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        msg = SendMessageClient2(user1, ForwardedHeader + message + hashtag + date)
                            else:
                                if DateEnd is False:
                                    if len(date+ForwardedHeader+message) > 4096:
                                        msg = SendMessageClient2(user1, message)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date + ForwardedHeader,
                                                                  reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        msg = SendMessageClient2(user1, date + ForwardedHeader + message)
                                else:
                                    if len(ForwardedHeader+message+date) > 4096:
                                        msg = SendMessageClient2(user1, message)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, ForwardedHeader + date,
                                                                  reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        msg = SendMessageClient2(user1, ForwardedHeader + message + date)
                        else:
                            if AppendHashtag is True:
                                if len(ForwardedHeader+message+hashtag) > 4096:
                                    msg = SendMessageClient2(user1, message)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, ForwardedHeader + hashtag,
                                                              reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    msg = SendMessageClient2(user1, ForwardedHeader + message + hashtag)
                            else:
                                if len(ForwardedHeader+message) > 4096:
                                    msg = SendMessageClient2(user1, message)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, ForwardedHeader,
                                                              reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    msg = SendMessageClient2(user1, ForwardedHeader + message)

            elif has_media is True:
                hintPath = None
                FileName = None
                if (mediaType == "WebPage Preview" and SendAllLinkPreviews is True) or (mediaType == "Animated GIF" and mimeType == "image/gif"):
                    db2 = database.cursor()
                    db2.execute('SELECT * FROM MediaPaths WHERE message_id={id}'.\
                        format(id=id))
                    for row in db2:
                        hintPath = row[2]
                        FileName = row[1]
                    db2.close()

                if (mediaType == "Animated GIF" and mimeType == "image/gif"):
                    if out is True:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is False:
                                    msg = SendFileClient1(user2, file=hintPath, caption=message)
                                else:
                                    if (len(date+message) > 200):
                                        msg2 = SendMessageClient1(user2, date)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                        msg = SendFileClient1(user2, file=hintPath, caption=message, reply_to=msg2.id)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                    else:
                                        msg = SendFileClient1(user2, file=hintPath, caption=date + message)
                            else:
                                if AgressiveTimestamps is False:
                                    msg = SendFileClient1(user2, file=hintPath, caption=message, reply_to=NewReplyId)
                                else:
                                    if (len(date+message) > 200):
                                        msg = SendFileClient1(user2, file=hintPath, caption=message, reply_to=NewReplyId)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        msg = SendFileClient1(user2, file=hintPath, caption=date + message, reply_to=NewReplyId)
                        else:
                            if AgressiveTimestamps is True:
                                if (len(ForwardedHeader+date+message) > 200):
                                    msg2 = SendMessageClient1(user2, date + ForwardedHeader)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                    msg = SendFileClient1(user2, file=hintPath, caption=message, reply_to=msg2.id)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                else:
                                    msg = SendFileClient1(user2, file=hintPath, caption=ForwardedHeader + date + message)                                    
                            else:
                                if not (len(ForwardedHeader+message) > 200):
                                    msg = SendFileClient1(user2, file=hintPath, caption=ForwardedHeader + message)
                                else:
                                    msg2 = SendMessageClient1(user2, ForwardedHeader)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                    msg = SendFileClient1(user2, file=hintPath, caption=ForwardedHeader, reply_to=msg2.id)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)

                    else:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    if (len(date+message) > 200):
                                        msg2 = SendMessageClient2(user1, date)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                        msg = SendFileClient2(user1, file=hintPath, caption=message, reply_to=msg2.id)                                       
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                    else:
                                        msg = SendFileClient2(user1, file=hintPath, caption=date + message)                                        
                                else:
                                    msg = SendFileClient2(user1, file=hintPath, caption=message)
                            else:
                                if AgressiveTimestamps is True:
                                    if (len(date+message) > 200):
                                        msg = SendFileClient2(user1, file=hintPath, caption=message, reply_to=NewReplyId)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date, reply_to=msg.id)                                                                                
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        msg = SendFileClient2(user1, file=hintPath, caption=date + message, reply_to=NewReplyId)
                                else:
                                    msg = SendFileClient2(user1, file=hintPath, caption=message, reply_to=NewReplyId)
                        else:
                            if AgressiveTimestamps is True:
                                if (len(ForwardedHeader+date+message) > 200):
                                    msg2 = SendMessageClient2(user1, date + ForwardedHeader)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                    msg = SendFileClient2(user1, file=hintPath, caption=message, reply_to=msg2.id)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                else:
                                    msg = SendFileClient2(user1, file=hintPath, caption=ForwardedHeader + date + message)
                            else:
                                if (len(ForwardedHeader+message) > 200):
                                    msg2 = SendMessageClient2(user1, ForwardedHeader)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                    msg = SendFileClient2(user1, file=hintPath, caption=message, reply_to=msg2.id)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                else:
                                    msg = SendFileClient2(user1, file=hintPath, caption=ForwardedHeader + message)

                elif mediaType == "Photo":
                    db40 = database.cursor()
                    db40.execute('SELECT * FROM PhotoMediaInfo WHERE message_id={id}'.\
                        format(id=id))
                    DocumentID = None
                    Access_Hash = None
                    AccHash2 = None
                    FileRef = None
                    FileRef2 = None
                    for row in db40:
                        DocumentID = row[1]
                        Access_Hash = row[2]
                        AccHash2 = row[3]
                        FileRef = row[4]
                        FileRef2 = row[5]
                    if out is True:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    if len(date+message) > 200:
                                        request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)                                     
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        if DateEnd is False:
                                            request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=date+message)
                                        else:
                                            request = SendMediaRequest(user2, media=InputMediaPhoto(
                                                id=InputPhoto(id=DocumentID, access_hash=Access_Hash)),
                                                                       message=message + date)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                            else:
                                if AgressiveTimestamps is True:
                                    if len(date+message) > 200:
                                        request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        if DateEnd is False:
                                            request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=date+message, reply_to_msg_id=NewReplyId)
                                        else:
                                            request = SendMediaRequest(user2, media=InputMediaPhoto(
                                                id=InputPhoto(id=DocumentID, access_hash=Access_Hash)),
                                                                       message=message + date,
                                                                       reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message, reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                        else:
                            if AgressiveTimestamps is True:
                                if len(date+ForwardedHeader+message) > 200:
                                    request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    if DateEnd is False:
                                        msg2 = SendMessageClient1(user2, date + ForwardedHeader, reply_to=msg.id)
                                    else:
                                        msg2 = SendMessageClient1(user2, ForwardedHeader + date, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    if DateEnd is False:
                                        request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=date+ForwardedHeader+message)
                                    else:
                                        request = SendMediaRequest(user2, media=InputMediaPhoto(
                                            id=InputPhoto(id=DocumentID, access_hash=Access_Hash)),
                                                                   message=ForwardedHeader + message + date)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                            else:
                                if len(ForwardedHeader+message) > 200:
                                    request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=ForwardedHeader+message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                    else:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    if len(date+message) > 200:
                                        request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        if DateEnd is False:
                                            request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=date+message)
                                        else:
                                            request = SendMediaRequest(user1, media=InputMediaPhoto(
                                                id=InputPhoto(id=DocumentID, access_hash=AccHash2)),
                                                                       message=message + date)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                            else:
                                if AgressiveTimestamps is True:
                                    if len(date+message) > 200:
                                        request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        if DateEnd is False:
                                            request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=date+message, reply_to_msg_id=NewReplyId)
                                        else:
                                            request = SendMediaRequest(user1, media=InputMediaPhoto(
                                                id=InputPhoto(id=DocumentID, access_hash=AccHash2)),
                                                                       message=message + date,
                                                                       reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message, reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                        else:
                            if AgressiveTimestamps is True:
                                if len(date+ForwardedHeader+message) > 200:
                                    request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    if DateEnd is False:
                                        msg2 = SendMessageClient2(user1, date + ForwardedHeader, reply_to=msg.id)
                                    else:
                                        msg2 = SendMessageClient2(user1, ForwardedHeader + date, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=date+ForwardedHeader+message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                            else:
                                if len(ForwardedHeader+message) > 200:
                                    request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, ForwardedHeader, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaPhoto(id=InputPhoto(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=ForwardedHeader+message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                    db40.close()

                elif DocType is True and (mediaType == "StickerPack" or mediaType == "HasSticker" or mediaType == "VideoNote"):
                    db60 = database.cursor()
                    db60.execute('SELECT * FROM DocumentMediaInfo WHERE message_id={id}'. \
                                 format(id=id))
                    DocumentID = None
                    Access_Hash = None
                    AccHash2 = None
                    FileRef = None
                    FileRef2 = None
                    for row in db60:
                        DocumentID = row[1]
                        Access_Hash = row[2]
                        AccHash2 = row[3]
                        FileRef = row[4]
                        FileRef2 = row[5]
                    if out is True:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(
                                        id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(
                                        id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                            else:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(
                                        id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message,
                                                               reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(
                                        id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message,
                                                               reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                        else:
                            if AgressiveTimestamps is True:
                                request = SendMediaRequest(user2, media=InputMediaDocument(
                                    id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                result = SendRequestClient1(request)
                                msg = client1._get_response_message(request, result, user2)
                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                if DateEnd is True:
                                    msg2 = SendMessageClient1(user2, ForwardedHeader + date, reply_to=msg.id)
                                else:
                                    msg2 = SendMessageClient1(user2, date + ForwardedHeader, reply_to=msg.id)
                                User1IDs.append(msg2.id)
                                if not SoloImporting:
                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                            else:
                                request = SendMediaRequest(user2, media=InputMediaDocument(
                                    id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                result = SendRequestClient1(request)
                                msg = client1._get_response_message(request, result, user2)
                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                msg2 = SendMessageClient1(user2, ForwardedHeader, reply_to=msg.id)
                                User1IDs.append(msg2.id)
                                if not SoloImporting:
                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                    else:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(
                                        id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(
                                        id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                            else:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(
                                        id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message,
                                                               reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(
                                        id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message,
                                                               reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                        else:
                            if AgressiveTimestamps is True:
                                request = SendMediaRequest(user1, media=InputMediaDocument(
                                    id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                result = SendRequestClient2(request)
                                msg = client2._get_response_message(request, result, user1)
                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                if DateEnd is True:
                                    msg2 = SendMessageClient2(user1, ForwardedHeader + date, reply_to=msg.id)
                                else:
                                    msg2 = SendMessageClient2(user1, date + ForwardedHeader, reply_to=msg.id)
                                User2IDs.append(msg2.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))
                            else:
                                request = SendMediaRequest(user1, media=InputMediaDocument(
                                    id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                result = SendRequestClient2(request)
                                msg = client2._get_response_message(request, result, user1)
                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                msg2 = SendMessageClient2(user1, ForwardedHeader, reply_to=msg.id)
                                User2IDs.append(msg2.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))
                    db60.close()

                elif DocType is True:
                    db60 = database.cursor()
                    db60.execute('SELECT * FROM DocumentMediaInfo WHERE message_id={id}'.\
                        format(id=id))
                    DocumentID = None
                    Access_Hash = None
                    AccHash2 = None
                    FileRef = None
                    FileRef2 = None
                    for row in db60:
                        DocumentID = row[1]
                        Access_Hash = row[2]
                        AccHash2 = row[3]
                        FileRef = row[4]
                        FileRef2 = row[5]
                    if out is True:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    if len(date+message) > 200:
                                        request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)                                     
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        if DateEnd is False:
                                            request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=date+message)
                                        else:
                                            request = SendMediaRequest(user2, media=InputMediaDocument(
                                                id=InputDocument(id=DocumentID, access_hash=Access_Hash)),
                                                                       message=message + date)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                            else:
                                if AgressiveTimestamps is True:
                                    if len(date+message) > 200:
                                        request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        if DateEnd is False:
                                            request = SendMediaRequest(user2, media=InputMediaDocument(
                                                id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)),
                                                                       message=date + message,
                                                                       reply_to_msg_id=NewReplyId)
                                        else:
                                            request = SendMediaRequest(user2, media=InputMediaDocument(
                                                id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)),
                                                                       message=message + date,
                                                                       reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message, reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                        else:
                            if AgressiveTimestamps is True:
                                if len(date+ForwardedHeader+message) > 200:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    if DateEnd is True:
                                        msg2 = SendMessageClient1(user2, ForwardedHeader + date, reply_to=msg.id)
                                    else:
                                        msg2 = SendMessageClient1(user2, date + ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    if DateEnd is False:
                                        request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=date+ForwardedHeader+message)
                                    else:
                                        request = SendMediaRequest(user2, media=InputMediaDocument(
                                            id=InputDocument(id=DocumentID, access_hash=Access_Hash)),
                                                                   message=ForwardedHeader + message + date)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                            else:
                                if len(ForwardedHeader+message) > 200:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=Access_Hash, file_reference=FileRef)), message=ForwardedHeader+message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                    else:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    if len(date+message) > 200:
                                        request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        if DateEnd is False:
                                            request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=date+message)
                                        else:
                                            request = SendMediaRequest(user1, media=InputMediaDocument(
                                                id=InputDocument(id=DocumentID, access_hash=AccHash2)),
                                                                       message=message + date)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                            else:
                                if AgressiveTimestamps is True:
                                    if len(date+message) > 200:
                                        request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        if DateEnd is False:
                                            request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=date+message, reply_to_msg_id=NewReplyId)
                                        else:
                                            request = SendMediaRequest(user1, media=InputMediaDocument(
                                                id=InputDocument(id=DocumentID, access_hash=AccHash2)),
                                                                       message=message + date,
                                                                       reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message, reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                        else:
                            if AgressiveTimestamps is True:
                                if len(date+ForwardedHeader+message) > 200:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    if DateEnd is True:
                                        msg2 = SendMessageClient2(user1, ForwardedHeader + date, reply_to=msg.id)
                                    else:
                                        msg2 = SendMessageClient2(user1, date + ForwardedHeader, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    if DateEnd is False:
                                        request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=date+ForwardedHeader+message)
                                    else:
                                        request = SendMediaRequest(user1, media=InputMediaDocument(
                                            id=InputDocument(id=DocumentID, access_hash=AccHash2)),
                                                                   message=ForwardedHeader + message + date)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                            else:
                                if len(ForwardedHeader+message) > 200:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, ForwardedHeader, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaDocument(id=InputDocument(id=DocumentID, access_hash=AccHash2, file_reference=FileRef2)), message=ForwardedHeader+message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                    db60.close()

                elif mediaType == "Contact":
                    db4 = database.cursor()
                    db4.execute('SELECT * FROM ContactMediaInfo WHERE message_id={id}'.\
                        format(id=id))
                    for row in db4:
                        first_name = row[1]
                        last_name = row[2]
                        phoneNumber = row[3]
                        vcard = row[4]
                        if out is True:
                            if fwd_from_id is None:
                                if reply_to_msg_id is None:
                                    if AgressiveTimestamps is True:
                                        request = SendMediaRequest(user2, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))

                                    else:
                                        request = SendMediaRequest(user2, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                else:
                                    if AgressiveTimestamps is True:
                                        request = SendMediaRequest(user2, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        request = SendMediaRequest(user2, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                            else:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user2, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    if DateEnd is True:
                                        msg2 = SendMessageClient1(user2, ForwardedHeader + date, reply_to=msg.id)
                                    else:
                                        msg2 = SendMessageClient1(user2, date + ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                        else:
                            if fwd_from_id is None:
                                if reply_to_msg_id is None:
                                    if AgressiveTimestamps is True:
                                        request = SendMediaRequest(user1, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        request = SendMediaRequest(user1, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                else:
                                    if AgressiveTimestamps is True:
                                        request = SendMediaRequest(user1, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                        msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                    else:
                                        request = SendMediaRequest(user1, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient2(request)
                                        msg = client2._get_response_message(request, result, user1)
                            else:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user1, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    if DateEnd is True:
                                        msg2 = SendMessageClient2(user1, ForwardedHeader + date, reply_to=msg.id)
                                    else:
                                        msg2 = SendMessageClient2(user1, date + ForwardedHeader, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaContact(phoneNumber, first_name, last_name, vcard), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, ForwardedHeader, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                    db4.close()

                elif mediaType == "Game":
                    if out is True:
                        if AgressiveTimestamps is True:
                            OrigMessage = ForwardMessageClient1(SelfUser1, id, ChosenChat)
                            msg = ForwardMessageClient1(user2, OrigMessage)
                            NewUser2ID = GetIncomingIdOfUser1(user1)
                            DeleteMessageClient1(SelfUser1, OrigMessage)
                            msg2 = SendMessageClient1(user2, message=date, reply_to=msg.id)
                            User1IDs.append(msg2.id)
                            if not SoloImporting:
                                User2IDs.append(GetIncomingIdOfUser1(user1))
                        else:
                            OrigMessage = ForwardMessageClient1(SelfUser1, id, ChosenChat)
                            msg = ForwardMessageClient1(user2, OrigMessage)
                            DeleteMessageClient1(SelfUser1, OrigMessage)
                    else:
                        if AgressiveTimestamps is True:
                            OrigMessage = ForwardMessageClient1(SelfUser1, id, ChosenChat)
                            NewMessage = ForwardMessageClient1(user2, OrigMessage)
                            DeleteMessageClient1(SelfUser1, OrigMessage)
                            GotMessageID = GetIncomingIdOfUser1(user1)
                            GotMessage = ForwardMessageClient2(SelfUser2, GotMessageID, user1)
                            msg = ForwardMessageClient2(user1, GotMessage)
                            NewUser1ID = GetIncomingIdOfUser2(user2)
                            DeleteMessageClient2(SelfUser2, GotMessage)
                            msg2 = SendMessageClient2(user1, message=date, reply_to=msg.id)
                            User2IDs.append(msg2.id)
                            User1IDs.append(GetIncomingIdOfUser2(user2))
                        else:
                            OrigMessage = ForwardMessageClient1(SelfUser1, id, ChosenChat)
                            NewMessage = ForwardMessageClient1(user2, OrigMessage)
                            DeleteMessageClient1(SelfUser1, OrigMessage)
                            GotMessageID = GetIncomingIdOfUser1(user1)
                            GotMessage = ForwardMessageClient2(SelfUser2, GotMessageID, user1)
                            msg = ForwardMessageClient2(user1, GotMessage)
                            DeleteMessageClient2(SelfUser2, GotMessage)

                elif mediaType == "Venue":
                    db6 = database.cursor()
                    db6.execute('SELECT * FROM VenueMediaInfo WHERE message_id={id}'.\
                        format(id=id))
                    long = None
                    lat = None
                    title = None
                    address = None
                    provider = None
                    venue_id = None
                    venue_type = None
                    for row in db6:
                        long = row[1]
                        lat = row[2]
                        title = row[3]
                        address = row[4]
                        provider = row[5]
                        venue_id = row[6]
                        venue_type = row[7]
                    if out is True:
                            if fwd_from_id is None:
                                if reply_to_msg_id is None:
                                    if AgressiveTimestamps is True:
                                        request = SendMediaRequest(user2, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        request = SendMediaRequest(user2, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                else:
                                    if AgressiveTimestamps is True:
                                        request = SendMediaRequest(user2, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        request = SendMediaRequest(user2, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                            else:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user2, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    if DateEnd is True:
                                        msg2 = SendMessageClient1(user2, ForwardedHeader + date, reply_to=msg.id)
                                    else:
                                        msg2 = SendMessageClient1(user2, date + ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                    else:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user1, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                            else:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user1, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message, reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message, reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                        else:
                            if AgressiveTimestamps is True:
                                request = SendMediaRequest(user1, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message)
                                result = SendRequestClient2(request)
                                msg = client2._get_response_message(request, result, user1)
                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                if DateEnd is True:
                                    msg2 = SendMessageClient2(user1, ForwardedHeader + date, reply_to=msg.id)
                                else:
                                    msg2 = SendMessageClient2(user1, date + ForwardedHeader, reply_to=msg.id)
                                User2IDs.append(msg2.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))
                            else:
                                request = SendMediaRequest(user1, media=InputMediaVenue(InputGeoPoint(lat, long), title, address, provider, venue_id, venue_type), message=message)
                                result = SendRequestClient2(request)
                                msg = client2._get_response_message(request, result, user1)
                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                msg2 = SendMessageClient2(user1, ForwardedHeader, reply_to=msg.id)
                                User2IDs.append(msg2.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))
                    db6.close()

                elif mediaType == "Geo":
                    db7 = database.cursor()
                    db7.execute('SELECT * FROM GeoMediaInfo WHERE message_id={id}'.\
                        format(id=id))
                    long = None
                    lat = None
                    for row in db7:
                        long = row[1]
                        lat = row[2]
                    if out is True:
                            if fwd_from_id is None:
                                if reply_to_msg_id is None:
                                    if AgressiveTimestamps is True:
                                        request = SendMediaRequest(user2, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message)                                        
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        request = SendMediaRequest(user2, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                else:
                                    if AgressiveTimestamps is True:
                                        request = SendMediaRequest(user2, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                        msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                    else:
                                        request = SendMediaRequest(user2, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message, reply_to_msg_id=NewReplyId)
                                        result = SendRequestClient1(request)
                                        msg = client1._get_response_message(request, result, user2)
                            else:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user2, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    if DateEnd is True:
                                        msg2 = SendMessageClient1(user2, ForwardedHeader + date, reply_to=msg.id)
                                    else:
                                        msg2 = SendMessageClient1(user2, date + ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                                else:
                                    request = SendMediaRequest(user2, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message)
                                    result = SendRequestClient1(request)
                                    msg = client1._get_response_message(request, result, user2)
                                    NewUser2ID = GetIncomingIdOfUser1(user1)
                                    msg2 = SendMessageClient1(user2, ForwardedHeader, reply_to=msg.id)
                                    User1IDs.append(msg2.id)
                                    if not SoloImporting:
                                        User2IDs.append(GetIncomingIdOfUser1(user1))
                    else:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user1, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                            else:
                                if AgressiveTimestamps is True:
                                    request = SendMediaRequest(user1, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message, reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                                    NewUser1ID = GetIncomingIdOfUser2(user2)
                                    msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                    User2IDs.append(msg2.id)
                                    User1IDs.append(GetIncomingIdOfUser2(user2))
                                else:
                                    request = SendMediaRequest(user1, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message, reply_to_msg_id=NewReplyId)
                                    result = SendRequestClient2(request)
                                    msg = client2._get_response_message(request, result, user1)
                        else:
                            if AgressiveTimestamps is True:
                                request = SendMediaRequest(user1, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message)
                                result = SendRequestClient2(request)
                                msg = client2._get_response_message(request, result, user1)
                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                if DateEnd is True:
                                    msg2 = SendMessageClient2(user1, ForwardedHeader + date, reply_to=msg.id)
                                else:
                                    msg2 = SendMessageClient2(user1, date + ForwardedHeader, reply_to=msg.id)
                                User2IDs.append(msg2.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))
                            else:
                                request = SendMediaRequest(user1, media=InputMediaGeoPoint(InputGeoPoint(lat, long)), message=message)
                                result = SendRequestClient2(request)
                                msg = client2._get_response_message(request, result, user1)
                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                msg2 = SendMessageClient2(user1, ForwardedHeader, reply_to=msg.id)
                                User2IDs.append(msg2.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))
                    db7.close()

                elif SendAllLinkPreviews is True and mediaType == "WebPage Preview":
                    PreviewCaption = "`Original Link Preview 👆🏻`"
                    if out is True:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if NoTimestamps is False:
                                    if AppendHashtag is True:
                                        if DateEnd is False:
                                            if len(date+message+hashtag) > 4096:
                                                msg2 = SendMessageClient1(user2, date + hashtag)
                                                User1IDs.append(msg2.id)
                                                if not SoloImporting:
                                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                                                msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                            else:
                                                msg = SendMessageClient1(user2, date + message + hashtag)
                                        else:
                                            if len(date+message+hashtag) > 4096:
                                                msg2 = SendMessageClient1(user2, hashtag + date)
                                                User1IDs.append(msg2.id)
                                                if not SoloImporting:
                                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                                                msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                            else:
                                                msg = SendMessageClient1(user2, message + hashtag + date)
                                    else:
                                        if DateEnd is False:
                                            if len(date + message) > 4096:
                                                msg2 = SendMessageClient1(user2, date)
                                                User1IDs.append(msg2.id)
                                                if not SoloImporting:
                                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                                                msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                            else:
                                                msg = SendMessageClient1(user2, date + message)
                                        else:
                                            if len(date + message) > 4096:
                                                msg2 = SendMessageClient1(user2, date)
                                                User1IDs.append(msg2.id)
                                                if not SoloImporting:
                                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                                                msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                            else:
                                                msg = SendMessageClient1(user2, message + date)
                                else:
                                    if AppendHashtag is True:
                                        if len(message+hashtag) > 4096:
                                            msg2 = SendMessageClient1(user2, hashtag)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                            msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient1(user2, message + hashtag)
                                    else:
                                        msg = SendMessageClient1(user2, message)
                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                msg3 = SendFileClient1(user2, file=hintPath, caption=PreviewCaption, reply_to=msg.id, parse_mode="md")
                                User1IDs.append(msg3.id)
                                if not SoloImporting:
                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                            else:
                                if NoTimestamps is True:
                                    if AppendHashtag is True:
                                        if len(message + hashtag) > 4096:
                                            msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                            msg2 = SendMessageClient1(user2, hashtag, reply_to=msg.id)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                        else:
                                            msg = SendMessageClient1(user2, message + hashtag, reply_to=NewReplyId)
                                            NewUser2ID = GetIncomingIdOfUser1(user1)
                                    else:
                                        msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                                        NewUser2ID = GetIncomingIdOfUser1(user1)
                                else:
                                    if AppendHashtag is True:
                                        if DateEnd is False:
                                            if len(date+message+hashtag) > 4096:
                                                msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                                msg2 = SendMessageClient1(user2, date + hashtag, reply_to=msg.id)
                                                User1IDs.append(msg2.id)
                                                if not SoloImporting:
                                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                                            else:
                                                msg = SendMessageClient1(user2, date + message + hashtag, reply_to=NewReplyId)
                                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                        else:
                                            if len(message+hashtag+date) > 4096:
                                                msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                                msg2 = SendMessageClient1(user2, hashtag + date, reply_to=msg.id)
                                                User1IDs.append(msg2.id)
                                                if not SoloImporting:
                                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                                            else:
                                                msg = SendMessageClient1(user2, message + hashtag + date,
                                                                         reply_to=NewReplyId)
                                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                    else:
                                        if DateEnd is False:
                                            if len(date+message) > 4096:
                                                msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                                msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                                User1IDs.append(msg2.id)
                                                if not SoloImporting:
                                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                                            else:
                                                msg = SendMessageClient1(user2, date + message, reply_to=NewReplyId)
                                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                        else:
                                            if len(message+date) > 4096:
                                                msg = SendMessageClient1(user2, message, reply_to=NewReplyId)
                                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                                msg2 = SendMessageClient1(user2, date, reply_to=msg.id)
                                                User1IDs.append(msg2.id)
                                                if not SoloImporting:
                                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                                            else:
                                                msg = SendMessageClient1(user2, message + date, reply_to=NewReplyId)
                                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                msg3 = SendFileClient1(user2, file=hintPath, caption=PreviewCaption, reply_to=msg.id, parse_mode="md")
                                User1IDs.append(msg3.id)
                                if not SoloImporting:
                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                        else:
                            if AgressiveTimestamps is True:
                                if AppendHashtag is True:
                                    if DateEnd is False:
                                        if len(date+ForwardedHeader+message+hashtag) > 4096:
                                            msg2 = SendMessageClient1(user2, date + ForwardedHeader + hashtag)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                            msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient1(user2, date + ForwardedHeader + message + hashtag)
                                    else:
                                        if len(date+ForwardedHeader+message+hashtag) > 4096:
                                            msg2 = SendMessageClient1(user2, ForwardedHeader + hashtag + date)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                            msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient1(user2, ForwardedHeader + message + hashtag + date)
                                else:
                                    if DateEnd is False:
                                        if len(date+ForwardedHeader+message) > 4096:
                                            msg2 = SendMessageClient1(user2, date + ForwardedHeader)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                            msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient1(user2, date + ForwardedHeader + message)
                                    else:
                                        if len(date+ForwardedHeader+message) > 4096:
                                            msg2 = SendMessageClient1(user2, ForwardedHeader + date)
                                            User1IDs.append(msg2.id)
                                            if not SoloImporting:
                                                User2IDs.append(GetIncomingIdOfUser1(user1))
                                            msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient1(user2, ForwardedHeader + message + date)
                            else:
                                if AppendHashtag is True:
                                    if len(date + ForwardedHeader + message) > 4096:
                                        msg2 = SendMessageClient1(user2, ForwardedHeader + hashtag)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                        msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                    else:
                                        msg = SendMessageClient1(user2, ForwardedHeader + message + hashtag)
                                else:
                                    if len(date + ForwardedHeader + message) > 4096:
                                        msg2 = SendMessageClient1(user2, ForwardedHeader)
                                        User1IDs.append(msg2.id)
                                        if not SoloImporting:
                                            User2IDs.append(GetIncomingIdOfUser1(user1))
                                        msg = SendMessageClient1(user2, message, reply_to=msg2.id)
                                    else:
                                        msg = SendMessageClient1(user2, ForwardedHeader + message)
                                NewUser2ID = GetIncomingIdOfUser1(user1)
                                msg3 = SendFileClient1(user2, file=hintPath, caption=PreviewCaption, reply_to=msg.id, parse_mode="md")
                                User1IDs.append(msg3.id)
                                if not SoloImporting:
                                    User2IDs.append(GetIncomingIdOfUser1(user1))
                    else:
                        if fwd_from_id is None:
                            if reply_to_msg_id is None:
                                if NoTimestamps is True:
                                    if AppendHashtag is True:
                                        if len(message + hashtag) > 4096:
                                            msg2 = SendMessageClient2(user1, hashtag)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                            msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient2(user1, message + hashtag)
                                    else:
                                        msg = SendMessageClient2(user1, message)
                                else:
                                    if AppendHashtag is True:
                                        if DateEnd is False:
                                            if len(date + message + hashtag) > 4096:
                                                msg2 = SendMessageClient2(user1, date + hashtag)
                                                User2IDs.append(msg2.id)
                                                User1IDs.append(GetIncomingIdOfUser2(user2))
                                                msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                            else:
                                                msg = SendMessageClient2(user1, date + message + hashtag)
                                        else:
                                            if len(message+hashtag+date) > 4096:
                                                msg2 = SendMessageClient2(user1, hashtag + date)
                                                User2IDs.append(msg2.id)
                                                User1IDs.append(GetIncomingIdOfUser2(user2))
                                                msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                            else:
                                                msg = SendMessageClient2(user1, message + hashtag + date)
                                    else:
                                        if DateEnd is False:
                                            if len(date+message) > 4096:
                                                msg2 = SendMessageClient2(user1, date)
                                                User2IDs.append(msg2.id)
                                                User1IDs.append(GetIncomingIdOfUser2(user2))
                                                msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                            else:
                                                msg = SendMessageClient2(user1, date + message)
                                        else:
                                            if len(date+message) > 4096:
                                                msg2 = SendMessageClient2(user1, date)
                                                User2IDs.append(msg2.id)
                                                User1IDs.append(GetIncomingIdOfUser2(user2))
                                                msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                            else:
                                                msg = SendMessageClient2(user1, message + date)
                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                msg3 = SendFileClient2(user1, file=hintPath, caption=PreviewCaption, reply_to=msg.id, parse_mode="md")
                                User2IDs.append(msg3.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))
                            else:
                                if NoTimestamps is True:
                                    if AppendHashtag is True:
                                        if len(message + hashtag) > 4096:
                                            msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                            msg2 = SendMessageClient2(user1, hashtag, reply_to=msg.id)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                        else:
                                            msg = SendMessageClient2(user1, message + hashtag, reply_to=NewReplyId)
                                            NewUser1ID = GetIncomingIdOfUser2(user2)
                                    else:
                                        msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                        NewUser1ID = GetIncomingIdOfUser2(user2)
                                else:
                                    if AppendHashtag is True:
                                        if DateEnd is False:
                                            if len(date+message+hashtag) > 4096:
                                                msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                                msg2 = SendMessageClient2(user1, date + hashtag, reply_to=msg.id)
                                                User2IDs.append(msg2.id)
                                                User1IDs.append(GetIncomingIdOfUser2(user2))
                                            else:
                                                msg = SendMessageClient2(user1, date + message + hashtag, reply_to=NewReplyId)
                                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                        else:
                                            if len(message+hashtag+date) > 4096:
                                                msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                                msg2 = SendMessageClient2(user1, hashtag + date, reply_to=msg.id)
                                                User2IDs.append(msg2.id)
                                                User1IDs.append(GetIncomingIdOfUser2(user2))
                                            else:
                                                msg = SendMessageClient2(user1, message + hashtag + date,
                                                                     reply_to=NewReplyId)
                                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                    else:
                                        if DateEnd is False:
                                            if len(date + message) > 4096:
                                                msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                                msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                                User2IDs.append(msg2.id)
                                                User1IDs.append(GetIncomingIdOfUser2(user2))
                                            else:
                                                msg = SendMessageClient2(user1, date + message, reply_to=NewReplyId)
                                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                        else:
                                            if len(date + message) > 4096:
                                                msg = SendMessageClient2(user1, message, reply_to=NewReplyId)
                                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                                msg2 = SendMessageClient2(user1, date, reply_to=msg.id)
                                                User2IDs.append(msg2.id)
                                                User1IDs.append(GetIncomingIdOfUser2(user2))
                                            else:
                                                msg = SendMessageClient2(user1, message + date, reply_to=NewReplyId)
                                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                msg3 = SendFileClient2(user1, file=hintPath, caption=PreviewCaption, reply_to=msg.id, parse_mode="md")
                                User2IDs.append(msg3.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))
                        else:
                            if AgressiveTimestamps is True:
                                if AppendHashtag is True:
                                    if DateEnd is False:
                                        if len(date+ForwardedHeader+message+hashtag) > 4096:
                                            msg2 = SendMessageClient2(user1, date + ForwardedHeader + hashtag)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                            msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient2(user1, date + ForwardedHeader + message + hashtag)
                                    else:
                                        if len(ForwardedHeader + message + hashtag + date) > 4096:
                                            msg2 = SendMessageClient2(user1, ForwardedHeader + hashtag + date)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                            msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient2(user1, ForwardedHeader + message + hashtag + date)
                                else:
                                    if DateEnd is False:
                                        if len(date+ForwardedHeader+message) > 4096:
                                            msg2 = SendMessageClient2(user1, date + ForwardedHeader)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                            msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient2(user1, date + ForwardedHeader + message)
                                    else:
                                        if len(ForwardedHeader + message + date) > 4096:
                                            msg2 = SendMessageClient2(user1, ForwardedHeader + date)
                                            User2IDs.append(msg2.id)
                                            User1IDs.append(GetIncomingIdOfUser2(user2))
                                            msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                        else:
                                            msg = SendMessageClient2(user1, ForwardedHeader + message + date)
                            else:
                                if AppendHashtag is True:
                                    if len(ForwardedHeader+message+hashtag) > 4096:
                                        msg2 = SendMessageClient2(user1, ForwardedHeader + hashtag)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                        msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                    else:
                                        msg = SendMessageClient2(user1, ForwardedHeader + message + hashtag)
                                else:
                                    if len(ForwardedHeader+message) > 4096:
                                        msg2 = SendMessageClient2(user1, ForwardedHeader)
                                        User2IDs.append(msg2.id)
                                        User1IDs.append(GetIncomingIdOfUser2(user2))
                                        msg = SendMessageClient2(user1, message, reply_to=msg2.id)
                                    else:
                                        msg = SendMessageClient2(user1, ForwardedHeader + message)
                                NewUser1ID = GetIncomingIdOfUser2(user2)
                                msg3 = SendFileClient2(user1, file=hintPath, caption=PreviewCaption, reply_to=msg.id, parse_mode="md")
                                User2IDs.append(msg3.id)
                                User1IDs.append(GetIncomingIdOfUser2(user2))

                else:
                    logging.warning("TLMERGER EXCEPTION IN EXPORTINGMESSAGES: Media conditions weren't met while exporting messages. Message ID: " + str(id) + ". Unknown Class: " + UnkownClass)
                    print("\nAn error happened and it has been written inside the log.")
                    Errors = True
            cursor = database.cursor()
            if out is True:
                User1IDs.append(msg.id)
                if not SoloImporting:
                    client2.send_read_acknowledge(user1, max_id=0)
                    if NewUser2ID is None:
                        NewUser2ID = GetIncomingIdOfUser1(user1)
                    User2IDs.append(NewUser2ID)
                    reg = (id, msg.id, NewUser2ID)
                else:
                    reg = (id, msg.id, msg.id)
                cursor.execute("INSERT INTO NewChat VALUES(?,?,?)", reg)
            else:
                client1.send_read_acknowledge(user2, max_id=0)
                User2IDs.append(msg.id)
                if NewUser1ID is None:
                    NewUser1ID = GetIncomingIdOfUser2(user2)
                User1IDs.append(NewUser1ID)
                reg1 = (id, NewUser1ID, msg.id)
                cursor.execute("INSERT INTO NewChat VALUES(?,?,?)", reg1)
            cursor.close()
            del cursor
            completed = (completed + 1)
            RawLoopCount = RawLoopCount + 1
            bar.update(completed)
            # Seems that with modern Telethon versions flood waitings are really fine tuned, so let it handle them is the best idea. Instead,
            # we refresh the file references each 2000 messages.
            # if RawLoopCount == 2000:
            if RawLoopCount == 1000:
                # time.sleep(420)
                if not SoloImporting:
                    RefreshFileRefs(user1, user2)
                else:
                    RefreshFileRefs(None, user2)
                RawLoopCount = 0
        client1.send_read_acknowledge(user2, max_id=0)
        if not SoloImporting:
            client2.send_read_acknowledge(user1, max_id=0)
        if Warnings is True or Errors is True:
            confirm = SendMessageClient1(user2, "✅⚠️ **SUCCESS WITH SOME ERRORS!!**\nThe messages were merged successfully, but some messages couldn't be handled properly by TLMerger. You can see more details in the 'TLMerger-log.log' file, which is in the same folder where you run TLMerger. Thank you very much for using TLMerger!\n\n**--ferferga** ✅⚠️")
        else:
            confirm = SendMessageClient1(user2, "✅ **SUCCESS!!**\nSuccessfully merged " + str(count) + " messages. Thank you very much for using TLMerger!\n\n**--ferferga** ✅")
        User1IDs.append(confirm.id)
        if not SoloImporting:
            User2IDs.append(GetIncomingIdOfUser1(user1))
        bar.finish()
        print("\n\n")
        if not SoloImporting:
            reg8 = (SelfUser1.id, SelfUser2.id, SelfUser1.first_name + " (+" + SelfUser1.phone + ")", SelfUser2.first_name + " (+" + SelfUser2.phone + ")", client1.get_messages(user2, limit=0).total, client2.get_messages(user1, limit=0).total, count, SoloImporting)
        else:
            reg8 = (SelfUser1.id, None, SelfUser1.first_name + " (+" + SelfUser1.phone + ")",
                    None, client1.get_messages(user1, limit=0).total,
                    None, count, SoloImporting)
        database.execute("INSERT INTO Statistics VALUES(?,?,?,?,?,?,?,?)", reg8)
        if Errors is False:
            print("\nThe process has been finished. No known errors were found.")
        else:
            print("\nThe process has been finished. Some errors were found and were written to 'TLMerger-log.log' file.")
        print("\nSaving changes into the database...")
        CommitMessages(database, False)
        if DeleteOriginalMessages is True:
            print("You have chosen to delete the original messages. Deleting them now...\nThis might take a while.")
            IDsToDelete = []
            db20 = database.cursor()
            db20.execute('SELECT * FROM OriginalChat')
            for row in db20:
                IDsToDelete.append(row[2])
            db20.close()
            DeleteMessageClient1(ChosenChat, message_ids=IDsToDelete)
            del IDsToDelete
        DBConnection(False, True)
        print("Changes saved! You will be able to use TLRevert to revert the changes made by TLMerger in the future, and remove all the messages sent by the application.")
        if SendDatabase is True:
            print("You have chosen to make a copy of your database in your 'Saved Messages' inside Telegram.\nBacking up database...")
            databasecopy = SendFileClient1(SelfUser1, file="data\TLMerger-Database.db",
                                           caption="This is the TLMerger's database with " + peer)
            SendMessageClient1(SelfUser1,
                               "💾 You can read this database using programs like https://github.com/sqlitebrowser/sqlitebrowser/releases. This database is **mandatory** if you want to use [TLRevert](https://github.com/TelegramTools/TLRevert) in order to revert all the changes made by TLMerger. Read the manuals of both programs if you have any doubt about them. **Thank you very much for using** [TLMerger](https://github.com/TelegramTools/TLMerger)**!**\n\n**--ferferga**", reply_to=databasecopy.id)

    except KeyboardInterrupt:

        bar.finish()
        print("\nThe process has been cancelled. Saving changes in the database...")
        if not SoloImporting:
            DeleteMessageClient1(SelfUser2, message_ids=FetchableMsgIDs, revoke=True)
            reg8 = (SelfUser1.id, SelfUser2.id, SelfUser1.first_name + " (+" + SelfUser1.phone + ")", SelfUser2.first_name + " (+" + SelfUser2.phone + ")", client1.get_messages(user2, limit=0).total, client2.get_messages(user1, limit=0).total, count, SoloImporting)
        else:
            reg8 = (SelfUser1.id, None, SelfUser1.first_name + " (+" + SelfUser1.phone + ")",
                    None, client1.get_messages(user1, limit=0).total,
                    None, count, SoloImporting)
        database.execute("INSERT INTO Statistics VALUES(?,?,?,?,?,?,?,?)", reg8)
        CommitMessages(database, False)
        DBConnection(False, True)
        print("Changes saved! You will be able to use TLRevert to revert the changes made by TLMerger in the future, and remove all the messages sent by the application.\nYou will need to start from scratch if you want to continue the merging process later.")
        if SendDatabase is True:
            print("You have chosen to make a copy of your database in your 'Saved Messages' inside Telegram.\nBacking up database...")
            databasecopy = SendFileClient1(SelfUser1, file="data\TLMerger-Database.db",
                                           caption="This is the TLMerger's database with " + peer)
            SendMessageClient1(SelfUser1,
                               "💾 You can read this database using programs like https://github.com/sqlitebrowser/sqlitebrowser/releases. This database is **mandatory** if you want to use [TLRevert](https://github.com/TelegramTools/TLRevert) in order to revert all the changes made by TLMerger. Read the manuals of both programs if you have any doubt about them. **Thank you very much for using** [TLMerger](https://github.com/TelegramTools/TLMerger)**!**\n\n**--ferferga**", reply_to=databasecopy.id)
        else:
            return

    except Exception as e:
        logging.exception("TLMERGER EXCEPTION IN EXPORTINGMESSAGES: " + str(e))
        bar.finish()
        print("Something went wrong in our side. This is the full exception:\n\n"  + str(e))
        print("\nSaving changes in the database, so you can use TLRevert to revert the changes made by TLMerger and remove all the messages sent by the application...")
        if not SoloImporting:
            DeleteMessageClient1(SelfUser2, message_ids=FetchableMsgIDs, revoke=True)
            reg8 = (SelfUser1.id, SelfUser2.id, SelfUser1.first_name + " (+" + SelfUser1.phone + ")", SelfUser2.first_name + " (+" + SelfUser2.phone + ")", client1.get_messages(user2, limit=0).total, client2.get_messages(user1, limit=0).total, count, SoloImporting)
        else:
            reg8 = (SelfUser1.id, None, SelfUser1.first_name + " (+" + SelfUser1.phone + ")",
                    None, client1.get_messages(user1, limit=0).total,
                    None, count, SoloImporting)
        database.execute("INSERT INTO Statistics VALUES(?,?,?,?,?,?,?,?)", reg8)
        CommitMessages(database, False)
        DBConnection(False, True)
        if SendDatabase is True:
            print("You have chosen to make a copy of your database in your 'Saved Messages' inside Telegram.\nBacking up database...")
            databasecopy = SendFileClient1(SelfUser1, file="data\TLMerger-Database.db",
                                           caption="This is the TLMerger's database with " + peer)
            SendMessageClient1(SelfUser1,
                               "💾 You can read this database using programs like https://github.com/sqlitebrowser/sqlitebrowser/releases. This database is **mandatory** if you want to use [TLRevert](https://github.com/TelegramTools/TLRevert) in order to revert all the changes made by TLMerger. Read the manuals of both programs if you have any doubt about them. **Thank you very much for using** [TLMerger](https://github.com/TelegramTools/TLMerger)**!**\n\n**--ferferga**", reply_to=databasecopy.id)
        getpass("This part of the process can't be recovered. Press ENTER to close the app...")
        exit(0)

def DBConnection(first, close):
    try:
        conn = sqlite3.connect("data\TLMerger-Database.db", timeout=10)        
        if first is True:
            print("Created database successfully!")
        if close is True:
            conn.close()
            return
        return conn        
    except sqlite3.OperationalError:
        print("ERROR 1: DATABASE OPERATION ERROR! Trying again...")
        DBConnection(first, close)

def Checkings():
    database = DBConnection(False, False)
    db = database.cursor()
    db.execute('SELECT * FROM OriginalChat')
    UnknownType = False
    UnknownClass = None
    for row in db:
        UnknownType = row[14] #bool
        if (row[12] == "Unsupported" or row[12] == "Unknown"):
            logging.warning("TLMERGER EXCEPTION! Unsupported Media messages found during the database checkings: " + row[15])
            print("Some unsupported media messages were found. You can continue without any problem, but some media might be missing. \nHere is all the information we know: " + row[15])
            Warnings = True
        elif UnknownType is True:
            logging.warning("TLMERGER EXCEPTION!: Unkown messages found during the database checkings. Class: " + row[15])
            print("Some Unknown messages were found in the chat. You should check if there are available updates for TLMerger or report this error\nHere is the full information: " + row[15])
            Warnings = True
    return

##ENTRY POINT OF THE CODE
try:
    os.remove("TLMerger-log.log")
except:
    pass
logging.basicConfig(filename="TLMerger-log.log", level=logging.DEBUG, format='%(asctime)s %(message)s')
print("Hello! WELCOME TO TELEGRAM CHAT MERGER.\n\nThis tiny script made by ferferga will copy all the media and messages from a chat to another conversation.")
print("\n\nLogging you into Telegram...")
StartClient1()
print("\n\nYou are logged in as " + SelfUser1.first_name + "!")
if os.path.exists("data") is True:
    shutil.rmtree('data', ignore_errors=True)
os.mkdir('data')
print("\nCreating database...")	
database = DBConnection(True, False)
CreateTables(database)
print("By default, Telegram returns the hours in GMT+0. If this is not your timezone, please, write how many hours we need to add or substract for your timezone")
print("\nExamples: If GMT+1, type 1. If it's GMT-9, type -9. If it's GMT+0, type 0.")
while True:
    try:
        timezonediff = int(input("How much we need to sum/substract to the hours?: "))
        break
    except ValueError:
        print("This is not a valid number, please, try again\n")
getpass("\nNow, you must choose the chat from which we are going to copy the messages: The 'Source' chat. Press ENTER to continue: ")
print("Gathering chat list from " + SelfUser1.first_name + "...")
ChosenChat = PrintChatList()
GatherAllMessages(ChosenChat)
print("\n\nChecking the database's data...")
Checkings()
if Warnings is True:
    print("WARNING: Take in mind that some unknown messages were detected in the database. This means that some messages can be missed by TLMerger and they won't be copied to the new chat.\nYou should close the app, check if there are updates for it, and create a new issue at https://github.com/TelegramTools/TLMerger pasting the error messages above.\nYou can still continue, but you might lose messages")
    getpass("Press ENTER to Continue. Close the app if you want to cancel the process.")
else:
    print("Nothing wrong detected. You are good to go!")
AskSoloMode()
if not SoloImporting:
    print("Now, you have to log in your partner in Telegram...")
    while True:
        answer = None
        answer = input(
            "\nDo you want to log in your partner using the 'Secret Mode'? Refer to the documentation in GitHub (check https://github.com/TelegramTools/TLSecret as well) for more information. [y/n]: ")
        answer = answer.replace(" ", "")
        answer = answer.upper()
        if not (answer == 'Y' or answer == 'N'):
            while True:
                print()
                answer = input("The command you entered was not valid. Please, enter a valid one: ")
                answer = answer.replace(" ", "")
                answer = answer.upper()
                if (answer == "Y") or (answer == "N"):
                    break
        if answer == "Y":
            SecretMode = True
            break
        if answer == "N":
            SecretMode = False
            break
    if SecretMode:
        StartSecretMode()
    else:
        client2 = TelegramClient('User2', api_id, api_hash, device_model=TLdevice_model,
                                 system_version=TLsystem_version, app_version=TLapp_version, lang_code=TLlang_code,
                                 system_lang_code=TLsystem_lang_code)
        print("")
        StartClient2()
    print ("\nYour partner is logged in as " + SelfUser2.first_name + " (+" + SelfUser2.phone + ")")
    print('\n\nYou are going to copy a conversation from ' + SelfUser1.first_name + ' (+' + SelfUser1.phone + ') to ' + SelfUser2.first_name + ' (+' + SelfUser2.phone + ')')
    dialogs.clear()
else:
    print("Now, you have to choose the destination group/chat/channel")
    DestinationChat = PrintChatList()
    dialogs.clear()
print("Now, before merging the chat, you need to set up a few settings:\n")
print()
while True:
    answer = None
    print("Here are your current settings:\n")
    if AgressiveTimestamps is True:
        print("> 1. Timestamp Mode: Agressive")
    elif NoTimestamps is True:
        print("> 1. Timestamp Mode: Disabled timestamps")
    else:
        print("> 1. Timestamp Mode: Default")
    if NoTimestamps is False:
        if YYYYMMDD is False:
            print("  > Format: DD/MM/YYYY")
        else:
            print("  > Format: YYYY/MM/DD")
        if DateSeconds is True:
            print("  > Seconds: Seconds will be added to timestamps, like this: HH:MM:SS")
        else:
            print("  > Seconds: Seconds won't be added to timestamps. They will appear like this: HH:MM")
        if DateEnd is True:
            print("  > Position: The timestamp will be added to the end of each message")
        else:
            print("  > Position: The timestamp will be added to the beginning of each message")
    if AppendHashtag is True:
        print("> 2. Add hashtags to each message: Yes")
    else:
        print("> 2. Add hashtags to each message: No")
    if SendAllLinkPreviews is True:
        print("> 3. Attach all Link Previews: Yes")
    else:
        print("> 3. Attach all Link Previews: No")
    if SendDatabase is True:
        print("> 4. Backup of the database in 'Saved Messages': Yes")
    else:
        print("> 4. Backup of the database in 'Saved Messages': No")
    if DeleteOriginalMessages is True:
        print("> 5. Delete original messages: Yes")
    else:
        print("> 5. Delete original messages: No")
    if AddFwdHeader:
        print("> 6. Add 'Forwarded from' header to messages: Yes")
    else:
        print("> 6. Add 'Forwarded from' header to messages: No")
    if SoloImporting:
        if AddSender:
            print("> (Solo Mode) 7. Add the original sender's name to each message: Yes")
        else:
            print("> (Solo Mode) 7. Add the original sender's name to each message: No")
    print()
    print("> Available commands: ")
    print("  !C: Confirm these settings and start the merging of the chats")
    print("  !1: See a description and change timestamps settings")
    print("  !2: See a description and change hashtags settings")
    print("  !3: See a description and change Link Previews settings")
    print("  !4: See a description and change Database settings")
    print("  !5: See a description and switch between deleting messages or not")
    print("  !6: See a description and switch between adding the 'Forwarded from' header to messages or not")
    if SoloImporting:
        print("  !7: See a description and switch between adding the original sender's name to each message or not")
    answer = str(input("Enter a command: "))
    answer = answer.replace(" ", "")
    answer = answer.upper()
    if not (answer == '!C' or answer == '!1' or answer == '!2' or answer == '!3' or answer == '!4' or answer == "!5" or answer == '!6' or (answer == "!7" and SoloImporting)):
        while True:
            print()
            answer = input("The command you entered was not valid. Please, enter a valid one: ")
            answer = answer.replace(" ", "")
            answer = answer.upper()
            if (answer == "!C") or (answer == "!1") or (answer == "!2") or (answer == "!3") or (answer == "!4") or (answer == "!5") or (answer == "!6") or (answer == "!7" and SoloImporting):
                break
    if (answer == "!C"):
        if Warnings is True:
            getpass("You are going to continue even you had some warnings while checking the database's data. Press ENTER to confirm.")
        break
    if (answer == "!1"):
        ChangeTimestampSettings()
    if (answer == "!2"):
        ChangeHashtagsSettings()
    if (answer == "!3"):
        ChangeLinkPreviewSettings()
    if (answer == "!4"):
        ChangeDatabaseSettings()
    if (answer == "!5"):
        ChangeDeleteSettings()
    if (answer == "!6"):
        ChangeFwdHeaderSettings()
    if (answer == "!7" and SoloImporting):
        ChangeSenderSettings()
print()
getpass("Take in mind that this might trigger some flood limits in Telegram. Press ENTER to continue: ")
getpass("\nAlso, please, don't interact or chat with your partner while TLMerger is copying messages. This can lead to problems.\nPress ENTER to continue: ")
print("STARTED! Now copying the conversation in Telegram...")
print()
ExportMessages()
if Errors is True or Warnings is True:
    print("There were some errors during the execution of the app. Check 'TLMerger-log.log' file, and report the issue at https://github.com/TelegramTools/TLMerger/issues/new, describing what you want to do and your issue as detailed as possible.")
else:
    print("Everything went good and it seems that no errors happened during the execution of the app!")
print()
print()
getpass("Press ENTER to log out of Telegram")
if not SoloImporting:
    print('\nLogging ' + SelfUser1.first_name + ' (+' + SelfUser1.phone + ') and ' + SelfUser2.first_name + ' (+' + SelfUser2.phone + ') out of Telegram...')
    client1.log_out()
    client2.log_out()
else:
    print('\nLogging ' + SelfUser1.first_name + ' (+' + SelfUser1.phone + ')')
    client1.log_out()
print("Thank you very much for using the app!\n\n--ferferga\n\nGOODBYE!")
print()
getpass("Press ENTER to close the app: ")
exit(0)