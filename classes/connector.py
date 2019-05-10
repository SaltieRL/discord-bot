############################################
#
#  Connector class is an abstraction layer
#  To make connections from each platform
#  standardized.
#
#  -Skyl3r
#
############################################

from classes.message import Message

class Connector:

    # Discord seems to support the most commands
    # So all commands will be based on discord


    # each connector will implement commands as it can
    commands = {}

    # each connector can have precommand processing
    precommand_processors = {}

    prefix = "!"

    # Default bad command response
    bad_command_response = "Not a command. To see a list of commands, run " + prefix + "list - You can use " + prefix + "help on any command to get a description"

    wrong_arguments = "Invalid arguments. "

    def __init__(self):
        pass

    def connector_run(self):
        pass

    # Do whatever the connector requires to load commands
    def load_commands(self):
        pass

    # Send typing message to channel (EG: "User is typing" for discord)
    def typing(self, target):
        pass

    # Send message to channel
    async def send_message(self, message):
        pass

    async def received_message(self, sender, channel, message):
        for processor in self.precommand_processors:
            await processor.action(sender=sender, channel=channel, message=message)

        if message.startswith(self.prefix):
            # Get everything after the prefix and split by spaces to get command/arguments
            message_components = message[len(self.prefix):].split(" ")

            # Make sure we have supplied something besides prefix
            if len(message_components) == 0:
                say = Message().set_target(channel)
                say.add_field(name="", value=self.bad_command_response)
                await self.send_message(say)

                return

            # Get command and drop out of array
            command = message_components[0]
            del(message_components[0])

            # make sure command exists
            if command not in self.commands:
                say = Message().set_target(channel)
                say.add_field(name="", value=self.bad_command_response)
                await self.send_message(say)

                return

            # Make sure we have supplied the right amount of arguments
            if len(message_components) != self.commands[command].requiredArgs and self.commands[command].requiredArgs != -1:
                say = Message().set_target(channel)
                say.add_field(name="", value=self.wrong_arguments + " Command requires " + str(self.commands[command].requiredArgs) + " arguments. See " + self.prefix + "help " + command)
                await self.send_message(say)

                return

            # Everything is okay, so pass args into command
            await self.commands[command].action(sender, channel, message_components)
