import os

class Config:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    START_MSG = os.environ.get("START_MSG", "歡迎使用音樂機器人！")
    START_IMG = os.environ.get("START_IMG", "")
    OWNER = os.environ.get("OWNER")
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./downloads/")
    COOKIES = os.environ.get("COOKIES", "")
