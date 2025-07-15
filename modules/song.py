from pyrogram import Client, filters
import yt_dlp
from youtube_search import YoutubeSearch
import requests
import os
import time
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 自訂 UI 文本
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

@Client.on_message(filters.command('help'))
async def help_command(client, message):
    help_text = (
        "**📖 指令說明：**\n\n"
        "`/start` - 開始使用機器人\n"
        "`/help` - 查看此說明訊息\n"
        "`/s 關鍵字` - 搜尋並下載 YouTube 音樂\n"
        "`/cookie_check` - 檢查 cookies 設定是否正確\n\n"
        "⚠️ 若出現登入失敗，請確認 Heroku 中的 COOKIES 變數已正確設定。"
    )
    await message.reply(help_text, parse_mode="markdown")

@Client.on_message(filters.command("cookie_check"))
async def cookie_check(client, message):
    m = await message.reply("🔍 檢查 cookie 是否有效...")

    cookies_content = os.environ.get("COOKIES")
    if not cookies_content:
        await m.edit("❌ 找不到 COOKIES 環境變數，請設定 Heroku Config Vars。")
        return

    with open("cookies.txt", "w", encoding="utf-8") as f:
        for line in cookies_content.splitlines():
            if line.strip() == "":
                continue
            if line.startswith("#") or line.count("\t") >= 6:
                f.write(line + "\n")

    if not os.path.exists("cookies.txt") or os.path.getsize("cookies.txt") < 50:
        await m.edit("❌ Cookie 檔案內容異常，請重新貼上有效格式。")
        return

    try:
        test_url = "https://www.youtube.com/watch?v=uu0k4cQS7_8"
        ydl_opts = {
            "format": "bestaudio",
            "cookiefile": "cookies.txt",
            "quiet": True,
            "skip_download": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(test_url, download=False)
        await m.edit("✅ Cookie 驗證成功，可以正常使用。")
    except Exception as e:
        await m.edit(f"❌ Cookie 驗證失敗：\n`{str(e)[:300]}`", parse_mode="markdown")

@Client.on_message(filters.command(['s']))
async def download_song(client, message):
    query = ' '.join(message.command[1:])
    m = await message.reply('正在搜索...請稍候...')

    cookies_content = os.environ.get("COOKIES")
    if not cookies_content:
        await m.edit("❌ 找不到 COOKIES 環境變數。")
        return

    with open("cookies.txt", "w", encoding="utf-8") as f:
        for line in cookies_content.splitlines():
            if line.strip() == "":
                continue
            if line.startswith("#") or line.count("\t") >= 6:
                f.write(line + "\n")

    if not os.path.exists("cookies.txt") or os.path.getsize("cookies.txt") < 50:
        await m.edit("❌ Cookie 檔案異常，請確認格式。")
        return

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "cookiefile": "cookies.txt"
    }

    audio_file = None
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count > 0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1

        if not results:
            await m.edit('❌ 沒有搜尋到，請換其他關鍵字。')
            return

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        performer = ""

        thumb_name = f'thumb{getattr(message, "message_id", "default")}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)

        await m.edit("🎶 找到歌曲，正在下載...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        rep = f'🎧 <b>標題：</b> <a href="{link}">{title}</a>\n⏳ <b>時長：</b> <code>{duration}</code>'
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
        await m.edit(f'❌ 發生錯誤：{e}')
        print(e)

    try:
        if audio_file:
            os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)
