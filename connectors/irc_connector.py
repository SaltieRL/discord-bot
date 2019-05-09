###########################################
#
#  IRC Connector
#
#  Will implement connectors and override
#  methods to create an abstraction layer
#  uses Pydle
#
#  -Skyl3r
#
###########################################

from discord import Embed
from classes.connector import Connector
from pydle import Client


class IrcConnector(Connector, Client):
    nickname = ""
    channel_list = []
    password = ""
    server = ""
    port = 6667
    tls = False
    tls_verify = False

    def __init__(self):
        pass

    async def on_connect(self):
        await super().on_connect()
        for channel in self.channel_list:
            print("Joining: " + channel)
            await self.join(channel)

    def connector_run(self):
        Client.__init__(self, self.nickname)
        self.run(self.server, self.tls, self.tls_verify)

    async def send_message(self, message):
        message.message_embed: Embed

        say = []
        for field in message.message_embed.fields:
            if field.name != "":
                say.append(field.name + " - " + field.value)
            else:
                say.append(field.value)

        await self.message(message.target, " | ".join(say).replace("\n", ", "))

    async def on_message(self, channel, sender, message):
        if sender != self.nickname:
            await self.received_message(sender, channel, message)

    def privmsg(self, user, channel, message):
        self.received_message(user, channel, message)
