import os
import discord
import asyncio
import logging
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger()

TOKEN = '' # Add bot token
FOLDER_TO_MONITOR = '' # Import path to monitor
CHANNEL_ID = ...
# Repalce ... with Channel ID


# Initialize the bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Watchdog event handler
class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def on_created(self, event):
        try:
            if event.is_directory:
                return
            if event.src_path.endswith('.mp4') or event.src_path.endswith('.MP4'):
                self.loop.create_task(send_video(event.src_path))
        except Exception as e:
            logger.error(f"Error in event handler: {e}")

# Function to send video to Discord channel
async def send_video(video_path):
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(file=discord.File(video_path))
            logger.info(f"Sent {video_path} to Discord channel.")
        else:
            logger.error("Channel not found.")
    except Exception as e:
        logger.error(f"Error sending video to Discord: {e}")

# Bot event
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=FOLDER_TO_MONITOR, recursive=False)
    observer.start()
    logger.info(f'Watching folder: {FOLDER_TO_MONITOR}')

bot.run(TOKEN)
