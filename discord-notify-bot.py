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
    message += f"\n\nTriggered by: {data.get('triggered_b', 'unknown')}"

    # Schedule the task inside the bot event loop
    asyncio.create_task(send_discord_notification(status, message))

    return {"status": "ok", "message": "Notification sent to Discord"}


# Function to run both bot and FastAPI together
async def main():
    loop = asyncio.get_running_loop()

    # Run the bot and FastAPI server as tasks
    loop.create_task(bot.start(TOKEN))
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())  # This will now work correctly!
