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
    async def mute(self, ctx, member: discord.Member, seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0, reason: str = None) ->None:
        
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
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member) ->None:
        await member.timeout(None, reason=None)
        await ctx.send(f'Unmuted {member.mention} .', ephemeral=False)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member:discord.Member, role: discord.Role, reason: str = None) ->None:
        await member.add_roles(role, reason=None , atomic=True)
        await ctx.send(f'{role.name} added for {member.mention}')
        
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx , member:discord.Member, role: discord.Role , reason: str = None)->None:
        await member.remove_roles(role, reason=None, atomic=True)
        await ctx.send(f'{role.name} removed for {member.mention}')
    

async def setup(bot):
    await bot.add_cog(moderationtext(bot))
