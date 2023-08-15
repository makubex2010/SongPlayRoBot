from pyrogram import Client, filters

import yt_dlp
from youtube_search import YoutubeSearch
import requests

import os
import time
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ABS="源代碼"
APPER="shamilhabeeb"
OWNER="所有者"
GITCLONE="https://t.me/PlayStationTw"
B2="github.com/makubex2010/SongPlayRoBot"
BUTTON1="🎮 PlayStation 世界玩家會館 🎮"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))

@Client.on_message(filters.command('start') & filters.private)
async def start(client, message):
    await message.reply_photo(photo=Config.START_IMG, caption=Config.START_MSG.format(message.from_user.mention),
         reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(BUTTON1, url=GITCLONE)
                 ],[
                    InlineKeyboardButton(OWNER, url=f"https://telegram.dog/{Config.OWNER}"),
                    InlineKeyboardButton(ABS, url=B2)
            ]
          ]
        ),
        reply_to_message_id=message.message_id
    )


@Client.on_message(filters.command(['s']))
def a(client, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('`正在搜索...請稍候...`')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count>0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        # results = YoutubeSearch(query, max_results=1).to_dict()
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]
            views = results[0]["views"]

             ## 如果您想限制持續時間，請取消註釋。 將 1800 更改為您自己的首選持續時間並編輯消息（30 分鐘上限）限制在幾秒鐘內
             # if time_to_seconds(duration) >= 7000: # 持續時間限制
             # m.edit("超過 30 分鐘上限")
             # 返回

            performer = f""
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            m.edit('**沒有搜尋到！請用另一種方式搜尋**')
            return
    except Exception as e:
        m.edit(
            "**使用 /s 輸入歌曲名稱！**"
        )
        print(str(e))
        return
    m.edit("🔎 找到歌曲 🎶 請稍等 ⏳️ 幾秒鐘 [🚀](https://telegra.ph/file/d0a3a739f8a9b7e86e1f6.mp4)")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f'🎧  <b>標題 : </b> <a href="{link}">{title}</a>\n⏳ <b>歌曲時間 : </b> <code>{duration}</code>'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode='HTML',quote=False, title=title, duration=dur, performer=performer, thumb=thumb_name)
        m.delete()
    except Exception as e:
        m.edit('**❌ 發生內部錯誤，向報告@Kevin_RX！！**')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)
