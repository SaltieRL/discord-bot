

from classes.processor import Processor
from classes.message import Message
from profanity_check import predict_prob

import random

# Profanity Check requires profanity-check
class ProfanityCheckProcessor(Processor):

    profanity_threshold = 0.35
    random_response_chance = 0.15

    async def action(self, channel, sender, message):
        quick_chats = ["OMG!", "Wow!", "Okay.", "Savage!", "Thanks!", "Holy cow!"]

        profanity = predict_prob([message])
        if profanity[0] > self.profanity_threshold and random.random() < self.random_response_chance:
            say = Message().set_target(channel)
            say.add_field(name="", value=random.choice(quick_chats))
            await self.connector.send_message(say)
