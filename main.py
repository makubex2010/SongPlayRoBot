import os
import re
from YoutubeDL import YoutubeDL

class Config:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    START_MSG = os.environ.get("START_MSG")
    START_IMG = os.environ.get("START_IMG")
    OWNER = os.environ.get("OWNER") 
    DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS/")
    msg = {}
