from pyrogram import Client, filters
import yt_dlp
from youtube_search import YoutubeSearch
import requests
import os
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 你可以把這些放在 config.py 或自己改
class Config:
    START_IMG = "https://telegra.ph/file/abcd1234.jpg"  # 你的啟動圖片網址
    START_MSG = "你好，{}！歡迎使用音樂下載機器人。"
    OWNER = "你的TelegramID或username"

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

@Client.on_message(filters.command(['help']) & filters.private)
async def help_cmd(client, message):
    help_text = (
        "/start - 啟動機器人\n"
        "/s <歌曲名稱> - 搜尋並下載YouTube音樂\n"
        "/cookie_check - 檢查 cookies 設定是否有效\n"
        "/help - 顯示幫助訊息"
    )
    await message.reply(help_text)

@Client.on_message(filters.command(['cookie_check']) & filters.private)
async def cookie_check(client, message):
    cookies_content = os.environ.get('COOKIES', '')
    if not cookies_content.strip():
        await message.reply("⚠️ 尚未設定 COOKIES 環境變數，請先設置有效的 YouTube Cookies。")
        return
    try:
        # 簡單檢查是否看起來像 Netscape 格式（有無換行且有 tabs）
        if '\n' in cookies_content and '\t' in cookies_content:
            await message.reply("✅ COOKIES 環境變數看起來格式正常。")
        else:
            await message.reply("⚠️ COOKIES 格式異常，請確認為Netscape格式的cookies內容。")
    except Exception as e:
        await message.reply(f"❌ 檢查 COOKIES 時發生錯誤：{e}")

@Client.on_message(filters.command(['s']) & filters.private)
async def search_and_download(client, message):
    query = ' '.join(message.command[1:])
    if not query:
        await message.reply("請輸入歌曲名稱，例如： /s 南拳媽媽-下雨天")
        return

    m = await message.reply('正在搜尋...請稍候...')

    cookies_content = os.environ.get('COOKIES', '')
    if not cookies_content.strip():
        await m.edit("⚠️ 尚未設定 COOKIES 環境變數，無法進行下載。")
        return

    # 把環境變數中的換行符號 '\n' 轉成真正換行，避免寫檔格式錯誤
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookies_content.replace('\\n', '\n'))

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "cookiefile": "cookies.txt",
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "nocheckcertificate": True,
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192',
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

        thumb_name = f'thumb{message.message_id}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        with open(thumb_name, 'wb') as f:
            f.write(thumb.content)

        await m.edit("🔎 找到歌曲 🎶 請稍等 ⏳ 幾秒鐘...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info_dict)
            # yt-dlp 已自動下載並轉檔，音檔路徑在 audio_file

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
        await m.edit('❌ 發生錯誤，請確認 cookies 有效並重試。')
        print(f"Error: {e}")

    finally:
        try:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
            if thumb_name and os.path.exists(thumb_name):
                os.remove(thumb_name)
            if os.path.exists('cookies.txt'):
                os.remove('cookies.txt')
        except Exception as e:
            print(f"Clean up error: {e}")

