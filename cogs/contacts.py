import csv
import io
import typing
from functools import cached_property

import aiohttp
import discord
from discord.ext import commands

EMBED_FIELDS = (
    ("Patrol", "Patrol", True),
    ("Grade", "Grade", True),
    ("Rank", "Rank", True),
    ("Job", "Scout Troop Job", False),
    ("Job", "Parent ASM", False),
    ("Job", "Parent Committee Job", False),
    ("Email", "Email", False),
    ("Phone Number", "Phone #", False),
    ("Address", "Address", False),
)


def setup(bot: commands.Bot):
    bot.add_cog(Contacts(bot))


class Contacts(commands.Cog):
    """For getting contact information."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.load_db())

    async def load_db(self):
        if "contacts_csv" not in self.bot.db:
            self.db = None

        async with aiohttp.ClientSession() as session:
            async with session.get(self.bot.db["contacts_csv"]) as r:
                if r.status == 200:
                    reader = csv.DictReader(io.StringIO(await r.text()))
                    self.db = {row["Concat"]: row for row in reader}

    @commands.command()
    async def reloadcontacts(self, ctx: commands.Context):
        await self.load_db()

    @commands.command()
    async def contact(
        self, ctx: commands.Context, *, name: typing.Union[discord.Member, str]
    ):

        # Get the string query and the discord member

        if isinstance(name, discord.Member):
            member = name
            name = member.display_name
        else:
            member = None

        # Lookup query

        try:
            person = next(
                x
                for x in self.db.values()
                if name.lower()
                in x["First Name"].lower() + " " + x["Last Name"].lower()
            )
        except StopIteration:
            await ctx.send("Couldn't find anyone matching that query.")
            return

        if member is None:
            try:
                member = next(
                    x
                    for x in ctx.guild.members
                    if x.display_name.lower()
                    == person["First Name"].lower() + " " + person["Last Name"].lower()
                )
            except StopIteration:
                pass

        # Send embed

        embed = discord.Embed(
            title=person["First Name"] + " " + person["Last Name"], color=0xF44336
        )

        if member is not None:
            embed.set_author(name=str(member), icon_url=member.avatar_url)

        for name, key, inline in EMBED_FIELDS:
            if (value := person[key]) != "":
                embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)
