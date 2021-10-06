import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from sys import executable

from telegram import ParseMode
from telegram.ext import CommandHandler
from telegraph import Telegraph
from wserver import start_server_async
from bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, PORT, alive, web, OWNER_ID, AUTHORIZED_CHATS, telegraph_token
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, torrent_search, delete, speedtest, count


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
    stats = f'<b>Bot Uptime:</b> <code>{currentTime}</code>\n' \
            f'<b>Total Disk Space:</b> <code>{total}</code>\n' \
            f'<b>Used:</b> <code>{used}</code> ' \
            f'<b>Free:</b> <code>{free}</code>\n\n' \
            f'<b>Upload:</b> <code>{sent}</code>\n' \
            f'<b>Download:</b> <code>{recv}</code>\n\n' \
            f'<b>CPU:</b> <code>{cpuUsage}%</code> ' \
            f'<b>RAM:</b> <code>{memory}%</code> ' \
            f'<b>DISK:</b> <code>{disk}%</code>'
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Source", "https://github.com/gabrierr/zukkymirrorbot")
    buttons.buildbutton("My Master", "https://t.me/RosySandro")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
Hello, Saya Zukky si Mirror Bot. Tugas saya adalah mengubah Torrent / Direct Link menjadi GDrive Url!

Ketik /{BotCommands.HelpCommand} untuk membuka list perintah
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup(
            'Oops! bukan Authorized user.\nSilahkan kontak owner @RosySandro.',
            context.bot,
            update,
            reply_markup,
        )


def restart(update, context):
    restart_message = sendMessage("Proses Restart, Tunggu Sebentar!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.terminate()
    web.terminate()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b>: Untuk membuka pesan ini
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [download_url][magnet_link]: Memulai mirroring link menjadi Google Drive.
<br><br>
<b>/{BotCommands.TarMirrorCommand}</b> [download_url][magnet_link]: Mulai mirroring dan upload versi unduhan (.tar) yang diarsipkan
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Mulai mirroring dan upload versi unduhan (.zip) yang diarsipkan
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Mulai mirroring file arsip menggunakan dan otomatis mengekstrak file ke Google Drive
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [magnet_link]: Mulai mirroring menggunakan qBittorrent, gunakan <b>/{BotCommands.QbMirrorCommand} s</b> untuk memilih file sebelum download
<br><br>
<b>/{BotCommands.QbTarMirrorCommand}</b> [magnet_link]: Mulai mirroring menggunakan qBittorrent dan unggah versi unduhan (.tar) yang diarsipkan
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [magnet_link]: Mulai mirroring menggunakan qBittorrent dan unggah versi unduhan (.zip) yang diarsipkan
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [magnet_link]:  Mulai mirroring file arsip menggunakan qBittorrent dan otomatis mengekstrak file ke Google Drive
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url]: Menyalin file/folder ke Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url]: Menghitung file/folder Google Drive Links
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file dari Google Drive (hanya Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [youtube-dl supported link]: Mirror menggunakan youtube-dl. klik <b>/{BotCommands.WatchCommand}</b> untuk bantuan
<br><br>
<b>/{BotCommands.TarWatchCommand}</b> [youtube-dl supported link]: Mirror menggunakan youtube-dl dan tar sebelum uploading
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [youtube-dl supported link]: Mirror menggunakan youtube-dl dan zip sebelum uploading
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Membatalkan proses mirroring
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: Membatalkan semua proses yang berjalan
<br><br>
<b>/{BotCommands.ListCommand}</b> [search term]: Mencari file/folder yang tersimpan di Google Drive
<br><br>
<b>/{BotCommands.StatusCommand}</b>: Menampilkan status mirroring
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Menampilkan Statistik mesin tempat bot dihosting
'''

    help_string = f'''
/{BotCommands.PingCommand}: Melakukan tes koneksi pada bot

/{BotCommands.AuthorizeCommand}: Authorize chat atau user untuk menggunakan bot (hanya bisa dilakukan oleh Owner & Sudo)

/{BotCommands.UnAuthorizeCommand}: Unauthorize chat atau user untuk menggunakan bot (hanya bisa dilakukan oleh Owner & Sudo)

/{BotCommands.AuthorizedUsersCommand}: Menampilkan Authorized user (Hanya Owner & Sudo)

/{BotCommands.AddSudoCommand}: Menambah sudo user (Hanya Owner)

/{BotCommands.RmSudoCommand}: Menghapus sudo users (Hanya Owner)

/{BotCommands.RestartCommand}: Melakukan restart bot

/{BotCommands.LogCommand}: Mendapatkan log file dari bot. Berguna untuk mendapatkan laporan kerusakan

/{BotCommands.SpeedCommand}: Cek kecepatan internet host dari bot

/{BotCommands.ShellCommand}: Menjalankan perintah di Shell (Hanya Owner)

/{BotCommands.ExecHelpCommand}: Mendapatkan bantuan untuk Executor module (Hanya Owner)

/{BotCommands.TsHelpCommand}: Mendapatkan bantuan untuk modul pencarian Torrent
'''
    help = Telegraph(access_token=telegraph_token).create_page(title = 'Bantuan Zukky Mirrorbot', author_name='Rosydr',
                                                               author_url='https://t.me/RosySandro', html_content=help_string_telegraph)["path"]
    button = button_build.ButtonMaker()
    button.buildbutton("Lihat Perintah Lainnya >>", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

'''
botcmds = [
        (f'{BotCommands.HelpCommand}','Mendapatkan bantuan secara detail'),
        (f'{BotCommands.MirrorCommand}', 'Memulai mirror'),
        (f'{BotCommands.TarMirrorCommand}','Memulai mirroring dan upload sebagai .tar'),
        (f'{BotCommands.ZipMirrorCommand}','Memulai mirroring dan upload sebagai .zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Extract file'),
        (f'{BotCommands.QbMirrorCommand}','Memulai mirroring menggunakan qBittorrent'),
        (f'{BotCommands.QbTarMirrorCommand}','Memulai mirroring dan upload sebagai .tar menggunakan qb'),
        (f'{BotCommands.QbZipMirrorCommand}','Memulai mirroring dan upload sebagai .zip menggunakan qb'),
        (f'{BotCommands.QbUnzipMirrorCommand}','Extract file menggunakan qBitorrent'),
        (f'{BotCommands.CloneCommand}','Salin file/folder ke Drive'),
        (f'{BotCommands.CountCommand}','Menghitung file/folder pada Drive Link'),
        (f'{BotCommands.DeleteCommand}','Menghapus file dari Drive'),
        (f'{BotCommands.WatchCommand}','Mirror Youtube menggunakan Youtube-dl'),
        (f'{BotCommands.TarWatchCommand}','Mirror Youtube playlist link sebagai .tar'),
        (f'{BotCommands.ZipWatchCommand}','Mirror Youtube playlist link sebagai .zip'),
        (f'{BotCommands.CancelMirror}','Membatalkan proses mirror'),
        (f'{BotCommands.CancelAllCommand}','Membatalkan semua proses mirror'),
        (f'{BotCommands.ListCommand}','Mencari file di Drive'),
        (f'{BotCommands.StatusCommand}','Mendapatkan status mirror bot'),
        (f'{BotCommands.StatsCommand}','mendapatkan Stats pada bot'),
        (f'{BotCommands.PingCommand}','Melakukan ping pada bot'),
        (f'{BotCommands.RestartCommand}','Restart bot [hanya owner/sudo]'),
        (f'{BotCommands.LogCommand}','Mendapatkan log file bot [hanyaowner/sudo]'),
        (f'{BotCommands.TsHelpCommand}','Mendapatkan modul bantuan pencarian Torrent')
    ]
'''

def main():
    fs_utils.start_cleanup()
    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(PORT))
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Proses Restart Berhasil!", chat_id, msg_id)
        os.remove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Bot Telah di Restart!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)
    # bot.set_my_commands(botcmds)
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
