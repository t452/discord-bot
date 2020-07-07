import json

import aiohttp
import discord
from discord.ext import commands

from helpers import constants
from helpers import pagination

with open("data/scraped.json") as json_file:
    data = json.load(json_file)


def setup(bot: commands.Bot):
    bot.add_cog(Req(bot))


class Req(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = data["ranks"] + data["meritBadges"]

    @commands.command()
    async def req(self, ctx: commands.Context, *args):

        if args[-1].isdigit():
            page = int(args[-1]) - 1
            args = args[:-1]
        else:
            page = 0

        try:
            badge = next(
                x for x in self.data if " ".join(args).lower() in x["name"].lower()
            )
        except StopIteration:
            await ctx.send("Couldn't find anything matching that query.")
            return

        image_name = badge["name"].replace(" ", "").lower()

        groups = []
        for x in badge["requirements"]:
            if x["depth"] == 0:
                groups.append([])
            groups[-1].append(x)

        async def get_page(idx):
            title = badge["name"]
            if badge.get("isEagle", False):
                title += " 🦅"

            lines = [f"**Requirement {idx + 1}**"]
            lines += [
                ("" if x["index"] == "" else f"{x['index']}. ") + x["text"]
                for x in groups[idx]
            ]

            embed = discord.Embed(
                title=title, description="\n\n".join(lines), color=0xF44336,
            )
            embed.set_thumbnail(
                url=f"http://t452.oliverni.com/merit-badges/{image_name}.png"
            )
            embed.set_footer(
                text=f"Displaying requirement {idx+1} out of {len(groups)}."
            )
            return embed

        paginator = pagination.Paginator(get_page, len(groups))
        await paginator.send(self.bot, ctx, page=page)
