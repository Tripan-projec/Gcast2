import os
import asyncio
import random
import string

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

FAILED_CHATS = []
LAST_MESSAGES = {}

AUTO_GCAST_RUNNING = False
AUTO_GCAST_TASK = None


# =========================
# RANDOM TASK ID
# =========================

def random_id(length=8):

    return ''.join(
        random.choice(
            string.ascii_letters + string.digits
        ) for _ in range(length)
    )


# =========================
# SEND GCAST
# =========================

async def send_gcast(message, owner_name):

    global FAILED_CHATS
    global LAST_MESSAGES

    success = 0
    failed = 0

    FAILED_CHATS = []

    tid = random_id()

    async for dialog in client.iter_dialogs():

        try:

            if dialog.is_group:

                # =========================
                # HAPUS PESAN LAMA
                # =========================

                if dialog.id in LAST_MESSAGES:

                    try:

                        await client.delete_messages(
                            dialog.id,
                            LAST_MESSAGES[dialog.id]
                        )

                    except:
                        pass

                # =========================
                # KIRIM GCAST BARU
                # =========================

                msg = await client.send_message(
                    dialog.id,
                    message
                )

                LAST_MESSAGES[dialog.id] = msg.id

                success += 1

                await asyncio.sleep(1)

        except Exception as e:

            failed += 1

            FAILED_CHATS.append(
                f"{dialog.name} -> {str(e)}"
            )

    text = f"""
<blockquote expandable>
⚠️ <b>Gcast Sukses</b>

✅ Success: {success}
❌ Failed: {failed}
✉️ Type: gcast
⚙️ Task ID: {tid}
👤 Owner: {owner_name}

Type <code>.bc-error</code> to view failed broadcast.
</blockquote>
"""

    return text


# =========================
# GCAST SEKALI
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.gcast\s+(.+)'
))
async def gcast(event):

    text = event.pattern_match.group(1)

    await event.edit(
        "⏳ Mengirim broadcast..."
    )

    me = await client.get_me()

    result = await send_gcast(
        text,
        me.first_name
    )

    await event.edit(
        result,
        parse_mode='html'
    )


# =========================
# AUTO GCAST
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.autogcast(\d+)\s+(.+)'
))
async def auto_gcast(event):

    global AUTO_GCAST_RUNNING
    global AUTO_GCAST_TASK

    menit = int(
        event.pattern_match.group(1)
    )

    text = event.pattern_match.group(2)

    if AUTO_GCAST_RUNNING:

        return await event.edit(
            "⚠️ Auto gcast sudah aktif."
        )

    AUTO_GCAST_RUNNING = True

    await event.edit(
        f"🔥 Auto Gcast aktif\n"
        f"⏱ Interval: {menit} menit"
    )

    async def loop_gcast():

        global AUTO_GCAST_RUNNING

        while AUTO_GCAST_RUNNING:

            try:

                me = await client.get_me()

                result = await send_gcast(
                    text,
                    me.first_name
                )

                await client.send_message(
                    "me",
                    result,
                    parse_mode='html'
                )

            except Exception as e:

                await client.send_message(
                    "me",
                    f"❌ Error:\n{str(e)}"
                )

            await asyncio.sleep(
                menit * 60
            )

    AUTO_GCAST_TASK = asyncio.create_task(
        loop_gcast()
    )


# =========================
# STOP GCAST
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.stopgcast$'
))
async def stop_gcast(event):

    global AUTO_GCAST_RUNNING
    global AUTO_GCAST_TASK

    AUTO_GCAST_RUNNING = False

    if AUTO_GCAST_TASK:

        AUTO_GCAST_TASK.cancel()

    await event.edit(
        "🛑 Auto Gcast dihentikan"
    )


# =========================
# BC ERROR
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.bc-error$'
))
async def bc_error(event):

    if not FAILED_CHATS:

        return await event.edit(
            "✅ Tidak ada chat gagal."
        )

    text = "❌ CHAT GAGAL:\n\n"

    for x in FAILED_CHATS:

        text += f"{x}\n"

    await event.edit(text)


# =========================
# HELP
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.help$'
))
async def help_cmd(event):

    text = """
🔥 MENU GCAST

.gcast teks
= gcast sekali

.autogcast10 teks
= auto gcast tiap 10 menit

.autogcast15 teks
= auto gcast tiap 15 menit

.stopgcast
= stop auto gcast

.bc-error
= lihat chat gagal

.ping
= cek bot online

.help
= menu bantuan
"""

    await event.edit(text)


# =========================
# PING
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.ping$'
))
async def ping(event):

    await event.edit(
        "🏓 Pong! Bot aktif."
    )


# =========================
# START BOT
# =========================

async def main():

    await client.start()

    me = await client.get_me()

    print(
        f"🔥 USERBOT GCAST ONLINE: {me.first_name}"
    )

    await client.run_until_disconnected()

asyncio.run(main())
