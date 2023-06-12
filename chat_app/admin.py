from django.contrib import admin
from . models import *


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'profile_id', 'is_forwarded', 'is_deleted', 'created_at')


class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'profile_id', 'is_deleted', 'is_archived', 'is_muted')


class ChatDeletionTrackerAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'profile_id', 'deleted_at')


class chatAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by_id', 'created_at')


class ChatMessageMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_message_id', 'created_at')


admin.site.register(Chat, chatAdmin)
admin.site.register(ChatParticipant, ChatParticipantAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(ChatMessageMedia, ChatMessageMediaAdmin)
admin.site.register(ChatDeletionTracker, ChatDeletionTrackerAdmin)
