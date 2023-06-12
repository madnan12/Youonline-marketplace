from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Utility EndPoints
    path('start_individual_chat/', views.start_individual_chat),
    path('get_user_chatslist/', views.get_user_chatslist),
    path('get_chat/', views.get_chat),
    path('send_chat_message/', views.send_chat_message),

    path('block_chat/' , views.block_chat),
    path('unblock_chat/' , views.unblock_chat),

    # Group Chat
    path('start_group_chat/', views.start_group_chat),
    path('add_group_chat_member/', views.add_group_chat_member),
    path('remove_group_chat_member/', views.remove_group_chat_member),

    # Delete Chat
    path('delete_chat_message/', views.delete_chat_message),
    path('delete_chat/', views.delete_chat),

    # Miscellaneous
    path('archive_chat/', views.archive_chat),
    path('get_archived_chats/', views.get_archived_chats),
    path('search_chat_message/', views.search_chat_message),
    path('mute_chat/', views.mute_chat),
    path('get_muted_chats/', views.get_muted_chats),
    path('forward_chat_message/', views.forward_chat_message),
    path('send_post_in_chat/', views.send_post_in_chat),
    path('read_chat_message/', views.read_chat_message),
    path('deliver_chat_message/', views.deliver_chat_message),
    path('mute_user_chat/', views.mute_user_chat),
    path('mute_group_chat/', views.mute_group_chat),
    path('unmute_user_chat/', views.unmute_user_chat),
    path('unmute_group_chat/', views.unmute_group_chat),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
