import discord
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime

import os

load_dotenv()  # Load environment variables from .env file

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        # Try getting the channel from cache
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            # Fetch from API if not found in cache
            channel = await bot.fetch_channel(CHANNEL_ID)

        if channel:
            await channel.send("HEHEHEHEHHE")
            print(f"Message sent to {channel.name}")
        else:
            print(f"Could not find channel: {CHANNEL_ID}")

    except Exception as e:
        print(f"Error finding/sending message to channel: {e}")

async def send_build_notification(status, duration):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="📢 GitHub Build Notification",
            color=discord.Color.green() if status == "Success" else discord.Color.red(),
        )
        embed.add_field(name="Status", value=f"🛠 {status}", inline=True)
        embed.add_field(name="Build Time", value=f"⏳ {duration} seconds", inline=True)
        embed.timestamp = datetime.utcnow()
        await channel.send(embed=embed)

bot.run(TOKEN)
