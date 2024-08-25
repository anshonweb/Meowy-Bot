import discord 
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import datetime

class Numbers(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.warnings = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('Moderation cog loaded.')
    
    
    @commands.command()
    async def sync(self,ctx) -> None:
        fmt= await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'synced {len(fmt)} commands.')


    @app_commands.command(name='purge', description='Purges Messages')
    async def purge(self, interaction: discord.Interaction, number: int) ->None:
        await interaction.response.defer(ephemeral=False)
        
        response_message = await interaction.original_response()

        # Purge the specified number of messages, excluding the bot's confirmation message
        def check(message):
            return message.id != response_message.id
        
        deleted = await interaction.channel.purge(limit=number, check=check)
        await asyncio.sleep(1)
        if len(deleted) == 0:
            embed=discord.Embed(title='Purge Complete!' , description='No messages were purged.')
            await interaction.followup.send(embed=embed, ephemeral=False)

        else:
            embed=discord.Embed(title='Purge Complete!', description= f'{number} Messages were purged.')          
            await interaction.followup.send(embed=embed, ephemeral=False)
    
    # Slash command to issue a warning
    @app_commands.command(name="warn", description="Warn a member.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to warn", reason="The reason for the warning")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        
        if member == interaction.user:
            await interaction.response.send_message("You cannot warn yourself.", ephemeral=True)
            return

        if member.bot:
            await interaction.response.send_message("You cannot warn a bot.", ephemeral=True)
            return

        # Add the warning to the warnings dictionary
        if member.id not in self.warnings:
            self.warnings[member.id] = []
        self.warnings[member.id].append(reason)

        await interaction.response.send_message(f"{member.mention} has been warned for: {reason}")

    # Slash command to check warnings of a user
    @app_commands.command(name="warnings", description="Check warnings of a member.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member whose warnings you want to check")
    async def check_warnings(self, interaction: discord.Interaction, member: discord.Member):
        if member.id in self.warnings:
            warning_list = self.warnings[member.id]
            warning_message = f"{member.mention} has {len(warning_list)} warning(s):\n" + "\n".join(warning_list)
            await interaction.response.send_message(warning_message)
        else:
            await interaction.response.send_message(f"{member.mention} has no warnings.")

    # Slash command to clear warnings of a user
    @app_commands.command(name="clearwarnings", description="Clear all warnings of a member.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member whose warnings you want to clear")
    async def clear_warnings(self, interaction: discord.Interaction, member: discord.Member):
        if member.id in self.warnings:
            del self.warnings[member.id]
            await interaction.response.send_message(f"Cleared all warnings for {member.mention}.")
        else:
            await interaction.response.send_message(f"{member.mention} has no warnings to clear.")

    # Error handling for permission errors
    @warn.error
    @check_warnings.error
    @clear_warnings.error
    async def on_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

    
    """The Timeout Command"""
    @app_commands.command(name='mute', description='Mutes member for the duration specified.' )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0, reason: str = None) ->None:
        
        duration = datetime.timedelta(seconds=seconds, minutes=minutes, hours= hours, days=days)
        if member.top_role > interaction.guild.me.top_role:
            await interaction.response.send_message(f"Cannot mute {member}. They have a higher role than me.", ephemeral=False )
        
       # elif duration=:
          #  await member.timeout(1, reason=reason)
          #  await interaction.response.send_message("Member has been timedout for 1 second")
        
        
        else:
            
            await member.timeout(duration, reason=reason)
            await interaction.response.send_message(f'{member.mention} was timed out until for {duration}', ephemeral=False)
    
    
async def setup(bot):
    await bot.add_cog(Numbers(bot) , guilds=[discord.Object(id='1246531747106132060')])