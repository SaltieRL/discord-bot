###########################################
# A standard message interface that
# each connector can decide how to use
#
# All messages will be discord embeds
# Please ONLY put useful data in fields
# that way text only platforms can retrieve
# a pleasant text only view
#
# -Skyl3r
############################################

import discord


class Message:
    message_embed = discord.Embed
    target = ""

    def __init__(self):
        self.message_embed = discord.Embed(
            color=discord.Color.blue()
        )

    def add_field(self, name, value):
        self.message_embed.add_field(name=name, value=value)
        return self

    def set_author(self, name, url="", icon_url=""):
        self.message_embed.set_author(name=name, url=url, icon_url=icon_url)
        return self

    def set_thumbnail(self, url):
        self.message_embed.set_thumbnail(url=url)
        return self

    def set_target(self, channel):
        self.target = channel
        return self
