from connectors.discord_connector import DiscordConnector
from commands.default_commands import *

# Example of launching discord bot
connector = DiscordConnector()

commands = {
    "help": HelpCommand(connector),
    "queue": QueueCommand(connector),
    "fullqueue": FullQueueCommand(connector),
    "profile": ProfileCommand(connector),
    "ranks": RanksCommand(connector)
}

connector.commands = commands
connector.token = "YOUR DISCORD TOKEN"
connector.connector_run()
