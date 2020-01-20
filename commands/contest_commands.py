##################################################
#
#  This is for commands relating to weekly goal contests
#  It allows users to submit a link and vote on other
#  users' submissions
#
# -Skyl3r
#
###################################################


import datetime
from tinydb import TinyDB, Query
from classes.command import Command
from classes.message import Message


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


################################################
# Need to add in checking for a tie condition
################################################
class LastWinnerCommand(Command):
    requiredArgs = 0
    helpMessage = "Gets last weeks most voted submission"

    async def action(self, sender, channel, args):
        week_of_year = datetime.date.today().isocalendar()[1] - 1
        msg = Message().set_target(channel)

        shots = TinyDB("shots.json")
        votes = TinyDB("votes.json")
        vote_query = Query()
        shots_query = Query()

        submitted_shots = shots.search((shots_query.week == week_of_year))

        if len(submitted_shots) < 1:
            msg.add_field(name="",
                          value="No goals submitted last week")
            await self.send_message(msg)
            return

        for shot in submitted_shots:
            votes_for_shot = votes.search((vote_query.week == week_of_year) & (vote_query.vote == shot['username']))
            shot['votes'] = len(votes_for_shot)

        winner = sorted(submitted_shots, key=lambda x: x['votes'])

        msg.add_field(name="",
                      value="Last weeks winner was " + winner[0]['username'] + " (" + winner[0]['url'] + ")")
        await self.send_message(msg)
