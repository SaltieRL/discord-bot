from connectors.irc_connector import IrcConnector
from commands.default_commands import *
from processors.default_processors import *

# Example of launching discord bot
connector = IrcConnector()
connector.nickname = "RLRankTracker"
connector.server = "irc.freenode.net"
connector.channel_list.append("#davc")
connector.channel_list.append("##rocketleague")

commands = {
    "help": HelpCommand(connector),
    "queue": QueueCommand(connector),
    "fullqueue": FullQueueCommand(connector),
    "profile": ProfileCommand(connector),
    "ranks": RanksCommand(connector)
}
precommand_processors = {
    ProfanityCheckProcessor(connector)
}

connector.precommand_processors = precommand_processors
connector.commands = commands
connector.connector_run()
