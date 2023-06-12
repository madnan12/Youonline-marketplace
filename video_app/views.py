import datetime
import json
import jwt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from . models import *
from .serializers import GetVideoSerializer
from django.db.models import Q, Prefetch
from youonline_social_app.models import *
from youonline_social_app.decorators import *
from youonline_social_app.constants import *
from youonline_social_app.custom_api_settings import CustomPagination
from youonline_social_app.serializers import post_serializers
from . import serializers as video_serializers
from itertools import chain
from operator import attrgetter
from moviepy.editor import VideoFileClip
import random, string
from django.conf import settings
from firebase_admin.messaging import Notification as FB_Notification
from fcm_django.models import FCMDevice
from django.views.decorators.csrf import csrf_exempt
from youonline_social_app.views.user import get_video_response


# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_categories(request):
	categories = VideoCategory.objects.all()
	serializer = video_serializers.VideoCategorySerializer(categories, many=True)
	return Response({"success": True, 'response': {'message': serializer.data}},
			status=status.HTTP_200_OK)


# Channel
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_channel(request):
	name = request.data['name'] if 'name' in request.data else None
	description = request.data['description'] if 'description' in request.data else None
	picture = request.data['picture'] if 'picture' in request.data else None
	cover = request.data['cover'] if 'cover' in request.data else None
	if not name:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_401_UNAUTHORIZED)
	request.data._mutable = True
	request.data['profile'] = profile.id
	serializer = video_serializers.VideoChannelSerializer(data=request.data)
	if serializer.is_valid():
		channel = serializer.save()
		if picture:
			channel_picture = ChannelPicture(
					channel = channel,
					picture = picture
				)
			channel_picture.save()
		if cover:
			channel_cover = ChannelCover(
					channel = channel,
					cover = cover
				)
			channel_cover.save()
		VideoChannelSubscribe.objects.create(channel=channel, profile=channel.profile)
		serializer = video_serializers.GetVideoChannelSerializer(channel, context={"profile": channel.profile})
		channel.save()
		return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_201_CREATED)
	else:
		return Response({"success": False, 'response': {'message': serializer.errors}},
			status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_channel(request):
	id = request.data['id'] if 'id' in request.data else None
	name = request.data['name'] if 'name' in request.data else None
	description = request.data['description'] if 'description' in request.data else None
	picture = request.data['picture'] if 'picture' in request.data else None
	cover = request.data['cover'] if 'cover' in request.data else None
	if not id or (not name and not description and not picture and not cover):
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		channel = VideoChannel.objects.get(id=id)
		serializer = video_serializers.VideoChannelSerializer(channel, data=request.data, partial=True)
	except:
		return Response({"success": False, 'response': {'message': 'Invalid Channel ID.'}},
				status=status.HTTP_400_BAD_REQUEST)
	if serializer.is_valid():
		channel = serializer.save()
		if picture:
			try:
				channel_picture = ChannelPicture.objects.get(channel=channel)
				channel_picture.delete()
			except:
				pass
			channel_picture = ChannelPicture(
					channel = channel,
					picture = picture
				)
			channel_picture.save()
		if cover:
			try:
				channel_cover = ChannelCover.objects.get(channel=channel)
				channel_cover.delete()
			except:
				pass
			channel_cover = ChannelCover(
					channel = channel,
					cover = cover
				)
			channel_cover.save()
		serializer = video_serializers.GetVideoChannelSerializer(channel)
		return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_200_OK)
	else:
		return Response({"success": False, 'response': {'message': serializer.errors}},
			status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_channel_videos(request):
	channel = request.query_params.get('channel')
	if not channel:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	else:
		try:
			channel = VideoChannel.objects.get(slug=channel, is_deleted=False)
		except Exception as e:
			return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
		try:
			profile = Profile.objects.get(user=request.user)
		except:
			profile = None
		videos = Video.objects.filter(channel=channel, is_deleted=False).order_by('-created_at')
		paginator = CustomPagination()
		paginator.page_size = 10
		result_page = paginator.paginate_queryset(videos, request)
		if profile:
			serializer = GetVideoSerializer(result_page, many=True, context={"profile": profile})
		else:
			serializer = GetVideoSerializer(result_page, many=True)
		return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_channel(request):
	channel = request.query_params.get('channel')
	if not channel:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	else:
		try:
			channel = VideoChannel.objects.get(slug=channel, is_deleted=False)
		except Exception as e:
			return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
		try:
			profile = Profile.objects.get(user=request.user)
		except:
			profile = None
		if profile:
			serializer = video_serializers.GetVideoChannelSerializer(channel, context={"profile": profile})
		else:
			serializer = video_serializers.GetVideoChannelSerializer(channel)
		return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_channel(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_401_UNAUTHORIZED)
	try:
		channel = VideoChannel.objects.get(profile=profile, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_404_NOT_FOUND)
	serializer = video_serializers.GetVideoChannelSerializer(channel, context={"profile": channel.profile})
	return Response({"success": True, 'response': serializer.data},
				status=status.HTTP_200_OK)


# Video
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_video(request):
	title = request.data['title'] if 'title' in request.data else None
	description = request.data['description'] if 'description' in request.data else None
	video = request.data['video'] if 'video' in request.data else None
	youtube_link = request.data['youtube_link'] if 'youtube_link' in request.data else None
	category = request.data['category'] if 'category' in request.data else None
	sub_category = request.data['sub_category'] if 'sub_category' in request.data else None
	channel = request.data['channel'] if 'channel' in request.data else None
	playlist = request.data['playlist'] if 'playlist' in request.data else None
	short_description = request.data['short_description'] if 'short_description' in request.data else None

	if not title or not description or not category or not channel or (not video and not youtube_link) or (video and youtube_link):
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	else:
		try:
			profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
		except Exception as e:
			return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_401_UNAUTHORIZED)
		request.data._mutable = True
		request.data['profile'] = profile.id
		serializer = video_serializers.VideoSerializer(data=request.data)
		if serializer.is_valid():
			video = serializer.save()
			post = Post.objects.create(
					profile=video.profile,
					privacy=video.privacy,
					text=video.description,
					normal_post=False,
					video_module=True,
					video_post=True,
				)
			video.post = post
			video.is_deleted = False
			video.save()
			if playlist:
				try:
					playlist = VideoPlaylist.objects.get(id=playlist, is_deleted=False)
					VideoPlaylistPost.objects.create(
							playlist=playlist,
							post=post,
						)
				except:
					pass
			serializer = post_serializers.PostGetSerializer(post, context={"profile": profile})
			# SEO Meta Creation
			filename ='CSVFiles/XML/videos.xml'
			open_file=open(filename,"r")
			read_file=open_file.read()
			open_file.close()
			new_line=read_file.split("\n")
			last_line="\n".join(new_line[:-1])
			open_file=open(filename,"w+")
			for i in range(len(last_line)):
				open_file.write(last_line[i])
			open_file.close()

			loc_tag=f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{video.slug}</loc>\n"
			lastmod_tag=f"<lastmod>{video.created_at}</lastmod>\n"
			priorty_tag=f"<priority>0.8</priority>\n</url>\n</urlset>"
			with open(filename, "a") as fileupdate:
				fileupdate.write(loc_tag)
				fileupdate.write(lastmod_tag)
				fileupdate.write(priorty_tag)
			# SEO Meta Close
			return Response({"success": True, 'response': {'message': serializer.data}},
					status=status.HTTP_201_CREATED)
		else:
			return Response({"success": False, 'response': {'message': serializer.errors}},
					status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_video(request):
	ids = json.loads(request.data['id']) if 'id' in request.data else None
	if not ids or type(ids) != list:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)

	for id_ in ids:
		try:
			video = Video.objects.get(id=id_, is_deleted=False)
			video.is_deleted = True
			video.save()
			post = video.post
			post.is_deleted = True
			post.save()
		except Exception as err:
			pass
		
	return Response({"success": True, 'response': {'message': 'Video deleted successfully!'}},
			status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_video(request):
	video = request.query_params.get('video')
	if not video:
		return Response(
			{
				"success": False, 
				'response': {
					'message': 'Invalid Data!'
				}
			},
			status=status.HTTP_400_BAD_REQUEST
		)
	else:
		try:
			profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
		except:
			profile = None
		try:
			video = Post.objects.get(id=video, is_deleted=False, is_hidden=False)
		except ObjectDoesNotExist:
			return Response({"success": False, 'response': {'message': 'Video does not exist.'}},
					status=status.HTTP_404_NOT_FOUND)
		except:
			try:
				video = Post.objects.get(videomodule_post__slug=video, is_deleted=False)
			except Exception as e:
				return Response({"success": False, 'response': {'message': str(e)}},
							status=status.HTTP_404_NOT_FOUND)
		if profile:
			serializer = post_serializers.PostGetSerializer(video, context={"profile": profile})
		else:
			serializer = post_serializers.PostGetSerializer(video)
		return Response({"success": True, 'response': serializer.data},
				status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_video(request):
	id = request.data['id'] if 'id' in request.data else None
	title = request.data['title'] if 'title' in request.data else None
	short_description = request.data['short_description'] if 'short_description' in request.data else None
	description = request.data['description'] if 'description' in request.data else None
	category = request.data['category'] if 'category' in request.data else None
	sub_category = request.data['sub_category'] if 'sub_category' in request.data else None

	if not id or not title:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	if description == '':
		return Response({"success": False, 'response': {'message': 'Provide description of video'}},
					status=status.HTTP_400_BAD_REQUEST)
	
	try:
		video = Video.objects.get(id=id, is_deleted=False)
	except ObjectDoesNotExist:
		return Response({"success": False, 'response': {'message': 'Video does not exist.'}},
				status=status.HTTP_404_NOT_FOUND)
	except:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
					status=status.HTTP_400_BAD_REQUEST)
	if category:
		try:
			category = VideoCategory.objects.get(id=category)
		except Exception as e:
			return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_400_BAD_REQUEST)
	if sub_category:
		try:
			sub_category = VideoSubCategory.objects.get(id=sub_category)
		except Exception as e:
			return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_400_BAD_REQUEST)
	

	serializer = video_serializers.VideoSerializer(video, request.data, partial=True)
	if serializer.is_valid():
		serializer.save()
		post = video.post
		post.text = video.description
		post.save()
		serializer = video_serializers.GetVideoSerializer(video)
		return Response({"success": True, 'response': serializer.data},
					status=status.HTTP_200_OK)
	else:
		return Response({"success": False, 'response': serializer.errors},
					status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_video_posts(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except:
		profile = None
	
	# posts = Post.objects.filter(
	# 	is_deleted=False,
	# 	video_module=True
	# ).select_related('profile').order_by("-created_at")

	# videos = Video.objects.filter(is_deleted=False).select_related('channel').order_by("-created_at")
	# paginator = CustomPagination()
	# paginator.page_size = 20
	# result_page = paginator.paginate_queryset(videos, request)
	# serialized_list = []
	# for post in result_page:
	# 	post_dictionary = get_video_response(request, post)
	# 	serialized_list.append(post_dictionary)
	# serializer = serialized_list
	# response = paginator.get_paginated_response(serializer)
	# return response

	videos = Video.objects.filter(is_deleted=False).select_related('channel').order_by("-created_at")
	paginator = CustomPagination()
	paginator.page_size = 20
	result_page = paginator.paginate_queryset(videos, request)
	if profile:
		serializer = GetVideoSerializer(result_page, many=True, context={"profile": profile})
	else:
		serializer = GetVideoSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_most_liked_videos(request):
	posts = Post.objects.filter(video_module=True, reactions_count__gte=1, is_deleted=False, is_hidden=False).order_by('-reactions_count')
	paginator = CustomPagination()
	paginator.page_size = 10
	result_page = paginator.paginate_queryset(posts, request)
	serializer = post_serializers.PostGetSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_uploaded_videos(request):
	profile = request.query_params.get('profile')
	try:
		profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	posts = Post.objects.filter(profile=profile, media_post=True, video_post=True, is_deleted=False, is_hidden=False).order_by('-created_at')
	paginator = CustomPagination()
	paginator.page_size = 20
	result_page = paginator.paginate_queryset(posts, request)
	serializer = post_serializers.PostGetSerializer(result_page, many=True, context={"profile": profile})
	return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_video(request):
	title = request.query_params.get('title')
	if not title:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	else:
		try:
			profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
		except Exception as e:
			return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_401_UNAUTHORIZED)
		videos = Video.objects.filter(title__icontains=title, is_deleted=False).values_list('post__id', flat=True)
		posts = Post.objects.filter(id__in=videos, is_deleted=False, is_hidden=False)
		paginator = CustomPagination()
		paginator.page_size = 20
		result_page = paginator.paginate_queryset(posts, request)
		serializer = post_serializers.PostGetSerializer(result_page, many=True, context={"profile": profile})
		return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_liked_videos(request):
	sort_option = request.query_params.get('sort_option')
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_401_UNAUTHORIZED)
	if sort_option == 'date_created':
		videos = Video.objects.filter(post__postreaction_post__profile=profile, is_deleted=False).order_by('post__postreaction_post').distinct()
	elif sort_option == 'title':
		videos = Video.objects.filter(post__postreaction_post__profile=profile, is_deleted=False).order_by('title').distinct()
	elif sort_option == 'popular':
		videos = Video.objects.filter(post__postreaction_post__profile=profile, is_deleted=False).order_by('-post__reactions_count').distinct()
	else:
		videos = Video.objects.filter(post__postreaction_post__profile=profile, is_deleted=False).order_by('-post__postreaction_post__created_at').distinct()
	paginator = CustomPagination()
	paginator.page_size = 10
	result_page = paginator.paginate_queryset(videos, request)
	serializer = video_serializers.DefaultVideoSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_videos_by_category(request):
	category = request.query_params.get('category')
	sort_option = request.query_params.get('sort_option' , 'default')

	SORT_OPTIONS = {
		'date_created' : 'created_at',
		'title' : 'videomodule_post__title',
		'popular' : '-reactions_count',
		'default' : '-created_at'
	}

	if not category:
		return Response(
			{
				"success": False, 
				'response': {
					'message': 'Invalid Data.'
				}
			},
			status=status.HTTP_400_BAD_REQUEST
		)

	try:
		category = VideoCategory.objects.get(id=category)
	except Exception as e:
		return Response(
			{
				"success": False, 
				'response': {
					'message': str(e)
				}
			},
			status=status.HTTP_404_NOT_FOUND
		)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except:
		profile = None

	videos = Video.objects.filter(category=category, is_deleted=False).order_by(SORT_OPTIONS[sort_option])
	paginator = CustomPagination()
	paginator.page_size = 10
	result_page = paginator.paginate_queryset(videos, request)
	if profile:
		serializer = GetVideoSerializer(result_page, many=True, context={"profile": profile})
	else:
		serializer = GetVideoSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


# Playlist
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_playlist(request):
	id = request.data['id'] if 'id' in request.data else None
	channel = request.data['channel'] if 'channel' in request.data else None
	banner = request.data['banner'] if 'banner' in request.data else None
	name = request.data['name'] if 'name' in request.data else None
	if not channel or not name:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_401_UNAUTHORIZED)
	request.data._mutable = True
	request.data['profile'] = profile.id
	try:
		channel_obj = VideoChannel.objects.get(id=channel, profile=profile)
	except:
		return Response({"success": False, 'response': {'message': 'You cannot create playlist against this channel'}},
			status=status.HTTP_403_FORBIDDEN)
	serializer = video_serializers.VideoPlaylistSerializer(data=request.data)
	if serializer.is_valid():
		playlist = serializer.save()
		if banner:
			banner = PlaylistBanner(
					playlist = playlist,
					banner = banner
				)
			banner.save()
		serializer = video_serializers.GetVideoPlaylistSerializer(playlist)
		playlist.save()
		return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_201_CREATED)
	else:
		return Response({"success": False, 'response': {'message': serializer.errors}},
			status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_playlist(request):
	id = request.data['id'] if 'id' in request.data else None
	name = request.data['name'] if 'name' in request.data else None
	banner = request.data['banner'] if 'banner' in request.data else None
	if not id or not name:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		playlist = VideoPlaylist.objects.get(id=id, is_deleted=False)
		serializer = video_serializers.VideoPlaylistSerializer(playlist, request.data, partial=True)
	except:
		return Response({"success": False, 'response': {'message': 'Invalid Playlist ID.'}},
				status=status.HTTP_400_BAD_REQUEST)
	if serializer.is_valid():
		playlist = serializer.save()
		if banner:
			try:
				d_banner = PlaylistBanner.objects.get(playlist=playlist)
				d_banner.delete()
			except:
				pass
			banner_obj = PlaylistBanner.objects.create(
				playlist = playlist,
				banner = banner
			)
		serializer = video_serializers.GetVideoPlaylistSerializer(playlist)
		return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_200_OK)
	else:
		return Response({"success": False, 'response': {'message': serializer.errors}},
			status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_playlist_videos(request):
	playlist = request.query_params.get('playlist')
	sort_option = request.query_params.get('sort_option', 'default')
	if not playlist:
		return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_401_UNAUTHORIZED)
	try:
		playlist = VideoPlaylist.objects.get(slug=playlist, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_404_NOT_FOUND)

	if playlist.privacy == 'OnlyMe' and playlist.channel.profile != profile:
		return Response(
			{
				'status' : False,
				'response' : {
					'message' : "You are not authorized to view this playlist"
				}
			},
			status=status.HTTP_403_FORBIDDEN
		)

	SORT_OPTIONS = {
		'date_created' : 'created_at',
		'title' : 'videomodule_post__title',
		'popular' : '-reactions_count',
		'default' : '-created_at',
	}

	posts = Post.objects.filter(
		videoplaylistpost_post__playlist=playlist, 
		video_post=True, 
		is_hidden=False, 
		is_deleted=False
	).order_by(SORT_OPTIONS[sort_option])

	paginator = CustomPagination()
	paginator.page_size = 20
	result_page = paginator.paginate_queryset(posts, request)
	serializer = post_serializers.PostGetSerializer(result_page, many=True, context={"profile": profile})
	try:
		channel = video_serializers.VideoChannelSerializer(playlist.channel).data
	except:
		channel = None
	return paginator.get_paginated_response(serializer.data, details=channel, playlist=video_serializers.GetVideoPlaylistSerializer(playlist).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_playlists(request):

	try:
		user_profile = Profile.objects.get(user=request.user , is_deleted=False)
	except:
		return Response({"success": False, 'response': {'message': 'Please login to proceed'}},
			status=status.HTTP_401_UNAUTHORIZED)

	profile = request.query_params.get('profile')
	if not profile:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
			status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)

	if user_profile == profile : 
		playlists = VideoPlaylist.objects.filter(channel__profile=profile, is_deleted=False).order_by('-created_at')
	else :
		playlists = VideoPlaylist.objects.filter(
			channel__profile=profile, 
			is_deleted=False,
			privacy='Public'
		).order_by('-created_at')
			
	serializer = video_serializers.GetVideoPlaylistSerializer(playlists, many=True)
	return Response({"success": True, 'response': serializer.data},
				status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_playlist(request):
	posts = request.data['posts'] if 'posts' in request.data else None
	playlist = request.data['playlist'] if 'playlist' in request.data else None
	if not posts or not playlist:
		return Response({'success': False, 'response': {'message': 'Invalid data'}},
						status=status.HTTP_400_BAD_REQUEST)
	try:
		playlist = VideoPlaylist.objects.get(id=playlist, is_deleted=False)
	except Exception as e:
		return Response({'success': False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	posts = posts[1:-1].replace('"', "").split(',')
	for i in posts:
		try:
			post = Post.objects.get(id=i, is_deleted=False, video_post=True)
		except:
			return Response({'success': False, 'response': {'message': 'The requested post does not exist or is not video post!'}},
						status=status.HTTP_404_NOT_FOUND)
		try:
			VideoPlaylistPost.objects.create(
				playlist = playlist,
				post = post
			)
		except Exception as e:
			print(str(e))
			pass
	return Response({'success': True, 'response': {'message': 'Video added to playlist successfully.'}},
				status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_playlist(request):
	post = request.data['post'] if 'post' in request.data else None
	playlist = request.data['playlist'] if 'playlist' in request.data else None
	if not post or not playlist:
		return Response({'success': False, 'response': {'message': 'Invalid data'}},
						status=status.HTTP_400_BAD_REQUEST)
	else:
		try:
			post = Post.objects.get(id=post, is_deleted=False, video_post=True)
		except:
			return Response({'success': False, 'response': {'message': 'The requested post does not exist or is not video post!'}},
						status=status.HTTP_404_NOT_FOUND)
		try:
			playlist = VideoPlaylist.objects.get(id=playlist, is_deleted=False)
		except:
			return Response({'success': False, 'response': {'message': 'Playlist does not exist!'}},
						status=status.HTTP_404_NOT_FOUND)
		try:
			playlist_video = VideoPlaylistPost.objects.get(post=post, playlist=playlist)
			playlist_video.delete()
		except Exception as e:
			return Response({'success': False, 'response': {'message': str(e)}},
						status=status.HTTP_404_NOT_FOUND)
		return Response({'success': True, 'response': {'message': 'Video removed from playlist successfully.'}},
					status=status.HTTP_200_OK)


# Watch Later
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_watch_later(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({'success': False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	request.data._mutable = True
	request.data['profile'] = profile.id
	serializer = video_serializers.VideoWatchLaterSerializer(data=request.data)
	if serializer.is_valid():
		watch_later = serializer.save()
		serializer = video_serializers.GetVideoWatchLaterSerializer(watch_later)
		return Response({'success': True, 'response': {'message': serializer.data}},
					status=status.HTTP_201_CREATED)
	else:
		return Response({'success': False, 'response': {'message': serializer.errors}},
				status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_watch_later(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	video = request.data['video'] if 'video' in request.data else None
	if not video:
		return Response({'success': False, 'response': {'message': 'Invalid data'}},
						status=status.HTTP_400_BAD_REQUEST)
	try:
		video = Video.objects.get(id=video, is_deleted=False)
	except:
		return Response({'success': False, 'response': {'message': 'The requested video does not exist!'}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		watch_later = VideoWatchLater.objects.get(
				profile=profile,
				video=video
			)
		watch_later.delete()
		return Response({'success': True, 'response': {'message': 'Video removed from watch later!!'}},
					status=status.HTTP_200_OK)
	except:
		return Response({'success': False, 'response': {'message': 'Video does not exist in watch later.'}},
				status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_watch_later_videos(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_401_UNAUTHORIZED)
	sort_option = request.query_params.get('sort_option')
	if sort_option == 'date_created':
		videos = VideoWatchLater.objects.filter(profile=profile, video__is_deleted=False).order_by('-created_at')
	elif sort_option == 'title':
		videos = VideoWatchLater.objects.filter(profile=profile, video__is_deleted=False).order_by('video__title')
	elif sort_option == 'popular':
		videos = VideoWatchLater.objects.filter(profile=profile, video__is_deleted=False).order_by('-created_at')
	else:
		videos = VideoWatchLater.objects.filter(profile=profile, video__is_deleted=False).order_by('-created_at')
	paginator = CustomPagination()
	paginator.page_size = 10
	result_page = paginator.paginate_queryset(videos, request)
	serializer = video_serializers.GetVideoWatchLaterSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_watched(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_401_UNAUTHORIZED)
	video = request.data['video'] if 'video' in request.data else None
	try:
		video = Video.objects.get(id=video, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)
	try:
		watched_video = VideoWatched.objects.get(video = video, profile=profile)
	except ObjectDoesNotExist:
		watched_video = VideoWatched.objects.create(
							video = video,
							profile = profile
						)
	except Exception as e:
		return Response({'success': False, 'response': {'message': str(e)}},
					status=status.HTTP_400_BAD_REQUEST)
	watched_video.times_watched += 1
	watched_video.last_watched = datetime.datetime.now()
	watched_video.save()
	video.total_views += 1
	video.save()
	return Response({'success': True, 'response': {'message': 'Video watched'}},
				status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_watched_videos(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	# Sorting Options
	sort_option = request.query_params.get('sort_option')
	if sort_option == 'date_created':
		videos = VideoWatched.objects.filter(profile=profile, video__is_deleted=False).order_by('last_watched')
	elif sort_option == 'title':
		videos = VideoWatched.objects.filter(profile=profile, video__is_deleted=False).order_by('video__title')
	elif sort_option == 'popular':
		videos = VideoWatched.objects.filter(profile=profile, video__is_deleted=False).order_by('-last_watched')
	else:
		videos = VideoWatched.objects.filter(profile=profile, video__is_deleted=False).order_by('-last_watched')
	paginator = CustomPagination()
	paginator.page_size = 10
	result_page = paginator.paginate_queryset(videos, request)
	serializer = video_serializers.GetVideoWatchedSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_library(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	
	# # Watched Videos
	watched_videos = VideoWatched.objects.filter(profile=profile, video__is_deleted=False).order_by('-created_at')[:4]
	watched_videos = video_serializers.GetVideoWatchedSerializer(watched_videos, many=True).data

	# # Watch Later
	watch_later = VideoWatchLater.objects.filter(profile=profile, video__is_deleted=False).order_by('-created_at')[0:4]
	watch_later = video_serializers.GetVideoWatchLaterSerializer(watch_later, many=True).data

	# # Liked Videos
	liked_videos = Video.objects.filter(post__postreaction_post__profile=profile, is_deleted=False).order_by('-post__postreaction_post__created_at')[0:4]
	liked_videos = video_serializers.DefaultVideoSerializer(liked_videos, many=True).data
	
	results = {
		'watched_videos': watched_videos,
		'watch_later': watch_later,
		'liked_videos': liked_videos,
	}
	return Response({'success': True, 'response': {'message': results}},
				status=status.HTTP_200_OK)


# Trending
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trending_videos(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_401_UNAUTHORIZED)
	yesterday_time = datetime.datetime.now() - datetime.timedelta(days=1)
	posts = Post.objects.filter(
		is_deleted=False,
		video_module=True,
		is_hidden=False,
		videomodule_post__videowatched_video__created_at__gte=yesterday_time
	) .order_by('-created_at').distinct()
	paginator = CustomPagination()
	paginator.page_size = 10
	result_page = paginator.paginate_queryset(posts, request)
	serializer = post_serializers.PostGetSerializer(result_page, many=True, context={"profile": profile})
	return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending_category_videos(request):
	category = request.query_params.get('category')
	if not category:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except:
		profile = None
	try:
		category = VideoCategory.objects.get(id=category)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_404_NOT_FOUND)
	yesterday_time = datetime.datetime.now() - datetime.timedelta(days=1)
	posts = Post.objects.filter(videowatched_post__created_at__gte=yesterday_time, videomodule_post__category=category, video_module=True, is_hidden=False, is_deleted=False).order_by('created_at')
	paginator = CustomPagination()
	paginator.page_size = 10
	result_page = paginator.paginate_queryset(list(set(posts)), request)
	if profile:
		serializer = post_serializers.PostGetSerializer(result_page, many=True, context={"profile": profile})
	else:
		serializer = post_serializers.PostGetSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_related_videos(request):
	category = request.query_params.get('category')
	video = request.query_params.get('video')
	if not category or not video:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except:
		profile = None
	try:
		category = VideoCategory.objects.get(id=category)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_404_NOT_FOUND)
	posts = Post.objects.filter(videomodule_post__category=category, video_module=True, is_hidden=False, is_deleted=False).exclude(videomodule_post__id=video).order_by('created_at')
	paginator = CustomPagination()
	paginator.page_size = 10
	result_page = paginator.paginate_queryset(posts, request)
	if profile:
		serializer = post_serializers.PostGetSerializer(result_page, many=True, context={"profile": profile})
	else:
		serializer = post_serializers.PostGetSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_channel(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	request.data._mutable = True
	request.data['profile'] = profile.id
	serializer = video_serializers.VideoChannelSubscribeSerializer(data=request.data)
	if serializer.is_valid():
		subscribe = serializer.save()
		serializer = video_serializers.GetVideoChannelSubscribeSerializer(subscribe)
		return Response({'success': True, 'response': {'message': serializer.data}},
					status=status.HTTP_201_CREATED)
	else:
		return Response({'success': False, 'response': {'message': serializer.errors}},
				status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_channel(request):
	channel = request.data['channel'] if 'channel' in request.data else None
	if not channel:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	try:
		channel = VideoChannel.objects.get(id=channel, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		subscribe = VideoChannelSubscribe.objects.get(channel=channel, profile=profile)
		subscribe.delete()
		return Response({"success": True, 'response': {'message': 'Unsubscribed Successfully !!'}},
					status=status.HTTP_200_OK)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_channel_subscribers(request):
	channel = request.query_params.get('channel')
	if not channel:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		channel = VideoChannel.objects.get(id=channel, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	subscribers = Profile.objects.filter(videochannelsubscribe_profile__channel=channel)
	serializer = post_serializers.DefaultProfileSerializer(subscribers, many=True)
	return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscribed_channels(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_401_UNAUTHORIZED)
	channels = VideoChannel.objects.filter(videochannelsubscribe_channel__profile=profile)
	serializer = video_serializers.GetVideoChannelSerializer(channels, many=True, context={"profile": profile})
	return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_200_OK)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_video_playlist(request):
	playlist = request.data['playlist'] if 'playlist' in request.data else None
	if not playlist:
		return Response({"success": False, 'response': {'message': 'Invalid Data'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_401_UNAUTHORIZED)
	try:
			VideoPlaylist.objects.get(id=playlist, is_deleted=False).delete()
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
				status=status.HTTP_404_NOT_FOUND)
	return Response({"success": True, 'response': {'message': 'Playlist deleted successfully !!'}},
				status=status.HTTP_200_OK)

