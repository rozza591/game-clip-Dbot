import asyncio
import logging
import discord
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger()

TOKEN = ''
FOLDER_TO_MONITOR = ''
CHANNEL_ID = 
MAX_FILE_SIZE_MB = 25  # Maximum file size in megabytes
WAIT_DURATION_SECONDS = 5  # Time to wait for the file size to stop growing

# Initialize the bot with updated intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Watchdog event handler
class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.pending_files = {}

    async def monitor_file_growth(self, file_path):
        print(f"Detected new file: {file_path}")
        while file_path in self.pending_files:
            current_size = os.path.getsize(file_path)
            if current_size != self.pending_files[file_path]['size']:
                self.pending_files[file_path]['size'] = current_size
                self.pending_files[file_path]['last_update'] = time.time()
            else:
                time_elapsed = time.time() - self.pending_files[file_path]['last_update']
                if time_elapsed >= WAIT_DURATION_SECONDS:
                    await send_video(file_path)
                    del self.pending_files[file_path]
                    break
            await asyncio.sleep(0.5)

    def on_created(self, event):
        try:
            if event.is_directory:
                return
            if event.src_path.endswith('.mp4') or event.src_path.endswith('.MP4'):
                self.pending_files[event.src_path] = {'size': 0, 'last_update': time.time()}
                self.loop.create_task(self.monitor_file_growth(event.src_path))
        except Exception as e:
            logger.error(f"Error in event handler: {e}")

# Function to send video to Discord channel
async def send_video(video_path):
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            file_size_bytes = os.path.getsize(video_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            if file_size_mb <= MAX_FILE_SIZE_MB:
                await channel.send(file=discord.File(video_path))
                logger.info(f"Sent {video_path} to Discord channel.")
            else:
                await channel.send(f"The latest Epic Clip is too epic and unfortunately doesn't fit on the server :( \n Please make sure your clips are under 25MB.")
                logger.warning(f"The latest Epic Clip is too epic and unfortunately doesn't fit on the server :( \n Please make sure your clips are under 25MB.")
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
    observer.schedule(event_handler, path=FOLDER_TO_MONITOR, recursive=True)
    observer.start()
    logger.info(f'Watching folder: {FOLDER_TO_MONITOR}')

bot.run(TOKEN)
