from channels.consumer import SyncConsumer, AsyncConsumer
import json
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync

from youonline_social_app.models import Profile
import json


class NotificationConsumer(SyncConsumer):

    def __init__(self):
        self.layer_base = 'Notification'
        self.notification_group_name = self.layer_base



    def websocket_connect(self , event):
        self.params = self.scope['url_route']['kwargs']
        self.user = self.scope['user']
        
        
        if self.user.is_authenticated and (self.params['user_id'] == str(self.user.profile_user.id)):
            self.notification_group_name += f"-{self.params['user_id']}"
            print(self.notification_group_name)
            self.add_to_group()
            self.send({
                'type' : 'websocket.accept'
            })
            self.send_group_message({
                'status' : True,
                'message' : 'Connected!',
                'status_code' : 200
            })
        else:
            self.send({
                'type' : 'websocket.accept'
            })

    def close_websocket_connection(self):
        raise Exception()


    def websocket_receive(self, event):
        content = event['text']
        content = json.loads(content)

        try:
            action = content.get('action')
        except:
            action = None
        if action is not None:
            action_types = {
                'disconnect' : self.close_websocket_connection
            }
            if action_types.get(action , None) is not None:
                action_types[action]()
    
    def add_to_group(self):
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name
            # 'Notification-user-id'
        )

    def send_group_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.notification_group_name,
                {
                    'type' : 'chat.message',
                    'message' : message
                }
        )
    

    def remove_from_group(self):
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name
        )
        


    def get_channel_data(self):
        data={
            'channel_layer' : f'{self.channel_layer}',
            'channel_name' : f'{self.channel_name}'
        }
        return json.dumps(data)



    def chat_message(self, event):
        self.send({
            'type' : 'websocket.send',
            "text" : json.dumps(event['message'])
        })

    def websocket_disconnect(self, event):
        self.remove_from_group()
        raise StopConsumer()

