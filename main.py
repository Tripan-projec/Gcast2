from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import asyncio
import random
import string
import time

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

AUTO_GCAST = False
AUTO_TASK = None
FAILED_CHATS = []
LAST_MESSAGES = {}

def random_id(length=8):
    return ''.join(
        random.choice(
            string.ascii_letters + string.digits
        ) for _ in range(length)
    )

async def send_gcast(message):

    global FAILED_CHATS
    global LAST_MESSAGES

    success = 0
    failed = 0

    FAILED_CHATS = []

    task_id = random_id()

    async for dialog in client.iter_dialogs():

        try:

            # KHUSUS GROUP
            if dialog.is_group:

                # HAPUS PESAN LAMA
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

       text = f"""
> ⚠️ Broadcast berhasil

> ✅ Berhasil: {ok}
> ❌ Gagal: {bad}
> ✉️ Tipe: gcast
> 🤖 ID Tugas: {tid}
> 👤 Owner: Anonymous

> Ketik .bc-error buat liat gagal.
"""

    await event.edit(text)


    return result


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
    global AUTO_TASK

    AUTO_GCAST = True

    menit = int(
        event.pattern_match.group(1)
    )

    pesan = event.pattern_match.group(2)

    delay = menit * 60

    await event.edit(
        f"🔥 Auto GCast aktif\n\n⏱ Delay: {menit} menit\n📨 Pesan: {pesan}"
    )

    async def loop_gcast():

        global AUTO_GCAST

        while AUTO_GCAST:

            result = await send_gcast(
                pesan
            )

            await event.respond(result)

            await asyncio.sleep(delay)

    AUTO_TASK = asyncio.create_task(
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

    global AUTO_GCAST
    global AUTO_TASK

    AUTO_GCAST = False

    if AUTO_TASK:
        AUTO_TASK.cancel()

    await event.edit(
        "🛑 Auto GCast dihentikan."
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

        await event.edit(
            "✅ Tidak ada error."
        )

        return

    text = "❌ LIST ERROR GCAST\n\n"

    for x in FAILED_CHATS[:30]:

        text += f"• {x}\n"

    await event.edit(text)


# =========================
# PING
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.ping$'
))
async def ping(event):

    start = time.time()

    msg = await event.edit(
        "🏓 Pinging..."
    )

    end = round(
        (time.time() - start) * 1000
    )

    await msg.edit(
        f"🏓 Pong!\n⚡ {end}ms"
    )


# =========================
# HELP
# =========================

@client.on(events.NewMessage(
    from_users='me',
    pattern=r'^\.help$'
))
async def help_menu(event):

    text = """
🔥 GCAST MENU 🔥

.gcast pesan
➜ Broadcast sekali

.gcast10 pesan
➜ Auto broadcast tiap 10 menit

.gcast15 pesan
➜ Auto broadcast tiap 15 menit

.stopgcast
➜ Stop auto broadcast

.bc-error
➜ Lihat list gagal

.ping
➜ Check userbot online

.help
➜ Menu command
"""

    await event.edit(text)

print("🔥 USERBOT GCAST ONLINE")

client.start()
client.run_until_disconnected()
