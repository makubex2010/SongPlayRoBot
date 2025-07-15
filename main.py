from pyrogram import Client, filters

import yt_dlp
from youtube_search import YoutubeSearch
import requests

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os
from config import Config

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)


app = pyrogram.Client(
      "mwk",
       bot_token=Config.BOT_TOKEN,
       api_id=Config.API_ID,
       api_hash=Config.API_HASH,
    )
app.run()
