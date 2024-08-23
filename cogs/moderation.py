import discord 
from discord.ext import commands



class Numbers(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    
   

    async def on_ready(self):
        print('Moderation cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('Moderation cog loaded.')   
        


async def setup(bot):
    await bot.add_cog(Numbers(bot))