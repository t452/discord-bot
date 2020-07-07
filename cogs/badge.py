import json
import asyncio
import io
from functools import cached_property

import aiohttp
import discord
from discord.ext import commands

from helpers import constants
from helpers import pagination

with open('data/scraped.json') as json_file:
  data = json.load(json_file)


def setup(bot: commands.Bot):
    bot.add_cog(Badge(bot))

'''for badge in data["meritBadges"]:
  print(badge["name"])
  for requirement in badge["requirements"]:
    print (requirement["text"])
    '''

class Badge(commands.Cog):

    def __init__(self, bot: commands.Bot):
      self.bot = bot
      self.data = iter(data["meritBadges"])

    @commands.command()
    async def badge(self, ctx: commands.Context, *, name):        
        try:
          badge = next(x for x in self.data if name.lower() in x["name"].lower())
        except StopIteration:
          await ctx.send("Couldn't find anything matching that query.")
          return
          
        def make_embed(badge):
            embed = discord.Embed(
                title=badge["name"],
                description = badge["name"],
                color=0xF44336,
            )
            return embed

        message = await ctx.send(embed=make_embed(badge))
