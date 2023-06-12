import datetime
from rest_framework import serializers
from . models import *
from youonline_social_app.models import *
from youonline_social_app.constants import password_validator
import random, string
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from fcm_django.models import FCMDevice
from youonline_social_app.serializers import post_serializers
from youonline_social_app.serialized_methods import *


class VideoChannelSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoChannel
		fields = '__all__'


class GetVideoChannelSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoChannel
		fields = '__all__'

	def to_representation(self, obj):
		# Get Channel Picture
		try:
			picture = ChannelPicture.objects.get(channel=obj)
			if picture.picture:
				picture = f"{settings.S3_BUCKET_LINK}{picture.picture}"
			else:
				picture = None
		except:
			picture = None
		# Get Channel Cover
		try:
			cover = ChannelCover.objects.get(channel=obj)
			if cover.cover:
				cover = f"{settings.S3_BUCKET_LINK}{cover.cover}"
			else:
				cover = None
		except:
			cover = None
		try:
			profile = self.context.get("profile")
			subscribe = VideoChannelSubscribe.objects.get(profile=profile, channel=obj)
			is_subscribed = True
		except Exception as e:
			is_subscribed = False
		total_subscribers = VideoChannelSubscribe.objects.filter(channel=obj).count()
		total_videos = Video.objects.filter(channel=obj, is_deleted=False).count()
		return {
			"id": obj.id,
			"slug": obj.slug,
			"profile": obj.profile.id,
			"name": obj.name,
			"description": obj.description,
			"picture": picture,
			"cover": cover,
			"created_at": obj.created_at,
			"is_subscribed": is_subscribed,
			"total_subscribers": total_subscribers,
			"total_videos": total_videos,
		}


class VideoPlaylistSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoPlaylist
		fields = '__all__'


class GetVideoPlaylistSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoPlaylist
		fields = '__all__'

	def to_representation(self, obj):
		# Get Channel Picture
		try:
			banner = PlaylistBanner.objects.get(playlist=obj)
			if banner.banner:
				banner = f"{settings.S3_BUCKET_LINK}{banner.banner}"
			else:
				banner = None
		except:
			banner = None
		total_videos = VideoPlaylistPost.objects.filter(playlist=obj).count()
		return {
			"id": obj.id,
			"channel": GetVideoChannelSerializer(obj.channel).data,
			"name": obj.name,
			"banner": banner,
			"description": obj.description,
			"privacy": obj.privacy,
			"created_at": obj.created_at,
			"total_videos": total_videos,
			"slug": obj.slug,
		}


class VideoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Video
		fields = ['id', 'profile', 'title', 'description', 'video', 'vid_thumbnail', 'short_description',
				'youtube_link', 'category', 'sub_category', 'created_at', 'channel', 'post', 'slug', 'duration']


class GetVideoSerializer(serializers.ModelSerializer):
	video = serializers.SerializerMethodField()
	vid_thumbnail = serializers.SerializerMethodField()
	channel = serializers.SerializerMethodField()
	watch_later = serializers.SerializerMethodField()
	likes = serializers.SerializerMethodField()
	dislikes = serializers.SerializerMethodField()
	comment_count = serializers.SerializerMethodField()
	class Meta:
		model = Video
		fields = ['id', 'profile', 'title', 'description', 'video', 'vid_thumbnail',
				'short_description', 'youtube_link', 'category', 'sub_category',
				'created_at', 'channel', 'post', 'slug', 'watch_later', 'likes','dislikes', 'duration', 'comment_count','total_views', 'inactive_video']
		read_only_fields = fields

	def get_video(self, video):
		if video.video:
			video = f"{settings.S3_BUCKET_LINK}{video.video}"
		else:
			video = None
		return video

	def get_vid_thumbnail(self, video):
		if video.vid_thumbnail:
			vid_thumbnail = f"{settings.S3_BUCKET_LINK}{video.vid_thumbnail}"
		else:
			vid_thumbnail = None
		return vid_thumbnail

	def get_channel(self, video):
		try:
			profile = self.context.get("profile")
			return GetVideoChannelSerializer(video.channel, context={"profile": profile}).data
		except:
			return GetVideoChannelSerializer(video.channel).data

	def get_likes(self, video):
		try:
			likes = PostReaction.objects.filter(post=video.post)
			return post_serializers.PostReactionSerializer(likes, many=True).data
		except Exception as e:
			print(e)

	def get_dislikes(self, video):
		try:
			dislikes = PostDislike.objects.filter(post=video.post)
			return post_serializers.PostDislikeSerializer(dislikes, many=True).data
		except Exception as e:
			print(e)

	def get_comment_count(self, video):
		try:
			comment_count = PostComment.objects.filter(post=video.post).count()
			return comment_count
		except:
			comment_count = None
			return comment_count

	def get_watch_later(self, video):
		try:
			profile = self.context.get("profile")
			watch_later = VideoWatchLater.objects.get(video=video, profile=profile)
			watch_later = True
		except:
			watch_later = False
		return watch_later
		

class DefaultVideoSerializer(serializers.ModelSerializer):
	video = serializers.SerializerMethodField()
	vid_thumbnail = serializers.SerializerMethodField()
	channel = serializers.SerializerMethodField()
	class Meta:
		model = Video
		fields = ['id', 'title', 'video', 'category', 'vid_thumbnail', 'youtube_link',
				'created_at', 'channel', 'post', 'slug', 'duration', 'inactive_video']
		read_only_fields = fields

	def get_video(self, video):
		if video.video:
			video = f"{settings.S3_BUCKET_LINK}{video.video}"
		else:
			video = None
		return video

	def get_vid_thumbnail(self, video):
		if video.vid_thumbnail:
			vid_thumbnail = f"{settings.S3_BUCKET_LINK}{video.vid_thumbnail}"
		else:
			vid_thumbnail = None
		return vid_thumbnail

	def get_channel(self, video):
		try:
			profile = self.context.get("profile")
			return GetVideoChannelSerializer(video.channel, context={"profile": profile}).data
		except:
			return GetVideoChannelSerializer(video.channel).data


class VideoSubCategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoSubCategory
		fields = '__all__'


class VideoCategorySerializer(serializers.ModelSerializer):
	sub_categories = serializers.SerializerMethodField()
	class Meta:
		model = VideoCategory
		fields = ['id', 'title', 'sub_categories']

	def get_sub_categories(self, obj):
		return VideoSubCategorySerializer(obj.videosubcategory_set.all(), many=True).data


class VideoWatchLaterSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoWatchLater
		fields = '__all__'


class GetVideoWatchLaterSerializer(serializers.ModelSerializer):
	video = DefaultVideoSerializer()
	profile = serializers.SerializerMethodField()

	def get_profile(self, obj):
		return serialized_post_profile(obj.profile)

	class Meta:
		model = VideoWatchLater
		fields = '__all__'


class GetVideoWatchedSerializer(serializers.ModelSerializer):
	video = DefaultVideoSerializer()
	profile = serializers.SerializerMethodField()

	def get_profile(self, obj):
		return serialized_post_profile(obj.profile)

	class Meta:
		model = VideoWatched
		fields = '__all__'


class VideoWatchedSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoWatched
		fields = '__all__'


class VideoPlaylistPostSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoPlaylistPost
		fields = '__all__'
		

class VideoChannelSubscribeSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoChannelSubscribe
		fields = '__all__'
		

class GetVideoChannelSubscribeSerializer(serializers.ModelSerializer):
	class Meta:
		model = VideoChannelSubscribe
		fields = '__all__'