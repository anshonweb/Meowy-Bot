import discord
from utils.paginator import ButtonPaginator
from discord.ext import commands
from discord import app_commands
from utils.paginator import ButtonPaginator
from saucenao_api import AIOSauceNao
import requests
import asyncio
from io import BytesIO

class Select(discord.ui.Select):
    def __init__(self, image_url):
        self.image_url = image_url
        options=[
            discord.SelectOption(label="TraceMoe",emoji="👌",description="TraceMoe can be used to search Anime videos/images from episodes."),
            discord.SelectOption(label="SauceNao",emoji="✨",description="SauceNao can be used to search for artworks/anime"),
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'{self.image_url}')

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(Select())


class AnimeSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    
    @commands.command(name='menu')
    async def menu(self, ctx):
        # Check if the user replied to a message
        if ctx.message.reference is None:
            await ctx.send("You need to reply to a message that contains an image.")
            return

        # Fetch the replied message
        replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        # Check if the replied message has attachments
        image_url = None  # Initialize the image_url variable

        if replied_message.attachments:
            attachment = replied_message.attachments[0]

            if attachment.content_type and attachment.content_type.startswith("image/"):
                image_url = attachment.url
                await ctx.send(f"Here is the image from the replied message: {image_url}")
                view = SelectView(image_url=image_url)
                await ctx.send("Menus!", view=view)

            else:
                await ctx.send("The attachment in the replied message is not an image.")

        elif replied_message.embeds:
            embed = replied_message.embeds[0]  # Assuming you want the first embed

            if embed.image.url:
                image_url = embed.image.url
                await ctx.send(f"Here is the image from the embed: {image_url}")
            elif embed.thumbnail.url:
                image_url = embed.thumbnail.url
                await ctx.send(f"Here is the thumbnail image from the embed: {image_url}")
            else:
                await ctx.send("The embed does not contain an image.")

        else:
            await ctx.send("The replied message does not contain any attachments.")

        



        











async def setup(bot):
    await bot.add_cog(AnimeSearch(bot) , guilds=[discord.Object(id='1246531747106132060')])
