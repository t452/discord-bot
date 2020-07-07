import asyncio

from discord.ext import commands


class Paginator:
    def __init__(self, get_page, num_pages):
        self.num_pages = num_pages
        self.get_page = get_page

    async def send(self, bot: commands.Bot, ctx: commands.Context, page: int = 0):
        message = await ctx.send(embed=await self.get_page(page))

        async def do_reactions():
            await message.add_reaction("⏮️")
            await message.add_reaction("◀")
            await message.add_reaction("▶")
            await message.add_reaction("⏭️")

        asyncio.create_task(do_reactions())

        try:
            while True:
                reaction, user = await bot.wait_for(
                    "reaction_add",
                    check=lambda r, u: r.message.id == message.id
                    and u.id == ctx.author.id,
                    timeout=120,
                )
                await reaction.remove(user)

                page = {
                    "⏮️": 0,
                    "◀": page - 1,
                    "▶": page + 1,
                    "⏭️": self.num_pages - 1,
                }[reaction.emoji] % self.num_pages

                await message.edit(embed=await self.get_page(page, clear))

        except asyncio.TimeoutError:
            await message.add_reaction("🛑")