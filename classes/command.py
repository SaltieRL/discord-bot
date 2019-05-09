##########################################
# Command class is a standard
# interface for commands.
# Each connector can decide how to handle
#
# -Skyl3r
##########################################

from classes.message import Message

class Command:

    helpMessage = ""
    icon = ""
    requiredArgs = 0
    connector = object

    def __init__(self, connector):
        self.connector = connector

    async def action(self, sender, channel, args):
        pass

    # An alias for self.connector.send_message...
    async def send_message(self, message: Message):
        await self.connector.send_message(message)
    pass
