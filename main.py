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

AUTO_GCAST = False
FAILED_CHATS = []
LAST_MESSAGES = {}

def random_id(length=8):
    return ''.join(
        random.choice(
            string.ascii_letters + string.digits
        ) for _ in range(length)
    )

# =========================
# SEND GCAST
# =========================

async def send_gcast(message):

    global FAILED_CHATS
    global LAST_MESSAGES

    success = 0
    failed = 0

    FAILED_CHATS = []

    tid = random_id()

    async for dialog in client.iter_dialogs():

        try:

            # KHUSUS GROUP
            if dialog.is_group:

                # HAPUS PESAN GCAST LAMA
                if dialog.id in LAST_MESSAGES:

                    try:
                        await client.delete_messages(
                            dialog.id,
                            LAST_MESSAGES[dialog.id]
                        )

                    except:
                        pass

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

    ttext = f"""
> ⚠️ Gcast Sukses

> ✅ Success: {success}
> ❌ Failed: {failed}
> ✉️ Type: gcast
> ⚙️ Task ID: {tid}
> 👤 Owner: POPAYE?

> Type .bc-error to view failed in broadcast.
"""

    return text


# =========================
# GCAST SEKALI
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.gcast (.+)'
))
async def gcast(event):

    text = event.pattern_match.group(1)

    await event.edit(
        "⏳ Mengirim broadcast..."
    )

    result = await send_gcast(text)

    await event.edit(result)


# =========================
# AUTO GCAST
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.gcast(\d+) (.+)'
))
async def auto_gcast(event):

    global AUTO_GCAST

    menit = int(
        event.pattern_match.group(1)
    )

    text = event.pattern_match.group(2)

    AUTO_GCAST = True

    await event.edit(
        f"🔥 Auto Gcast aktif\n⏱ {menit} menit"
    )

    while AUTO_GCAST:

        result = await send_gcast(text)

        await event.respond(result)

        await asyncio.sleep(
            menit * 60
        )


# =========================
# STOP GCAST
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.stopgcast$'
))
async def stop_gcast(event):

    global AUTO_GCAST

    AUTO_GCAST = False

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

.gcast10 teks
= auto gcast 10 menit

.gcast15 teks
= auto gcast 15 menit

.stopgcast
= stop auto gcast

.bc-error
= lihat chat gagal

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
# START
# =========================

async def main():

    await client.start()

    me = await client.get_me()

    print(
        f"🔥 USERBOT GCAST ONLINE: {me.first_name}"
    )

    await client.run_until_disconnected()

asyncio.run(main())
