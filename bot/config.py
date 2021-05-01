# -*- coding: utf-8 -*-
import aria2p
from pyromod import listen
from pyrogram import Client

import os
import json


Aria2_host="http://127.0.0.1"
Aria2_port="8080"
Aria2_secret=os.environ.get('Aria2_secret')
App_title=os.environ.get('Title')
Telegram_bot_api=os.environ.get('Telegram_bot_api')
Telegram_user_id=os.environ.get('Telegram_user_id')
Api_hash=os.environ.get('Api_hash')
Api_id=os.environ.get('Api_id')


aria2 = aria2p.API(
    aria2p.Client(
        host=Aria2_host,
        port=int(Aria2_port),
        secret=Aria2_secret
    )
)


client = Client("my_bot", bot_token=Telegram_bot_api,
             api_hash=Api_hash, api_id=Api_id

             )

client.start()

client.send_message(chat_id=int(Telegram_user_id), text="Bot上线")
Bot_info=client.get_me()

BOT_name=Bot_info.username
client.stop()

