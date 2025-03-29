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


async def send_discord_notification(status: str, message: str, repository: str, triggered_by: str, commit_hash: str, change_log: str, deploy_time: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ Error: Channel not found!")
        return

    thread = channel.get_thread(THREAD_ID)
    if thread:
        embed = discord.Embed(
            title="🚀 Deployment Notification",
            description=message,
            color=discord.Color.green() if status == "success" else discord.Color.red()
        )

        embed.add_field(name="📌 Repository", value=f"[View on GitHub]({repository})", inline=False)
        embed.add_field(name="👤 Triggered By", value=triggered_by, inline=True)
        embed.add_field(name="🔗 Commit Hash", value=f"`{commit_hash}`", inline=True)
        embed.add_field(name="📝 Change Log", value=change_log, inline=False)
        embed.add_field(name="⏰ Deployment Time", value=deploy_time, inline=False)

        embed.set_footer(text="Automated Deployment Notification")

        await thread.send(embed=embed)
    else:
        print("❌ Error: Thread not found!")


@app.post("/send")
async def receive_github_notification(request: Request):
    data = await request.json()
    status = data.get("status", "unknown")
    message = data.get("message", "No message provided.")
    repository = data.get("repository", "N/A")
    triggered_by = data.get("triggered_by", "unknown")
    commit_hash = data.get("commit_hash", "N/A")
    change_log = data.get("change_log", "N/A")
    deploy_time = data.get("time", "N/A")

    # Schedule the task inside the bot event loop
    asyncio.create_task(send_discord_notification(status, message, repository, triggered_by, commit_hash, change_log, deploy_time))

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
    asyncio.run(main())