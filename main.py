import discord 
from discord.ext import commands

class Login(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self , message):
        print(f'Message from {message.author}: {message.content}')

intents=discord.Intents.default()
intents.message_content = True 

client = Login(intents=intents)
client.run('MTI0NjUyNjE3MjA4NzU4Njg0OA.GBj7WA.uDa0jXfZNk9SgNHP0NV92anw3kYVgjJk9BpDwM')