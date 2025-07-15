from pyrogram import Client, filters
import yt_dlp
from youtube_search import YoutubeSearch
import requests
import os
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 你自己的設定參數
class Config:
    START_IMG = "https://telegra.ph/file/your_start_image.jpg"
    START_MSG = "你好，{}！歡迎使用音樂播放機器人。"
    OWNER = "你的TelegramID"

ABS = "源代碼"
OWNER_TEXT = "所有者"
GITCLONE = "https://t.me/PlayStationTw"
B2 = "github.com/makubex2010/SongPlayRoBot"
BUTTON1 = "🎮 PlayStation 世界玩家會館 🎮"

def time_to_seconds(time_str):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(time_str.split(':'))))

@Client.on_message(filters.command('start') & filters.private)
async def start(client, message):
    reply_to_id = message.id
    await message.reply_photo(
        photo=Config.START_IMG,
        caption=Config.START_MSG.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(BUTTON1, url=GITCLONE)],
                [
                    InlineKeyboardButton(OWNER_TEXT, url=f"https://telegram.dog/{Config.OWNER}"),
                    InlineKeyboardButton(ABS, url=B2)
                ]
            ]
        ),
        reply_to_message_id=reply_to_id
    )

@Client.on_message(filters.command(['help']) & filters.private)
async def help_command(client, message):
    help_text = """
指令說明：
/s <歌名> - 搜尋並下載 YouTube 音樂
/cookie_check - 檢查 cookies 是否有效
/help - 顯示此說明
"""
    await message.reply(help_text)

@Client.on_message(filters.command(['cookie_check']) & filters.private)
async def cookie_check(client, message):
    cookies_content = os.environ.get('COOKIES')
    if cookies_content:
        await message.reply("✅ COOKIES 變數已設定。")
    else:
        await message.reply("❌ COOKIES 變數尚未設定或為空。")

@Client.on_message(filters.command(['s']) & filters.private)
async def search_and_download(client, message):
    query = ' '.join(message.command[1:])
    if not query:
        await message.reply("請提供搜尋關鍵字，例如：/s 南拳媽媽 下雨天")
        return

    m = await message.reply('正在搜尋...請稍候...')

    # 將 COOKIES 環境變數內容寫入 cookies.txt
    cookies_content = os.environ.get('COOKIES')
    if not cookies_content:
        await m.edit("❌ 尚未設定 COOKIES 環境變數，無法下載需要驗證的影片。")
        return

    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookies_content.strip())

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "cookiefile": "cookies.txt",
        "quiet": True,
        "no_warnings": True,
        "outtmpl": "%(title)s.%(ext)s",
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
            await m.edit('❌ 沒有搜尋到結果，請換個關鍵字再試。')
            return

        video = results[0]
        link = f"https://youtube.com{video['url_suffix']}"
        title = video["title"]
        thumbnail_url = video["thumbnails"][0]
        duration = video["duration"]

        # 下載縮圖
        thumb_name = f"thumb{message.id}.jpg"
        thumb_resp = requests.get(thumbnail_url, allow_redirects=True)
        with open(thumb_name, 'wb') as f:
            f.write(thumb_resp.content)

        await m.edit("🔎 找到歌曲，正在下載中，請稍候...")

        audio_file = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.download([link])

        dur_seconds = time_to_seconds(duration)
        caption = f'🎧 <b>標題：</b> <a href="{link}">{title}</a>\n⏳ <b>歌曲時間：</b> <code>{duration}</code>'

        await message.reply_audio(
            audio_file,
            caption=caption,
            parse_mode='HTML',
            quote=False,
            title=title,
            duration=dur_seconds,
            thumb=thumb_name
        )
        await m.delete()

    except Exception as e:
        await m.edit("❌ 發生錯誤，請聯繫機器人管理員。")
        print(f"錯誤：{e}")

    finally:
        # 清理檔案
        try:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(thumb_name):
                os.remove(thumb_name)
        except Exception as e:
            print(f"清理檔案時發生錯誤：{e}")
