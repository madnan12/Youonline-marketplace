from chat_app.models import ChatParticipant
import datetime

def unmute_user_chat():
    current_time = datetime.datetime.now()
    chat_particepant = ChatParticipant.objects.filter(muted_till__lte=current_time)
    for c in chat_particepant:
        c.is_muted = False
        c.muted_till = None
        c.save()