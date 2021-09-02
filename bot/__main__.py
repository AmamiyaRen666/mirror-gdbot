import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from bot import app, alive
from sys import executable

from telegram import ParseMode
from telegram.ext import CommandHandler
from wserver import start_server_async
from bot import bot, dispatcher, updater, IMAGE_URL, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, SERVER_PORT
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, torrent_search, clone, watch, delete, speedtest, reboot


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>⏰ Uptime : {currentTime}</b>\n' \
            f'<b>💨 Total Disk Space : {total}</b>\n' \
            f'<b>📈 Used : {used}</b> ' \
            f'<b>📉 Free : {free}</b>\n\n' \
            f'<b>📊 Data Usage 📊</b>\n\n<b>🔺 Upload : {sent}</b>\n' \
            f'<b>🔻 Download : {recv}</b>\n\n📊 <b>Performance Meter</b> 📊\n\n' \
            f'<b> 🖥️ CPU  : {cpuUsage}%</b>\n ' \
            f'<b>⚙️ RAM : {memory}%</b>\n ' \
            f'<b>🗃️ DISK  : {disk}%</b>'
    update.effective_message.reply_photo(IMAGE_URL, stats, parse_mode=ParseMode.HTML)


def start(update, context):
    start_string = f'''
This Bot can mirroring your file/link download to upload on Google Drive (For Better Fast Speed & Full Speed Bandwidth).
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
    buttons = button_build.ButtonMaker()
    buttons.buildbutton(" ↗️ ", "https://t.me/TrucyWrightAgency")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))
    uptime = get_readable_time((time.time() - botStartTime))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        if update.message.chat.type == "private" :
            sendMessage(f"Hey, I'm Alive 🙂\nSince : <code>{uptime}</code>", context.bot, update)
        else :
            update.effective_message.reply_photo(IMAGE_URL, start_string, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else :
        sendMessage(f"🚫 Oops! You Not a Authorized User 🚫", context.bot, update)


def restart(update, context):
    restart_message = sendMessage("🔄 Restarting, Please Wait! 🔄", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.terminate()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start Mirroring

/{BotCommands.MirrorCommand} qb [magnet_link][torrent_file]: Start Mirroring With qBittorrent

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start Mirroring and Upload the Archived (.tar) Extension

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Start Mirroring and Upload the Archived (.zip) Extension

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts Mirroring and Extracts to Google Drive

/{BotCommands.CloneCommand} [gdrive_url]: Copy File/Folder to Google Drive

/{BotCommands.DeleteCommand} [gdrive_url]: Delete File From Google Drive

/{BotCommands.WatchCommand} [youtube-dl]: Mirror Through YouTube-DL. Click /{BotCommands.WatchCommand} For More Help

/{BotCommands.TarWatchCommand} [youtube-dl]: Mirror Through YouTube-DL and Upload the Archived (.tar) Extension

/{BotCommands.CancelMirror}: Cancel Mirror

/{BotCommands.AddSudoCommand}: Add Sudo User (Only Owner)

/{BotCommands.RmSudoCommand}: Remove Sudo Users (Only Owner)

/{BotCommands.ListCommand} [keywords] : Search File/Folder in the Google Drive

/{BotCommands.StatusCommand}: Shows a status of all the Downloads

/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.PingCommand}: Check Bot Alive/Dead

/{BotCommands.SpeedCommand}: Check Internet Speed

/{BotCommands.TsHelpCommand}: Torrent Search Module
'''

    help_string = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start Mirroring

/{BotCommands.MirrorCommand} qb [magnet_link][torrent_file]: Start Mirroring With qBittorrent

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start Mirroring and Upload the Archived (.tar) Extension

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Start Mirroring and Upload the Archived (.zip) Extension

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts Mirroring and Extracts to Google Drive

/{BotCommands.CloneCommand} [gdrive_url]: Copy File/Folder to Google Drive

/{BotCommands.DeleteCommand} [gdrive_url]: Delete File From Google Drive

/{BotCommands.WatchCommand} [youtube-dl]: Mirror Through YouTube-DL. Click /{BotCommands.WatchCommand} For More Help

/{BotCommands.TarWatchCommand} [youtube-dl]: Mirror Through YouTube-DL and Upload the Archived (.tar) Extension

/{BotCommands.CancelMirror}: Cancel Mirror

/{BotCommands.AddSudoCommand}: Add Sudo User (Only Owner)

/{BotCommands.RmSudoCommand}: Remove Sudo Users (Only Owner)

/{BotCommands.AuthorizeCommand}: Authorize a Chat or a User to use the Bot

/{BotCommands.UnAuthorizeCommand}: Unauthorize a Chat or a User to use the Bot 

/{BotCommands.ListCommand} [keywords] : Search File/Folder in the Google Drive

/{BotCommands.StatusCommand}: Shows a status of all the Downloads

/{BotCommands.PingCommand}: Check Bot Alive/Dead

/{BotCommands.SpeedCommand}: Check Internet Speed

/{BotCommands.TsHelpCommand}: Torrent Search Module
'''

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


botcmds = [
        (f'{BotCommands.HelpCommand}','Get Detailed Help'),
        (f'{BotCommands.MirrorCommand}', 'Start Mirroring'),
        (f'{BotCommands.TarMirrorCommand}','Start Mirroring and upload as .tar'),
        (f'{BotCommands.ZipMirrorCommand}','Start Mirroring and upload as .zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Extract Files and Upload to Drive'),
        (f'{BotCommands.CloneCommand}','Copy File/Folder to Drive'),
        (f'{BotCommands.DeleteCommand}','Delete File From Drive'),
        (f'{BotCommands.WatchCommand}','Mirror YouTube-DL'),
        (f'{BotCommands.TarWatchCommand}','Mirror YouTube-DL as .tar'),
        (f'{BotCommands.CancelMirror}','Cancel Mirror'),
        (f'{BotCommands.CancelAllCommand}','Cancel all tasks'),
        (f'{BotCommands.ListCommand}','Search Files in Drive'),
        (f'{BotCommands.StatusCommand}','Check Status Mirror'),
        (f'{BotCommands.StatsCommand}','Bot Usage'),
        (f'{BotCommands.PingCommand}','Ping the Bot'),
        (f'{BotCommands.RestartCommand}','Restart the bot [owner/sudo only]'),
        (f'{BotCommands.TsHelpCommand}','Torrent Search Module')
    ]


def main():
    fs_utils.start_cleanup()

    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(SERVER_PORT))

    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("🔄 Restarted successfully! ✅", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
