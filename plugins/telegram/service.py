import os
import threading
import asyncio
import traceback
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from langchain_core.tools import tool

LIMIT = 4000

class TelegramBot:
    def __init__(self, token):
        self.graph = None
        self.loop = None
        self.app = Application.builder().token(token).build()
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_message)
        )

    def graph_bind(self, graph):
        self.graph = graph

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.effective_message
        user = update.effective_user
        chat = update.effective_chat

        if not message or not user or user.is_bot:
            return

        username = user.username or user.first_name or str(user.id)
        chat_label = "Direct Message" if chat.type == "private" else str(chat.id)

        prefix = f"TELEGRAM\nFrom: {username}\nChannel: {chat.id}\nType: {chat_label}\n\n"
        config = {"configurable": {"thread_id": f"{username}-{chat.id}"}}

        async def send_long(content, limit=LIMIT):
            if not content:
                return
            for i in range(0, len(content), limit):
                await message.reply_text(content[i:i + limit])

        async def keep_typing():
            while True:
                await context.bot.send_chat_action(chat.id, ChatAction.TYPING)
                await asyncio.sleep(4)

        typing_task = asyncio.create_task(keep_typing())
        try:
            response = await asyncio.to_thread(
                self.graph.invoke,
                {"messages": [{"role": "user", "content": prefix + message.text}]},
                config,
            )

            msgs = response.get("messages", [])
            if msgs:
                last = msgs[-1]
                content = last.content if hasattr(last, "content") else str(last)
                if isinstance(content, list):
                    text = "".join(
                        b.get("text", "") if isinstance(b, dict) else str(b)
                        for b in content
                    )
                else:
                    text = str(content)
                await send_long(text)

        except Exception as e:
            traceback.print_exc()
            await message.reply_text(str(e)[:LIMIT])
        finally:
            typing_task.cancel()

    async def _main(self):
        self.loop = asyncio.get_running_loop()
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        await asyncio.Event().wait()


bot = TelegramBot(os.getenv("TELEGRAM_KEY"))

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot._main())

@tool
def tool_call(channel_id: str, message: str):
    '''
        DILARANG: mengirim pesan ke telegram jika pesan sebelumnya memiliki prefix TELEGRAM, kecuali user secara eksplisit meminta untuk mengirim ke chat telegram tertentu

        Kirim pesan ke telegram, entah itu notifikasi, pengingat ataupun cross access (user tidak mengirimkan pesan dari telegram namun ingin kirim ke telegram)
        arguments:
            channel_id: id chat (bisa negatif untuk grup), bisa didapatkan dari riwayat jangka panjang
            message: pesan yang akan dikirimkan

        Penting, cari terlebih dahulu chat id dari tool manapun yang mendukung akses ke memori jangka panjang,
        lakukan konfirmasi terlebih dahulu sebelum mengirimkan ke tool ini jika channel_id ditemukan,
        jika channel id tidak ada, maka jangan lakukan.
    '''
    from telegram.error import BadRequest, Forbidden

    async def send():
        print(f"[DEBUG] channel_id diterima: {channel_id}")
        try:
            chat_id = int(channel_id)
            for i in range(0, len(message), LIMIT):
                await bot.app.bot.send_message(chat_id, message[i:i + LIMIT])
            return "Pesan sudah terkirim"
        except ValueError:
            return "channel_id harus berupa angka"
        except BadRequest as e:
            return f"Chat tidak ditemukan / request tidak valid: {e}"
        except Forbidden:
            return "Bot tidak punya izin (diblokir / belum di-start / bukan anggota grup)"
        except Exception as e:
            traceback.print_exc()
            return f"Gagal mengirim: {e}"

    future = asyncio.run_coroutine_threadsafe(send(), bot.loop)
    return future.result()

threading.Thread(target=run, daemon=True).start()