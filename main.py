import os
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
import yt_dlp

# 時間轉秒數函式
def time_to_seconds(time_str):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(time_str.split(':'))))

# 環境變數配置
class Config:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    START_MSG = os.environ.get("START_MSG", "歡迎使用音樂下載機器人，{0}！")
    START_IMG = os.environ.get("START_IMG", "")  # 可放URL或本地路徑
    OWNER = os.environ.get("OWNER", "ownerusername")
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./downloads/")
    COOKIES = os.environ.get("COOKIES", "")  # Youtube cookies

# 文字與按鈕
ABS = "源代碼"
OWNER = "所有者"
GITCLONE = "https://t.me/PlayStationTw"
B2 = "github.com/makubex2010/SongPlayRoBot"
BUTTON1 = "🎮 PlayStation 世界玩家會館 🎮"

app = Client(
    "music_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
)

@app.on_message(filters.command('start') & filters.private)
async def start(client, message):
    reply_to_id = message.id
    await message.reply_photo(
        photo=Config.START_IMG,
        caption=Config.START_MSG.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(BUTTON1, url=GITCLONE)],
                [
                    InlineKeyboardButton(OWNER, url=f"https://telegram.dog/{Config.OWNER}"),
                    InlineKeyboardButton(ABS, url=f"https://{B2}"),
                ],
            ]
        ),
        reply_to_message_id=reply_to_id,
    )

@app.on_message(filters.command('help') & filters.private)
async def help_handler(client, message):
    help_text = (
        "使用說明：\n"
        "/s [歌曲名稱] - 搜尋並下載 YouTube 音樂\n"
        "/cookie_check - 檢查 cookies 是否有效\n"
        "/help - 顯示此說明"
    )
    await message.reply(help_text)

@app.on_message(filters.command('cookie_check') & filters.private)
async def cookie_check(client, message):
    cookies_content = Config.COOKIES
    if cookies_content and cookies_content.strip():
        await message.reply("✅ Cookies 已設定。")
    else:
        await message.reply("❌ Cookies 未設定或為空。")

@app.on_message(filters.command(['s']) & filters.private)
async def search_and_download(client, message):
    query = ' '.join(message.command[1:])
    if not query:
        await message.reply("請提供要搜尋的歌曲名稱，例如：\n/s 南拳媽媽-下雨天")
        return

    m = await message.reply('正在搜尋...請稍候...')

    cookies_content = Config.COOKIES
    if not cookies_content or not cookies_content.strip():
        await m.edit("❌ Cookies 未設定，無法下載受限影片。請設置環境變數 COOKIES。")
        return

    # 將 cookies 內容寫入本地檔案
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookies_content.strip())

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "cookiefile": "cookies.txt",
        "quiet": True,
        "no_warnings": True,
        "outtmpl": Config.DOWNLOAD_LOCATION + "%(title)s.%(ext)s",
        "extractor_args": {
            "youtubetab": {"skip": "authcheck"}
        }
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
        thumb_name = f'thumb_{message.id}.jpg'
        thumb_data = requests.get(thumbnail).content
        with open(thumb_name, 'wb') as thumb_file:
            thumb_file.write(thumb_data)

        await m.edit("🔎 找到歌曲 🎶，準備下載...")

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
            thumb=thumb_name,
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
