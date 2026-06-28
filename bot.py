import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

bot.run(os.getenv('TOKEN'))
