import discord 
from discord.ext import commands
import asyncio


class Test(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member) ->None:
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send(f"{member} has joined the server")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send(f"{member} has joined the server")


async def setup(bot):
    await bot.add_cog(Test(bot))
