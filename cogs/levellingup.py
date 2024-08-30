import discord
from discord.ext import commands
import asyncio
import sqlite3
from discord import app_commands
from discord.ext.paginators.button_paginator import ButtonPaginator
import os
from PIL import Image, ImageDraw, ImageFont
import io


class XpSystem(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.conn = sqlite3.connect('maindatabase.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        ''')
        self.conn.commit()

    def get_user_data(self, user_id):
        self.cursor.execute('SELECT xp, level FROM users WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()

    def add_user(self, user_id):
        self.cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        self.conn.commit()

    def update_user_data(self, user_id, xp, level):
        self.cursor.execute('UPDATE users SET xp = ?, level = ? WHERE user_id = ?', (xp, level, user_id))
        self.conn.commit()

    def calculate_xp_needed(self, level):
        return 100 * level


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        user_id = message.author.id
        user_data = self.get_user_data(user_id)

        if not user_data:
            self.add_user(user_id)
            user_data = (0, 1)

        xp, level = user_data
        xp += 10  # Add XP per message, adjust as needed
        if message.content.startswith('?'):
            xp-=10

        xp_needed = self.calculate_xp_needed(level)
        
        if xp >= xp_needed:
            level += 1
            xp = xp - xp_needed
            await message.channel.send(f"Congratulations {message.author.mention}, you leveled up to level {level}!")

        self.update_user_data(user_id, xp, level)

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = member.id
        user_data = self.get_user_data(user_id)
        
        if user_data:
            xp, level = user_data
            await ctx.send(f"{member.mention} is currently at level {level} with {xp} XP.")
        else:
            await ctx.send(f"{member.mention} has no XP data yet.")


    @commands.command(name='setlevel')
    @commands.has_permissions(administrator=True)
    async def setlevel(self, ctx, member: discord.Member = None, level: int = None) -> None:
        if member is None:
            await ctx.send("Please mention a user whose level you want to set!")
            return

        if level is None:
            await ctx.send("Please specify the level you want to set!")
            return

        if level < 1:
            await ctx.send("The level must be a positive integer!")
            return

        user_id = member.id
        user_data = self.get_user_data(user_id)

        if not user_data:
            self.add_user(user_id)
            user_data = (0, 1)

        xp, _ = user_data
        xp_needed = self.calculate_xp_needed(level)

        # Update user's level and set their XP to the necessary amount for the new level
        self.update_user_data(user_id, xp_needed, level)
        await ctx.send(f"{member.mention}'s level has been set to level {level} with {xp_needed} XP.")
    
    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx):
        self.cursor.execute('SELECT user_id, xp, level FROM users ORDER BY xp DESC LIMIT 10')
        top_users = self.cursor.fetchall()

        if not top_users:
            await ctx.send("No users found in the leaderboard.")
            return

        leaderboard_message = "**Leaderboard**\n"

            # Create the embed
        embed = discord.Embed(title=f"{ctx.guild.name}'s Leaderboard", color=discord.Color.blue())
        embed.set_footer(text="Top users based on XP")

        for idx, (user_id, xp, level) in enumerate(top_users, start=1):
            user = self.bot.get_user(user_id)
            username = f"<@{user_id}>"
            embed.add_field(name=f"{idx}. {username}", value=f"Level {level} - {xp} XP", inline=False)
        
        await ctx.send(embed=embed)

    async def create_rank_card(self, user: discord.User, level: int, xp: int, rank: int):
        # Create a blank image with a white background
        width, height = 600, 200
        card = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(card)

        # Draw the background rectangle
        draw.rectangle([10, 10, width - 10, height - 10], fill=(240, 240, 240), outline=(200, 200, 200), width=2)

        # Load the user's profile picture
        profile_picture = await self.get_profile_picture(user)
        profile_picture = profile_picture.resize((80, 80))  # Resize the profile picture
        card.paste(profile_picture, (20, 20))

        # Load the font
        font_path = "/home/ansh/projects/Bot/cogs/fonts/Playfair_Display/PlayfairDisplay-VariableFont_wght.ttf"  # Path to your TTF font
        title_font = ImageFont.truetype(font_path, 30)
        text_font = ImageFont.truetype(font_path, 24)

        # Draw the user name, level, XP, and rank
        draw.text((110, 20), f"{user.name}#{user.discriminator}", fill=(0, 0, 0), font=title_font)
        draw.text((110, 60), f"Rank: #{rank}", fill=(0, 0, 0), font=text_font)
        draw.text((110, 90), f"Level: {level}", fill=(0, 0, 0), font=text_font)
        draw.text((110, 120), f"XP: {xp}", fill=(0, 0, 0), font=text_font)

        # Save the image to a BytesIO object
        image_bytes = io.BytesIO()
        card.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        return image_bytes

    async def get_profile_picture(self, user: discord.User):
        # Get the user's avatar
        avatar_url = str(user.avatar_url_as(size=128))  # Adjust size as needed
        async with self.bot.session.get(avatar_url) as response:
            if response.status == 200:
                image_data = await response.read()
                return Image.open(io.BytesIO(image_data))
        return Image.new('RGB', (128, 128), color=(255, 255, 255))  # Fallback image

    @commands.command(name='rank')
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = member.id
        user_data = self.get_user_data(user_id)

        if user_data:
            xp, level, rank = user_data
            rank_card_image = await self.create_rank_card(member, level, xp, rank)

            await ctx.send(file=discord.File(rank_card_image, filename='rank_card.png'))
        else:
            await ctx.send(f"No XP data found for {member.mention}.")




async def setup(bot):

    await bot.add_cog(XpSystem(bot))

