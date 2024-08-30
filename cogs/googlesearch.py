import discord
from discord.ext import commands
import asyncio
from discord.ext.paginators.button_paginator import ButtonPaginator
import requests
from google_images_search import GoogleImagesSearch

gis = GoogleImagesSearch('AIzaSyBRpywZW5wv_FOY7sEpaAZHrgKTgpz_v4c', '35913d4c2284847a4')

class googlesearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog loaded")

    @commands.command(name='img')
    async def img(self, ctx, *, srh: str) ->None:
        await ctx.send(f'Searching for images related to: {srh}')

        # Define the search parameters
        search_params = {
            'q': srh,
            'num': 10,  # Number of images to return
            'safe': 'off',  # Filter safe search
            'fileType': 'jpg|png|gif'  # Limit file types
        }

        # Perform the search
        gis.search(search_params=search_params)

        # Send the first few image URLs in the chat
        if gis.results():
            embeds = []
            results = gis.results()[:10]  # Retrieve only the first 10 images
            for image in results:  # Send the first 3 images
                embed=discord.Embed(title=f'Results ',  description=f'{image.referrer_url}')
                embed.set_image(url=image.url)
                embeds.append(embed)
                

            paginator = ButtonPaginator(embeds, author_id=ctx.author.id)
            await paginator.send(ctx)

        else:
            await ctx.send('No images found.')


async def setup(bot):
    await bot.add_cog(googlesearch(bot) , guilds=[discord.Object(id='1246531747106132060')])