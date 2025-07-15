from pyrogram import Client, filters
import yt_dlp
from youtube_search import YoutubeSearch
import requests
import os
import time
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ABS = "源代碼"
APPER = "shamilhabeeb"
OWNER = "所有者"
GITCLONE = "https://t.me/PlayStationTw"
B2 = "github.com/makubex2010/SongPlayRoBot"
BUTTON1 = "🎮 PlayStation 世界玩家會館 🎮"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))

@Client.on_message(filters.command('start') & filters.private)
async def start(client, message):
    reply_to_id = message.message_id if hasattr(message, 'message_id') else None
    await message.reply_photo(photo=Config.START_IMG, caption=Config.START_MSG.format(message.from_user.mention),
         reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(BUTTON1, url=GITCLONE)
                ],
                [
                    InlineKeyboardButton(OWNER, url=f"https://telegram.dog/{Config.OWNER}"),
                    InlineKeyboardButton(ABS, url=B2)
                ]
            ]
        ),
        reply_to_message_id=reply_to_id
    )

@Client.on_message(filters.command(['s']))
async def a(client, message):
    query = ' '.join(message.command[1:])
    m = await message.reply('正在搜索...請稍候...')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count > 0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1

        if not results:
            await m.edit('**沒有搜尋到！請用另一種方式搜尋**')
            return

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        duration = results[0]["duration"]

        performer = ""
        thumb_name = f'thumb{message.message_id}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)

        await m.edit("🔎 找到歌曲 🎶 請稍等 ⏳ 幾秒鐘 [🚀](https://telegra.ph/file/d0a3a739f8a9b7e86e1f6.mp4)")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        rep = f'🎧  <b>標題 : </b> <a href="{link}">{title}</a>n⏳ <b>歌曲時間 : </b> <code>{duration}</code>'
        dur = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':'))))
        await message.reply_audio(audio_file, caption=rep, parse_mode='HTML', quote=False, title=title, duration=dur, performer=performer, thumb=thumb_name)
        await m.delete()

    except Exception as e:
        await m.edit('❌ 發生內部錯誤，向報告@Kevin_RX！！')
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)
