from telegram.ext import CommandHandler
from bot.helper.mirror_utils.upload_utils import gdriveTools
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, download_dict, download_dict_lock, Interval
from bot.helper.ext_utils.bot_utils import get_readable_file_size, check_limit
import random
import string


def cloneNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    if len(args) > 1:
        link = args[1]
        gd = gdriveTools.GoogleDriveHelper()
        res, size, name, files = gd.clonehelper(link)
        if res != "":
            sendMessage(res, context.bot, update)
            return
        if STOP_DUPLICATE:
            LOGGER.info(f"๐ Checking File/Folder if Already in Drive... ๐")
            smsg, button = gd.drive_list(name)
            if smsg:
                msg3 = "๐ File/Folder is Already Available in Drive. โ\n\n๐ Here : โคต๏ธ"
                sendMarkup(msg3, context.bot, update, button)
                return
        if CLONE_LIMIT is not None:
            result = check_limit(size, CLONE_LIMIT)
            if result:
                msg2 = f'๐ซ Failed ๐ซ - Clone Limit {CLONE_LIMIT}.\n๐ Your File/Folder Size : {get_readable_file_size(clonesize)}.'
                sendMessage(msg2, context.bot, update)
                return
        if files < 15:
            msg = sendMessage(f"๐ Cloning : <code>{link}</code> ๐", context.bot, update)
            result, button = gd.clone(link)
            deleteMessage(context.bot, msg)
        else:
            drive = gdriveTools.GoogleDriveHelper(name)
            gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=12))
            clone_status = CloneStatus(drive, size, update, gid)
            with download_dict_lock:
                download_dict[update.message.message_id] = clone_status
            sendStatusMessage(update, context.bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[update.message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass
        if update.message.from_user.username:
            uname = f'@{update.message.from_user.username}'
        else:
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
        if uname is not None:
            cc = f'\nโ <b>Status :- Successfully Cloned</b>\n\n๐๐ปโโ๏ธ <b>By :- {uname}</b> โจ'
            men = f'{uname} '
        if button == "cancelled" or button == "":
            sendMessage(men + result, context.bot, update)
        else:
            sendMarkup(result + cc, context.bot, update, button)
    else:
        sendMessage('๐ซ <b>Send Me Google Drive Shareable Link</b> ๐ซ', context.bot, update)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
