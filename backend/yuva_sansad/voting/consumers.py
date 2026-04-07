import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

votes = {"yes": 0, "no": 0}
users_online = 0
time_left = 30
timer_running = False
voting_closed = False
final_result = ""


class VoteConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        global users_online, timer_running

        users_online += 1

        await self.channel_layer.group_add("voting", self.channel_name)
        await self.accept()

        # 🚀 start timer only once globally
        if not timer_running:
            timer_running = True
            asyncio.create_task(self.global_timer())

        # 🌍 send current live state to new user
        await self.send_state()

        # 👥 update everyone user count
        await self.send_state_to_all()

    async def disconnect(self, close_code):
        global users_online
        users_online -= 1
        await self.channel_layer.group_discard("voting", self.channel_name)

        await self.send_state_to_all()

    async def receive(self, text_data):
        global votes, voting_closed
        data = json.loads(text_data)

        # 🔒 stop votes after timer ends
        if voting_closed:
            return

        if data.get("vote") == "yes":
            votes["yes"] += 1
        elif data.get("vote") == "no":
            votes["no"] += 1

        await self.send_state_to_all()

    async def global_timer(self):
        global time_left, voting_closed, final_result

        while True:
            await asyncio.sleep(1)

            if voting_closed:
                continue

            time_left -= 1

            if time_left <= 0:
                time_left = 0
                voting_closed = True

                # 🏆 final result
                if votes["yes"] > votes["no"]:
                    final_result = "✅ PASSED"
                elif votes["no"] > votes["yes"]:
                    final_result = "❌ REJECTED"
                else:
                    final_result = "⚖️ TIE"

            await self.send_state_to_all()

    async def send_state(self):
        await self.send(text_data=json.dumps({
            "yes": votes["yes"],
            "no": votes["no"],
            "users": users_online,
            "time": time_left,
            "result": final_result
        }))

    async def send_state_to_all(self):
        await self.channel_layer.group_send(
            "voting",
            {
                "type": "broadcast_state"
            }
        )

    async def broadcast_state(self, event):
        await self.send_state()