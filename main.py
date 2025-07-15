import os
import re
from yt_dlp import YoutubeDL
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time

class Config:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    START_MSG = os.environ.get("START_MSG", "歡迎使用本機器人")
    START_IMG = os.environ.get("START_IMG", "")
    OWNER = os.environ.get("OWNER", "")
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS/")
    msg = {}

def time_to_seconds(time):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(time.split(':'))))

app = Client(
    "bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("PlayStation 世界玩家會館", url="https://t.me/PlayStationTw")],
            [
                InlineKeyboardButton("所有者", url=f"https://telegram.dog/{Config.OWNER}"),
                InlineKeyboardButton("源代碼", url="https://github.com/makubex2010/SongPlayRoBot"),
            ],
        ]
    )
    await message.reply_photo(
        photo=Config.START_IMG,
        caption=Config.START_MSG.format(message.from_user.mention),
        reply_markup=reply_markup,
        reply_to_message_id=message.message_id
    )

@app.on_message(filters.command("help") & filters.private)
async def help_handler(client, message):
    text = (
        "使用說明：\n"
        "/s [歌曲名稱] - 搜尋並下載 YouTube 音樂\n"
        "/cookie_check - 檢查 cookies 是否有效\n"
        "/help - 顯示此說明"
    )
    await message.reply(text)

@app.on_message(filters.command("cookie_check") & filters.private)
async def cookie_check(client, message):
    cookies_content = os.environ.get('COOKIES')
    if cookies_content and cookies_content.strip():
        await message.reply("✅ Cookies 已設定。")
    else:
        await message.reply("❌ Cookies 未設定或為空。")

@app.on_message(filters.command("s") & filters.private)
async def search_and_download(client, message):
    query = ' '.join(message.command[1:])
    if not query:
        await message.reply("請提供要搜尋的歌曲名稱，例如：\n/s 南拳媽媽-下雨天")
        return

    m = await message.reply('正在搜尋...請稍候...')

    cookies_content = os.environ.get('COOKIES')
    if not cookies_content or not cookies_content.strip():
        await m.edit("❌ Cookies 未設定，無法下載受限影片。請設置環境變數 COOKIES。")
        return

    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookies_content.strip())

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "cookiefile": "cookies.txt",
        "quiet": True,
        "no_warnings": True,
        "outtmpl": Config.DOWNLOAD_LOCATION + "%(title)s.%(ext)s",
        "extractor_args": {"youtubetab": {"skip": "authcheck"}}
    }

    audio_file = None
    thumb_name = None

    try:
        results = []
        count = 0
        from youtube_search import YoutubeSearch
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

        thumb_name = f'thumb_{message.message_id}.jpg'
        thumb_data = requests.get(thumbnail).content
        with open(thumb_name, 'wb') as thumb_file:
            thumb_file.write(thumb_data)

        await m.edit("🔎 找到歌曲 🎶，準備下載...")

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.download([link])

        rep = (
            f'🎧 <b>標題 :</b> <a href="{link}">{title}</a>\n'
            f'⏳ <b>歌曲時間 :</b> <code>{duration}</code>'
        )
        dur = time_to_seconds(duration)

        await message.reply_audio(
            audio_file,
            caption=rep,
            parse_mode='HTML',
            quote=False,
            title=title,
            duration=dur,
            thumb=thumb_name
        )
        await m.delete()

    except Exception as e:
        await m.edit('❌ 發生內部錯誤，請聯絡管理員！')
        print("錯誤:", e)

    finally:
        try:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
            if thumb_name and os.path.exists(thumb_name):
                os.remove(thumb_name)
        except Exception as e:
            print("刪除檔案錯誤：", e)

if __name__ == "__main__":
    app.run()
