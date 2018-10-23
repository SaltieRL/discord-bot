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


def get_user_id(user):
    url = "https://calculated.gg/api/player/{}".format(user)
    id = get_json(url)
    return id


def resolve_custom_url(url):
    # fetches the ID for the given username
    response_id = get_json("https://calculated.gg/api/player/{}".format(url))
    return response_id

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
# ping command
@bot.command(pass_context=True)
async def ping(ctx):
    await bot.send_message(ctx.message.channel, "Pong!")


# help command
@bot.command(name="help", aliases="h", pass_context=True)
async def get_help(ctx):
    args = ctx.message.content.lower().split(" ")

    # if the message only contains the !help, send the help_embed
    if len(args) == 1:
        help_embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        help_embed.set_footer(text="do \"!help <command name>\" for more information on a command.")
        help_embed.set_author(name="Help",
                              icon_url="https://media.discordapp.net/attachments/495315775423381518/499487940414537728/confirmation_verification-512.png")
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

        stats_help_embed.set_footer(
            text="Note: alle parameters can have mixed up upper-/lowercase letters, and the bot will still recognize it.")
        stats_help_embed.set_author(name="Stats",
                                    icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
        stats_help_embed.add_field(name="Descrition", value="Shows the stats for the given id.", inline=False)
        stats_help_embed.add_field(name="Parameters", value="!stats takes in the following parameters: `id`",
                                   inline=False)
        stats_help_embed.add_field(name="id accepts:", value="The Calculated.gg id of a user (can be found with !id)"
                                                             "\n The players username, more succesful if you use the id instead of the username.")

        await bot.send_message(ctx.message.channel, embed=stats_help_embed)
    elif args[1] == "stat":

        stats = get_json("https://calculated.gg/api/player/76561198055442516/play_style/all")['dataPoints']
        stats_list = [s['name'].replace(' ', '\_') for s in stats]
        stats_help_embed = discord.Embed(
            description="!stat <stat> <ids...>",
            colour=discord.Colour.blue()
        )
        for i, l in enumerate(chunks(stats_list, 25)):
            stats_help_embed.add_field(name='Stats ' + str(i + 1), value=", ".join(l))
        await bot.send_message(ctx.message.channel, embed=stats_help_embed)
    # if the arguments does not match any embed, send an error message
    else:
        await bot.send_message(ctx.message.channel,
                               "Command does not seem to exist, or the command does not have any additional information. Please try again.")


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


def get_player_profile(id):
    response_profile = get_json("https://calculated.gg/api/player/{}/profile".format(id))

    avatar_link = response_profile["avatarLink"]
    avatar_name = response_profile["name"]
    platform = response_profile["platform"]
    past_names = response_profile["pastNames"]

    return avatar_link, avatar_name, platform, past_names


# stats command
@bot.command(name="profile", aliases="p", pass_context=True)
async def get_profile(ctx):
    args = ctx.message.content.split(" ")
    id = resolve_custom_url(args[1])

    # fetches the stats for the ID
    response_stats = get_json("https://calculated.gg/api/player/{}/profile_stats".format(id))

    car_name = response_stats["car"]["carName"]
    car_percentage = str(round(response_stats["car"]["carPercentage"] * 100, 1)) + "%"
    avatar_link, avatar_name, platform, past_names = get_player_profile(id)

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


@bot.command(name="ranks", aliases="rank", pass_context=True)
async def get_rank(ctx):
    args = ctx.message.content.split(" ")
    id = resolve_custom_url(args[1])

    avatar_link, avatar_name, platform, past_names = get_player_profile(id)

    ranks = get_json("https://calculated.gg/api/player/{}/ranks".format(id))
    stats_embed = discord.Embed(
        color=discord.Color.blue()
    )

    stats_embed.set_author(name=avatar_name, url="https://calculated.gg/players/{}/overview".format(id),
                           icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
    stats_embed.set_thumbnail(url=avatar_link)
    order = ['duel', 'doubles', 'solo', 'standard', 'hoops', 'rumble', 'dropshot', 'snowday']
    for playlist in order:
        stats_embed.add_field(name=playlist.title(), value=ranks[playlist]['name'])

    await bot.send_message(ctx.message.channel, embed=stats_embed)


@bot.command(name="stat", aliases="s", pass_context=True)
async def get_stat(ctx):
    args = ctx.message.content.split(" ")
    if len(args) < 3:
        await bot.send_message(ctx.message.channel, 'Not enough arguments!')
        return
    stat = args[1].replace('_', ' ')
    ids_maybe = args[2:]
    if len(ids_maybe) == 1:
        id = resolve_custom_url(ids_maybe[0])
        stats = get_json("https://calculated.gg/api/player/{}/play_style/all".format(id))['dataPoints']
        matches = [s for s in stats if s['name'] == stat]
        if len(matches) == 0:
            await bot.send_message(ctx.message.channel, "Could not find stat: {}".format(stat))
            return

        await bot.send_message(ctx.message.channel, str(matches[0]['average']))
    else:
        stats_embed = discord.Embed(
            color=discord.Color.blue()
        )
        stats_embed.set_author(name=stat,
                               icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
        for name in ids_maybe:
            id = resolve_custom_url(name)
            stats = get_json("https://calculated.gg/api/player/{}/play_style/all".format(id))['dataPoints']
            matches = [s for s in stats if s['name'] == stat]
            if len(matches) == 0:
                await bot.send_message(ctx.message.channel, "Could not find stat: {}".format(stat))
                return
            stats_embed.add_field(name=name, value=matches[0]['average'])
        await bot.send_message(ctx.message.channel, embed=stats_embed)


@bot.command(name="replays", pass_context=True)
async def get_replays(ctx):
    args = ctx.message.content.split(" ")
    if len(args) < 3:
        await bot.send_message(ctx.message.channel, "Not enough arguments!")
        return

    replays_count = args[1]
    user = get_user_id(args[2])
    url = "https://calculated.gg/api/player/{}/match_history?page=0&limit={}".format(user, replays_count)
    user_name = get_player_profile(user)[1]


    replays = {}
    response_replays = get_json(url)
    user_replay_count = response_replays["totalCount"]
    all_replay_info = response_replays["replays"]

    replay_name = 1
    for replay in all_replay_info:
        replays[str(replay_name)] = [replay["id"], replay["date"]]
        replay_name += 1


    replays_embed = discord.Embed(
        title="Replays",
        color=discord.Color.blue()
    )

    footer = user_name + " has " + str(user_replay_count) + " replays."
    replays_embed.set_footer(text=footer)

    for x in replays_count:
        replays_embed.add_field(name="ID: " + str(replays[x]), value="Date of replay: " + str(replays[x]))

    await bot.send_message(ctx.message.channel, embed=replays_embed)



# id command
@bot.command(name="id", pass_context=True)
async def get_id(ctx):
    args = ctx.message.content.split(" ")
    user_id = get_user_id(args[1])

    await bot.send_message(ctx.message.channel, "Your id is: " + user_id)


# when bot user is ready, prints "READY"
@bot.event
async def on_ready():
    print('READY')


if __name__ == '__main__':
    bot.run(TOKEN)
