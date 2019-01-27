<p align="center">
  <img src="https://github.com/TelegramTools/TLMerger/raw/master/images/Intro.png">
 </p>
<p align="center">
  <img src="https://github.com/TelegramTools/TLSecret/raw/master/images/SecretModeLabel.png">
 </p>

# TLMerger - Telegram Chat Merger

This application can merge two chats inside Telegram. It tries to achieve the same goal as [TLImporter](https://github.com/TelegramTools/TLImporter), 
but using an existing Telegram chat as the source of the messages.

· You deleted a chat, but your partner still keeps it? You can ask him to run TLMerger and join his chat history with your chat history, so you both can keep the exact message history.
· One friend deleted his Telegram account and he joined back, but you still keep the old chat with him? You can join the new and old chat history together
· Moving one channel to another one and forwarding is too much work? TLMerger can do it!

*Joining channels/groups is an experimental feature, as TLMerger was designed to join private chats. Little changes incode might be required for this, you can help by publishing a pull request*


## How does it work?

TLMerger makes use of two chats, the **source dialog** and the **destination dialog**.
From the *source dialog*, TLMerger will copy all the messages, photos, replies, media and files that will be copied afterwards into the *destination dialog*

## How to use?

· Login into Telegram. Follow on-screen instructions
· Choose the *source dialog*. Wait until TLMerger downloads all the messages.
· Choose if you want to copy the messages into your own account or into the account's of another person. You can use [Secret Mode](https://github.com/TelegramTools/TLSecret/wiki/What's-the-Secret-Mode%3F) to log your partner into TLMerger.
  Further documentation on how this work can be found in [TLImporter's wiki](https://github.com/TelegramTools/TLImporter/wiki/Using-Telegram-Tools'-Secret-Mode)
**If you are logging another person in:**

· Wait until TLMerger copies the messages from the *source dialog* into your chat between you and the partner you logged in (the *destination dialog*).
· You will be done after a while!

**If you are not logging another person in:**

· Choose the chat where do you want to copy the messages (the *destination dialog*)
· Wait until TLMerger copies the messages from the *source dialog* into the *destination dialog*
· You will be done after a while!

## Download

You can always grab the latest version heading over the [releases tab](https://github.com/TelegramTools/TLMerger/releases)
The zip file includes an standalone executable for Windows (you can run it without needing any other dependencies) and a binary file for Mac OS and Linux under the *bin* folder. 
If you are running this binary, make sure to download the *requirements.txt* file from this repository and run the following command: `pip3 install -r requirements.txt` (or `pip install -r requirements.txt` if the other one doesn't work)

## Build from sources

Make sure that you replace the apiID, apiHash and password variables in your own script. Read instructions [here](https://core.telegram.org/api/obtaining_api_id) for getting your own apiID and apihash variables for Telegram apps.

Remember that you need to use the same password variable in TLMerger and in TLSecret, otherwise encryption will fail.

## Credits

This couldn't be possible without [Telethon](https://github.com/LonamiWebs/Telethon), and his great creator, [Lonami](https://github.com/Lonami), who always was ready to answer some questions and helping in development.

And also without [PyInstaller](https://www.pyinstaller.org/) which I used to build the Windows binaries.

Also, huge acknowledgements to Telegram for making such a great messenger!

**Give always credits to all the original authors and owners when using some parts of their hard work in your own projects**