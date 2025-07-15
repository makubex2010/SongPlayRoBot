from pyrogram import Client, filters
import yt_dlp
from youtube_search import YoutubeSearch
import requests
import os
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 這裡可以改成你的 config 或自己設定
class Config:
    START_IMG = "https://telegra.ph/file/your_start_image.jpg"
    START_MSG = "嗨，{0}，歡迎使用音樂機器人！\n用 /s 指令搜尋音樂"
    OWNER = "yourtelegramusername"  # Telegram 使用者帳號

# 介面文字
ABS = "源代碼"
OWNER = "所有者"
GITCLONE = "https://t.me/PlayStationTw"
B2 = "github.com/makubex2010/SongPlayRoBot"
BUTTON1 = "🎮 PlayStation 世界玩家會館 🎮"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))

@Client.on_message(filters.command('start') & filters.private)
async def start(client, message):
    reply_to_id = getattr(message, 'message_id', None)
    await message.reply_photo(
        photo=Config.START_IMG,
        caption=Config.START_MSG.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(BUTTON1, url=GITCLONE)],
                [
                    InlineKeyboardButton(OWNER, url=f"https://telegram.dog/{Config.OWNER}"),
                    InlineKeyboardButton(ABS, url=B2)
                ]
            ]
        ),
        reply_to_message_id=reply_to_id
    )

@Client.on_message(filters.command('help') & filters.private)
async def help_command(client, message):
    help_text = (
        "/start - 啟動機器人\n"
        "/help - 幫助資訊\n"
        "/s <關鍵字> - 搜尋並下載YouTube音樂\n"
        "/cookie_check - 檢查是否有成功載入 cookies"
    )
    await message.reply(help_text)

@Client.on_message(filters.command('cookie_check') & filters.private)
async def cookie_check(client, message):
    cookies = os.environ.get('COOKIES')
    if cookies:
        await message.reply("✅ 已成功載入 COOKIES 環境變數。")
    else:
        await message.reply("❌ 未設定 COOKIES 環境變數，請設定正確的 YouTube cookies。")

@Client.on_message(filters.command('s') & filters.private)
async def search_and_download(client, message):
    query = ' '.join(message.command[1:])
    if not query:
        await message.reply("請輸入搜尋關鍵字。範例： /s 南拳媽媽 下雨天")
        return
    
    m = await message.reply('正在搜尋...請稍候...')
    
    # 讀取環境變數 COOKIES 並寫入 cookies.txt
    cookies_content = os.environ.get('COOKIES')
    if not cookies_content:
        await m.edit("❌ 未設定 COOKIES 環境變數，無法使用 YouTube 需要登入的功能。")
        return
    
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookies_content)
    
    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "cookiefile": "cookies.txt",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "outtmpl": "%(title)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "192",
        }],
    }
    
    audio_file = None
    thumb_name = None
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
        thumb_name = f"thumb{message.message_id}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        with open(thumb_name, 'wb') as f:
            f.write(thumb.content)

        await m.edit("🔎 找到歌曲 🎶 請稍等 ⏳ ...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info_dict).replace(".webm", ".m4a").replace(".mp4", ".m4a")

        rep = (f'🎧  <b>標題 : </b> <a href="{link}">{title}</a>\n'
               f'⏳ <b>歌曲時間 : </b> <code>{duration}</code>')
        dur = time_to_seconds(duration)

        await message.reply_audio(
            audio_file,
            caption=rep,
            parse_mode='HTML',
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name
        )
        await m.delete()

    except Exception as e:
        await m.edit('❌ 發生內部錯誤，請聯繫管理員！')
        print("錯誤:", e)

    # 清理檔案
    try:
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
        if thumb_name and os.path.exists(thumb_name):
            os.remove(thumb_name)
    except Exception as e:
        print("清理檔案錯誤:", e)
