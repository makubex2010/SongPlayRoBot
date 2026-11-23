import os
from pathlib import Path


def _required(name: str, fallback: str = "") -> str:
    value = os.getenv(name, fallback).strip()
    if not value:
        raise RuntimeError(
            f"缺少必要環境變數 {name}。請複製 .env.example 為 .env 並完成設定。"
        )
    return value


class Config:
    _api_id = os.getenv("API_ID") or os.getenv("APP_ID") or ""
    try:
        API_ID = int(_api_id)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("API_ID（或舊名稱 APP_ID）必須是整數。") from exc

    API_HASH = _required("API_HASH")
    BOT_TOKEN = _required("BOT_TOKEN")
    OWNER = os.getenv("OWNER", "ownerusername").strip().lstrip("@")
    START_MSG = os.getenv("START_MSG", "歡迎使用音樂下載機器人，{0}！\n傳送 /s 歌曲名稱即可開始。")
    START_IMG = os.getenv("START_IMG", "").strip()
    DOWNLOAD_LOCATION = os.getenv("DOWNLOAD_LOCATION", "./downloads/")
    SESSION_LOCATION = os.getenv("SESSION_LOCATION", "./sessions/")
    COOKIES = os.getenv("COOKIES", "")
    MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "2"))
    COMMUNITY_URL = os.getenv("COMMUNITY_URL", "https://t.me/PlayStationTw")
    COMMUNITY_BUTTON = os.getenv("COMMUNITY_BUTTON", "🎮 PlayStation 世界玩家會館 🎮")
    REPOSITORY_URL = "https://github.com/makubex2010/SongPlayRoBot"

    Path(DOWNLOAD_LOCATION).expanduser().mkdir(parents=True, exist_ok=True)
    Path(SESSION_LOCATION).expanduser().mkdir(parents=True, exist_ok=True)
