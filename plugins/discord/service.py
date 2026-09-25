import os
import threading
import discord
import asyncio
import traceback
from langchain_core.tools import tool

class DiscordBot(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.graph = None
        self.loop = None

    async def setup_hook(self):
        self.loop = asyncio.get_running_loop()

    def graph_bind(self, graph):
        self.graph = graph

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        if message.author.bot:
            return

        prefix = f"DISCORD\nFrom: {message.author.name}\nChannel: {message.channel.id if message.channel else "Direct Message"}\n\n"
        config = {
            "configurable": {
                "thread_id": f"{message.author.name}-{message.channel.id if message.channel else "Direct Message"}"
            }
        }

        async def send_long(message, content, limit=2000):
            if not content:
                return
            chunks = [content[i:i+limit] for i in range(0, len(content), limit)]
            result = None
            for chunk in chunks:
                result = await message.reply(chunk)
            return result

        async def send():
            try:
                response = await asyncio.to_thread(
                    self.graph.invoke,
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": prefix + message.content
                            }
                        ]
                    },
                    config
                )
        
                msg = response.get("messages", [])
                if msg:
                    last = msg[-1]
                    content = last.content if hasattr(last, "content") else str(last)
                    if isinstance(content, list):
                        text = "".join(
                            block.get("text", "") if isinstance(block, dict) else str(block)
                            for block in content
                        )
                    else:
                        text = str(content)

                    return await send_long(message, text)

            except Exception as e:
                print(f"Error: {e}")
                return await message.reply("Unexpected Error")

        if message.channel:
            async with message.channel.typing():
                return await send()

        return await send()

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.messages = True
intents.message_content = True

bot = DiscordBot(intents=intents)

def run():
    bot.run(os.getenv("DISCORD_KEY"))

@tool
def tool_call(channel_id: str, message: str):
    '''
        Kirim pesan ke discord, entah itu notifikasi, pengingat ataupun cross access (user tidak mengirimkan pesan dari discord namun ingin kirim ke discord)
        arguments:
            channel_id: id channel, bisa didapatkan dari riwayat jangka panjang
            message: pesan yang akan dikirimkan

        Penting, cari terlebih dahulu channel id dari tool manapun yang mendukung akses ke memori jangka panjang,
        lakukan konfirmasi terlebih dahulu sebelum mengirimkan ke tool ini jika channel_id ditemukan,
        jika channel id tidak ada, maka jangan lakukan
    '''
    async def send():
        channel = bot.get_channel(channel_id)
        print(f"[DEBUG] channel_id diterima: {channel_id}")
        try:
            if channel is None:
                channel = await bot.fetch_channel(channel_id)
            await channel.send(message)
            return "Pesan sudah terkirim"
        except discord.NotFound:
            return "Channel tidak ditemukan (ID salah atau channel sudah dihapus)"
        except discord.Forbidden:
            return "Bot tidak punya izin akses ke channel ini"
        except Exception as e:
            traceback.print_exc()
            return f"Gagal mengirim: {e}"

    future = asyncio.run_coroutine_threadsafe(
        send(),
        bot.loop
    )

    return future.result()

threading.Thread(
    target=run,
    daemon=True
).start()