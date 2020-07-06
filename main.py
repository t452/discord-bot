import logging
import os
import shelve

from discord.ext import commands

import cogs

# Setup

logging.basicConfig(level=logging.INFO)

bot_token = os.getenv("BOT_TOKEN")
command_prefix = os.getenv("COMMAND_PREFIX")

bot = commands.Bot(
    command_prefix=command_prefix,
    help_command=commands.MinimalHelpCommand(),
    case_insensitive=True,
)

# Load cogs

bot.load_extension(f"jishaku")

for i in dir(cogs):
    if not i.startswith("_"):
        bot.load_extension(f"cogs.{i}")

# Run bot

bot.run(bot_token)
