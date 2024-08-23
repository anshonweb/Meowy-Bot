import discord 
from discord.ext import commands
import requests


class Numbers(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation cog loaded')
        channel = self.bot.get_channel(1246534324925501521)
        await channel.send('Moderation cog loaded.')
    
    

    @commands.hybrid_group(name="parent" ,  with_app_command=True, description="Different Moderation Commands")
    @commands.guild_only()  # Ensures this command only works in guilds (servers)
    async def parent_command(self, ctx: commands.Context) -> None:
          """
    We even have the use of parents. This will work as usual for ext.commands but will be un-invokable for app commands.
    This is a discord limitation as groups are un-invokable.
    """
    ...   # nothing we want to do in here, I guess!
    @parent_command.command(name='avatar')
    async def avatar(self, ctx : commands.Context , member: discord.Member):
        embed=discord.Embed(title= member._user)
        embed.set_image(url='{}'.format(member.display_avatar))
        await ctx.send(embed=embed)

    @parent_command.command(name='numbers')    
    async def hello(self,ctx: commands.Context, numbers: int):
        response=requests.get(f'http://numbersapi.com/{numbers}')
        embed=discord.Embed(description=response.text)
        
        await ctx.send(embed=embed)
    

    
async def setup(bot):
    await bot.add_cog(Numbers(bot))