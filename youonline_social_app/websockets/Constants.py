

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat_app.models import ChatParticipant, Chat
import random, string


def send_notifications_ws(instance): # Web socket Notifications
    channel_layer = get_channel_layer()

    for usr_prf in instance.notifiers_list.all().exclude(notifiers_list=instance.profile):
        total_count = ''.join(
        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
        
        grp_chnl_name = f'Notification-{str(usr_prf.id)}'
        async_to_sync(channel_layer.group_send)(
            grp_chnl_name,
            {
                'type' : 'chat.message',
                'message' : {
                    'id': str(instance.id),
                    'total_count': total_count,
                    'type' : str(instance.type),
                    'text' : f'{instance.text}',
                    # 'text' : f'{instance.profile.user.username}{instance.text}',
                    'receiver_profile' : str(usr_prf.id),
                    'created_at' : str(instance.created_at),
                    'profile' : str(instance.profile.id),
                }
            }
        )


def send_chat_message_ws(request, chat_message, profile, chat, receiver):
    channel_layars = get_channel_layer()
    
    all_participants = ChatParticipant.objects.filter(chat=chat['id'])

    chat_message['chat'] = chat

    message = {}
    message['chat_id'] = chat['id']
    message['text'] = chat_message['text']
    profile_obj = dict(chat_message['profile'])

    profile_obj['country'] = str(profile_obj['country'])
    profile_obj['state'] = str(profile_obj['state'])
    profile_obj['city'] = str(profile_obj['city'])
    message['profile'] = profile_obj
    message['receiver'] = receiver
    
    try:
        media = chat_message['media']
        output = []
        if media and len(media) > 0:
            for med in media:
                med['id'] = str(med['id'])
                output.append(med)
        chat_message['media'] = output
    except:
        pass

    try:
        for prt in all_participants:
            message['receiver'] = str(prt.profile.id)

            receiver_socket = f'user-socket-{str(prt.profile.id)}'
            async_to_sync(channel_layars.group_send)(
                receiver_socket,
                {
                    'type' : 'send.room.message',
                    'message' : message
                }
            )
            # chat-socket-68338d34-cd80-4adc-a8c6-bc5cc0ab8f41
    except Exception as err:
        print(err)

    
def delete_chat_message_ws(request, chat_message_id, profile, chat):
    channel_layars = get_channel_layer()
    all_participants = ChatParticipant.objects.filter(chat=chat)
    
    response = {
        'type' : 'DeleteChatMessage',
        'id' : str(chat_message_id)
    }

    try:
        for prt in all_participants:
            async_to_sync(channel_layars.group_send)(
                f'user-chat-{str(prt.profile.id)}',
                {
                    'type' : 'chat.user.ws.message',
                    'message' : response
                }
            )
    except Exception as err:
        print(err)