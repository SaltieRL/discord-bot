import hashlib

from explanations_list import explanations

import datetime
import json
import sys

from discord.errors import Forbidden
from discord import Game, ChannelType
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
    try:
        return requests.get(url).json()
    except json.decoder.JSONDecodeError as e:
        print("Error decoding JSON for url:", url)
        raise e


def get_user_id(user):
    url = "https://calculated.gg/api/player/{}".format(user)
    id = get_json(url)
    return id


def get_player_profile(id):
    response_profile = get_json("https://calculated.gg/api/player/{}/profile".format(id))

    avatar_link = response_profile["avatarLink"]
    avatar_name = response_profile["name"]
    platform = response_profile["platform"]
    past_names = response_profile["pastNames"]

    return avatar_link, avatar_name, platform, past_names


def resolve_custom_url(url):
    # fetches the ID for the given username
    response_id = get_json("https://calculated.gg/api/player/{}".format(url))
    if str(type(response_id)) == "<class 'dict'>":
        response_id = "User not found"
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
    await bot.send_typing(ctx.message.channel)
    args = ctx.message.content.lower().split(" ")
    final_embed = 1
    if ctx.message.channel.type != ChannelType.private and ctx.message.channel.type != ChannelType.group:
        await bot.send_message(ctx.message.channel, "Check your PMs!")
    # if the message only contains the !help, send the help_embed
    if len(args) == 1:
        help_embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        help_embed.set_footer(text=f"do \"{BOT_PREFIX}help <command name>\" for more information on a command.")
        help_embed.set_author(name="Help",
                              icon_url="https://media.discordapp.net/attachments/495315775423381518/499487940414537728/confirmation_verification-512.png")
        help_embed.add_field(name=f"{BOT_PREFIX}help", value="Shows this message", inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}queue", value="Shows the current amount of replays in the queue.",
                             inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}profile <id>", value="Shows the profile for the given id.",
                             inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}id <username>", value="Gives the Calulated.gg id for the username.",
                             inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}stat <stat> <id1> <id2> ...",
                             value="Shows the id's value for the given stat. Can cmpare stats if multiple ids included",
                             inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}replays <id> <amount>",
                             value="Sends link to the latest amount of replays for the given id.", inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}explain <stat>", value="Gives an explanation for the the given stat",
                             inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}ranks <id>", value="Shows the ranks for the given id", inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}upload (optional -q)", value="Uploads attached replay", inline=False)
        help_embed.add_field(name=f"{BOT_PREFIX}status <replay_id>", value="Returns the status of an uploaded replay",
                             inline=False)

        final_embed = help_embed

    # otherwise if the first argument is "profile", send the stats_help_embed
    elif args[1] == "profile":

        profile_help_embed = discord.Embed(
            description="{BOT_PREFIX}profile <id>",
            colour=discord.Colour.blue()
        )

        profile_help_embed.set_footer(
            text="Note: alle parameters can have mixed up upper-/lowercase letters, and the bot will still recognize it.")
        profile_help_embed.set_author(name="Profile",
                                    icon_url="https://cdn.discordapp.com/attachments/495315775423381518/504677577722691598/person_1058425.png")
        profile_help_embed.add_field(name="Description", value="Shows the profile for the given id.", inline=False)
        profile_help_embed.add_field(name="Arguments", value="{BOT_PREFIX}profile takes in the following parameters: `id`",
                                   inline=False)
        profile_help_embed.add_field(name="id accepts:", value="The Calculated.gg id of a user (can be found with {BOT_PREFIX}id)"
                                                             "\n The players username, more succesful if you use the id instead of the username.")
        final_embed = profile_help_embed


    # if first argument is stat send stats_help_embed
    elif args[1] == "stat":

        stats = get_json("https://calculated.gg/api/player/76561198055442516/play_style/all")['dataPoints']
        stats_list = [s['name'].replace(' ', '\_') for s in stats]
        stats_help_embed = discord.Embed(
            description=f"{BOT_PREFIX}stat <stat> <id1> <id2> ...",
            colour=discord.Colour.blue()
        )

        stats_help_embed.set_author(name="Stat",
                                    icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
        stats_help_embed.add_field(name="Description",
                                   value="Shows the id's value for the given stat. Can cmpare stats if multiple ids included",
                                   inline=False)
        stats_help_embed.add_field(name="Arguments",
                                   value=f"{BOT_PREFIX}stat takes the following arguments: `stat` and `id`",
                                   inline=False)
        stats_help_embed.add_field(name="id accepts:", value=f"A Calculated.gg ID, can be found with {BOT_PREFIX}id",
                                   inline=False)

        for i, l in enumerate(chunks(stats_list, 25)):
            stats_help_embed.add_field(name='Stats ' + str(i + 1), value=", ".join(l))

        final_embed = stats_help_embed

    # if first argument is replays send replays_help_embed
    elif args[1] == "replays":
        replays_help_embed = discord.Embed(
            description=f"{BOT_PREFIX}replays <id> <amount>",
            colour=discord.Colour.blue()
        )
        replays_help_embed.set_author(name="Replays",
                                      icon_url="https://cdn.discordapp.com/attachments/495315775423381518/504675168640172032/495386-200.png")
        replays_help_embed.add_field(name="Description",
                                     value="Sends link to the latest amount of replays for the given id.", inline=False)
        replays_help_embed.add_field(name="Arguments",
                                     value=f"{BOT_PREFIX}replays takes the following arguments: `id` and `amount`",
                                     inline=False)
        replays_help_embed.add_field(name="id accepts: ",
                                     value=f"The Calculated.gg id of a user (can be found with {BOT_PREFIX}id)",
                                     inline=False)
        replays_help_embed.add_field(name="amount accepts: ",
                                     value="an integer between 1 and 10. If no amount is given, bot will give 5 replays",
                                     inline=False)

        final_embed = replays_help_embed

    # if first argument is explain send explain_help_embed
    elif args[1] == "explain":
        accepts = ""
        for stat in explanations:
            accepts = accepts + stat + ", "

        explain_help_embed = discord.Embed(
            description=f"{BOT_PREFIX}explain <stat>",
            color=discord.Color.blue()
        )
        explain_help_embed.set_author(name="Explain",
                                      icon_url="https://media.discordapp.net/attachments/495315775423381518/499487940414537728/confirmation_verification-512.png")
        explain_help_embed.add_field(name="Description", value="Gives an explanation for the the given stat",
                                     inline=False)
        explain_help_embed.add_field(name="Arguments",
                                     value=f"{BOT_PREFIX}explain takes the following arguments: `stat`",
                                     inline=False)
        explain_help_embed.add_field(name="stat accepts", value=accepts)

        final_embed = explain_help_embed

    elif args[1] == "ranks":
        ranks_help_embed = discord.Embed(
            description="{BOT_PREFIX}ranks <id>",
            color=discord.Color.blue()
        )
        ranks_help_embed.set_author(name="Ranks")
        ranks_help_embed.add_field(name="Description", value="Shows the ranks for the given id.", inline=False)
        ranks_help_embed.add_field(name="Arguments", value="{BOT_PREFIX}ranks takes the following arguments: `id`", inline=False)
        ranks_help_embed.add_field(name="id accepts", value="A Calculated.gg ID. Can be found with {BOT_PREFIX}id")

        final_embed = ranks_help_embed

    elif args[1] == "upload":
        upload_help_embed = discord.Embed(
            description="{BOT_PREFIX}upload (optional -q)",
            color=discord.Color.blue()
        )
        upload_help_embed.set_author(name="upload")
        upload_help_embed.add_field(name="Description", value="Uploads the attached replay to calculated.gg", inline=False)
        upload_help_embed.add_field(name="Arguments", value="{BOT_PREFIX}upload takes the followig optional argument: `-q`", inline=False)
        upload_help_embed.add_field(name="-q", value="Stops the bot from replying to the upload command if it uploads correctly")

        final_embed = upload_help_embed

    elif args[1] == "status":
        status_help_embed = discord.Embed(
            description="{BOT_PREFIX}status <replay_id>",
            color=discord.Color.blue()
        )
        status_help_embed.set_author(name="status")
        status_help_embed.add_field(name="Description", value="Returns the status of uploaded replay", inline=False)
        status_help_embed.add_field(name="Arguments", value="{BOT_PREFIX}status takes the followig optional argument: `<replay_id>`", inline=False)
        status_help_embed.add_field(name="<replay_id>", value="Given to the user after uploading a replay using the bot")

        final_embed = status_help_embed

    if final_embed == 1:
        await bot.send_message(ctx.message.channel, "Command does not seem to exist, or the command does not have any additional information. Please try again.")
    else:
        try:
            await bot.send_message(ctx.message.author, embed=final_embed)
        except Forbidden:
            await bot.send_message(ctx.message.channel, embed=final_embed)

# queue command
@bot.command(name="queue", aliases="q", pass_context=True)
async def display_queue(ctx):
    await bot.send_typing(ctx.message.channel)
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


# profile command
@bot.command(name="profile", aliases="p", pass_context=True)
async def get_profile(ctx):
    await bot.send_typing(ctx.message.channel)
    args = ctx.message.content.split(" ")

    if len(args) < 2:
        await bot.send_message(ctx.message.channel,
                               f"Not enough arguments! The proper form of this command is: `{BOT_PREFIX}profile <id>`")
        return
    elif len(args) > 2:
        await bot.send_message(ctx.message.channel,
                               f"Too many arguments! The proper form of this command is: `{BOT_PREFIX}profile <id>`")
        return

    id = resolve_custom_url(args[1])
    # fetches the profile for the ID. if user can not be found, tell the user so.
    response_stats = get_json("https://calculated.gg/api/player/{}/profile_stats".format(id))

    car_name = response_stats["car"]["carName"]
    car_percentage = str(round(response_stats["car"]["carPercentage"] * 100, 1)) + "%"
    try:
        avatar_link, avatar_name, platform, past_names = get_player_profile(id)
    except KeyError:
        await bot.send_message(ctx.message.channel, "User could not be found, please try again.")
        return

    list_past_names = ""
    for name in past_names:
        list_past_names = list_past_names + name + "\n"

    # creates stats_embed
    stats_embed = discord.Embed(
        color=discord.Color.blue()
    )

    stats_embed.set_author(name=avatar_name, url="https://calculated.gg/players/{}/overview".format(id),
                           icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
    stats_embed.set_thumbnail(url=avatar_link)
    stats_embed.add_field(name="Favourite car", value=car_name + " (" + car_percentage + ")")
    stats_embed.add_field(name="Past names", value=list_past_names)

    # send message
    await bot.send_message(ctx.message.channel, embed=stats_embed)


# ranks command
@bot.command(name="ranks", aliases="rank", pass_context=True)
async def get_rank(ctx):
    await bot.send_typing(ctx.message.channel)
    args = ctx.message.content.split(" ")

    if len(args) < 2:
        await bot.send_message(ctx.message.channel,
                               f"Not enough arguments! The proper form of this command is: `{BOT_PREFIX}ranks <id>`")
        return
    elif len(args) > 2:
        await bot.send_message(ctx.message.channel,
                               f"Too many arguments! The proper form of this command is: `{BOT_PREFIX}ranks <id>`")
        return

    id = resolve_custom_url(args[1])

    try:
        avatar_link, avatar_name, platform, past_names = get_player_profile(id)
    except KeyError:
        await bot.send_message(ctx.message.channel, "User could not be found, please try again.")
        return

    # get user's ranks
    ranks = get_json("https://calculated.gg/api/player/{}/ranks".format(id))

    # create embed
    stats_embed = discord.Embed(
        color=discord.Color.blue()
    )

    stats_embed.set_author(name=avatar_name, url="https://calculated.gg/players/{}/overview".format(id),
                           icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
    stats_embed.set_thumbnail(url=avatar_link)
    order = ['duel', 'doubles', 'solo', 'standard', 'hoops', 'rumble', 'dropshot', 'snowday']
    for playlist in order:
        stats_embed.add_field(name=playlist.title(), value=ranks[playlist]['name'] + " - " + str(ranks[playlist]['rating']))

    # send embed
    await bot.send_message(ctx.message.channel, embed=stats_embed)


# stat command
@bot.command(name="stat", aliases=["s", "stats"], pass_context=True)
async def get_stat(ctx):
    await bot.send_typing(ctx.message.channel)
    args = ctx.message.content.split(" ")
    # responds if not enough arguments
    if len(args) < 3:
        await bot.send_message(ctx.message.channel,
                               f'Not enough arguments! The proper form of this command is: `{BOT_PREFIX}stat <stat> <id1> <id2> ...`')
        return

    stat = args[1].replace('_', ' ')
    ids_maybe = [i.replace('_', ' ') for i in args[2:]]
    # if only one id is given
    if len(ids_maybe) == 1:
        id = resolve_custom_url(ids_maybe[0])
        url = "https://calculated.gg/api/player/{}/play_style/all".format(id)
        if len(id) == 11 and id[0] == 'b' and id[-1] == 'b':
            url += "?playlist=8"
        stats = get_json(url)['dataPoints']
        matches = [s for s in stats if s['name'] == stat]
        # if stat does not match tell user so
        if len(matches) == 0:
            await bot.send_message(ctx.message.channel, "Could not find stat: {}".format(stat))
            return

        await bot.send_message(ctx.message.channel, str(matches[0]['average']))
    # else if more ids are given
    else:
        # create embed
        stats_embed = discord.Embed(
            color=discord.Color.blue()
        )
        stats_embed.set_author(name=stat,
                               icon_url="https://media.discordapp.net/attachments/495315775423381518/499488781536067595/bar_graph-512.png")
        # sets footer of embed to the explanation of the stat
        if args[1] in explanations:
            stats_embed.set_footer(text=explanations[args[1]][0])

        # fields with the usernames as names and their stats as values
        for name in ids_maybe:
            id = resolve_custom_url(name)
            name = get_player_profile(id)[1]
            url = "https://calculated.gg/api/player/{}/play_style/all".format(id)
            if len(id) == 11 and id[0] == 'b' and id[-1] == 'b':
                url += "?playlist=8"
            stats = get_json(url)['dataPoints']
            matches = [s for s in stats if s['name'] == stat]
            if len(matches) == 0:
                await bot.send_message(ctx.message.channel, "Could not find stat: {}".format(stat))
                return
            stats_embed.add_field(name=name, value=matches[0]['average'], inline=False)

        # send embed
        await bot.send_message(ctx.message.channel, embed=stats_embed)


# replays command
@bot.command(name="replays", pass_context=True)
async def get_replays(ctx):
    await bot.send_typing(ctx.message.channel)
    args = ctx.message.content.split(" ")
    set_replay_count = True
    state = False
    # if there are too many arguments. tell the user so
    if len(args) > 3:
        await bot.send_message(ctx.message.channel,
                               f"Too many arguments! The proper form of this command is: `{BOT_PREFIX}replays <id> <amount>`")
        return
    elif len(args) < 2:
        await bot.send_message(ctx.message.channel,
                               f"Not enough arguments! The proper form of this command is: `{BOT_PREFIX}replays <id> <amount>`")
        return
    elif len(args) == 2:
        replays_count = 5
        set_replay_count = False

    # check if there is too many replays requested
    if set_replay_count:
        replays_count = int(args[2])
    if replays_count > 10:
        state = True
        real_count = replays_count
        replays_count = 9

    # get the user's information and replays
    user = get_user_id(args[1])
    url = "https://calculated.gg/api/player/{}/match_history?page=0&limit={}".format(user, replays_count)
    try:
        user_name = get_player_profile(user)[1]
    except KeyError:
        await bot.send_message(ctx.message.channel, "User could not be found, please try again.")
        return

    # devide the information of the replays
    response_replays = get_json(url)
    user_replay_count = response_replays["totalCount"]
    all_replay_info = response_replays["replays"]

    # create embed
    replays_embed = discord.Embed(
        title="Replays",
        color=discord.Color.blue()
    )

    footer = user_name + " has " + str(user_replay_count) + " replays."
    replays_embed.set_footer(text=footer)

    # add fields with replays to embed
    for replay in all_replay_info[:int(replays_count)]:
        date_str = replay['date']
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        date_str = date_obj.strftime("%A, %b %d, %Y %I:%M %p")

        blue_wins = replay['gameScore']['team0Score'] > replay['gameScore']['team1Score']
        blue_ids = [plr['id'] for plr in replay['players'] if plr['isOrange'] is False]
        on_blue = (user in blue_ids)
        win = not (blue_wins ^ on_blue)
        lines = [
            "Link: [{}]({})".format(replay['id'], "https://calculated.gg/replays/" + replay['id']),
            "Score: " + ("**{}**-{}" if on_blue else "{}-**{}**").format(replay['gameScore']['team0Score'],
                                                                         replay['gameScore']['team1Score'])
        ]
        msg = ""
        for line in lines:
            msg += line + "\n"

        replays_embed.add_field(
            value=msg,
            name="{} | {} | {}".format(replay['gameMode'], date_str, "Win" if win else "Loss"))
    # if there is more than 10 replays requested, add another field linking to the full replays page for the user
    if state:
        url = "https://calculated.gg/search/replays?page=0&limit={}&player_ids=".format(real_count)
        link = "Link: [{}]({})".format("Rest of replays", url + user)
        replays_embed.add_field(name="Rest of replays can be found here: ", value=link, inline=False)

    # send embed
    await bot.send_message(ctx.message.channel, embed=replays_embed)


# explain command
@bot.command(name="explain", aliases=["e", "ex", "expl"], pass_context=True)
async def get_explanation(ctx):
    await bot.send_typing(ctx.message.channel)
    args = ctx.message.content.split(" ")
    if len(args) < 2:
        await bot.send_message(ctx.message.channel,
                               f"Not enough arguments! The proper form of this command is: `{BOT_PREFIX}explain <stat>`")
        return
    if len(args) > 2:
        await bot.send_message(ctx.message.channel,
                               f"Too many arguments! The proper form of this command is: `{BOT_PREFIX}explain <stat>`")
        return

    # see if stat exists, if not tell user and end, if yes continue
    stat = args[1]
    try:
        response = explanations[stat]
    except KeyError:
        await bot.send_message(ctx.message.channel, "Stat does not seem to exist, please try again.")
        return

    explanation = response[0]

    # create embed
    explain_embed = discord.Embed(
        color=discord.Color.blue(),
        title=stat,
        description=explanation
    )

    # send embed
    await bot.send_message(ctx.message.channel, embed=explain_embed)


# id command
@bot.command(name="id", pass_context=True)
async def get_id(ctx):
    await bot.send_typing(ctx.message.channel)
    # fetch user id
    args = ctx.message.content.split(" ")

    if len(args) < 2:
        await bot.send_message(ctx.message.channel,
                               f"Not enough arguments! The proper form of this command is. `{BOT_PREFIX}id <username>`")
        return
    if len(args) > 2:
        await bot.send_message(ctx.message.channel,
                               f"Too many arguments! The proper form of this command is: `{BOT_PREFIX}id <username>`")
        return

    user_id = get_user_id(args[1])

    # send response
    try:
        await bot.send_message(ctx.message.channel, "Your id is: " + user_id)
    except TypeError:
        await bot.send_message(ctx.message.channel, "User could not be found, please try again.")
        return


# upload replay command
@bot.command(name="upload", aliases=["up"], pass_context=True)
async def upload_file(ctx):
    args = ctx.message.content.split(" ")
    if len(args) > 2:
        await bot.send_message(ctx.message.channel,
                               f"Too many arguments! The proper form of this command is: `{BOT_PREFIX}upload` and provide a file")
        return
    if len(args) > 1 and args[1] == '-q':
        silent = True
    else:
        silent = False

    attachment = ctx.message.attachments
    if len(attachment) > 0:
        replays = {}

        replay_url = attachment[0]['url']
        replay_name = attachment[0]['filename']
        replay_request = requests.get(replay_url, allow_redirects=True, stream=True)
        replay_file = replay_request.content

        replays['replays'] = (replay_name, replay_file)

        up_url = 'https://calculated.gg/api/upload'
        reply = requests.post(up_url, files=replays)
        if not list(reply.json()):
            message = 'No files uploaded, not a replay'
            await bot.send_message(ctx.message.channel, message)
            return

        if reply.status_code == 202:
            reply_id = list(reply.json())[0]
            payload = {'ids': reply_id}
            status = requests.get(up_url, params=payload)
            if list(status.json())[0] == 'FAILURE':
                message = 'No files uploaded: FAILURE'

            elif list(status.json())[0] in ['PENDING', 'STARTED', 'SUCCESS']:
                if not silent:
                    message = f'Replays have been queued for parsing. Check its status with \n`{BOT_PREFIX}status {reply_id}`'

            else:
                message = "Unknown status: " + list(status.json())[0]
        else:
            message = 'No files uploaded, error ' + reply.status_code

        await bot.send_message(ctx.message.channel, message)
    else:
        await bot.send_message(ctx.message.channel, 'Please provide a replay file as an attachment')
    return


# status replay command
@bot.command(name="status", aliases=["st"], pass_context=True)
async def status_replay(ctx):
    args = ctx.message.content.split(" ")
    if len(args) > 2:
        await bot.send_message(ctx.message.channel,
                               f"Too many arguments! The proper form of this command is: `{BOT_PREFIX}status <task_id>`")
        return

    up_url = 'https://calculated.gg/api/upload'
    replay_id = args[1]
    # 8-4-4-4-12
    if len(replay_id) == 8 + 4 + 4 + 4 + 12 + 1 * 4:
        split_id = replay_id.split('-')
        if len(split_id[0]) == 8 and len(split_id[1]) == 4 and len(split_id[2]) == 4 and len(split_id[3]) == 4 and len(
                split_id[4]) == 12:
            payload = {'ids': replay_id}
            status = requests.get(up_url, params=payload)
            if list(status.json())[0] == 'FAILURE':
                message = 'No files uploaded: FAILURE'
            elif list(status.json())[0] in ['PENDING', 'STARTED', 'SUCCESS']:
                message = f'Status: {list(status.json())[0]}'
            else:
                message = "Unknown status: " + list(status.json())[0]
        else:
            message = 'Invalid id'
    else:
        message = 'Invalid id'

    await bot.send_message(ctx.message.channel, message)
    return


# when bot user is ready, prints "READY", and set presence
@bot.event
async def on_ready():
    await bot.change_presence(game=Game(name=f"with a TI-84 ({BOT_PREFIX}help)"))
    print('READY')


if __name__ == '__main__':
    bot.run(TOKEN)
