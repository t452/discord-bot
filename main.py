import logging
import os
import shelve

import mongoengine
from discord.ext import commands

import cogs

# Setup

mongoengine.connect("t452", host=os.getenv("DATABASE_URI"))

logging.basicConfig(level=logging.INFO)

bot_token = os.getenv("BOT_TOKEN")
command_prefix = os.getenv("COMMAND_PREFIX")

bot = commands.Bot(
    command_prefix=command_prefix,
    help_command=commands.MinimalHelpCommand(),
    case_insensitive=True,
)


@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)

    ignore = False
    delete = False

    for cog in bot.cogs.values():
        try:
            i, d = await cog.check_message(ctx)
            ignore, delete = ignore or i, delete or d
        except AttributeError:
            continue

    if delete:
        await message.delete()
        return

    if not ignore:
        await bot.process_commands(message)


# Load cogs

bot.load_extension(f"jishaku")

for i in dir(cogs):
    if not i.startswith("_"):
        bot.load_extension(f"cogs.{i}")

# Run bot

bot.run(bot_token)
