##################################################
#
#  This is where default commands will be defined
#  It will be a dictionary that is supplied to
#  connector when initialized
#
# -Skyl3r
#
###################################################
from typing import Dict, Any

import requests
from os.path import exists
import operator
import json
import datetime
from bs4 import BeautifulSoup
from classes.command import Command
from classes.message import Message
from tinydb import TinyDB, Query

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
    print(e)

#########################
# Commands
#########################


# Help command, gets help message for given command
class HelpCommand(Command):
    # Requires one arg. The name of the command
    requiredArgs = 1

    # Simple message there...
    helpMessage = """do <prefix>help [command name] for more information on a command. To see all commands, try <prefix>list"""

    async def action(self, sender, channel, args):
        self.helpMessage = self.helpMessage.replace("<prefix>", self.connector.prefix)

        if args[0] not in self.connector.commands:
            await self.send_message(Message().set_target(channel).add_field(name="Not a command", value=args[0]))

        message = Message().set_target(channel)
        message.set_author(name="Help", icon_url="https://i.imgur.com/LqUmKRh.png", url="")
        message.add_field(name=args[0], value=self.connector.commands[args[0]].helpMessage)
        message.add_field(name="Required Arguments", value=str(self.connector.commands[args[0]].requiredArgs))

        await self.send_message(message)


class ListCommand(Command):
    requiredArgs = 0

    helpMessage = "Lists available commands."

    command_list = []

    async def action(self, sender, channel, args):
        self.command_list.clear()

        for command_name, command in self.connector.commands.items():
            self.command_list.append(command_name)
        self.command_list.sort()

        say = Message().set_target(channel)
        say.add_field(name="Available Commands", value="\n".join(self.command_list))
        await self.send_message(say)


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


class ReplaysCommand(Command):
    requiredArgs = 2
    helpMessage = "Get replays for a play. (max of 10)"

    async def action(self, sender, channel, args):
        player_id = get_player_id(args[0])
        requested_replay_count = int(args[1])
        say = Message().set_target(channel)

        if not (0 < requested_replay_count <= 10):
            say.add_field(name="Error", value="Number of replays must be between 1 and 10")
            await self.send_message(say)
            return

        url = "https://calculated.gg/api/player/{}/match_history?page=0&limit={}".format(player_id, requested_replay_count)

        response = requests.get(url).json()

        user_replay_count = response["totalCount"]
        all_replay_info = response["replays"]

        for replay in all_replay_info[:int(user_replay_count)]:
            date_str = replay['date']
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            date_str = date_obj.strftime("%b %d %H:%M")

            blue_wins = replay['gameScore']['team0Score'] > replay['gameScore']['team1Score']
            blue_ids = [plr['id'] for plr in replay['players'] if plr['isOrange'] is False]
            on_blue = (args[0] in blue_ids)
            win = not (blue_wins ^ on_blue)
            lines = [
                # "Link: [{}]({})".format(replay['id'], "https://calculated.gg/replays/" + replay['id']),
                "Score: " + "{}-{}".format(replay['gameScore']['team0Score'], replay['gameScore']['team1Score'])
            ]
            msg = ""
            for line in lines:
                msg += line + "\n"

            say.add_field(
                name="{} ({})".format(replay['gameMode'], date_str),
                value="Win! " if win else "Loss! " + msg)

        await self.send_message(say)


class SubmitCommand(Command):
    requiredArgs = 1
    helpMessage = "Submits a goal for weekly voting"

    async def action(self, sender, channel, args):
        week_of_year = datetime.date.today().isocalendar()[1]

        shots = TinyDB('shots.json')
        shot_query = Query()
        test = shots.search((shot_query.username == sender) & (shot_query.week == week_of_year))
        if len(test) < 1:
            shots.insert({'url': args[0], 'username': sender, 'week': week_of_year})
        else:
            shots.update({'url': args[0]}, ((shot_query.username == sender) & (shot_query.week == week_of_year)))

        await self.send_message(Message().set_target(channel).add_field(name="", value="Submitted!"))


class EntriesCommand(Command):
    requiredArgs = 0
    helpMessage = "View weekly submissions to best shot contest"

    async def action(self, sender, channel, args):
        week_of_year = datetime.date.today().isocalendar()[1]

        messages = []

        shots = TinyDB('shots.json')
        votes = TinyDB('votes.json')

        shots_query = Query()
        vote_query = Query()
        current_shots = shots.search(shots_query.week == week_of_year)

        if len(current_shots) < 1:
            msg = Message().set_target(channel)
            msg.add_field(name="", value="No shots submitted this week")
            messages.append(msg)
        else:
            for shot in current_shots:
                user_votes = votes.search((vote_query.week == week_of_year) & (vote_query.vote == shot['username']))
                msg = Message().set_target(channel)
                msg.add_field(
                    name="",
                    value=(shot['username'] + ": " + shot['url'] + " - " + str(len(user_votes)) + " votes!"))
                messages.append(msg)

        for msg in messages:
            await self.send_message(msg)


class VoteCommand(Command):
    requiredArgs = 1
    helpMessage = "Submit a vote for a user's shot submission"

    async def action(self, sender, channel, args):
        week_of_year = datetime.date.today().isocalendar()[1]

        msg = Message().set_target(channel)

        shots = TinyDB("shots.json")
        votes = TinyDB("votes.json")
        vote_query = Query()
        shots_query = Query()

        shot = shots.search((shots_query.username == args[0]) & (shots_query.week == week_of_year))
        if len(shot) < 1:
            msg.add_field(name="", value="No submission for user " + args[0])
            await self.send_message(msg)
            return

        test = votes.search((vote_query.username == sender) & (vote_query.week == week_of_year))

        if len(test) < 1:
            votes.insert({'vote': args[0], 'username': sender, 'week': week_of_year})
        else:
            votes.update({'vote': args[0]}, ((vote_query.username == sender) & (vote_query.week == week_of_year)))

        total_votes = votes.search((vote_query.vote == args[0]) & (vote_query.week == week_of_year))

        msg.add_field(name="",
                      value="Vote submitted for " + args[0] + ". Total votes: " +
                            str(len(total_votes)) + ".  (" + shot[0]['url'] + ")")

        await self.send_message(msg)
