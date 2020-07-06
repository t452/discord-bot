import asyncio
import csv
import io
import typing
from functools import cached_property

import aiohttp
import discord
from discord.ext import commands

from helpers import constants

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

CONTACTS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSUSaX2yTNs9r6F6vtVUUCUafc3iY43IhpgVBgYAKOvkIA8TfkkxcHl6l1mQqqSKVeOXydoyyI7V2Q/pub?output=csv"


def setup(bot: commands.Bot):
    bot.add_cog(Contact(bot))


class Contact(commands.Cog):
    """For getting contact information."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.run_until_complete(self.load_db())

    async def load_db(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(CONTACTS_URL) as r:
                if r.status == 200:
                    reader = csv.DictReader(io.StringIO(await r.text()))
                    self.db = {
                        row["Concat"]: row for row in reader if row["Patrol"] != ""
                    }

    @commands.is_owner()
    @commands.command()
    async def reloadcontacts(self, ctx: commands.Context):
        """Reload the contacts database."""

        message = await ctx.send("Reloading contacts database...")
        await self.load_db()
        await message.edit(content="Contacts database has been reloaded.")

    @commands.command()
    async def contact(
        self, ctx: commands.Context, *, name: typing.Union[discord.Member, str]
    ):
        """Look up a contact in the T452 database."""

        if not hasattr(self, "db"):
            await ctx.send(
                "The database isn't loaded, please try again in a few seconds."
            )
            return

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

        def make_embed(person, member=None):
            embed = discord.Embed(
                title=person["First Name"] + " " + person["Last Name"],
                description=person["S/F/M"],
                color=0xF44336,
            )

            if member is not None:
                embed.set_author(name=str(member), icon_url=member.avatar_url)

            for name, key, inline in EMBED_FIELDS:
                if (value := person[key]) != "":
                    embed.add_field(name=name, value=value, inline=inline)

            return embed

        message = await ctx.send(embed=make_embed(person, member))

        # Look for reactions, edit embed

        reactions = {
            "👶🏻": person["Patrol"] + person["P_Num"] + "1",
            "👨🏻": person["Patrol"] + person["P_Num"] + "2",
            "👩🏻": person["Patrol"] + person["P_Num"] + "3",
        }

        async def add_reactions():
            for x in reactions:
                await message.add_reaction(x)

        def check(reaction, user):
            return (
                user.id == ctx.author.id
                and reaction.emoji in reactions
                and reaction.message.id == message.id
            )

        self.bot.loop.create_task(add_reactions())

        try:
            while True:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=120, check=check
                )
                person = self.db[reactions[reaction.emoji]]
                try:
                    member = next(
                        x
                        for x in ctx.guild.members
                        if x.display_name.lower()
                        == person["First Name"].lower()
                        + " "
                        + person["Last Name"].lower()
                    )
                except StopIteration:
                    member = None

                await reaction.remove(user)
                await message.edit(embed=make_embed(person, member))

        except asyncio.TimeoutError:
            await message.add_reaction("🛑")
