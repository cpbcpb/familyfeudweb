from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json

class DisplayConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'familyfeud_base'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        display = text_data_json['display']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'display_message',
                'display': display
            }
        )

    async def display_message(self, event):
        display = event['display']

        await self.send(text_data=json.dumps({
            'display': display
        }))

class DisplayAnswerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'displayanswer_base'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        if action == 'revealAnswer': 
            question_id = text_data_json['question_id']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'display_answer',
                    'action': 'revealAnswer',
                    'question_id': question_id
                }
            )
        if action == 'addWrong':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'add_wrong',
                    'action': 'addWrong'
                }
            )
            
    async def display_answer(self, event):
        question_id = event['question_id']
        action = event['action']

        await self.send(text_data=json.dumps({
            'question_id': question_id,
            'action': action
        }))

    async def add_wrong(self, event):
        action = event['action']
        await self.send(text_data=json.dumps({
            'action': action
        }))
