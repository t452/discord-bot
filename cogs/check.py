import asyncio
import csv
import io
import typing
from functools import cached_property

import aiohttp
import discord
from discord.ext import commands
import os


def setup(bot: commands.Bot):
    bot.add_cog(Check(bot))


PATROL_STANDINGS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2KqaDEtHDkdZGX3xRWe1OlQG-O0q_MWKUPrQ5EdW9jIGrbtBZkFyVGdUnoUMHuHGBK5A69gy9lDiI/pub?gid=1890823625&single=true&output=csv"


class Check(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def standings(self, ctx: commands.Context, *args):
        async with ctx.typing(), aiohttp.ClientSession() as session:
            async with session.get(PATROL_STANDINGS) as r:
                if r.status != 200:
                    return await ctx.send("Error fetching Patrolympics standings.")

                reader = csv.DictReader(io.StringIO(await r.text()))
                row = next(reader)

                embed = discord.Embed(title="Patrolympic Standings", color=0xF44336)
                for patrol in reader.fieldnames:
                    embed.add_field(name=patrol, value=row[patrol], inline=True)
                await ctx.send(embed=embed)
