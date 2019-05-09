##############################
#
# Processor is an action that
# can take place regardless of
# if a prefix was used.
#
# -Skyl3r
#
###############################


from classes.connector import Connector

class Processor:
    connector = object

    def __init__(self, connector: Connector):
        self.connector = connector

    async def action(self, sender, channel, message):
        pass