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
    names = ['Internal', 'Priority', 'Public', 'Reparsing']
    for index, queue_priority in enumerate([0, 3, 6, 9]):
        msg = str(response["priority " + str(queue_priority)])
        embed.add_field(name=names[index], value=msg,
                        inline=True)

    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def stats(ctx):
    args = ctx.message.content.split(" ")

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

    if platform == "Steam":
        platform_url = "https://cdn.discordapp.com/attachments/317990830331658240/498493530402979842/latest.png"
    else:
        platform_url = ""
    stats_embed = discord.Embed(
        color=discord.Color.blue()
    )

    stats_embed.set_author(name=avatar_name, url="https://calculated.gg/players/{}/overview".format(id),
                           icon_url=platform_url)
    stats_embed.set_thumbnail(url=avatar_link)
    stats_embed.add_field(name="Favourite car", value=car_name + " (" + car_percentage + ")")
    stats_embed.add_field(name="Past names", value=list_past_names)

    await bot.send_message(ctx.message.channel, embed=stats_embed)


@bot.command(pass_context=True)
async def id(ctx):
    args = ctx.message.content.split(" ")
    idurl = "https://calculated.gg/api/player/{}".format(args[1])
    responseID = get_json(idurl)

    await bot.send_message(ctx.message.channel, "Your Calculated ID is " + responseID)


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
