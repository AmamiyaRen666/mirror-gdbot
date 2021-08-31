from telegram.ext import CommandHandler
from telegram import Bot, Update
from bot import DOWNLOAD_DIR, dispatcher, LOGGER
from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage
from .mirror import MirrorListener
from bot.helper.mirror_utils.download_utils.youtube_dl_download_helper import YoutubeDLHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
import threading


def _watch(bot: Bot, update, isTar=False):
    mssg = update.message.text
    message_args = mssg.split(' ')
    name_args = mssg.split('|')
    
    try:
        link = message_args[1]
    except IndexError:
        msg = f"<b>Open-Source Download Manager For Video & Audio from YouTube and over 1000 other Video Hosting Websites</b>\n\n"
        msg += "Tutorial ⤵️\n\n"
        msg += "‼️ /{BotCommands.WatchCommand} [YTDL Supported Link] [Quality] | [Custom Name]\n"
        msg += f"‼️ <b>Features Available :- Quality & Custom Name & Add Extension</b>\n"
        msg += "‼️ <b>Quality Available :- audio (mp3), 144, 240, 360, 480, 720, 1080, 1440, 2160</b>\n"
        msg += "‼️ <b>Supported Link : https://ytdl-org.github.io/youtube-dl/supportedsites.html\n\n"
        msg += "A. Custom File Name, Enter it After |\n\n"
        msg += f"Example :-\n"
        msg += "<code>/{BotCommands.WatchCommand} https://youtu.be/QMOadtGpwlw 720 |Ikson - New Day.mp4</code>\n\n"
		msg += "This file will be downloaded in 720p quality and its name will be Ikson - New Day.mp4\n\n"
		msg += f"B. Converting to .mp3 / Audio\n\n"
        msg += "Example :-\n"
        msg += "<code>/{BotCommands.WatchCommand} https://youtu.be/QMOadtGpwlw audio</code>\n\n"
        msg += "This file will be downloaded in .mp3/audio and its name will be Ikson - Alive.mp3\n\n"
		msg += f"C. Add Extension / Change Extension / Custom File Name\n\n"
        msg += "Example :-\n"
        msg += "<code>/{BotCommands.WatchCommand} https://www.youtube.com/watch?v=kEm3PiNVEsI 720 |Ikson - Paradise.mp4</code>\n\n"
        msg += "add at the end of the word, for example .mp4 .mkv .mp3 and others"
        sendMessage(msg, bot, update)
        return
    
    try:
      if "|" in mssg:
        mssg = mssg.split("|")
        qual = mssg[0].split(" ")[2]
        if qual == "":
          raise IndexError
      else:
        qual = message_args[2]
      if qual != "audio":
        qual = f'bestvideo[height<={qual}]+bestaudio/best[height<={qual}]'
    except IndexError:
      qual = "bestvideo+bestaudio/best"
    
    try:
      name = name_args[1]
    except IndexError:
      name = ""
    
    pswd = ""
    listener = MirrorListener(bot, update, pswd, isTar)
    ydl = YoutubeDLHelper(listener)
    threading.Thread(target=ydl.add_download,args=(link, f'{DOWNLOAD_DIR}{listener.uid}', qual, name)).start()
    sendStatusMessage(update, bot)


def watchTar(update, context):
    _watch(context.bot, update, True)


def watch(update, context):
    _watch(context.bot, update)


mirror_handler = CommandHandler(BotCommands.WatchCommand, watch,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
tar_mirror_handler = CommandHandler(BotCommands.TarWatchCommand, watchTar,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)


dispatcher.add_handler(mirror_handler)
dispatcher.add_handler(tar_mirror_handler)
