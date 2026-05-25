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

# =========================
# MULTI SESSION
# =========================

SESSIONS = [
    os.getenv("SESSION1"),
    os.getenv("SESSION2"),
    os.getenv("SESSION3"),
    os.getenv("SESSION4"),
    os.getenv("SESSION5")
]

clients = []

for session in SESSIONS:

    if session:

        client = TelegramClient(
            StringSession(session),
            API_ID,
            API_HASH
        )

        clients.append(client)

FAILED_CHATS = {}
LAST_MESSAGES = {}
AUTO_GCAST = {}


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

async def send_gcast(client, message, owner_name):

    global FAILED_CHATS
    global LAST_MESSAGES

    success = 0
    failed = 0

    FAILED_CHATS[client] = []

    tid = random_id()

    async for dialog in client.iter_dialogs():

        try:

            if dialog.is_group:

                key = f"{client}_{dialog.id}"

                # =========================
                # HAPUS PESAN LAMA
                # =========================

                if key in LAST_MESSAGES:

                    try:

                        await client.delete_messages(
                            dialog.id,
                            LAST_MESSAGES[key]
                        )

                    except:
                        pass

                # =========================
                # KIRIM PESAN BARU
                # =========================

                msg = await client.send_message(
                    dialog.id,
                    message
                )

                LAST_MESSAGES[key] = msg.id

                success += 1

                await asyncio.sleep(3)

        except Exception as e:

            failed += 1

            FAILED_CHATS[client].append(
                f"{dialog.name} -> {str(e)}"
            )

    text = f"""
<blockquote expandable>
⚠️ <b>GCAST SUKSES</b>

✅ Success: {success}
❌ Failed: {failed}
⚙️ Task ID: {tid}
👤 Owner: {owner_name}

Type <code>.bc-error</code>
to view failed broadcast.
</blockquote>
"""

    return text


# =========================
# PASANG HANDLER KE SEMUA AKUN
# =========================

for client in clients:

    # =========================
    # GCAST SEKALI
    # =========================

    @client.on(events.NewMessage(
        from_users='me',
        pattern=r'^\.gcast\s+(.+)'
    ))
    async def gcast(event, client=client):

        text = event.pattern_match.group(1)

        await event.edit(
            "⏳ Mengirim broadcast..."
        )

        me = await client.get_me()

        result = await send_gcast(
            client,
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
    async def auto_gcast(event, client=client):

        global AUTO_GCAST

        menit = int(
            event.pattern_match.group(1)
        )

        text = event.pattern_match.group(2)

        AUTO_GCAST[client] = True

        await event.edit(
            f"🔥 Auto Gcast aktif\n"
            f"⏱ Interval: {menit} menit"
        )

        while AUTO_GCAST.get(client):

            try:

                me = await client.get_me()

                result = await send_gcast(
                    client,
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


    # =========================
    # STOP GCAST
    # =========================

    @client.on(events.NewMessage(
        from_users='me',
        pattern=r'^\.stopgcast$'
    ))
    async def stop_gcast(event, client=client):

        AUTO_GCAST[client] = False

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
    async def bc_error(event, client=client):

        if not FAILED_CHATS.get(client):

            return await event.edit(
                "✅ Tidak ada chat gagal."
            )

        text = "❌ CHAT GAGAL:\n\n"

        for x in FAILED_CHATS[client]:

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
🔥 MULTI USERBOT GCAST

.gcast teks
= gcast sekali

.autogcast10 teks
= auto gcast tiap 10 menit

.autogcast15 teks
= auto gcast tiap 15 menit

.stopgcast
= stop auto gcast

.bc-error
= lihat grup gagal

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
    async def ping(event, client=client):

        me = await client.get_me()

        await event.edit(
            f"🏓 Pong!\n"
            f"👤 {me.first_name}"
        )


# =========================
# START CLIENT
# =========================

async def start_client(client):

    while True:

        try:

            await client.start()

            me = await client.get_me()

            print(
                f"🔥 Login: {me.first_name}"
            )

            await client.run_until_disconnected()

        except Exception as e:

            print(
                f"❌ {e}"
            )

            print(
                "🔄 Reconnecting 5 detik..."
            )

            await asyncio.sleep(5)


# =========================
# START BOT
# =========================

async def main():

    tasks = []

    for client in clients:

        tasks.append(
            asyncio.create_task(
                start_client(client)
            )
        )

    print("✅ Semua akun aktif")

    await asyncio.gather(*tasks)

asyncio.run(main())
