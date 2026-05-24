# Advanced GCast Features Upgrade

Ganti isi `main.py` kamu dengan versi ini.

```python
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import asyncio
import random
import string

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

AUTO_GCAST = False
AUTO_MESSAGE = ""
AUTO_DELAY = 600
LAST_MESSAGES = {}
FAILED_CHATS = []


def random_id(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


async def send_gcast(message):
    global FAILED_CHATS

    success = 0
    failed = 0
    FAILED_CHATS = []
    task_id = random_id()

    async for dialog in client.iter_dialogs():
        try:
            if dialog.is_group:

                # hapus pesan lama
                if dialog.id in LAST_MESSAGES:
                    try:
                        await client.delete_messages(dialog.id, LAST_MESSAGES[dialog.id])
                    except:
                        pass

                msg = await client.send_message(dialog.id, message)
                LAST_MESSAGES[dialog.id] = msg.id
                success += 1

            await asyncio.sleep(1)

        except Exception as e:
            failed += 1
            FAILED_CHATS.append(f"{dialog.name} -> {str(e)}")

    result = f"""
⚠️ Broadcast berhasil

✅ Berhasil: {success}
❌ Gagal: {failed}
✉️ Tipe: gcast
🤖 ID Tugas: {task_id}
👤 Owner: Anonymous

Ketik .bc-error buat lihat yang gagal.
"""

    return result


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.gcast (.+)'))
async def gcast(event):
    text = event.pattern_match.group(1)
    await event.edit("⏳ Mengirim broadcast...")

    result = await send_gcast(text)
    await event.edit(result)


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.gcast(\d+) (.+)'))
async def auto_gcast(event):
    global AUTO_GCAST, AUTO_MESSAGE, AUTO_DELAY

    AUTO_GCAST = True

    menit = int(event.pattern_match.group(1))
    AUTO_DELAY = menit * 60
    AUTO_MESSAGE = event.pattern_match.group(2)

    await event.edit(
        f"🔥 Auto GCast aktif\n\n⏱ Delay: {menit} menit\n📨 Pesan: {AUTO_MESSAGE}"
    )

    while AUTO_GCAST:
        result = await send_gcast(AUTO_MESSAGE)
        await event.respond(result)
        await asyncio.sleep(AUTO_DELAY)


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.stopgcast$'))
async def stop_gcast(event):
    global AUTO_GCAST

    AUTO_GCAST = False
    await event.edit("🛑 Auto GCast dihentikan.")


@client.on(events.NewMessage(outgoing=True, pattern=r'^\.bc-error$'))
async def bc_error(event):
    global FAILED_CHATS

    if not FAILED_CHATS:
        await event.edit("✅ Tidak ada error broadcast.")
        return

    text = "❌ LIST ERROR GCAST\n\n"

    for x in FAILED_CHATS[:30]:
        text += f"• {x}\n"

    await event.edit(text)


print("🔥 USERBOT GCAST ONLINE")
client.start()
client.run_until_disconnected()
```

## Cara update GitHub

```bash
git add .
git commit -m "upgrade gcast"
git push
```

## Command

```txt
.gcast halo
```

Broadcast sekali.

```txt
.gcast10 halo
```

Auto broadcast tiap 10 menit.

```txt
.gcast15 halo
```

Auto broadcast tiap 15 menit.

```txt
.stopgcast
```

Stop auto gcast.

```txt
.bc-error
```

Lihat grup yang gagal.
