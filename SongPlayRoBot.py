# © TamilBots 2021-22

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
import yt_dlp
from youtube_search import YoutubeSearch
import requests

import os

bot = Client(
    'SongPlayRoBot',
    api_id = os.environ["API_ID"],
    api_hash = os.environ["API_HASH"],
    bot_token = os.environ["BOT_TOKEN"]
)

## Extra Fns -------------------------------

# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


## Commands --------------------------------
@bot.on_message(filters.command(['start']))
def start(client, message):
    TamilBots = f'👋 嗨! @{message.from_user.username}\n\n我是 🎸歌曲播放機器人[🎶](https://telegra.ph/file/6cb884fe1cb943ec12df1.mp4)\n\n發送你想要的歌名或網址... 😍🥰🤗例如:`/s 南拳媽媽-下雨天`'
    message.reply_text(
        text=TamilBots, 
        quote=False,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('問題回報 👬', url='https://t.me/Kevin_RX'),
                    InlineKeyboardButton('有玩PlayStation歡迎加入群組 🤗', url='https://t.me/PlayStationTw')
                ]
            ]
        )
    )

@bot.on_message(filters.command(['s']))
def a(client, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('🔎 搜索歌曲中...')
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

            ## 如果您想限制持續時間，請取消註釋。 將 1800 更改為您自己的首選持續時間並在幾秒鐘內編輯消息（30 分鐘上限）限制
            # if time_to_seconds(duration) >= 1800:  # duration limit
            #     m.edit("Exceeded 30mins cap")
            #     return

            views = results[0]["views"]
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            m.edit('沒有找到歌曲，請嘗試使用網址 😕')
            return
    except Exception as e:
        m.edit(
            "✖️ 抱歉，沒有找到歌曲\n\n請嘗試其他關鍵詞或是用網址查詢\n\n例如:`/s 南拳媽媽-下雨天`"
        )
        print(str(e))
        return
    m.edit("🔎 找到歌曲 🎶 請稍等 ⏳️ 幾秒鐘 [🚀](https://telegra.ph/file/d9d542bf37174c38bdb8d.mp4)")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f'🎧 標題 : [{title[:35]}]({link})\n⏳ 歌曲時間 : `{duration}`'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode='md',quote=False, title=title, duration=dur, thumb=thumb_name)
        m.delete()
    except Exception as e:
        m.edit('❌ 錯誤\n\n 回報此錯誤給 @Kevin_RX 修復❤️')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

bot.run()
