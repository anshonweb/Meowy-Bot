import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Tools cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('Tools cog loaded.')


    @commands.command()
    async def say(self, ctx, *, message: str) ->None:
        await ctx.send(message)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=f"User Info - {member}", color=0x00ff00, timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar.url)  # Avatar of the member
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Display Name", value=member.display_name, inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%d %B %Y, %H:%M:%S"), inline=False)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%d %B %Y, %H:%M:%S"), inline=False)

        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        print('hello')
        await ctx.send(embed=embed)
    

    @app_commands.command(name='serverinfo', description='Fetches information of the current server.')
    async def info(self,interaction: discord.Interaction) ->None:
        await interaction.response.defer(ephemeral=False)
        embed = discord.Embed(title=f"{interaction.guild.name} Info")
        embed.add_field(name='Server ID', value=f"{interaction.guild.id}", inline=True)
        embed.add_field(name='Created On', value=interaction.guild.created_at.strftime("%b %d %Y"), inline=True)
        embed.add_field(name='Owner', value=f"<@{interaction.guild.owner_id}>", inline=True)
        embed.add_field(name='Members', value=f'{interaction.guild.member_count} Members', inline=True)
        embed.add_field(name='Channels', value=f'{len(interaction.guild.text_channels)} Text | {len(interaction.guild.voice_channels)} Voice', inline=True)
        #embed.add_field(name='Region', value=f'{ctx.guild.region}', inline=True)
        embed.set_thumbnail(url=interaction.guild.icon)

        embed.set_author(name=f'{interaction.user.name}' ,icon_url=interaction.user.avatar.url)

        await interaction.followup.send(embed=embed)
    @commands.command()
    async def serverinfo(self, ctx) -> None:
        embed = discord.Embed(title=f"{ctx.guild.name} Info")
        embed.add_field(name='Server ID', value=f"{ctx.guild.id}", inline=True)
        embed.add_field(name='Created On', value=ctx.guild.created_at.strftime("%b %d %Y"), inline=True)
        embed.add_field(name='Owner', value=f"<@{ctx.guild.owner_id}>", inline=True)
        embed.add_field(name='Members', value=f'{ctx.guild.member_count} Members', inline=True)
        embed.add_field(name='Channels', value=f'{len(ctx.guild.text_channels)} Text | {len(ctx.guild.voice_channels)} Voice', inline=True)
        #embed.add_field(name='Region', value=f'{ctx.guild.region}', inline=True)
        embed.set_thumbnail(url=ctx.guild.icon) 
          
        embed.set_author(name=f'{ctx.author.name}' ,icon_url=ctx.message.author.avatar.url)

        await ctx.send(embed=embed)

    @app_commands.command(name='avatar', description='Views avatar of the mentioned user.')
    async def av(self, interaction: discord.Interaction, member: discord.Member) ->None:
        await interaction.response.defer(ephemeral=False)
        avatar = member.avatar.url
        embed= discord.Embed(title=f'{member.name}')
        embed.set_image(url= avatar)

        await interaction.followup.send(embed=embed, ephemeral=False)

    @commands.command()
    async def avatar(self,ctx, member: discord.Member = None) ->None:
        if member is None:
            member = ctx.author
        avatar = member.avatar.url
        embed= discord.Embed(title=f'{member.name}')
        embed.set_image(url= avatar)
        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self,ctx, num: int = None) ->None:
        if num is None:
            await ctx.send("Please enter the number of messages you want to get purged.")
        deleted = await ctx.channel.purge(limit=num+1)
        embed=discord.Embed(title='Purge' , description= f'{len(deleted)} messages were purged by {ctx.author}')
        await ctx.send(embed=embed)


    @app_commands.command(name='purge', description='Purges Messages')
    async def delete(self, interaction: discord.Interaction, number: int) ->None:
        await interaction.response.defer(ephemeral=False)

        response_message = await interaction.original_response()

        # Purge the specified number of messages, excluding the bot's confirmation message
        def check(message):
            return message.id != response_message.id

        deleted = await interaction.channel.purge(limit=number, check=check)
        if len(deleted) == 0:
            embed=discord.Embed(title='Purge Complete!' , description='No messages were purged.')
            await interaction.followup.send(embed=embed, ephemeral=False)

        else:
            embed=discord.Embed(title='Purge Complete!', description= f'{len(deleted)} Messages were purged.')
            await interaction.followup.send(embed=embed, ephemeral=False)


async def setup(bot):
    await bot.add_cog(Tools(bot) , guilds=[discord.Object(id='1246531747106132060') , discord.Object(id='820326376673771540')])

     	
