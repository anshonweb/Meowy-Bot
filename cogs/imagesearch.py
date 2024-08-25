import discord
from discord import app_commands
from discord.ext import commands
import requests
import asyncio
from io import BytesIO
from saucenao_api import AIOSauceNao




class Trace(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='test1',
            callback=self.test1,
        )
        self.bot.tree.add_command(self.ctx_menu)
        

    @commands.Cog.listener()
    async def on_ready(self):
        print('TraceMoe cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('TraceMoe Cog loaded.')


    @app_commands.command(name='tracemoe', description='Anime Image Search (Upload image or URL)')
    async def tracemoe(self, interaction: discord.Interaction, file: discord.Attachment = None, url: str=None) ->None:
        await interaction.response.defer()  # Acknowledge the command
        if file:
            # Read the image data from the Discord attachment
            image_data = await file.read()
        elif url:
            # Download the image data from the provided URL
            try:
                image_response = requests.get(url)
                image_response.raise_for_status()  # Check if the download was successful
                image_data = image_response.content
            except requests.exceptions.RequestException as e:
                await interaction.followup.send(f"Failed to download image from URL: {e}")
                return
        else:
            await interaction.followup.send("Please provide either a file or a URL.")
            return

        # Send the POST request with the image data
        response = requests.post(
            "https://api.trace.moe/search",
            files={"image": ("image.jpg", image_data, "image/jpeg")}
        )

        # Check if the request was successful
        if response.status_code != 200:
            await interaction.followup.send("Failed to get a response from TraceMoe.")
            return

        # Parse the JSON response
        data = response.json()
        best_match = data['result'][0]

        embed = discord.Embed(title="Anime Match", color=0x00ff00)  # You can change the color as desired

        # Add fields to the embed
        embed.add_field(name="Anime ID", value=best_match['anilist'], inline=False)
        embed.add_field(name="Filename", value=best_match['filename'], inline=False)
        embed.add_field(name="Episode", value=best_match['episode'], inline=False)
        embed.add_field(name="From", value=f"{best_match['from']} seconds", inline=True)
        embed.add_field(name="To", value=f"{best_match['to']} seconds", inline=True)
        embed.add_field(name="Similarity", value=f"{best_match['similarity']:.2f}", inline=False)
        embed.add_field(name="Video URL", value=f"[Watch the scene]({best_match['video']})", inline=False)

        # Set the thumbnail or image (this will show the matching scene)
        embed.set_image(url=best_match['image'])


        await interaction.followup.send(embed=embed)

    

    @app_commands.command(name='saucenao', description='Reverse Searches images')
    async def SauceNao(self, interaction: discord.Interaction, file: discord.Attachment = None, url: str = None) ->None:
        async with AIOSauceNao('5fae52160f484ac5727ad10410490282c0c4338d') as aio:
            await interaction.response.defer()
            
            replied_message = await interaction.channel.fetch_message(interaction.message.reference.message_id)
            if file:
                image_data = await file.read()
                results = await aio.from_file(image_data)
            
            elif url:
                results = await aio.from_url(url)
            elif replied_message and replied_message.attachments:
                for attachment in replied_message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        results = await aio.from_url(attachment.url)
                        break
                else:
                    results = []
            else:
                await interaction.followup.send("Please provide either a file or a URL.")
                return
                 
            
            embed = discord.Embed(title='Best Match' , color=0x00ff00)
            embed.add_field(name='Title', value= results[0].title, inline=False)
            embed.add_field(name='URL' , value = results[0].urls, inline=False)
            embed.add_field(name= 'Similarity', value = results[0].similarity, inline=False)
            embed.set_image(url=results[0].thumbnail)
            await interaction.followup.send(embed=embed)

    
    @app_commands.guilds(1246531747106132060)
    async def test1(self, interaction: discord.Interaction, message: discord.Message):
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

            embed = discord.Embed(title='Best Match' , color=0x00ff00)
            embed.add_field(name='Title', value= results[0].title, inline=False)
            embed.add_field(name='URL' , value = results[0].urls, inline=False)
            embed.add_field(name= 'Similarity', value = results[0].similarity, inline=False)
            embed.set_image(url=results[0].thumbnail)
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Trace(bot) , guilds=[discord.Object(id='1246531747106132060')])
   