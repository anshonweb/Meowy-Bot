import discord
from discord.ext import commands
import asyncio
import datetime
class moderationtext(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('ModerationText cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('ModerationText cog loaded.')


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self,ctx, num: int) ->None:
        
        deleted = await ctx.channel.purge(limit=num+1)
        embed=discord.Embed(title='Purge' , description= f'{num} messages were purged by {ctx.author}')
        await ctx.send(embed=embed)
    

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def timeout(self, ctx, member: discord.Member, seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0, reason: str = None) ->None:
        
        duration = datetime.timedelta(seconds=seconds, minutes=minutes, hours= hours, days=days)
        if member.top_role > ctx.guild.me.top_role:
            await ctx.send(f"Cannot mute {member}. They have a higher role than me.", ephemeral=False )     
       # elif duration=:
          #  await member.timeout(1, reason=reason)
          #  await interaction.response.send_message("Member has been timedout for 1 second")
        else:
            
            await member.timeout(duration, reason=reason)
            await ctx.send(f'{member.mention} was timed out until for {duration}', ephemeral=False)
    
    
    @commands.command()
    async def avatar(self,ctx, member: discord.Member) ->None:
        avatar = member.avatar.url
        embed= discord.Embed(title=f'{member.name}')
        embed.set_image(url= avatar)

        await ctx.send(embed=embed)
    

async def setup(bot):
    await bot.add_cog(moderationtext(bot))