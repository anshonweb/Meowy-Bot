import discord
from  discord.ext import commands
from discord import app_commands
from utils.Anilist.anilist import anilist
from utils.Anilist.anilist_auth import anilist_auth
from utils.paginator import ButtonPaginator


class Anilist(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_ready(self):
        print('Anilist cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('Anilist Cog loaded.')


    @app_commands.command(name='anime', description='gives anime details')
    async def id(self, interaction: discord.Interaction, anime_id: int):
        await interaction.response.defer()
        try:
            anime_details = anilist.fetch_anime_details(anime_id)
            title = anime_details['title']['romaji']
            description = anime_details['description'][:300] + '...' if anime_details['description'] else 'No description available.'

            embed = discord.Embed(title=title, description=description)
            embed.add_field(name='Episodes', value=anime_details['episodes'])
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}")

    @commands.command(name='anime')
    async def fetch_or_search_anime(self, ctx, *, query: str):
        try:
            # Check if the input is numeric (ID) or a name
            if query.isdigit():
                anime_id = int(query)
                anime_info = anilist.fetch_anime_info(anime_id)

                title = anime_info['title']['romaji']
                description = anime_info['description'][:300] + '...' if anime_info['description'] else 'No description available.'
                score = anime_info['averageScore']
                episodes = anime_info['episodes'] if anime_info['episodes'] else 'N/A'
                cover_image = anime_info['coverImage']['large']

                embed = discord.Embed(title=title, description=description)
                embed.add_field(name='Score', value=score)
                embed.add_field(name='Episodes', value=episodes)
                embed.set_thumbnail(url=cover_image)  # Set the cover image
                await ctx.send(embed=embed)

            else:
                anime_list = anilist.search_anime(query)
                if not anime_list:
                    await ctx.send(f"No results found for '{query}'")
                    return

                embeds = []
                for anime in anime_list:
                    title = anime['title']['romaji']
                    description = anime['description'][:300] + '...' if anime['description'] else 'No description available.'
                    score = anime['averageScore']
                    episodes = anime['episodes'] if anime['episodes'] else 'N/A'
                    cover_image = anime['coverImage']['large']

                    embed = discord.Embed(title=title, description=description)
                    embed.add_field(name='Score', value=score)
                    embed.add_field(name='Episodes', value=episodes)
                    embed.set_image(url=cover_image)
                    embeds.append(embed)
                
                paginator = ButtonPaginator(embeds)
                await paginator.start(ctx)

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Anilist(bot), guilds=[discord.Object(id='1246531747106132060')])