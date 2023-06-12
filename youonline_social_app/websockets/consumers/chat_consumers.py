


from datetime import datetime
from channels.consumer import SyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import redis
from chat_app.models import Chat, ChatParticipant
from youonline_social_app.models import FriendsList
import json

from django.db.models import Q
from youonline_social_app.serializers.users_serializers import GetUserProfileSerializer


class UserAllChatsConsumer(SyncConsumer):
    def __init__(self):
        self.user_ws_name_base = 'user-chat-'
        self.user_ws_name = self.user_ws_name_base
        self.redis_status_ = 'online_users'
        self.redis_instance = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0
        )

    def notify_to_friends_online(self, status=True):
        all_friends = FriendsList.objects.filter(
            profile__id=self.user.profile_user.id,
            friends__id__in=self.online_users_list()
        ).values_list('friends__id' , flat=True)


        for frnd in all_friends:
            async_to_sync(self.channel_layer.group_send)(
                f'{self.user_ws_name_base}{frnd}',
                {
                    'type' : 'chat.message',
                    'message' : {
                        'type' : 'NEW_USER_ONLINE' if status else 'USER_OFFLINE',
                        'user_id' : str(frnd),
                    }
                }
            )
    
    def get_online_users_redis(self):
        return self.redis_instance.get(self.redis_status_)

    
    def add_online_user(self, user_id):
        self.online_users = self.get_online_users_redis()
        if self.online_users is not None:
            self.online_users = json.loads(self.online_users)
        else :
            self.online_users = []
        self.online_users.append(user_id)
        self.online_users = json.dumps(list(set(self.online_users)))
        self.redis_instance.set(self.redis_status_, self.online_users)

    def remove_online_user(self, user_id):
        ou_list = self.get_online_users_redis()
        if ou_list is not None:
            ou_list = json.loads(ou_list)
            ou_list.remove(str(user_id))
            ou_list = json.dumps(list(set(ou_list)))
            self.redis_instance.set(self.redis_status_, ou_list)

    def online_users_list(self):
        ou_list = self.redis_instance.get(self.redis_status_)
        return json.loads(ou_list)

    def send_online_users(self):
        all_online_users = self.online_users_list()

        user_friends = FriendsList.objects.filter(
            profile__id=self.user.profile_user.id,
            friends__id__in=all_online_users
        ).values_list('friends__id' , flat=True)

        self.send_message({
            'type' : 'ONLINE_USERS_LIST',
            'online_users' : [str(i) for i in user_friends],
            'status' : 200
        })





    def websocket_connect(self, event):
        self.user = self.scope['user']
        self.params = self.scope['url_route']['kwargs']

        if self.user.is_authenticated and str(self.user.profile_user.id) == self.params['user_id']:   
            self.user_ws_name += self.params['user_id']
            self.add_to_chat_group()
            self.send({
                'type' : 'websocket.accept'
            })
            self.add_online_user(str(self.user.profile_user.id))
            self.send_message({
                'message' : {
                    'status' : True,
                    'message' : 'Connected!',
                    'status_code' : 200
                }
            })
            self.send_online_users()
            self.notify_to_friends_online()

    def add_to_chat_group(self):
        async_to_sync(self.channel_layer.group_add)(
            self.user_ws_name,
            self.channel_name
        )

    def send_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.user_ws_name,
            {
                'type' : 'chat.user.ws.message',
                'message' : message
            }
        )

    def chat_user_ws_message(self, event):
        self.send(
            {
                'type' : 'websocket.send',
                'text' : json.dumps(event['message'])
            }
        )

    def chat_message(self, event):
        self.send(
            {
                'type' : 'websocket.send',
                'text' : json.dumps(event['message'])
            }
        )

    def user_chat(self, event):
        self.send(
            {
                'type' : 'websocket.send',
                'text' : json.dumps(event['message'])
            }
        )

    def close_websocket(self):
        raise Exception

    def websocket_receive(self, event):
        message = event['text']
        message = json.loads(message)
        try:
            action = message.get('action', None)
        except:
            action = None
        if action is not None:
            action_types = {
                'disconnect' : self.close_websocket
            }
            if action_types.get(action, None) is not None:
                action_types[action]()
            

    def websocket_disconnect(self, event):
        try:
            self.remove_online_user(self.user.profile_user.id)

            user = self.user.profile_user
            user.last_seen = datetime.now()
            user.save()
        except:
            pass
        try:
            self.send_online_users()
        except:
            pass
        try:
            self.notify_to_friends_online(status=False)
        except:
            pass
        raise StopConsumer()





class ChatRoomConsumer(SyncConsumer):

    def __init__(self):
        self.room_name = 'chat-room-'
        # chat-room-68338d34-cd80-4adc-a8c6-bc5cc0ab8f41

        
    def websocket_connect(self, event):
        self.params = self.scope['url_route']['kwargs']
        self.user = self.scope['user']
        self.chat = None
        pro_id = self.params['pro_id']
        self.chat_participants = None

        if self.user.is_authenticated:
            # try:
                chat = ChatParticipant.objects.filter(created_by=self.user.id)
                self.room_name += str(self.user.id)
                self.chat = chat
            # except Chat.DoesNotExist:
            #     chat = None
            # except:
            #     pass
            # if chat is not None:
                # try:
                #     self.chat_participants = ChatParticipant.objects.filter(created_by=self.user)
                # except:
                #     pass
                async_to_sync(self.channel_layer.group_add)(
                    self.room_name,
                    self.channel_name
                )
                self.send({
                    'type' : 'websocket.accept',
                })
                self.send_room_message({
                    'status' : True,
                    'message' : {
                        'type' : 'CONNECTION',
                        'text' : f'{self.user.username} join this chat right now',
                        'user' : GetUserProfileSerializer(self.user.profile_user).data,

                    },
                    'status_code' : 200
                })


    def add_to_room(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

    def send_room_message(self, message):

        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type' : 'chat.message',
                'message' : message
            }
        )
    
    def send_user_chats_ws_messages(self, user={}, message={}, chat={}):
        channel_layer_name = f"user-chat-{user.profile_user.id}"
        channel_ws_layer = get_channel_layer()
        async_to_sync(channel_ws_layer.group_send)(
            channel_layer_name,
            {
                'type' : 'chat.message',
                'message' : message
            }
        )

    
    def chat_message(self, event):
        
        self.send({
            'type' : 'websocket.send',
            'text' : json.dumps(event['message'])
        })

    
    def websocket_receive(self, event):
        message = event['text']
        message = json.loads(message)
        self.send_room_message(message)
        self.send_user_chats_ws_messages(user=self.user, message=message )

    def websocket_disconnect(self, event):
        raise StopConsumer()


class UserChatConsumer(SyncConsumer):

    def __init__(self):
        self.room_name = 'user-socket-'
        # chat-room-68338d34-cd80-4adc-a8c6-bc5cc0ab8f41

        
    def websocket_connect(self, event):
        self.params = self.scope['url_route']['kwargs']
        print(self.params)
        # self.user = self.scope['user']

        self.room_name += str(self.params['user_id'])
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.send({
            'type' : 'websocket.accept',
        })
        self.send_room_message({
            'status' : True,
            'message' : {
                'type' : 'CONNECTION',
                'text' : f'connected',
            },
            'status_code' : 200
        })


    def add_to_room(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

    def send_room_message(self, message):
        receiver_id = message.get('receiver' , None)
        if receiver_id is not None:
            receiver_address = f'user-socket-{receiver_id}'
            del message['receiver']
        else:
            receiver_address = self.room_name


        async_to_sync(self.channel_layer.group_send)(
            receiver_address,
            {
                'type' : 'chat.message',
                'message' : message
            }
        )
    
    
    def chat_message(self, event):

        self.send({
            'type' : 'websocket.send',
            'text' : json.dumps(event['message'])
        })

    
    def websocket_receive(self, event):
        message = event['text']
        message = json.loads(message)
        self.send_room_message(message)

    def websocket_disconnect(self, event):
        raise StopConsumer()