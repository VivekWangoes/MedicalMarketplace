import json

from channels.generic.websocket import AsyncWebsocketConsumer


class VideoCallSignalConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(VideoCallSignalConsumer, self).__init__(*args, **kwargs)
    print("in consumer")
    # import pdb;pdb.set_trace()
    async def connect(self):
        """
        join user to a general group and accept the connection
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        print('Signal disconnect')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print('recieve channel called')
        recieve_dict = json.loads(text_data)

        message = recieve_dict['message']
        print('message ', message)
        action = recieve_dict['action']
        
        print('action ', action)
        
        print(action)
        # print(len(self.channel_layer.group.get('1', {}).items()))
        if (action == 'new-offer') or (action == 'new-answer'):
            print('new-answer, new-offer')
            reciever_channel_name = recieve_dict['message']['reciever_channel_name']
            recieve_dict['message']['reciever_channel_name'] = self.channel_name
            await self.channel_layer.send(
                reciever_channel_name,
                {
                    'type': 'send.sdp',
                    'recieve_dict': recieve_dict
                }
            )
            return
        print('new-peer')
        recieve_dict['message']['reciever_channel_name'] = self.channel_name
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send.sdp',
                'recieve_dict': recieve_dict
            }
        )

    async def send_sdp(self, event):
        print('send message function called')
        recieve_dict = event['recieve_dict']
        await self.send(text_data=json.dumps(recieve_dict))

