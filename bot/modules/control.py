# -*- coding: utf-8 -*-

from config import aria2, BOT_name
import sys
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
import os
import time
import threading
import asyncio
import subprocess
import re

import nest_asyncio

nest_asyncio.apply()
os.system("df -lh")
task=[]

def check_upload(api, gid):

    time.sleep(15)
    global task
    print(f"检查上传 {task}")
    sys.stdout.flush()
    try:
        currdownload=api.get_download(gid)
    except:
        print("任务已删除，不需要上传")
        sys.stdout.flush()
        return
    dir=currdownload.dir
    key=1
    if len(task)!=0:
        for a in task:
            if a == dir:
                key=0
                print("该任务存在，不需要上传")
                sys.stdout.flush()
                task.remove(a)
    if key==1:
        Rclone_remote = os.environ.get('Remote')
        Upload = os.environ.get('Upload')
        file_dir = f"{currdownload.dir}/{currdownload.name}"
        file_num = int(len(currdownload.files))
        print(f"上传该任务:{file_dir}")
        sys.stdout.flush()
        name=currdownload.name

        if int(file_num) == 1:
            shell = f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}\"  -v --stats-one-line --stats=1s  "
        else:
            shell = f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}/{name}\"  -v --stats-one-line --stats=1s  "
        print(shell)
        cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                               stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)

        while True:
            time.sleep(2)
            if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
                print("上传结束")
                return




def the_download(client, message,url):

    try:
        download = aria2.add_magnet(url)
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='Markdown')
            return None
    prevmessagemag = None
    info=client.send_message(chat_id=message.chat.id,text="Downloading",parse_mode='markdown')

    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {download.gid}"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    client.edit_message_text(text="Downloading", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=reply_markup)


    temp_text=""
    while download.is_active:
        try:
            download.update()
            print("Downloading metadata")
            if temp_text!="Downloading metadata":
                client.edit_message_text(text="Downloading metadata",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=reply_markup)
                temp_text="Downloading metadata"
            barop = progessbar(download.completed_length,download.total_length)

            updateText = f"{download.status} \n" \
                         f"'{download.name}'\n" \
                         f"Progress : {hum_convert(download.completed_length)}/{hum_convert(download.total_length)} \n" \
                         f"Peers:{download.connections}\n" \
                         f"Speed {hum_convert(download.download_speed)}/s\n" \
                         f"{barop}\n" \
                         f"Free:{get_free_space_mb()}GB"
            if prevmessagemag != updateText:
                print(updateText)
                client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=reply_markup)
                prevmessagemag = updateText
            time.sleep(2)
        except:

            try:
                download.update()
            except Exception as e:
                if (str(e).endswith("is not found")):
                    print("Metadata Cancelled/Failed")
                    print("Metadata couldn't be downloaded")
                    if temp_text!="Metadata Cancelled/Failed":
                        client.edit_message_text(text="Metadata Cancelled/Failed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
                        temp_text="Metadata Cancelled/Failed"
                    return None
            time.sleep(2)


    time.sleep(2)
    match = str(download.followed_by_ids[0])
    downloads = aria2.get_downloads()
    currdownload = None
    for download in downloads:
        if download.gid == match:
            currdownload = download
            break
    print("Download complete")

    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    client.edit_message_text(text="Download complete", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)

    prevmessage = None

    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("Magnet Deleted")
                print("Magnet download was removed")
                client.edit_message_text(text="Magnet download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                break
            print(e)
            print("Issue in downloading!")

        if currdownload.status == 'removed':
            print("Magnet was cancelled")
            print("Magnet download was cancelled")
            client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            break

        if currdownload.status == 'error':
            print("Mirror had an error")
            currdownload.remove(force=True, files=True)
            print("Magnet failed to resume/download!\nRun /cancel once and try again.")
            client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
            break

        print(f"Magnet Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{download.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{download.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)



    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            files_num=int(len(currdownload.files))
            run_rclone(file_dir,currdownload.name,info=info,file_num=files_num,client=client,message=message)
            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
    return None


#@bot.message_handler(commands=['magnet'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_download(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/magnet@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=the_download, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/magnet ", "")
            print(keywords)
            t1 = threading.Thread(target=the_download, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"magnet :{e}")




def run_rclone(dir,title,info,file_num,client, message):
    global task
    task.append(dir)
    print(task)
    sys.stdout.flush()
    Rclone_remote=os.environ.get('Remote')
    Upload=os.environ.get('Upload')
    info = client.send_message(chat_id=message.chat.id, text="开始上传", parse_mode='markdown')
    name=f"{str(info.message_id)}_{str(info.chat.id)}"
    if int(file_num)==1:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    else:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}/{title}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    print(shell)
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    temp_text=None
    while True:
        time.sleep(2)
        fname = f'{name}.log'
        with open(fname, 'r') as f:  #打开文件
            try:
                lines = f.readlines() #读取所有行

                for a in range(-1,-10,-1):
                    last_line = lines[a] #取最后一行
                    if last_line !="\n":
                        break


                if temp_text != last_line and "ETA" in last_line:
                    print(f"上传中\n{last_line} end")
                    sys.stdout.flush()
                    log_time,file_part,upload_Progress,upload_speed,part_time=re.findall("(.*?)INFO.*?(\d.*?),.*?(\d+%),.*?(\d.*?s).*?ETA.*?(\d.*?)",last_line , re.S)[0]
                    text=f"{title}\n" \
                         f"更新时间：`{log_time}`\n" \
                         f"上传部分：`{file_part}`\n" \
                         f"上传进度：`{upload_Progress}`\n" \
                         f"上传速度：`{upload_speed}`\n" \
                         f"剩余时间:`{part_time}`"
                    try:
                        print(f"修改信息 {text}")
                        sys.stdout.flush()
                        client.edit_message_text(text=text,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                    except Exception as e:
                        print(f"修改信息失败 {e}")
                        sys.stdout.flush()
                    temp_text = last_line
                f.close()

            except Exception as e:
                print(f"检查进度失败 {e}")
                sys.stdout.flush()
                f.close()
                continue

        if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
            print("上传结束")
            client.send_message(text=f"{title}\n上传结束",chat_id=info.chat.id)
            os.remove(f"{name}.log")
            task.remove(dir)
            return

    return

#@bot.message_handler(commands=['mirror'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_http_download(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/mirror@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=http_download, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/mirror ", "")
            print(keywords)
            t1 = threading.Thread(target=http_download, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"start_http_download :{e}")

def file_download(client, message,file_dir):
    #os.system("df -lh")
    try:
        print("开始下载")
        sys.stdout.flush()
        currdownload = aria2.add_torrent(torrent_file_path=file_dir)
        info=client.send_message(chat_id=message.chat.id, text="开始下载", parse_mode='markdown')
        print("发送信息")
        sys.stdout.flush()
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')

        return
    new_inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
        InlineKeyboardButton(
            text=f"Pause",
            callback_data=f"Pause {currdownload.gid}"
        ),
        InlineKeyboardButton(
            text=f"Remove",
            callback_data=f"Remove {currdownload.gid}"
        )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    client.edit_message_text(text="Download complete",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
    prevmessage = None

    while currdownload.is_active or not currdownload.is_complete:
        time.sleep(2)
        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("Magnet Deleted")
                print("Magnet download was removed")
                client.edit_message_text(text="Magnet download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                break
            print(e)
            print("Issue in downloading!")

        if currdownload.status == 'removed':
            print("Magnet was cancelled")
            print("Magnet download was cancelled")
            client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
            break

        if currdownload.status == 'error':
            print("Mirror had an error")
            currdownload.remove(force=True, files=True)
            print("Magnet failed to resume/download!\nRun /cancel once and try again.")
            client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
            break

        print(f"Magnet Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)




    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            files_num=int(len(currdownload.files))
            run_rclone(file_dir,currdownload.name,info=info,file_num=files_num,client=client, message=message)
            currdownload.remove(force=True,files=True)
            return

        except Exception as e:
            print(e)
            print("Upload Issue!")
            return
    return None

def http_download(client, message,url):
    try:
        currdownload = aria2.add_uris([url])
        info = client.send_message(chat_id=message.chat.id, text="开始下载", parse_mode='markdown')
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')
            return None
    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    client.edit_message_text(text="Downloading", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)


    prevmessage=None
    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("url Deleted")
                print("url download was removed")
                client.edit_message_text(text="url download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                break
            print(e)
            print("url in downloading!")

        if currdownload.status == 'removed':
            print("url was cancelled")
            print("url download was cancelled")
            client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            break

        if currdownload.status == 'error':
            print("url had an error")
            currdownload.remove(force=True, files=True)
            print("url failed to resume/download!.")
            client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            break

        print(f"url Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)

    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            run_rclone(file_dir,currdownload.name,info=info,file_num=1,client=client, message=message)
            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
    return None


def progessbar(new, tot):
    """Builds progressbar
    Args:
        new: current progress
        tot: total length of the download
    Returns:
        progressbar as a string of length 20
    """
    length = 20
    progress = int(round(length * new / float(tot)))
    percent = round(new/float(tot) * 100.0, 1)
    bar = '=' * progress + '-' * (length - progress)
    return '[%s] %s %s\r' % (bar, percent, '%')


def hum_convert(value):
    value=float(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

def get_free_space_mb():
    result=os.statvfs('/root/')
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bfree
    # giga=1024*1024*1024
    giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga
    print('total_size = %s' % int(total_size))
    print('free_size = %s' % free_size)
    return int(free_size)

def progress(current, total,client,message,name):

    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as e:
        print("e")





async def temp_telegram_file(client, message):
    answer = await client.ask(chat_id=message.chat.id, text='请发送种子文件,或输入 /cancel 取消')
    print(answer)
    print(answer.text)
    if answer.document == None:
        await client.send_message(text="发送的不是文件", chat_id=message.chat.id, parse_mode='markdown')
        return "False"
    elif answer.text == "/cancel":
        await client.send_message(text="取消发送", chat_id=message.chat.id, parse_mode='markdown')
        return "False"
    else:
        try:

            file_dir = await client.download_media(message=answer, progress=progress)

            return file_dir
        except Exception as e:
            print(f"{e}")
            await client.send_message(text="下载文件失败", chat_id=message.chat.id, parse_mode='markdown')
            return "False"

#commands=['magfile']
def send_telegram_file(client, message):
    loop = asyncio.get_event_loop()
    temp = loop.run_until_complete(temp_telegram_file(client, message))
    print(temp)
    sys.stdout.flush()
    if temp =="False":
        return
    else:
        file_dir=temp
        t1 = threading.Thread(target=file_download, args=(client, message, file_dir))
        t1.start()
        return




def http_downloadtg(client, message,url):
    try:
        currdownload = aria2.add_uris([url])
        info = client.send_message(chat_id=message.chat.id, text="开始下载", parse_mode='markdown')
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')
            return None
    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    client.edit_message_text(text="Downloading", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)


    prevmessage=None
    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("url Deleted")
                print("url download was removed")
                client.edit_message_text(text="url download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                break
            print(e)
            print("url in downloading!")

        if currdownload.status == 'removed':
            print("url was cancelled")
            print("url download was cancelled")
            client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            break

        if currdownload.status == 'error':
            print("url had an error")
            currdownload.remove(force=True, files=True)
            print("url failed to resume/download!.")
            client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            break

        print(f"url Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)

        time.sleep(1)
    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            client.send_document(chat_id=info.chat.id, document=file_dir, caption=currdownload.name, progress=progress,
                                       progress_args=(client, info, currdownload.name,))

            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
            currdownload.remove(force=True, files=True)
    return None

#@bot.message_handler(commands=['mirrortg'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_http_downloadtg(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/mirrortg@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=http_downloadtg, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/mirrortg ", "")
            print(keywords)
            t1 = threading.Thread(target=http_downloadtg, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"start_http_download :{e}")




