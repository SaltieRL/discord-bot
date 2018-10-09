import sys

import discord
import requests
from discord.ext.commands import Bot

try:
    from config import TOKEN, BOT_PREFIX
except ImportError:
    print('Unable to run bot, as token does not exist!')
    sys.exit()

bot = Bot(BOT_PREFIX)
bot.remove_command("help")


def get_json(url):
    return requests.get(url).json()


@bot.command()
async def ping():
    await bot.say("Pong!")


@bot.command(name="queue", aliases="q")
async def display_queue():
    response = get_json("https://calculated.gg/api/global/queue/count")
    await bot.say(str(response['priority 3']) + ' replays in the queue.')



@bot.command(name="fullqueue")
async def display_full_queue():
    response = get_json("https://calculated.gg/api/global/queue/count")

    say = "Number of replays in each queue."

    embed = discord.Embed(
        title="Queue",
        description=say,
        colour=discord.Colour.blue()
    )
    for queue_priority in [0, 3, 6, 9]:
        msg = str(response["priority " + str(queue_priority)])
        embed.add_field(name="Priority " + str(queue_priority), value=msg,
                        inline=True)

    await bot.say(embed=embed)


@bot.command(name="help", aliases="h")
async def get_help():
    embed = discord.Embed(
        colour=discord.Colour.blue()
    )

    embed.set_author(name="Help")
    embed.add_field(name="!help", value="Shows this message", inline=False)
    embed.add_field(name="!queue !q", value="Shows the current amount of replays in the queue.", inline=False)

    await bot.say(embed=embed)


@bot.event
async def on_ready():
    print('READY')


if __name__ == '__main__':
    bot.run(TOKEN)
