import discord
import uvicorn
import asyncio
from discord.ext import commands
from fastapi import FastAPI, Request

# TODO: Get secrets from GitHub repository, CHANNEL_ID and THREAD_ID from Github Action inputs
# Temporary store the secrets here
TOKEN = "MTM1MzMxODI4NDEwNzMyMTM4NA.GK83U7.ykLqMbGFB-fKyuxOeltCPITZL9JUVfWlrZu9wQ"
CHANNEL_ID = 1352904828556283955
THREAD_ID = 1353306988607438931

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

app = FastAPI()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

async def send_discord_notification(status: str, message: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ Error: Channel not found!")
        return

    thread = channel.get_thread(THREAD_ID)
    if thread:
        embed = discord.Embed(
            title="🚀 Deployment Status",
            description=message,
            color=discord.Color.green() if status == "success" else discord.Color.red()
        )
        await thread.send(embed=embed)
    else:
        print("❌ Error: Thread not found!")

@app.post("/send")
async def receive_github_notification(request: Request):
    data = await request.json()
    status = data.get("status", "unknown")
    message = data.get("message", "No message provided.")

    # Schedule the task inside the bot event loop
    bot.loop.create_task(send_discord_notification(status, message))

    return {"status": "ok", "message": "Notification sent to Discord"}

# Start both Discord bot and FastAPI
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot.start(TOKEN))

if __name__ == "__main__":
    import threading
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)