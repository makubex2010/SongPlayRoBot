from pyrogram import Client, filters
import yt_dlp
from youtube_search import YoutubeSearch
import requests
import os
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 你的設定
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
    reply_to_id = message.message_id
    await message.reply_photo(
        photo=os.environ.get("START_IMG", ""),  # 從環境變量讀取圖片連結或本地路徑
        caption=f"歡迎 {message.from_user.mention} 使用音樂下載機器人！",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(BUTTON1, url=GITCLONE)],
                [
                    InlineKeyboardButton(OWNER, url=f"https://telegram.dog/{os.environ.get('OWNER', '')}"),
                    InlineKeyboardButton(ABS, url=f"https://{B2}"),
                ]
            ]
        ),
        reply_to_message_id=reply_to_id
    )

@Client.on_message(filters.command('help') & filters.private)
async def help_handler(client, message):
    text = (
        "使用說明：\n"
        "/s [歌曲名稱] - 搜尋並下載 YouTube 音樂\n"
        "/cookie_check - 檢查 cookies 是否有效\n"
        "/help - 顯示此說明"
    )
    await message.reply(text)

@Client.on_message(filters.command('cookie_check') & filters.private)
async def cookie_check(client, message):
    cookies_content = os.environ.get('COOKIES')
    if cookies_content:
        await message.reply("✅ Cookies 已設定。")
    else:
        await message.reply("❌ Cookies 未設定或為空。")

@Client.on_message(filters.command(['s']) & filters.private)
async def search_and_download(client, message):
    query = ' '.join(message.command[1:])
    if not query:
        await message.reply("請提供要搜尋的歌曲名稱，例如：\n/s 南拳媽媽-下雨天")
        return

    m = await message.reply('正在搜尋...請稍候...')

    cookies_content = os.environ.get('COOKIES')
    if not cookies_content:
        await m.edit("❌ Cookies 未設定，無法下載受限影片。請設置環境變數 COOKIES。")
        return

    # 將 cookies 寫入檔案
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookies_content.strip())

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "cookiefile": "cookies.txt",
        "quiet": True,
        "no_warnings": True,
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "extractor_args": {
            "youtubetab": {"skip": "authcheck"}
        }
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
        thumb_name = f'thumb_{message.message_id}.jpg'
        thumb_data = requests.get(thumbnail).content
        with open(thumb_name, 'wb') as thumb_file:
            thumb_file.write(thumb_data)

        await m.edit("🔎 找到歌曲 🎶，準備下載...")

        audio_file = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
            performer=performer,
            thumb=thumb_name
        )
        await m.delete()

    except Exception as e:
        await m.edit('❌ 發生內部錯誤，請聯絡管理員！')
        print(e)

    finally:
        try:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(thumb_name):
                os.remove(thumb_name)
        except Exception as e:
            print("刪除檔案錯誤：", e)
