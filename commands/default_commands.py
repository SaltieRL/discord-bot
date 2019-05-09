##################################################
#
#  This is where default commands will be defined
#  It will be a dictionary that is supplied to
#  connector when initialized
#
# -Skyl3r
#
###################################################

import requests
from classes.command import Command
from classes.message import Message

##########################
# Helper Functions
##########################


def get_player_id(player_name):
    response_id = requests.get("https://calculated.gg/api/player/{}".format(player_name)).json()
    if str(type(response_id)) == "<class 'dict'>":
            response_id = "User not found"
    return response_id


def get_player_profile(player_id):
    response_profile = requests.get("https://calculated.gg/api/player/{}/profile".format(player_id)).json()

    avatar_link = response_profile["avatarLink"]
    avatar_name = response_profile["name"]
    platform = response_profile["platform"]
    past_names = response_profile["pastNames"]

    return avatar_link, avatar_name, platform, past_names


#########################
# Commands
#########################

# Help command, gets help message for given command
class HelpCommand(Command):
    # Requires one arg. The name of the command
    requiredArgs = 1

    # Simple message there...
    helpMessage = """do <prefix>help [command name] for more information on a command.
    To see all commands, try <prefix>listcommands"""

    async def action(self, sender, channel, args):
        if args[0] not in self.connector.commands:
            await self.send_message(Message().set_target(channel).add_field(name="Not a command", value=args[0]))

        message = Message().set_target(channel)
        message.set_author(name="Help", icon_url="https://i.imgur.com/LqUmKRh.png", url="")
        message.add_field(name=args[0], value=self.connector.commands[args[0]].helpMessage)

        await self.send_message(message)


class QueueCommand(Command):
    requiredArgs = 0
    helpMessage = "Shows current amount of replays in the queue."

    async def action(self, sender, channel, args):
        response = requests.get("https://calculated.gg/api/global/queue/count").json()

        message = Message().set_target(channel)
        message.add_field(name="Replays in Queue", value=str(response[2]["count"]))

        await self.send_message(message)


class FullQueueCommand(Command):
    requiredArgs = 0
    helpMessage = "Shows all replay queues"

    async def action(self, sender, channel, args):
        response = requests.get("https://calculated.gg/api/global/queue/count").json()

        message = Message().set_target(channel)
        message.set_author(name="All Replay Queues")
        for priority in response:
            message.add_field(name=str(priority["name"]), value=str(priority["count"]))

        await self.send_message(message)


class ProfileCommand(Command):
    requiredArgs = 1
    helpMessage = "Get profile information for player"

    async def action(self, sender, channel, args):
        player_id = get_player_id(args[0])
        response_stats = requests.get("https://calculated.gg/api/player/{}/profile_stats".format(player_id)).json()

        car_name = response_stats["car"]["carName"]
        car_percentage = str(round(response_stats["car"]["carPercentage"] * 100, 1)) + "%"

        try:
            avatar_link, avatar_name, platform, past_names = get_player_profile(player_id)
        except KeyError:
            await self.connector.send_message(sender, channel, "User could not be found, please try again")

        list_past_names = []
        for name in past_names:
            list_past_names.append(name)

        message = Message().set_target(channel)
        message.set_author(name="Profile Information")
        message.add_field(name="Favourite Car", value=car_name + " (" + car_percentage + ")")
        message.add_field(name="Past names", value="\n".join(list_past_names))

        await self.send_message(message)


class RanksCommand(Command):
    requiredArgs = 1
    helpMessage = "Get rank data for player"

    async def action(self, sender, channel, args):
        player_id = get_player_id(args[0])
        ranks = requests.get("https://calculated.gg/api/player/{}/ranks".format(player_id)).json()

        message = Message().set_target(channel)
        message.set_author(name="Ranks")

        order = ['duel', 'doubles', 'solo', 'standard', 'hoops', 'rumble', 'dropshot', 'snowday']
        for playlist in order:
            message.add_field(name=playlist.title(), value=ranks[playlist]['name'] + " - " + str(ranks[playlist]['rating']))

        await self.send_message(message)
