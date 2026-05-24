import os
import asyncio
import random
import string

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.types import Chat, Channel
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
OWNER_ID = int(os.getenv("OWNER_ID"))
OWNER_NAME = os.getenv("OWNER_NAME", "OWNER")

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

active_auto = False
last_messages = {}

def task_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

async def get_groups():
    dialogs = await client.get_dialogs()
    groups = []

    for d in dialogs:
        if isinstance(d.entity, (Chat, Channel)):
            groups.append(d)

    return groups

async def send_broadcast(message):
    success = 0
    failed = 0

    groups = await get_groups()

    for group in groups:
        try:
            # hapus pesan sebelumnya kalau ada
            if group.id in last_messages:
                try:
                    await client.delete_messages(group.id, last_messages[group.id])
                except:
                    pass

            sent = await client.send_message(group.id, message)

            # simpan id pesan terakhir
            last_messages[group.id] = sent.id

            success += 1

        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)

        except Exception:
            failed += 1

        await asyncio.sleep(2)

    return success, failed

@client.on(events.NewMessage(pattern=r"\.gcast (.+)", outgoing=True))
async def gcast(event):
    if event.sender_id != OWNER_ID:
        return

    msg = event.pattern_match.group(1)

    await event.edit("📡 Memulai broadcast...")

    ok, bad = await send_broadcast(msg)

    tid = task_id()

    text = (
        f"⚠️ Broadcast berhasil\n\n"
        f"✅ Berhasil: {ok}\n"
        f"❌ Gagal: {bad}\n"
        f"✉️ Tipe: gcast\n"
        f"🤖 ID Tugas: {tid}\n"
        f"👤 Owner: {OWNER_NAME}"
    )

    await event.edit(text)

@client.on(events.NewMessage(pattern=r"\.autogcast (\d+) (.+)", outgoing=True))
async def auto_gcast(event):
    global active_auto

    if event.sender_id != OWNER_ID:
        return

    menit = int(event.pattern_match.group(1))
    pesan = event.pattern_match.group(2)

    active_auto = True

    await event.reply(
        f"🔥 AUTO GCAST AKTIF\n\n"
        f"⏱ Interval: {menit} menit"
    )

    while active_auto:
        await send_broadcast(pesan)
        await asyncio.sleep(menit * 60)

@client.on(events.NewMessage(pattern=r"\.stopgcast", outgoing=True))
async def stop_gcast(event):
    global active_auto

    active_auto = False

    await event.reply("🛑 AUTO GCAST dihentikan")

async def main():
    await client.start()

    me = await client.get_me()
    print(f"LOGIN BERHASIL: {me.first_name}")

    await client.run_until_disconnected()

asyncio.run(main())
