import json

import aiohttp
import discord
from discord.ext import commands

from helpers import constants
from helpers import pagination

with open('data/scraped.json') as json_file:
  data = json.load(json_file)


def setup(bot: commands.Bot):
    bot.add_cog(Req(bot))


class Req(commands.Cog):

    def __init__(self, bot: commands.Bot):
      self.bot = bot
      self.data = data["ranks"]+data["meritBadges"]

    @commands.command()
    async def req(self, ctx: commands.Context, *args):     
        #dont flame var badge can also be a "rank" object

        #convert args into name
        try: 
          startNum = int(args[-1])
          name = " ".join(args[0:-1])
        except:
          startNum = 1
          name = " ".join(args)

        #pull badge from scraped.json and format
        try:
          badge = next(x for x in self.data if name.lower() in x["name"].lower())
          imgName = badge["name"].replace(" ", "").lower()
        except StopIteration:
          await ctx.send("Couldn't find anything matching that query.")
          return
        
        groups = []
        prev = -1
        for x in badge["requirements"]:
          if x["depth"] == 0:
            prev = x["depth"]
            groups.append([])
          groups[-1].append(x)
          
        #make embed page (refer to /helpers/pagination.py)
        async def get_page(idx):
          #object title formatting
          try:
            title = (badge["name"] if not(badge["isEagle"]) else "{} 🦅".format(badge["name"]))
          except:
            title = badge["name"]
          embed = discord.Embed(
            title=title,
            color=0xF44336,
          )
          text_field = "\n".join("    " * x["depth"] + ("" if x["index"] == "" else x["index"] + ". ") + x["text"] for x in groups[idx])
          embed.add_field(name=f"Requirement {idx+1}", value=text_field, inline=False)
          embed.set_thumbnail(url=f"http://t452.oliverni.com/merit-badges/{imgName}.png")
          embed.set_footer(text=f"Displaying requirement {idx+1} out of {len(groups)}.")
          return embed

        paginator = pagination.Paginator(get_page, len(groups))
        await paginator.send( self.bot, ctx, page = startNum-1)
        
