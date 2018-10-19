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

# ping command
@bot.command(pass_context=True)
async def ping(ctx):
    await bot.send_message(ctx.message.channel, "Pong!")

#help command
@bot.command(name="help", aliases="h", pass_context=True)
async def get_help(ctx):
    args = ctx.message.content.lower().split(" ")

    # if the message only contains the !help, send the help_embed
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

    # otherwise if the first argument is "stats", send the stats_help_embed
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

    # if the arguments does not match any embed, send an error message
    else:
        await bot.send_message(ctx.message.channel, "Command does not seem to exist, or the command does not have any additional information. Please try again.")


# queue command
@bot.command(name="queue", aliases="q", pass_context=True)
async def display_queue(ctx):
    response = get_json("https://calculated.gg/api/global/queue/count")
    await bot.send_message(ctx.message.channel, str(response[2]["count"]) + ' replays in the queue.')


# fullqueue command
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

# stats command
@bot.command(name="stats", pass_context=True)
async def get_stats(ctx):
    args = ctx.message.content.split(" ")


    # fetches the ID for the given username
    response_id = get_json("https://calculated.gg/api/player/{}".format(args[1]))
    id = response_id

    # fetches the stats for the ID
    responseStats = get_json("https://calculated.gg/api/player/{}/profile_stats".format(id))

    response_id = get_json("https://calculated.gg/api/player/{}".format(args[1]))
    id = response_id

    response_stats = get_json("https://calculated.gg/api/player/{}/profile_stats".format(id))


    car_name = response_stats["car"]["carName"]
    car_percentage = str(round(response_stats["car"]["carPercentage"] * 100, 1)) + "%"

    response_profile = get_json("https://calculated.gg/api/player/{}/profile".format(id))

    avatar_link = response_profile["avatarLink"]
    avatar_name = response_profile["name"]
    platform = response_profile["platform"]
    past_names = response_profile["pastNames"]

    list_past_names = ""
    for x in past_names:
        list_past_names = list_past_names + x + "\n"


    # creates stats_embed

    if platform == "Steam":
        platform_url = "https://cdn.discordapp.com/attachments/317990830331658240/498493530402979842/latest.png"
    else:
        platform_url = ""

    stats_embed = discord.Embed(
        color=discord.Color.blue()
    )

    stats_embed.set_author(name=avatar_name, url="https://calculated.gg/players/{}/overview".format(id),
                           icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
    stats_embed.set_thumbnail(url=avatar_link)
    stats_embed.add_field(name="Favourite car", value=car_name + " (" + car_percentage + ")")
    stats_embed.add_field(name="Past names", value=list_past_names)

    await bot.send_message(ctx.message.channel, embed=stats_embed)


# id command
@bot.command(name="id",pass_context=True)
async def get_id(ctx):
    args = ctx.message.content.split(" ")
    idurl = "https://calculated.gg/api/player/{}".format(args[1])
    responseID = get_json(idurl)

    await bot.send_message(ctx.message.channel, "Your Calculated ID is " + responseID)


# when bot user is ready, prints "READY"
@bot.event
async def on_ready():
    print('READY')


if __name__ == '__main__':
    bot.run(TOKEN)
