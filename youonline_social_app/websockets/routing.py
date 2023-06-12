

from django.urls import path
from .consumers import notification_consumers, chat_consumers

websocket_urlpatterns = [
    path('ws/notification/<str:user_id>/' , notification_consumers.NotificationConsumer.as_asgi() ),
    path('ws/chat-room/<str:pro_id>/', chat_consumers.ChatRoomConsumer.as_asgi()),
    path('ws/chats/<str:user_id>/', chat_consumers.UserAllChatsConsumer.as_asgi()),
    path('ws/user-socket/<str:user_id>/', chat_consumers.UserChatConsumer.as_asgi()),
]