import discord
from discord import app_commands
from discord.ext import commands
import requests
import asyncio
from io import BytesIO
from saucenao_api import AIOSauceNao
from discord.ext.paginators.button_paginator import ButtonPaginator




class Trace(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ctx_menu_one = app_commands.ContextMenu(
            name='saucenao',
            callback=self.saucenao,
        )

        self.ctx_menu_two = app_commands.ContextMenu(
            name='trace', 
            callback=self.trace,
        )
        self.bot.tree.add_command(self.ctx_menu_one)
        self.bot.tree.add_command(self.ctx_menu_two)
        

    @commands.Cog.listener()
    async def on_ready(self):
        print('TraceMoe cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('TraceMoe Cog loaded.')


    @app_commands.command(name='tracemoe', description='Anime Image Search (Upload image or URL)')
    async def tracemoe(self, interaction: discord.Interaction, file: discord.Attachment = None, url: str = None) -> None:
        await interaction.response.defer()

        # Handle image input
        if file:
            image_data = await file.read()
        elif url:
            try:
                image_response = requests.get(url)
                image_response.raise_for_status()
                image_data = image_response.content
            except requests.exceptions.RequestException as e:
                await interaction.followup.send(f"Failed to download image from URL: {e}")
                return
        else:
            await interaction.followup.send("Please provide either a file or a URL.")
            return

        # Send POST request to TraceMoe API
        response = requests.post(
            "https://api.trace.moe/search",
            files={"image": ("image.jpg", image_data, "image/jpeg")}
        )

        if response.status_code != 200:
            await interaction.followup.send("Failed to get a response from TraceMoe.")
            return

        data = response.json()['result']

        if len(data) > 1:
            embeds = []
            for best_match in data[:10]:
                embed = discord.Embed(title="Anime Match", color=0x00ff00)
                embed.add_field(name="Anime ID", value=best_match['anilist'], inline=False)
                embed.add_field(name="Filename", value=best_match['filename'], inline=False)
                embed.add_field(name="Episode", value=best_match['episode'], inline=False)
                embed.add_field(name="From", value=f"{best_match['from']} seconds", inline=True)
                embed.add_field(name="To", value=f"{best_match['to']} seconds", inline=True)
                embed.add_field(name="Similarity", value=f"{best_match['similarity']:.2f}", inline=False)
                embed.add_field(name="Video URL", value=f"[Watch the scene]({best_match['video']})", inline=False)
                embed.set_image(url=best_match['image'])
                embeds.append(embed)

            # Initialize the paginator with embeds
            paginator = ButtonPaginator(embeds, author_id=interaction.user.id)
            await paginator.send(interaction)
        else:
            await interaction.followup.send("Not enough results returned by the API.")

    

    @app_commands.command(name='saucenao', description='Reverse Searches images')
    async def SauceNao(self, interaction: discord.Interaction, file: discord.Attachment = None, url: str = None) ->None:
        async with AIOSauceNao('5fae52160f484ac5727ad10410490282c0c4338d') as aio:
            await interaction.response.defer()
            
            
            if file:
                image_data = await file.read()
                results = await aio.from_file(image_data)
            
            elif url:
                results = await aio.from_url(url)
            
            else:
                await interaction.followup.send("Please provide either a file or a URL.")
                return
            
            if len(results)>1:
                embeds = []
                for best_match in results[:10]:

                        embed = discord.Embed(title='Best Match' , color=0x00ff00)
                        embed.add_field(name='Title', value= best_match.title, inline=False)
                        embed.add_field(name='URL' , value = best_match.urls, inline=False)
                        embed.add_field(name= 'Similarity', value = best_match.similarity, inline=False)
                        embed.set_image(url=best_match.thumbnail)
                        
                        embeds.append(embed)

                paginator = ButtonPaginator(embeds, author_id=interaction.user.id)
                await paginator.send(interaction)

            else:
                await interaction.followup.send('No results found.')

    
    @app_commands.guilds(1246531747106132060)
    async def saucenao(self, interaction: discord.Interaction, message: discord.Message):
        async with AIOSauceNao('5fae52160f484ac5727ad10410490282c0c4338d') as aio:
            await interaction.response.defer(thinking=True)
            print("Context menu invoked.")

            if message.attachments:
                image_found = False
                for attachment in message.attachments:
                    if attachment.content_type.startswith("image/"):
                        image_found = True
                        image_data = await attachment.read()
                        results = await aio.from_file(image_data)
                        break

                if not image_found:
                    await interaction.followup.send("The selected message doesn't contain any images.")
            else:
                await interaction.followup.send("The selected message doesn't contain any images.")
            
            if len(results)>1:
                embeds = []
                for best_match in results[:10]:

                        embed = discord.Embed(title='Best Match' , color=0x00ff00)
                        embed.add_field(name='Title', value= best_match.title, inline=False)
                        embed.add_field(name='URL' , value = best_match.urls, inline=False)
                        embed.add_field(name= 'Similarity', value = best_match.similarity, inline=False)
                        embed.set_image(url=best_match.thumbnail)
                        
                        embeds.append(embed)

                paginator = ButtonPaginator(embeds, author_id=interaction.user.id)
                await paginator.send(interaction)

            else:
                await interaction.followup.send('No results found.')
    
    @app_commands.guilds(1246531747106132060)
    async def trace(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer()  # Acknowledge the command

        if message.attachments:
                image_found = False
                for attachment in message.attachments:
                    if attachment.content_type.startswith("image/"):
                        image_found = True
                        image_data = await attachment.read()
                        

                if not image_found:
                    await interaction.followup.send("The selected message doesn't contain any images.")
        else:
            await interaction.followup.send("The selected message doesn't contain any images.")
        

        

        # Send the POST request with the image data
        response = requests.post(
            "https://api.trace.moe/search",
            files={"image": ("image.jpg", image_data, "image/jpeg")}
        )

        if response.status_code != 200:
            await interaction.followup.send("Failed to get a response from TraceMoe.")
            return

        data = response.json()['result']

        if len(data) > 1:
            embeds = []
            for best_match in data[:10]:
                embed = discord.Embed(title="Anime Match", color=0x00ff00)
                embed.add_field(name="Anime ID", value=best_match['anilist'], inline=False)
                embed.add_field(name="Filename", value=best_match['filename'], inline=False)
                embed.add_field(name="Episode", value=best_match['episode'], inline=False)
                embed.add_field(name="From", value=f"{best_match['from']} seconds", inline=True)
                embed.add_field(name="To", value=f"{best_match['to']} seconds", inline=True)
                embed.add_field(name="Similarity", value=f"{best_match['similarity']:.2f}", inline=False)
                embed.add_field(name="Video URL", value=f"[Watch the scene]({best_match['video']})", inline=False)
                embed.set_image(url=best_match['image'])
                embeds.append(embed)

            # Initialize the paginator with embeds
            paginator = ButtonPaginator(embeds, author_id=interaction.user.id)
            await paginator.send(interaction)
        else:
            await interaction.followup.send("Not enough results returned by the API.")



async def setup(bot):
    await bot.add_cog(Trace(bot) , guilds=[discord.Object(id='1246531747106132060') , discord.Object(id='820326376673771540')])
