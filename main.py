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

@bot.event
async def on_member_join(member):
    await member.send(''' 📋 **RULES** @everyone

1. All BSA policies are enforced in this server, as are all other troop rules. You must have Cyber Chip to talk in the server.
2. All content must be scout-appropriate. NSFW content will not be tolerated.
3. Keep discussions on-topic and in the designated channels. Any out of place conversation will be removed.
4. Be nice. Follow the Scout Oath and Law. Avoid conflicts with other scouts.
5. No swearing. Any profane content will be removed.
6. Use common sense. If you need to ask whether something is okay, it's probably not.
7. Ping @Admin if you have a question about the server.
8. No speedwatchers or speedreaders of anime/manga.

You must use your **REAL NAME** in order to participate. There are no exceptions.

**Please DM one of the Staff to change your nickname or send "Fname Lname" in this bot DM (ex. John Chang).** 

Violation of the above rules may result in a mute and/or, in severe cases, revoking of your Cyber Chip. ''')
    server = bot.get_guild(728821753182289961)
    message = await bot.wait_for('message', timeout=1000, check=lambda m: m.author.id == member.id)
    guildmember = server.get_member(message.author.id)

    await guildmember.edit(nick=message.content)
    await member.send(f'Nickname set to: "{message.content}"')

# Load cogs

bot.load_extension(f"jishaku")

for i in dir(cogs):
    if not i.startswith("_"):
        bot.load_extension(f"cogs.{i}")

# Run bot

bot.run(bot_token)
