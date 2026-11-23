# SongPlayRoBot

Telegram 音樂搜尋與音訊下載機器人。支援以歌曲名稱搜尋 YouTube，或直接傳入 YouTube 網址下載音訊。

## 功能

- `/start`：啟動訊息及導覽按鈕
- `/s <歌曲名稱或 YouTube 網址>`：搜尋並傳送音訊
- `/help`：使用說明
- `/ping`：服務狀態檢查
- `/cookie_check`：檢查 Cookies 是否已設定
- Cookies 選填；遇到登入、年齡或地區限制時可設定
- 非同步下載工作執行緒，避免阻塞 Telegram 事件迴圈
- 可設定同時下載數量
- 自動轉換及壓縮歌曲縮圖，符合 Telegram 音訊縮圖限制
- 每次下載使用獨立暫存目錄，完成後自動清理
- Docker / Docker Compose 部署，並保留 Windows 本機執行方式

## 部署方式 A：Ubuntu 22.04 + Docker Compose（建議）

### 1. 安裝 Docker Engine 與 Compose Plugin

請依照 Docker 官方 Ubuntu 安裝文件安裝 Docker Engine、containerd 及 Compose Plugin：
https://docs.docker.com/engine/install/ubuntu/

確認：
```bash
docker --version
docker compose version
```

### 2. 下載專案

```bash
git clone https://github.com/makubex2010/SongPlayRoBot.git
cd SongPlayRoBot
```

測試更新分支：
```bash
git fetch origin
git checkout update/ubuntu-docker-modernization
```

### 3. 設定環境變數

```bash
cp .env.example .env
nano .env
```

至少填入 `API_ID`、`API_HASH`、`BOT_TOKEN`。API ID 與 Hash 可從 https://my.telegram.org 取得，Bot Token 由 Telegram 的 @BotFather 提供。

### 4. 啟動

```bash
docker compose up -d --build
docker compose logs -f
```

停止：
```bash
docker compose down
```

更新：
```bash
git pull
docker compose up -d --build
```

## 部署方式 B：Windows 10 / 11

需要 Python 3.10 或更新版本，以及 FFmpeg。

1. 安裝 Python：https://www.python.org/downloads/
2. 安裝 FFmpeg，並將 `ffmpeg` 加入 PATH：https://ffmpeg.org/download.html
3. 複製 `.env.example` 為 `.env`，填入必要設定。
4. 在專案目錄開啟 PowerShell：

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## 環境變數

| 變數 | 必要 | 說明 |
|---|---|---|
| `API_ID` | 是 | Telegram API ID；舊設定 `APP_ID` 仍可作為相容備援 |
| `API_HASH` | 是 | Telegram API Hash |
| `BOT_TOKEN` | 是 | BotFather 提供的 Token |
| `OWNER` | 否 | Telegram 使用者名稱，不含 @ |
| `START_MSG` | 否 | 啟動訊息，`{0}` 會替換成使用者名稱 |
| `START_IMG` | 否 | 啟動圖片網址或本機路徑；留空則傳送文字 |
| `COOKIES` | 否 | Netscape 格式 YouTube cookies 內容 |
| `DOWNLOAD_LOCATION` | 否 | 下載暫存目錄 |
| `SESSION_LOCATION` | 否 | Pyrogram Session 目錄 |
| `MAX_CONCURRENT_DOWNLOADS` | 否 | 同時下載數量，預設 2 |
| `COMMUNITY_URL` | 否 | 社群按鈕網址 |
| `COMMUNITY_BUTTON` | 否 | 社群按鈕文字 |

## Cookies 注意事項

Cookies 不是所有影片都必須設定。公開可存取影片可先不設定；遇到 YouTube 登入、年齡或地區限制時，才嘗試設定有效 Cookies。請勿將 `.env` 或 cookies.txt 上傳到 GitHub，也不要分享 Bot Token。

## 安全與使用規範

- `.env`、session 檔案、cookies 與下載目錄不應提交至版本庫。
- 請遵守 YouTube 服務條款、著作權規範及所在地法律，只下載你有權使用的內容。
