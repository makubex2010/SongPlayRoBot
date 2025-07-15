from pyrogram import Client, filters
import yt_dlp
from youtube_search import YoutubeSearch
import requests
import os
import time
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
    reply_to_id = getattr(message, 'message_id', None)
    await message.reply_photo(
        photo=os.environ.get('START_IMG', ''),  # 你可改為你的圖片連結或本地路徑
        caption=f"你好 {message.from_user.mention}，歡迎使用機器人！",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(BUTTON1, url=GITCLONE)],
                [
                    InlineKeyboardButton(OWNER, url=f"https://telegram.dog/{os.environ.get('OWNER', 'username')}"),
                    InlineKeyboardButton(ABS, url=B2)
                ]
            ]
        ),
        reply_to_message_id=reply_to_id
    )

@Client.on_message(filters.command(['help']) & filters.private)
async def help_handler(client, message):
    help_text = (
        "指令列表:\n"
        "/s <歌曲名稱> - 搜尋並下載YouTube音樂\n"
        "/cookie_check - 檢查 Cookie 狀態\n"
        "/help - 顯示此說明訊息"
    )
    await message.reply(help_text)

@Client.on_message(filters.command(['cookie_check']) & filters.private)
async def cookie_check(client, message):
    cookies_content = os.environ.get("COOKIES", "")
    if cookies_content:
        await message.reply("✅ Cookie 內容已設置。")
    else:
        await message.reply("❌ 未設定 Cookie 內容，請設定環境變數 COOKIES。")

@Client.on_message(filters.command(['s']) & filters.private)
async def search_song(client, message):
    query = ' '.join(message.command[1:])
    if not query:
        await message.reply("請在指令後輸入歌曲名稱。例: /s 南拳媽媽 下雨天")
        return

    m = await message.reply('正在搜尋...請稍候...')

    # 取得環境變數 COOKIES，並把字串中的 \n 替換成換行符號
    cookies_content = os.environ.get('COOKIES', '')
    cookies_content = cookies_content.replace('\\n', '\n')  # 這裡很重要，確保格式正確

    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookies_content)

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "cookiefile": "cookies.txt",
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }

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
        thumb_name = f'thumb{getattr(message, "message_id", "default")}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        with open(thumb_name, 'wb') as fthumb:
            fthumb.write(thumb.content)

        await m.edit("🔎 找到歌曲 🎶 請稍等 ⏳")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info_dict)

        rep = f'🎧  <b>標題 : </b> <a href="{link}">{title}</a>\n⏳ <b>歌曲時間 : </b> <code>{duration}</code>'
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
        await m.edit('❌ 發生錯誤，請聯繫管理員。')
        print(e)

    # 清理檔案
    try:
        if os.path.exists(audio_file):
            os.remove(audio_file)
        if os.path.exists(thumb_name):
            os.remove(thumb_name)
    except Exception as e:
        print(e)
