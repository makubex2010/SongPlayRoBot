import asyncio
import html
import logging
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

import yt_dlp
from PIL import Image
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(),
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("songplayrobot")

DOWNLOAD_DIR = Path(Config.DOWNLOAD_LOCATION).expanduser()
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_LIMIT = max(1, Config.MAX_CONCURRENT_DOWNLOADS)
download_semaphore = asyncio.Semaphore(DOWNLOAD_LIMIT)

app = Client("songplayrobot", api_id=Config.API_ID, api_hash=Config.API_HASH,
             bot_token=Config.BOT_TOKEN, workdir=Config.SESSION_LOCATION)


def _is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


def _download_audio(query: str):
    temp_dir = tempfile.mkdtemp(prefix="songplay_", dir=str(DOWNLOAD_DIR))
    options = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": str(Path(temp_dir) / "%(id)s.%(ext)s"),
        "noplaylist": True, "quiet": True, "no_warnings": True,
        "socket_timeout": 20, "retries": 3, "fragment_retries": 3,
        "extractor_retries": 2, "overwrites": True,
        "writethumbnail": True,
        "postprocessors": [{"key": "FFmpegThumbnailsConvertor", "format": "jpg"}],
    }
    cookie_text = Config.COOKIES.strip()
    if cookie_text:
        cookie_path = Path(temp_dir) / "cookies.txt"
        cookie_path.write_text(cookie_text, encoding="utf-8")
        options["cookiefile"] = str(cookie_path)

    try:
        target = query if _is_url(query) else "ytsearch1:" + query
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(target, download=True)
        if not info:
            raise RuntimeError("YouTube 沒有回傳可用的影片資訊。")
        if "entries" in info:
            info = next((entry for entry in info.get("entries", []) if entry), None)
        if not info:
            raise RuntimeError("找不到符合條件的歌曲。")

        candidates = [Path(item["filepath"]) for item in info.get("requested_downloads") or []
                      if item.get("filepath")]
        if info.get("_filename"):
            candidates.append(Path(info["_filename"]))
        candidates.extend(Path(temp_dir).glob("*"))
        audio_path = next((p for p in candidates
                           if p.is_file() and p.name != "cookies.txt"), None)
        if audio_path is None:
            raise RuntimeError("下載完成但找不到音訊檔案。")

        thumbnail_path = None
        for candidate in Path(temp_dir).glob("*.jpg"):
            try:
                image = Image.open(candidate).convert("RGB")
                image.thumbnail((320, 320))
                thumb = Path(temp_dir) / "telegram_thumb.jpg"
                quality = 88
                image.save(thumb, format="JPEG", quality=quality, optimize=True)
                while thumb.stat().st_size > 190_000 and quality > 55:
                    quality -= 8
                    image.save(thumb, format="JPEG", quality=quality, optimize=True)
                if thumb.stat().st_size <= 200_000:
                    thumbnail_path = str(thumb)
                break
            except Exception as exc:
                logger.warning("縮圖處理失敗，將不附縮圖：%s", exc)
        return temp_dir, str(audio_path), thumbnail_path, info
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    welcome = Config.START_MSG.format(message.from_user.mention)
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(Config.COMMUNITY_BUTTON, url=Config.COMMUNITY_URL)],
        [InlineKeyboardButton("所有者", url=f"https://t.me/{Config.OWNER}"),
         InlineKeyboardButton("源代碼", url=Config.REPOSITORY_URL)],
    ])
    if Config.START_IMG:
        try:
            await message.reply_photo(Config.START_IMG, caption=welcome, reply_markup=buttons)
            return
        except Exception as exc:
            logger.warning("啟動圖片傳送失敗，改用文字訊息：%s", exc)
    await message.reply_text(welcome, reply_markup=buttons)


@app.on_message(filters.command(["help", "starthelp"]) & filters.private)
async def help_handler(client, message):
    await message.reply_text(
        "🎵 **SongPlayRoBot 使用說明**\n\n"
        "/s 歌曲名稱 — 搜尋並下載 YouTube 音訊\n"
        "/s YouTube網址 — 下載指定影片音訊\n"
        "/ping — 檢查機器人狀態\n"
        "/cookie_check — 檢查 Cookies 設定\n"
        "/help — 顯示說明\n\n"
        "Cookies 為選填；部分受限制影片仍可能需要有效 Cookies。"
    )


@app.on_message(filters.command("ping") & filters.private)
async def ping_handler(client, message):
    await message.reply_text("🏓 SongPlayRoBot 正常運作中！")


@app.on_message(filters.command("cookie_check") & filters.private)
async def cookie_check_handler(client, message):
    if Config.COOKIES.strip():
        await message.reply_text("✅ 已設定 YouTube Cookies。")
    else:
        await message.reply_text(
            "ℹ️ 尚未設定 Cookies。公開影片可先直接下載；遇到年齡、地區或登入限制時，可能需要有效 Cookies。"
        )


@app.on_message(filters.command("s") & filters.private)
async def search_and_download(client, message):
    query = " ".join(message.command[1:]).strip()
    if not query:
        # Send a normal message, not a reply to the user's command.
        await client.send_message(
            chat_id=message.chat.id,
            text="請提供歌曲名稱或 YouTube 網址。\\n例如：/s 南拳媽媽 下雨天",
        )
        return

    temp_dir = None
    async with download_semaphore:
        try:
            temp_dir, audio_path, thumbnail_path, info = await asyncio.to_thread(_download_audio, query)
            title = info.get("title") or Path(audio_path).stem
            webpage_url = info.get("webpage_url") or query
            duration = int(info.get("duration") or 0)
            caption = (f'<b>🎧 標題：</b><a href="{html.escape(webpage_url, quote=True)}">'
                       f'{html.escape(title)}</a>')

            # Send audio directly to the chat: do not quote/reply to the /s command.
            await client.send_audio(
                chat_id=message.chat.id,
                audio=audio_path,
                caption=caption,
                parse_mode=ParseMode.HTML,
                thumb=thumbnail_path,
                title=title[:64],
                duration=duration,
                performer=(info.get("artist") or info.get("uploader") or "")[:64],
            )

            # Delete the user's /s command only after Telegram accepted the audio.
            try:
                await message.delete()
                logger.info("已自動刪除使用者的歌曲下載指令")
            except Exception as delete_exc:
                logger.warning("無法刪除使用者下載指令：%s", delete_exc)

        except Exception as exc:
            logger.exception("歌曲處理失敗")
            error_text = str(exc).strip().replace("<", "‹").replace(">", "›")
            if len(error_text) > 700:
                error_text = error_text[:700] + "…"
            # Failure notice is sent as a standalone message, not as a reply.
            await client.send_message(
                chat_id=message.chat.id,
                text=(
                    "❌ 歌曲處理失敗。\\n"
                    f"<code>{html.escape(error_text)}</code>\\n\\n"
                    "請確認網址或歌曲名稱正確；若影片有存取限制，請檢查 Cookies。"
                ),
                parse_mode=ParseMode.HTML,
            )
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
