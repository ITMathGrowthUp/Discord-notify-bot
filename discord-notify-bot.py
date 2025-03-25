import discord
import uvicorn
import asyncio
import os
from discord.ext import commands
from fastapi import FastAPI, Request

# Fetch secrets from environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
THREAD_ID = int(os.getenv("DISCORD_THREAD_ID", "0"))

# Create bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Create FastAPI app
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
    asyncio.create_task(send_discord_notification(status, message))

    return {"status": "ok", "message": "Notification sent to Discord"}


# Run both FastAPI and the bot in an async loop
async def main():
    bot_task = asyncio.create_task(bot.start(TOKEN))
    server_task = asyncio.create_task(uvicorn.run(app, host="0.0.0.0", port=8000))

    await asyncio.gather(bot_task, server_task)


if __name__ == "__main__":
    asyncio.run(main())
