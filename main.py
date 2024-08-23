import discord
import os
from discord.ext import commands
from dotenv import  load_dotenv
import logging
import logging.handlers


intents=discord.Intents.default()
intents.message_content=True
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv('.env')

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix='.',
            intents=intents,
            help_command=None,
        )

    
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        channel = bot.get_channel(1246534324925501521)
        await channel.send(f"Logged in as {self.user}")

        
    async def on_message(self, message):
        print(f'message sent by {message.author} contains {message.content}')

    
    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for filename in os.listdir('./cogs'):
           if filename.endswith('.py'):
             await bot.load_extension(f'cogs.{filename[:-3]}')

                

    async def setup_hook(self) -> None:
        """
        This will just be executed when the bot starts the first time.
        """
        await self.load_cogs()
        
        





bot = DiscordBot()
bot.run(os.getenv("TOKEN") ,  log_handler=None)