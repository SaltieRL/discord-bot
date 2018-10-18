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


@bot.command(pass_context=True)
async def ping(ctx):
    await bot.send_message(ctx.message.channel, "Pong!")


@bot.command(name="help", aliases="h", pass_context=True)
async def get_help(ctx):
    args = ctx.message.content.lower().split(" ")

    if len(args) == 1:
        help_embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        help_embed.set_footer(text="do \"!help <command name>\" for more information on a command.")
        help_embed.set_author(name="Help", icon_url="https://media.discordapp.net/attachments/495315775423381518/499487940414537728/confirmation_verification-512.png")
        help_embed.add_field(name="!help", value="Shows this message", inline=False)
        help_embed.add_field(name="!queue !q", value="Shows the current amount of replays in the queue.", inline=False)
        help_embed.add_field(name="!stats <id>", value="Shows the stats for the given id.", inline=False)
        help_embed.add_field(name="!id <username>", value="Gives the Calulated.gg id for the username.")

        await bot.send_message(ctx.message.channel, embed=help_embed)

    elif args[1] == "stats":
        stats_help_embed = discord.Embed(
            description="!stats <id>",
            colour=discord.Colour.blue()
        )

        stats_help_embed.set_footer(text="Note: alle parameters can have mixed up upper-/lowercase letters, and the bot will still recognize it.")
        stats_help_embed.set_author(name="Stats", icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
        stats_help_embed.add_field(name="Descrition", value="Shows the stats for the given id.", inline=False)
        stats_help_embed.add_field(name="Parameters", value="!stats takes in the following parameters: `id`", inline=False)
        stats_help_embed.add_field(name="id accepts:", value="The Calculated.gg id of a user (can be found with !id)"
                                                             "\n The players username, more succesful if you use the id instead of the username.")

        await bot.send_message(ctx.message.channel, embed=stats_help_embed)
    else:
        await bot.send_message(ctx.message.channel, "Command does not seem to exist, or the command does not have any additional information. Please try again.")


@bot.command(name="queue", aliases="q", pass_context=True)
async def display_queue(ctx):
    response = get_json("https://calculated.gg/api/global/queue/count")
    await bot.send_message(ctx.message.channel, str(response['priority 3']) + ' replays in the queue.')


@bot.command(name="fullqueue")
async def display_full_queue():
    response = get_json("https://calculated.gg/api/global/queue/count")

    say = "Number of replays in each queue."

    embed = discord.Embed(
        title="Queue",
        description=say,
        colour=discord.Colour.blue()
    )


    for priority in response:
        msg = str(priority["count"])
        embed.add_field(name=str(priority["name"]), value=msg,
                        inline=True)

    await bot.say(embed=embed)


@bot.command(name="stats", pass_context=True)
async def get_stats(ctx):
    args = ctx.message.content.split(" ")

    idurl = "https://calculated.gg/api/player/{}".format(args[1])
    responseID = requests.get(idurl)
    id = responseID.json()

    urlStats = "https://calculated.gg/api/player/{}/profile_stats".format(id)
    responseStats = requests.get(urlStats)

    carName = responseStats.json()["car"]["carName"]
    carPercantage = str(round(responseStats.json()["car"]["carPercentage"] * 100, 1)) + "%"

    urlProfile = "https://calculated.gg/api/player/{}/profile".format(id)
    responseProfile = requests.get(urlProfile)

    avatarLink = responseProfile.json()["avatarLink"]
    authorName = responseProfile.json()["name"]
    pastNames = responseProfile.json()["pastNames"]

    list_pastNames = ""
    for x in pastNames:
        list_pastNames = list_pastNames + x + "\n"

    stats_embed = discord.Embed(
        color=discord.Color.blue()
    )

    stats_embed.set_author(name=authorName, url="https://calculated.gg/players/{}/overview".format(id),
                           icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
    stats_embed.set_thumbnail(url=avatarLink)
    stats_embed.add_field(name="Favourite car", value=carName + " (" + carPercantage + ")")
    stats_embed.add_field(name="Past names", value=list_pastNames)

    await bot.send_message(ctx.message.channel, embed=stats_embed)


@bot.command(name="id",pass_context=True)
async def get_id(ctx):
    args = ctx.message.content.split(" ")
    idurl = "https://calculated.gg/api/player/{}".format(args[1])
    responseID = get_json(idurl)

    await bot.send_message(ctx.message.channel, "Your Calculated ID is " + responseID)


@bot.event
async def on_ready():
    print('READY')


if __name__ == '__main__':
    bot.run(TOKEN)
