import discord 
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import datetime
import sqlite3

class Numbers(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
        self.conn = sqlite3.connect('maindatabase.db')
        self.cursor = self.conn.cursor()
        self.create_table()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('Moderation cog loaded.')
    
    
    @commands.command()
    async def sync(self,ctx) -> None:
        fmt= await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'synced {len(fmt)} commands.')
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderation (
                user_id INTEGER PRIMARY KEY,
                warns INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bans (
                user_id INTEGER PRIMARY KEY,
                ban_reason TEXT,
                banned_at TEXT,
                unbanned_at TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS filters (
                word TEXT PRIMARY KEY
            )
        ''')
        self.conn.commit()

    def add_member(self, user_id):
        self.cursor.execute('INSERT OR IGNORE INTO moderation (user_id, warns) VALUES (?, ?)', (user_id, 0))
        self.conn.commit()

    def fetch_warnings(self, user_id):
        self.cursor.execute('SELECT warns FROM moderation WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_warnings(self, user_id, warns):
        self.cursor.execute('UPDATE moderation SET warns = ? WHERE user_id = ?', (warns, user_id))
        self.conn.commit()

    def clear_warnings(self, user_id):
        self.cursor.execute('UPDATE moderation SET warns = 0 WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def add_ban(self, user_id, reason):
        self.cursor.execute('''
            INSERT OR REPLACE INTO bans (user_id, ban_reason, banned_at)
            VALUES (?, ?, ?)
        ''', (user_id, reason, datetime.datetime.utcnow().isoformat()))
        self.conn.commit()

    def remove_ban(self, user_id):
        self.cursor.execute('''
            UPDATE bans
            SET unbanned_at = ?
            WHERE user_id = ?
        ''', (datetime.datetime.utcnow().isoformat(), user_id))
        self.conn.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('Moderation cog loaded.')

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        # If a user is banned manually, this listener will update the database
        self.add_ban(user.id, "Banned manually")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        # If a user is unbanned manually, this listener will update the database
        self.remove_ban(user.id)

    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'synced {len(fmt)} commands.')

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

        # Ensure the member is in the database
        self.add_member(member.id)

        # Fetch the current warnings and increment
        current_warnings = self.fetch_warnings(member.id)
        new_warnings = current_warnings + 1
        self.update_warnings(member.id, new_warnings)

        await interaction.response.send_message(f"{member.mention} has been warned for: {reason}. They now have {new_warnings} warning(s).")

        if new_warnings > 3:
            duration = datetime.timedelta(minutes=20)
            await member.timeout(duration, reason=reason)
            await interaction.edit_original_response(f'{member.mention} was timed out until for {duration}', ephemeral=False)
        elif new_warnings > 6:
            duration = datetime.timedelta(minutes=40)
            await member.timeout(duration, reason=reason)
            await interaction.edit_original_response(f'{member.mention} was timed out until for {duration}', ephemeral=False)

    @app_commands.command(name="warnings", description="Check warnings of a member.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member whose warnings you want to check")
    async def check_warnings(self, interaction: discord.Interaction, member: discord.Member):
        current_warnings = self.fetch_warnings(member.id)
        if current_warnings > 0:
            await interaction.response.send_message(f"{member.mention} has {current_warnings} warning(s).")
        else:
            await interaction.response.send_message(f"{member.mention} has no warnings.")

    @app_commands.command(name="clearwarnings", description="Clear all warnings of a member.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member whose warnings you want to clear")
    async def clearwarnings(self, interaction: discord.Interaction, member: discord.Member):
        current_warnings = self.fetch_warnings(member.id)
        if current_warnings > 0:
            self.clear_warnings(member.id)  # Use the renamed method
            await interaction.response.send_message(f"Cleared all warnings for {member.mention}.")
        else:
            await interaction.response.send_message(f"{member.mention} has no warnings to clear.")
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
        
    @warn.error
    @check_warnings.error
    @clearwarnings.error
    async def on_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
    
    
    
    
    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member to ban", reason="The reason for the ban")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("You cannot ban yourself.", ephemeral=True)
            return

        if member.bot:
            await interaction.response.send_message("You cannot ban a bot.", ephemeral=True)
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(f"Cannot ban {member}. They have a higher role than me.", ephemeral=True)
            return

        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member.mention} has been banned for: {reason}", ephemeral=False)

    

    

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
    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member to ban", reason="The reason for the ban")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("You cannot ban yourself.", ephemeral=True)
            return

        if member.bot:
            await interaction.response.send_message("You cannot ban a bot.", ephemeral=True)
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(f"Cannot ban {member}. They have a higher role than me.", ephemeral=True)
            return

        # Ban the member and log it in the database
        await member.ban(reason=reason)
        self.add_ban(member.id, reason)
        await interaction.response.send_message(f"{member.mention} has been banned for: {reason}", ephemeral=False)
    
    @app_commands.command(name="unban", description="Unban a member from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user_id="The ID of the user to unban")
    async def unban(self, interaction: discord.Interaction, user_id: int):
        user = discord.Object(id=user_id)
        try:
            await interaction.guild.unban(user)
            self.remove_ban(user_id)
            await interaction.response.send_message(f"Unbanned user with ID {user_id}.", ephemeral=False)
        except discord.NotFound:
            await interaction.response.send_message(f"No banned user found with ID {user_id}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"Could not unban user with ID {user_id}.", ephemeral=True)
    
    @app_commands.command(name="viewbans", description="View all banned members.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def view_bans(self, interaction: discord.Interaction):
        self.cursor.execute('SELECT user_id, ban_reason, banned_at, unbanned_at FROM bans WHERE unbanned_at IS NULL')
        bans = self.cursor.fetchall()

        if not bans:
            await interaction.response.send_message("No members are currently banned.", ephemeral=True)
            return

        embed = discord.Embed(title="Banned Members", color=discord.Color.red())
        for ban in bans:
            user_id, reason, banned_at, _ = ban
            member = interaction.guild.get_member(user_id) or discord.Object(id=user_id)
            embed.add_field(
                name=f"User ID: {user_id}",
                value=f"**Reason:** {reason}\n**Banned At:** {banned_at}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member.mention} has been kicked from the server.")

    

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Fetch forbidden words from the database
        self.cursor.execute('SELECT word FROM filters')
        forbidden_words = [row[0].lower() for row in self.cursor.fetchall()]

        for word in forbidden_words:
            if word in message.content.lower():
                await message.delete()

                # Get current warnings for the user
                self.cursor.execute('SELECT warns FROM moderation WHERE user_id = ?', (message.author.id,))
                result = self.cursor.fetchone()

                if result is None:
                    # If user does not exist in the table, add them
                    self.cursor.execute('INSERT INTO moderation (user_id, warns) VALUES (?, ?)', (message.author.id, 1))
                    current_warns = 1
                else:
                    # Update the existing warning count
                    current_warns = result[0] + 1
                    self.cursor.execute('UPDATE moderation SET warns = ? WHERE user_id = ?', (current_warns, message.author.id))

                self.conn.commit()

                # Notify the user
                await message.channel.send(f"{message.author.mention}, your message contained forbidden content and was deleted. This is warning #{current_warns}.", delete_after=10)
                break

    @commands.command(name='addfilter')
    @commands.has_permissions(manage_messages=True)
    async def add_filter(self, ctx, *, word: str):
        """Add a forbidden word to the filter."""
        word = word.lower()
        try:
            self.cursor.execute('INSERT INTO filters (word) VALUES (?)', (word,))
            self.conn.commit()
            await ctx.send(f'The word "{word}" has been added to the filter list.')
        except sqlite3.IntegrityError:
            await ctx.send(f'The word "{word}" is already in the filter list.')

    @commands.command(name='removefilter')
    @commands.has_permissions(manage_messages=True)
    async def remove_filter(self, ctx, *, word: str):
        """Remove a forbidden word from the filter."""
        word = word.lower()
        self.cursor.execute('DELETE FROM filters WHERE word = ?', (word,))
        self.conn.commit()
        if self.cursor.rowcount > 0:
            await ctx.send(f'The word "{word}" has been removed from the filter list.')
        else:
            await ctx.send(f'The word "{word}" was not found in the filter list.')

    async def cog_unload(self):
        """Close the database connection when the cog is unloaded."""
        self.conn.close()


    @commands.command(name='showfilters')
    @commands.has_permissions(manage_messages=True)
    async def show_filters(self, ctx):
        """Show all forbidden words."""
        self.cursor.execute('SELECT word FROM filters')
        forbidden_words = [row[0] for row in self.cursor.fetchall()]
        if forbidden_words:
            await ctx.send("Forbidden words:\n" + "\n".join(forbidden_words))
        else:
            await ctx.send("No forbidden words found.")

    @app_commands.command(name='showfilters', description='Show all forbidden words.')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def show_filters_slash(self, interaction: discord.Interaction):
        """Show all forbidden words (slash command)."""
        self.cursor.execute('SELECT word FROM filters')
        forbidden_words = [row[0] for row in self.cursor.fetchall()]
        if forbidden_words:
            await interaction.response.send_message("Forbidden words:\n" + "\n".join(forbidden_words))
        else:
            await interaction.response.send_message("No forbidden words found.")
    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = None):
        """Warn a member."""
        if member == ctx.author:
            await ctx.send("You cannot warn yourself.")
            return

        if member.bot:
            await ctx.send("You cannot warn a bot.")
            return

        # Ensure the member is in the database
        self.add_member(member.id)

        # Fetch the current warnings and increment
        current_warnings = self.fetch_warnings(member.id)
        new_warnings = current_warnings + 1
        self.update_warnings(member.id, new_warnings)

        await ctx.send(f"{member.mention} has been warned for: {reason}. They now have {new_warnings} warning(s).")

        if new_warnings > 3:
            duration = datetime.timedelta(minutes=20)
            await member.timeout(duration, reason=reason)
            await ctx.send(f'{member.mention} was timed out for {duration}.')
        elif new_warnings > 6:
            duration = datetime.timedelta(minutes=40)
            await member.timeout(duration, reason=reason)
            await ctx.send(f'{member.mention} was timed out for {duration}.')

    @commands.command(name='warnings')
    @commands.has_permissions(manage_messages=True)
    async def check_warnings(self, ctx, member: discord.Member):
        """Check warnings of a member."""
        current_warnings = self.fetch_warnings(member.id)
        if current_warnings > 0:
            await ctx.send(f"{member.mention} has {current_warnings} warning(s).")
        else:
            await ctx.send(f"{member.mention} has no warnings.")

    @commands.command(name='clearwarnings')
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Clear all warnings of a member."""
        current_warnings = self.fetch_warnings(member.id)
        if current_warnings > 0:
            self.clear_warnings(member.id)
            await ctx.send(f"Cleared all warnings for {member.mention}.")
        else:
            await ctx.send(f"{member.mention} has no warnings to clear.")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        """Ban a member from the server."""
        if member == ctx.author:
            await ctx.send("You cannot ban yourself.")
            return

        if member.bot:
            await ctx.send("You cannot ban a bot.")
            return

        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send(f"Cannot ban {member}. They have a higher role than me.")
            return

        await member.ban(reason=reason)
        self.add_ban(member.id, reason)
        await ctx.send(f"{member.mention} has been banned for: {reason}.")

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """Unban a member from the server."""
        user = discord.Object(id=user_id)
        try:
            await ctx.guild.unban(user)
            self.remove_ban(user_id)
            await ctx.send(f"Unbanned user with ID {user_id}.")
        except discord.NotFound:
            await ctx.send(f"No banned user found with ID {user_id}.")
        except discord.Forbidden:
            await ctx.send(f"Could not unban user with ID {user_id}.")

    @commands.command(name='viewbans')
    @commands.has_permissions(ban_members=True)
    async def view_bans(self, ctx):
        """View all banned members."""
        self.cursor.execute('SELECT user_id, ban_reason, banned_at FROM bans WHERE unbanned_at IS NULL')
        bans = self.cursor.fetchall()

        if not bans:
            await ctx.send("No members are currently banned.")
            return

        embed = discord.Embed(title="Banned Members", color=discord.Color.red())
        for ban in bans:
            user_id, reason, banned_at = ban
            embed.add_field(
                name=f"User ID: {user_id}",
                value=f"**Reason:** {reason}\n**Banned At:** {banned_at}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = None):
        """Kick a member from the server."""
        if member == None:
            await ctx.send(f'Mention member that has to be kicked.')
        
        else:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked from the server.")

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
        
    @warn.error
    @check_warnings.error
    @clearwarnings.error
    @timeout.error
    @ban.error
    @unban.error
    @show_filters_slash.error
    async def on_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Numbers(bot) , guilds=[discord.Object(id='1246531747106132060') , discord.Object(id='820326376673771540')])
