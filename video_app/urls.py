from django.urls import path
from . import views as video 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('get_all_categories/', video.get_all_categories),
    # Video URLs
    path('create_channel/', video.create_channel),
    path('update_channel/', video.update_channel),
    
    # Playlist URLs
    path('create_playlist/', video.create_playlist),
    path('update_playlist/', video.update_playlist),
    path('get_user_playlists/', video.get_user_playlists),
    path('get_playlist_videos/', video.get_playlist_videos),
    path('remove_from_playlist/', video.remove_from_playlist),
    path('delete_video_playlist/', video.delete_video_playlist),
    
    # Channel URLs
    path('upload_video/', video.upload_video),
    path('delete_video/', video.delete_video),
    path('get_video/', video.get_video),
    path('search_video/', video.search_video),
    
    # Video URLs
    path('update_video/', video.update_video),
    path('get_channel/', video.get_channel),
    path('get_channel_videos/', video.get_channel_videos),
    path('get_all_video_posts/', video.get_all_video_posts),
    path('get_most_liked_videos/', video.get_most_liked_videos),
    path('get_user_channel/', video.get_user_channel),
    path('get_user_uploaded_videos/', video.get_user_uploaded_videos),

    # Video New Requirements
    path('get_liked_videos/', video.get_liked_videos),
    path('add_to_watch_later/', video.add_to_watch_later),
    path('remove_from_watch_later/', video.remove_from_watch_later),
    path('get_watch_later_videos/', video.get_watch_later_videos),
    path('add_to_watched/', video.add_to_watched),
    path('get_watched_videos/', video.get_watched_videos),
    path('get_video_library/', video.get_video_library),
    path('add_to_playlist/', video.add_to_playlist),
    path('get_videos_by_category/', video.get_videos_by_category),
    path('get_trending_videos/', video.get_trending_videos),
    path('get_trending_category_videos/', video.get_trending_category_videos),
    path('get_related_videos/', video.get_related_videos),

    # Subscribe Channel
    path('subscribe_channel/', video.subscribe_channel),
    path('unsubscribe_channel/', video.unsubscribe_channel),
    path('get_channel_subscribers/', video.get_channel_subscribers),
    path('get_subscribed_channels/', video.get_subscribed_channels),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
