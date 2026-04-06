# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# votes = {"yes": 0, "no": 0}

# class VoteConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.channel_layer.group_add("voting", self.channel_name)
#         await self.accept()

#         await self.send(text_data=json.dumps(votes))

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("voting", self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         if data["vote"] == "yes":
#             votes["yes"] += 1
#         else:
#             votes["no"] += 1

#         await self.channel_layer.group_send(
#             "voting",
#             {
#                 "type": "send_votes",
#                 "votes": votes
#             }
#         )

#     async def send_votes(self, event):
#         await self.send(text_data=json.dumps(event["votes"]))

import json
from channels.generic.websocket import AsyncWebsocketConsumer

votes = {"yes": 0, "no": 0}
users_online = 0   # 👥 Track users

class VoteConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        global users_online

        users_online += 1  # ➕ user joined

        await self.channel_layer.group_add("voting", self.channel_name)
        await self.accept()

        # 🔄 Send current data to ALL
        await self.channel_layer.group_send(
            "voting",
            {
                "type": "send_votes",
                "votes": votes,
                "users": users_online
            }
        )

    async def disconnect(self, close_code):
        global users_online

        users_online -= 1  # ➖ user left

        await self.channel_layer.group_discard("voting", self.channel_name)

        # 🔄 Update everyone
        await self.channel_layer.group_send(
            "voting",
            {
                "type": "send_votes",
                "votes": votes,
                "users": users_online
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["vote"] == "yes":
            votes["yes"] += 1
        else:
            votes["no"] += 1

        # 🔄 Send update to all users
        await self.channel_layer.group_send(
            "voting",
            {
                "type": "send_votes",
                "votes": votes,
                "users": users_online
            }
        )

    async def send_votes(self, event):
        await self.send(text_data=json.dumps({
            "yes": event["votes"]["yes"],
            "no": event["votes"]["no"],
            "users": event["users"]
        }))