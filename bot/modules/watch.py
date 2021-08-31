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
		msg = f"<b>Open-Source Download Manager For Video & Audio from YouTube and over 1000 other Video Hosting Websites</b>"
        msg += "\n\nTutorial ⤵️"
        msg += "\n‼️ /{BotCommands.WatchCommand} [YTDL Supported Link] [Quality] | [Custom Name]"
		msg = f"\n‼️ <b>Features Available :- Quality & Custom Name & Add Extension</b>"
        msg += "\n‼️ <b>Quality Available :- audio (mp3), 144, 240, 360, 480, 720, 1080, 1440, 2160</b>"
        msg += "\n‼️ <b>Supported Link :-</b> https://ytdl-org.github.io/youtube-dl/supportedsites.html"
		msg = f"\n\nA. Custom File Name, Enter it After |"
        msg += "\n\nExample :-"
        msg += "\n<code>/{BotCommands.WatchCommand} https://youtu.be/QMOadtGpwlw 720 |Ikson - New Day.mp4</code>"
		msg = f"\n\nThis file will be downloaded in 720p quality and its name will be Ikson - New Day.mp4"
        msg += "\n\nB. Converting to .mp3"
        msg += "\nExample :-"
		msg = f"\n<code>/{BotCommands.WatchCommand} https://youtu.be/QMOadtGpwlw audio</code>"
        msg += "\n\nThis file will be downloaded in .mp3/audio and its name will be Ikson - Alive.mp3"
        msg += "\n\nC. Add Extension / Change Extension / Custom File Name"
		msg = f"\n\nExample :-"
        msg += "\n<code>/{BotCommands.WatchCommand} https://www.youtube.com/watch?v=kEm3PiNVEsI 720 |Ikson - Paradise.mp4</code>"
        msg += "\n\nadd at the end of the word, for example .mp4 .mkv .mp3 and others"
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
