import discord
import re
from aiohttp import web
from discord.ext import commands
from dateutil.parser import parse
from helpers import constants

CHANNEL_ID = 729523809685733377


def setup(bot: commands.Bot):
    bot.add_cog(Email(bot))


class Email(commands.Cog):
    """For relaying emails from Google Groups."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.run_until_complete(self.start_server())

    async def start_server(self):
        routes = web.RouteTableDef()

        @routes.post("/email")
        async def hello(request):
            data = await request.json()

            channel = self.bot.get_channel(CHANNEL_ID)

            embed = discord.Embed(title=data["message"]["subject"], color=0xF44336,)

            match = re.match(
                r"^([\s\S]*)\s*--\s*([\s\S]*?)$", data["message"]["body_plain"]
            )
            embed.description = match.group(1)

            # Set author

            try:
                member = next(
                    x
                    for x in channel.guild.members
                    if x.display_name.lower() == data["message"]["from"]["name"].lower()
                )
                embed.set_author(
                    name=data["message"]["from"]["name"], icon_url=member.avatar_url
                )
            except StopIteration:
                embed.set_author(name=data["message"]["from"]["name"])

            embed.timestamp = parse(data["message"]["date"])
            embed.set_footer(text="Troop 452 Google Group")

            await channel.send(embed=embed)

            return web.Response(text="Success")

        app = web.Application()
        app.add_routes(routes)

        self.runner = web.AppRunner(app)

        await self.runner.setup()
        site = web.TCPSite(self.runner, "localhost", 5000)
        await site.start()

    def cog_unload(self):
        self.bot.loop.run_until_complete(self.runner.cleanup())
