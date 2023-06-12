from django.contrib import admin
from . models import *

# Register your models here.
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile','title', 'channel', 'category')

class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

class VideoSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category_id')

class VideoPlaylistPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'playlist')

admin.site.register(PlaylistBanner)
admin.site.register(VideoChannel)
admin.site.register(VideoPlaylist)
admin.site.register(VideoCategory, VideoCategoryAdmin)
admin.site.register(VideoSubCategory, VideoSubCategoryAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(VideoWatchLater)
admin.site.register(VideoWatched)
admin.site.register(VideoPlaylistPost)
admin.site.register(VideoChannelSubscribe)
admin.site.register(ChannelPicture)