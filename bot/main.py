# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
import sys
from modules.check import new_clock, second_clock
from config import client, Telegram_user_id,aria2
from pyrogram.handlers import MessageHandler,CallbackQueryHandler
from pyrogram import filters
from modules.pixiv import start_download_pixiv,start_download_id,start_download_pixivtg,start_download_pixivphoto,start_download_pixivtele
from modules.control import send_telegram_file,start_http_download,start_download,start_http_downloadtg,check_upload
from modules.call import start_pause,start_remove,start_Resume,start_benzi_down,start_download_video
from modules.moretg import get_telegram_file,get_file_id,sendfile_by_id
from modules.picacg import seach_main
from modules.rclone import start_rclonecopy,start_rclonelsd,start_rclonels,start_rclonecopyurl
from modules.video import start_get_video_info
import hashlib
import os
import md5 #Python2里的引用



async def chexk_group(_, client, query):
    print(query)
    try:
        info=await client.get_chat_member(chat_id=int(Telegram_user_id),user_id=query.from_user.id)
        print(info)
        sys.stdout.flush()
        return True
    except:
        return False




async def test(client, message):
    print(client)
    print(message)
    message.reply_text(message.text)
    await client.send_message(chat_id=int(Telegram_user_id), text="test")

def start_bot():
    scheduler = BlockingScheduler()
    scheduler = BackgroundScheduler()

    scheduler.add_job(new_clock, "interval", seconds=60)
    scheduler.add_job(second_clock, "interval", seconds=60)
    scheduler.start()
    print("开启监控")

    sys.stdout.flush()
    print("开始bot")
    print(Telegram_user_id)
    sys.stdout.flush()
    aria2.listen_to_notifications(on_download_complete=check_upload, threaded=True)



    start_message_handler = MessageHandler(
        test,
        filters=filters.command("start") & filters.user(int(Telegram_user_id))
        filters=filters.command("start") & filters.create(chexk_group)
    )

    pixivuser_message_handler = MessageHandler(
        start_download_pixiv,
        filters=filters.command("pixivuser") & filters.user(int(Telegram_user_id))
    )


    pixivid_message_handler = MessageHandler(
        start_download_id,
        filters=filters.command("pixivpid") & filters.user(int(Telegram_user_id))
    )

    magfile_message_handler = MessageHandler(
        send_telegram_file,
        filters=filters.command("magfile") & filters.user(int(Telegram_user_id))
    )



    http_download_message_handler = MessageHandler(
        start_http_download,
        filters=filters.command("mirror") & filters.user(int(Telegram_user_id))
    )
    magnet_download_message_handler = MessageHandler(
        start_download,
        filters=filters.command("magnet") & filters.user(int(Telegram_user_id))
    )

    telegram_file_message_handler = MessageHandler(
        get_telegram_file,
        filters=filters.command("downtgfile") & filters.user(int(Telegram_user_id))
    )
    seach_main_file_message_handler = MessageHandler(
        seach_main,
        filters=filters.command("search") & filters.user(int(Telegram_user_id))
    )

    start_download_idtg_message_handler = MessageHandler(
        start_download_pixivtg,
        filters=filters.command("pixivusertg") & filters.user(int(Telegram_user_id))
    )

    start_http_downloadtg_message_handler = MessageHandler(
        start_http_downloadtg,
        filters=filters.command("mirrortg") & filters.user(int(Telegram_user_id))
    )
    start_rclonecopy_message_handler = MessageHandler(
        start_rclonecopy,
        filters=filters.command("rclonecopy") & filters.user(int(Telegram_user_id))
    )

    start_rclonelsd_message_handler = MessageHandler(
        start_rclonelsd,
        filters=filters.command("rclonelsd") & filters.user(int(Telegram_user_id))
    )

    start_rclone_message_handler = MessageHandler(
        start_rclonels,
        filters=filters.command("rclone") & filters.user(int(Telegram_user_id))
    )

    start_rclonecopyurl_message_handler = MessageHandler(
        start_rclonecopyurl,
        filters=filters.command("rclonecopyurl") & filters.user(int(Telegram_user_id))
    )

    get_file_id_message_handler = MessageHandler(
        get_file_id,
        filters=filters.command("getfileid") & filters.user(int(Telegram_user_id))
    )
    sendfile_by_id_message_handler = MessageHandler(
        sendfile_by_id,
        filters=filters.command("getfile") & filters.user(int(Telegram_user_id))
    )

    start_download_pixivphoto_message_handler = MessageHandler(
        start_download_pixivphoto,
        filters=filters.command("pixivuserphoto") & filters.user(int(Telegram_user_id))
    )

    start_download_pixivtele_message_handler = MessageHandler(
        start_download_pixivtele,
        filters=filters.command("pixivusertele") & filters.user(int(Telegram_user_id))
    )

    start_get_video_info_message_handler = MessageHandler(
        start_get_video_info,
        filters=filters.command("video") & filters.user(int(Telegram_user_id))
    )

    start_Resume_handler = CallbackQueryHandler(
        callback=start_Resume,
        filters=filters.create(lambda _, __, query: "Resume" in query.data )
        )

    start_pause_handler = CallbackQueryHandler(
        callback=start_pause,
        filters=filters.create(lambda _, __, query: "Pause" in query.data )
        )
    start_remove_handler = CallbackQueryHandler(
        callback=start_remove,
        filters=filters.create(lambda _, __, query: "Remove" in query.data )
        )

    start_benzi_down_handler = CallbackQueryHandler(
        callback=start_benzi_down,
        filters=filters.create(lambda _, __, query: "down" in query.data )
        )
    start_download_video_handler = CallbackQueryHandler(
        callback=start_download_video,
        filters=filters.create(lambda _, __, query: "video" in query.data )
        )

    client.add_handler(start_download_video_handler, group=0)
    client.add_handler(start_Resume_handler, group=0)
    client.add_handler(start_pause_handler, group=0)
    client.add_handler(start_remove_handler, group=0)
    client.add_handler(start_benzi_down_handler, group=0)

    client.add_handler(start_message_handler,group=1)
    client.add_handler(pixivuser_message_handler,group=1)
    client.add_handler(pixivid_message_handler,group=1)
    client.add_handler(magfile_message_handler,group=3)

    client.add_handler(http_download_message_handler,group=1)
    client.add_handler(magnet_download_message_handler, group=1)
    client.add_handler(telegram_file_message_handler, group=1)
    client.add_handler(seach_main_file_message_handler, group=1)
    client.add_handler(start_download_idtg_message_handler, group=1)
    client.add_handler(start_http_downloadtg_message_handler, group=1)
    client.add_handler(start_rclonecopy_message_handler , group=1)
    client.add_handler(start_rclonelsd_message_handler, group=1)
    client.add_handler(start_rclone_message_handler, group=1)
    client.add_handler(start_rclonecopyurl_message_handler, group=1)
    client.add_handler(get_file_id_message_handler, group=1)
    client.add_handler(sendfile_by_id_message_handler, group=1)
    client.add_handler(start_download_pixivphoto_message_handler, group=1)
    client.add_handler(start_download_pixivtele_message_handler, group=1)
    client.add_handler(start_get_video_info_message_handler, group=1)
    client.run()

if __name__ == '__main__':

    start_bot()

