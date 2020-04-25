<p align="center">
  <img src="https://github.com/TelegramTools/TLMerger/raw/master/images/Intro.png">
 </p>
<p align="center">
  <img src="https://github.com/TelegramTools/TLSecret/raw/master/images/SecretModeLabel.png">
 </p>

# TLMerger - Telegram Chat Merger

This application can merge two chats inside Telegram. It tries to achieve the same goal as [TLImporter](https://github.com/TelegramTools/TLImporter), 
but using an existing Telegram chat as the source of the messages.

### Use cases

* **You deleted a chat, but your partner still keeps it? You can ask him to run TLMerger and join his chat history with your chat history, so you both can keep the exact message history.**

* **One friend deleted his Telegram account and he joined back, but you still keep the old chat with him? You can join the new and old chat history together**

* **Moving one channel to another one and forwarding is too much work? TLMerger can do it!**

*Joining channels/groups is an experimental feature, as TLMerger was designed to join private chats. Little changes incode might be required for this, you can help by publishing a pull request*

## How does it work?

TLMerger makes use of two chats, the **source dialog** and the **destination dialog**.
From the *source dialog*, TLMerger will copy all the messages, photos, replies, media and files that will be copied afterwards into the *destination dialog*.

The *destination dialog* will always be another chat in your account. However, you have two options: 
* You **can use 'Solo Mode'** and copy the messages from one chat to another (without the **Forwarded from** header)
* You **can log in another Telegram user** and merge the *source* dialog with your chat with the chat you have with the user that was logged in.

See how logging another user works. We are going to merge this chat from the user 'Diego Velázquez' to 'Francisco de Goya':

**Original chat**

<p align="center">
  <img src="https://github.com/TelegramTools/TLMerger/raw/master/images/original_chat.png">
 </p>

**Process and result (using *Secret Mode* for demonstration purposes)**

<p align="center">
  <img src="https://github.com/TelegramTools/TLSecret/raw/master/images/secret_mode-demo.webp">
 </p>

The demo chat used is very simple, but TLMerger can move successfully files, gifs, images, stickers, voice notes, video notes, contacts, live locations, locations,
games, link previews. You can customize some of the settings related to some kinds of media in TLMerger's menus (see video above to see the options).

## How to use?

* Log in to Telegram. Follow on-screen instructions

* Choose the *source dialog*. Wait until TLMerger fetch all the messages.

* Choose if you want to copy the messages into your own account or into the account's of another person. You can use [Secret Mode](https://github.com/TelegramTools/TLSecret/wiki/What's-the-Secret-Mode%3F) to log in your partner into TLMerger, as demoed in the video.
Further documentation on how this work can be found in [TLImporter's wiki](https://github.com/TelegramTools/TLImporter/wiki/Using-Telegram-Tools'-Secret-Mode)

**If you are merging your messages with your chat with another Telegram user:**

* Log in your partner, locally or by using Secret Mode.

* Customize your settings and confirm them

* Wait until TLMerger copies the messages from the *source dialog* into your chat between you and the partner you logged in (the *destination dialog*).

* You will be done after a while!

**If you are copying the messages into your own account:**

* Choose the chat where do you want to copy the messages (the *destination dialog*)

* Customize your settings and confirm them

* Wait until TLMerger copies the messages from the *source dialog* into the *destination dialog*

* You will be done after a while!

## Download

You can always grab the latest version heading over the [releases tab](https://github.com/TelegramTools/TLMerger/releases).
I built binaries for **Windows (64 bits)**, **Linux amd64** and **Linux armhf**

* On **Windows**: Simply double click on the ``.exe`` file
* On **Linux**: Download the binary, ``cd`` to the folder where the download is located and do ``./TLMerger-xxx``

If you're running other systems (like MacOS), you will need to **build the files from source**.

## Build from sources

Make sure that you replace the ``api_id`` and ``api_hash`` variables in the ``TLMerger.py`` file.
Read instructions [here](https://core.telegram.org/api/obtaining_api_id) for getting your own from Telegram.

You can't use Secret Mode if one of the sides is still using the binaries: I'm the only holder of the encryption key, so it's more
difficult for malicious people to compromise them. If you want to use the *Secret Mode*, you must build both TLMerger and TLSecret from
sources using the same password for it to work. You can specify the password used for encryption/decryption in the ``password`` variable.

## Credits

This couldn't be possible without [Telethon](https://github.com/LonamiWebs/Telethon), and his great creator, [Lonami](https://github.com/Lonami), who always was ready to answer some questions and helping in development.

Thanks to the [PyInstaller](https://www.pyinstaller.org/) team for their great tool, which I used to build the binaries.

Also, huge acknowledgements to Telegram for making such a great messenger!

**Give always credits to all the original authors and owners when using some parts of their hard work in your own projects**
