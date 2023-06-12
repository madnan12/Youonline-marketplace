import datetime
from functools import partial
from xmlrpc.client import DateTime
from django.core.exceptions import ObjectDoesNotExist

from youonline_social_app.views.user import get_post_response
from ..constants import *
from ..decorators import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import *
from ..serializers.post_serializers import *
from ..custom_api_settings import CustomPagination
from itertools import chain
from operator import attrgetter
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FB_Notification
from fcm_django.models import FCMDevice
from video_app import serializers as video_serializers
from youonline_social_app.websockets.Constants import send_notifications_ws
from itertools import chain

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_test_posts(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        hidden_posts = HiddenPost.objects.filter(profile=profile, post__is_deleted=False).values_list('post__id', flat=True)
        report_posts = ReportPost.objects.filter(reported_by=profile, post__is_deleted=False).values_list('post__id', flat=True)
        following_list = []
        try:
            following_list = FriendsList.objects.get(profile=profile)
            following_list = following_list.following.all()
        except Exception as e :
            pass
        posts = Post.objects.filter(normal_post=True, is_deleted=False).select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post').exclude(id__in=hidden_posts).exclude(id__in=report_posts).order_by('-created_at')[0:1200]
    except Exception as e:
        print(e)
        
    paginator = CustomPagination()
    paginator.page_size = 1200
    result_page = paginator.paginate_queryset(posts, request)
    
    # Create custom json response for API response optimization
    serialized_list = []
    for post in result_page:
        post_dictionary = get_post_response(post)
        serialized_list.append(post_dictionary)

    serializer = serialized_list
    response = paginator.get_paginated_response(serializer)

    # Shuffle the results
    try:
        random.shuffle(response.data['results'])
    except:
        pass
    return response
    
  



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    if request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            post = post.id
            post = Post.objects.select_related(
                                    'profile', 'group', 'page'
                                ).prefetch_related(
                                    'postreaction_post', 'post_post', 'sub_post',
                                    'albumpost_post', 'pollpost_post',
                                    'taguser_post', 'sharedpost_post').get(id=post)
            serializer = PostGetSerializer(post, context={"request": request, "profile": post.profile})
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    post = request.data['post'] if 'post' in request.data else None
    text = request.data['text'] if 'text' in request.data else None
    deleted_media = request.data['deleted_media'] if 'deleted_media' in request.data else None
    post_image = request.data['post_image'] if 'post_image' in request.data else None
    post_video = request.data['post_video'] if 'post_video' in request.data else None
    tagged = request.data['tagged_profiles'] if 'tagged_profiles' in request.data else None
    if not post:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        post = Post.objects.get(id=post, is_deleted=False, profile=profile)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    serializer = PostUpdateSerializer(post, data=request.data, partial=True)
    if serializer.is_valid():
        post = serializer.save()
        media = PostMedia.objects.filter(post=post)
        if deleted_media:
            deleted_media = deleted_media[1:-1].replace('"', '').split(',')
            for i in deleted_media:
                try:
                    media = PostMedia.objects.get(id=i)
                    media.is_deleted = True
                    media.save()
                except:
                    pass
        if post_image:
            for image in request.FILES.getlist('post_image'):
                media = PostMedia.objects.create(post=post, post_image=image)
        if post_video:
            media = PostMedia.objects.create(post=post, post_video=post_video)

                
        """
        Check if there are profiles in tagged_profiles to be tagged in this post.
        - Add them to the tagged list
        - Add them to the NotifiersList for this post to sendt them notifications.
        """
        if tagged:
            tagged_profiles=tagged[1:-1].replace('"', '').split(',')
            for i in tagged_profiles:
                try:
                    tag_profile = Profile.objects.get(id=str(i))
                    tag_user=TagUser.objects.create(
                        post=post,
                        tagged_profile=tag_profile,
                        tagged_by=post.profile
                    )
                    notification = Notification(
                        type = 'TaggedPost',
                        profile = post.profile,
                        text = 'Tagged you in a post.',
                        post = post,
                    )
                    notification.save()
                    for i in tagged_profiles:
                        notification.notifiers_list.add(i)
                        try:
                            devices = FCMDevice.objects.filter(device_id=i.id)
                            fb_body = {
                                'comment_reply': 'null',
                                'created_at': str(datetime.datetime.now()),
                                'post_comment': 'null',
                                'type': 'TaggedPost',
                                'profile': str(i.id),
                                'post_profile': str(post.profile.id),
                                'text': f"{post.profile.user.first_name} {post.profile.user.last_name} tagged you in a post.",
                                'post': str(post.id),
                            }
                            devices.send_message(
                                Message(
                                    data=fb_body,
                                    notification=FB_Notification(
                                        title="Tagged Post",
                                        body=fb_body['text'],
                                        image=notification_image)
                            ))
                        except:
                            pass
                    notification.save()
                    try:
                        send_notifications_ws(notification)
                    except:
                        pass
                    try:
                        notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture.url
                    except Exception as e:
                        notification_image = None
                except Exception as e:
                    print(e)
        post = Post.objects.select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post'
                ).get(id=post.id)
        serializer = PostGetSerializer(post)
        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_single_post_media(request):
    """
    Add media to an already existing post.
    """
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id
    post_id = request.query_params.get('post')
    try:
        post = Post.objects.get(id=post_id, is_deleted=False, profile=profile)
    except:
        return Response({"success": False, 'response': {'message': 'Post does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        serializer = PostMediaSerializer(data=request.data)
        if serializer.is_valid():
            media_object = serializer.save()
            media_object.post_id = post_id
            media_object.profile_id = profile.id
            media_object.save()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post_media(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        media = PostMedia.objects.get(id=id, is_deleted=False, post__profile=profile)
    except:
        return Response({'success': False, 'response': {'message': 'Post Media item does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)
    media.is_deleted = True
    media.save()
    return Response({'success': True, 'response': {'message': 'Media deleted successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            post = Post.objects.select_related(
                                    'profile', 'group', 'page').prefetch_related(
                                    'postreaction_post', 'post_post', 'sub_post',
                                    'albumpost_post', 'pollpost_post',
                                    'taguser_post', 'sharedpost_post').get(id=id, is_deleted=False)
            if profile:
                serializer = PostGetSerializer(post, context={"profile": profile}, read_only=True)
            else:
                serializer = PostGetSerializer(post, read_only=True)
            return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'DELETE':
        id = request.data['id'] if 'id' in request.data else None
        if not id:
            return Response({'success': False, 'response': {'message': 'Invalid data'}},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                post = Post.objects.get(id=id, is_deleted=False, profile=profile)
            except:
                return Response({'success': False, 'response': {'message': 'The requested post does not exist!'}},
                                status=status.HTTP_404_NOT_FOUND)

            post.is_deleted = True
            post.save()
            medias = PostMedia.objects.filter(post=post)
            for i in medias:
                i.is_deleted=True
                i.save()
            if post.video_module:
                video = Video.objects.get(post=post)
                video.is_deleted = True
            return Response({'success': True, 'response': {'message': 'Post Deleted Successfully!'}},
                            status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hide_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id
    post = request.data['post'] if 'post' in request.data else None    
    if not post:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            post = Post.objects.get(id=post, is_deleted=False)
        except:
            return Response({'success': False, 'response': {'message': 'The requested post does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)
        if post.profile == profile:
            post.is_hidden = True
            post.save()
        serializer = HiddenPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': {'message': 'Post Hidden Successfully!!'}},
                        status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unhide_post(request):
    post = request.data['post'] if 'post' in request.data else None
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    if not post or not profile:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            post = Post.objects.get(id=post, is_deleted=False)
        except:
            return Response({'success': False, 'response': {'message': 'The requested post does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)
        if post.profile == profile:
            post.is_hidden = False
            post.save()
        try:
            hidden_post = HiddenPost.objects.get(
                    profile = profile,
                    post = post
                )
            hidden_post.delete()
            return Response({'success': True, 'response': {'message': 'Post Unhidden Successfully!!'}},
                        status=status.HTTP_200_OK)
        except:
            return Response({'success': False, 'response': {'message': 'Hidden Post does not exist.'}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_hidden_posts(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    objs = HiddenPost.objects.filter(profile=profile, post__is_deleted=False).values_list('post__id', flat=True)
    posts  = Post.objects.filter(id__in=objs
                ).select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post').order_by('-hidden_post__created_at')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostGetSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote_poll(request):
    """
    Add vote to a given option of the poll.
    """
    poll = request.data['poll'] if 'poll' in request.data else None
    poll_option = request.data['poll_option'] if 'poll_option' in request.data else None
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    if not poll or not poll_option:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        poll = Poll.objects.get(id=poll, is_deleted=False, post__is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        poll_option = PollOption.objects.get(id=poll_option, poll=poll)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        vote = PollVote.objects.get(poll=poll, profile=profile)
        return Response({'success': False, 'response': {'message': 'You cannot vote again.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    except:
        pass
    try:
        # Increment the total votes on the option.
        poll_option.total_votes += 1
        poll_option.save()
        # Increment the total votes on the poll.
        poll.total_votes += 1
        poll.save()
        PollVote.objects.create(
                poll = poll,
                profile = profile,
                option = poll_option,
            )
        serializer = PollSerializer(poll)
        return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def undo_vote(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    poll = request.data['poll'] if 'poll' in request.data else None
    if not poll:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        vote = PollVote.objects.get(poll__id=poll, profile=profile)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    poll_option = vote.option
    poll_option.total_votes -= 1
    poll_option.save()
    poll = vote.poll
    poll.total_votes -= 1
    poll.save()
    vote.delete()
    return Response({'success': False, 'response': {'message': 'Vote Undone successfully !!'}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_post_comment(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id
    data = request.data
    post = data['post'] if 'post' in data else None
    text = data['text'] if 'text' in data else None
    comment_image = data['comment_image'] if 'comment_image' in data else None
    comment_video = data['comment_video'] if 'comment_video' in data else None
    comment_audio = data['comment_audio'] if 'comment_audio' in data else None
    comment_gif = data['comment_gif'] if 'comment_gif' in data else None
    mentioned_profiles = data['mentioned_profiles'] if 'mentioned_profiles' in data else None

    if not post or (not text and not comment_image and not comment_audio and not comment_video and not comment_gif and not mentioned_profiles):
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        post = Post.objects.get(id=post, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Post not found!'}},
                        status=status.HTTP_404_NOT_FOUND)
    comment = PostComment(
        post=post,
        profile=profile,
        text=text,
    )
    comment.save()

    try:
        notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture.url
    except Exception as e:
        notification_image = None

    try:
        cmnt_notifiers = NotifiersList.objects.get(post_comment=comment)
    except:
        cmnt_notifiers = NotifiersList.objects.create(post_comment=comment)

    
    # TagUser
    try:
        mentioned_profiles = mentioned_profiles[1:-1].replace('"', '').split(',')
        if mentioned_profiles is not None:
            mention_notification = Notification(
                type='PostComment',
                text='mentioned you in a comment.',
                post_comment=comment,
                profile=profile
            )
            for pf in mentioned_profiles:
                try:
                    get_pf = Profile.objects.get(id=pf)
                    tag_user = TagUser.objects.create(
                        tagged_profile = get_pf,
                        tagged_by = profile,
                        comment=comment,
                        post=post,
                        is_mentioned=True
                    )
                    mention_notification.notifiers_list.add(get_pf)
                    cmnt_notifiers.notifiers_list.add(get_pf)
                except Exception as e:
                    pass
            mention_notification.save()
            cmnt_notifiers.save()

            try:
                send_notifications_ws(mention_notification)
            except:
                pass

            # Sending Notifications to all Mentioned Users
            devices = FCMDevice.objects.filter(device_id__in=mentioned_profiles)
            fb_body = {
                'comment_reply': 'null',
                'created_at': str(datetime.datetime.now()),
                'post_comment': str(comment.id),
                'type': 'PostComment',
                'profile': str(profile.id),
                'post_profile': str(post.profile.id),
                'text': f"{profile.user.first_name} {profile.user.last_name} mentioned you in a comment.",
                'post': 'null',
            }
            devices.send_message(
                Message(
                    data=fb_body,
                    notification=FB_Notification(
                        title="Post Comment",
                        body=fb_body['text'],
                        image=notification_image)
            ))
    except:
        pass
    try:
        image = data['comment_image']
        if image is not None:    
            name = image.name.split('.')
            if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                commentmedia = CommentMedia.objects.create(comment=comment, comment_image=image)
                commentmedia.save()
            else:
                comment.delete()
                return Response({'success': False, 'response': {
                                                         'message': 'Error in Comment,'
                                                                    'Only these formats are allowed {}'.format(
                                                             ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}},
                            status=status.HTTP_400_BAD_REQUEST
                        )
    except:
        pass
    try:
        video = data['comment_video']
        if video is not None:
            name = video.name.split('.')
            if name[-1] in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                CommentMedia.objects.create(comment=comment, comment_video=video)
            else:
                comment.delete()
                return Response({'success': False, 'response': {
                                                         'message': 'Error in Comment Video format,'
                                                                    'Only these formats are allowed {}'.format(
                                                             ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}},
                                status=status.HTTP_400_BAD_REQUEST
                            )
    except:
        pass
    try:
        audio = data['comment_audio']
        if audio is not None:
            name = audio.name.split('.')
            if name[-1] in ['mp3', 'MP3']:
                CommentMedia.objects.create(comment=comment, comment_audio=audio)
            else:
                comment.delete()
                return Response({'success': False, 'response': {
                                                         'message': 'Error in Comment Audio field,'
                                                                    'Only these formats are allowed {}'.format(
                                                             ['mp3', 'MP3'])}},
                                status=status.HTTP_400_BAD_REQUEST
                            )
    except:
        pass
    try:
        gif = data['comment_gif']
        if gif is not None:
            CommentMedia.objects.create(comment=comment, comment_gif=gif)
    except:
        pass
    post.comments_count += 1
    post.save()
    try:
        notifiers = NotifiersList.objects.get(post=post)
    except:
        notifiers = NotifiersList.objects.create(post=post)

    
    if profile != post.profile:
        notification = Notification(
                type = 'PostComment',
                profile = profile,
                text = 'commented on your post.',
                post = post,
            )
        notification.save()
        for i in notifiers.notifiers_list.all():
            notification.notifiers_list.add(i)
        notification.notifiers_list.remove(profile)
        notification.save()
        notifiers.notifiers_list.add(profile)
        notifiers.save()
        try:
            send_notifications_ws(notification)
        except:
            pass

        devices = FCMDevice.objects.filter(device_id=post.profile.id)
        fb_body = {
            'comment_reply': 'null',
            'created_at': str(datetime.datetime.now()),
            'post_comment': 'null',
            'type': 'PostComment',
            'profile': str(profile.id),
            'post_profile': str(post.profile.id),
            'text': f"{profile.user.first_name} {profile.user.last_name} commented on your post.",
            'post': str(post.id),
        }
        devices.send_message(
            Message(
                data=fb_body,
                notification=FB_Notification(
                    title="Post Comment",
                    body=fb_body['text'],
                    image=notification_image)
        ))


        # Sending Notifications to all Other users who commented on this post 
        if len(notifiers.notifiers_list.all()) > 1:
            try:
                comment_users_notification = Notification(
                    type='PostComment',
                    profile=profile,
                    text=f"also commented on {post.profile.user.first_name}'s post.",
                    post=post
                )
                comment_users_notification.save()
                for usr in notifiers.notifiers_list.all():
                    comment_users_notification.notifiers_list.add(usr)
                comment_users_notification.notifiers_list.remove(profile)
                comment_users_notification.notifiers_list.remove(post.profile)
                comment_users_notification.save()
                try:
                    send_notifications_ws(comment_users_notification)
                except:
                    pass
            except:
                pass

            exclude_lists = []
            exclude_lists.append(profile.id)
            exclude_lists.append(post.profile.id)

            notifiers_ids = notifiers.notifiers_list.all().values_list('id', flat=True).exclude(id__in=exclude_lists)
            all_ids = []
            for i in notifiers_ids:
                all_ids.append(i)

            all_devices = FCMDevice.objects.filter(device_id__in=all_ids)
            fb_body = {
                'comment_reply': 'null',
                'created_at': str(datetime.datetime.now()),
                'post_comment': 'null',
                'type': 'PostComment',
                'profile': str(profile.id),
                'post_profile': str(post.profile.id),
                'text': f"{profile.user.first_name} {profile.user.last_name} also commented on {post.profile.user.first_name}'s post.",
                'post': str(post.id),
            }
            all_devices.send_message(
                Message(
                    data=fb_body,
                    notification=FB_Notification(
                        title="Post Comment",
                        body=fb_body['text'],
                        image=notification_image)
            ))
    

        
    serializer = PostCommentSerializer(comment, context={"request": request})
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post_comment(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            comment = PostComment.objects.get(id=id, profile=profile)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        # Soft delete all the comment replies
        comment_replies = CommentReply.objects.filter(comment=comment, is_deleted=False)
        for i in comment_replies:
            i.is_deleted = True
            i.save()
        post = comment.post
        # Decrement the comments count on the post.
        post.comments_count -= comment_replies.count() + 1
        post.save()
        comment.delete()
        return Response({'success': True, 'response': {'message': 'Comment deleted successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def create_post_reaction(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    post = data['post'] if 'post' in data else None
    video = data['video'] if 'video' in data else None
    reaction_type = data['type'] if 'type' in data else None

    if not post and not profile:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                    status=status.HTTP_400_BAD_REQUEST)

    try:
        post = Post.objects.get(id=post, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Post does not exist',}},
                status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        try:
            post_reaction = PostReaction.objects.get(post=post, profile=profile)
            post_reaction.delete()
            post.reactions_count -= 1
            post.save()
            return Response({'success': True, 'response': {'message': 'Reaction Deleted Successfully'}},
                            status=status.HTTP_200_OK)
        except:
            return Response({'success': False, 'response': {'message': 'Post Reaction does not exist'}},
                            status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        try:
            post_reaction = PostReaction.objects.get(post=post, profile=profile)
            post_reaction.type = reaction_type
            post_reaction.save()
            post.save()
        except:
            post_reaction = PostReaction.objects.create(
                post=post,
                profile=profile,
                type=reaction_type
            )
            post.reactions_count += 1
            post.save()
        if profile != post.profile:
            if post.story_post:
                text = "reacted on your story."
                notification_type = 'StoryReaction'
                title = "Story Reaction"
                story_post = post.post_profilestory.all()[0]
                story_id = post.post_profilestory.all()[0].id
            else:
                text = "reacted on your post."
                notification_type = 'PostReaction'
                title = "Post Reaction"
                story_post = None
                story_id = 'None'
            notification = Notification(
                        type = notification_type,
                        profile = profile,
                        text = text,
                        post = post,
                        story = story_post,
                    )
            notification.save()
            notification.notifiers_list.add(post.profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
            # Firebase Notification
            try:
                notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture.url
            except Exception as e:
                notification_image = None
            devices = FCMDevice.objects.filter(device_id=post.profile.id)
            if post.story_post:
                text = f"{profile.user.first_name} {profile.user.last_name} reacted on your story."
            else:
                text = f"{profile.user.first_name} {profile.user.last_name} reacted on your post."
            fb_body = {
                'comment_reply': 'null',
                'created_at': str(datetime.datetime.now()),
                'post_comment': 'null',
                'type': notification_type,
                'profile': str(profile.id),
                'post_profile': str(post.profile.id),
                'text': text,
                'post': str(post.id),
                'story_id': str(story_id),
            }
            devices.send_message(
                Message(
                    data=fb_body,
                    notification=FB_Notification(
                        title=title,
                        body=fb_body['text'],
                        image=notification_image)
            ))
    reactions = dict()
    reactions['type'] = post_reaction.type
    reactions['post'] = post_reaction.post.id
    reactions['profile'] = post_reaction.profile.id
    if video == 'true':
        video = Video.objects.get(post=post, is_deleted=False)
        serializer = video_serializers.DefaultVideoSerializer(video)
        return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({'success': True, 'response': {'message': reactions}},
                        status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def dislike_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    post = data['post'] if 'post' in data else None
    if not post:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        post = Post.objects.get(id=post, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        try:
            dislike = PostDislike.objects.get(post=post, profile=profile)
            dislike.delete()
            post.dislikes_count -= 1
            post.save()
            return Response({'success': True, 'response': {'message': 'Dislike removed successfully !!'}},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        serializer = PostDislikeSerializer(data=request.data)
        if serializer.is_valid():
            dislike = serializer.save()
            post.dislikes_count += 1
            post.save()
            serializer = GetPostDislikeSerializer(dislike)
            return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def single_post_reactions(request):
    data = request.data
    post = data['post'] if 'post' in data else None
    type = data['type'] if 'type' in data else None

    if not post:
        return Response({'success': False, 'response': {'message': 'Invalid data',}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        post = Post.objects.get(id=post, is_deleted=False)
    except:
        return Response({'success': False, 'response': {
            'message': 'Post does not exist',
            'status': status.HTTP_404_NOT_FOUND},
                         }, status=status.HTTP_404_NOT_FOUND)
    if not type:
        post_reactions = PostReaction.objects.filter(post=post)
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(post_reactions, request)
        serializer = GetPostReactionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        post_reactions = PostReaction.objects.filter(post=post, type=type)
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(post_reactions, request)
        serializer = GetPostReactionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def create_post_comment_reaction(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id
    comment = request.data['comment'] if 'comment' in request.data else None
    reaction_type = request.data['type'] if 'type' in request.data else None
    if not comment and not profile:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        comment = PostComment.objects.get(id=comment, is_deleted=False)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Comment does not exist'}},
                status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        try:
            reaction = CommentReaction.objects.get(profile=profile, comment=comment)
            reaction.type = reaction_type
            reaction.save()
            serializer = PostCommentReactionSerializer(reaction)
            return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
        except:
            serializer = PostCommentReactionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                comment.reactions_count += 1
                comment.save()
                if profile != comment.post.profile:
                    notification = Notification(
                            type = 'CommentReaction',
                            profile = profile,
                            text = 'reacted on your comment.',
                            post_comment = comment,
                        )
                    notification.save()
                    notification.notifiers_list.add(comment.post.profile)
                    notification.save()
                    try:
                        send_notifications_ws(notification)
                    except:
                        pass

                    # Firebase FCM Notification
                    try:
                        notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture.url
                    except Exception as e:
                        notification_image = None
                    devices = FCMDevice.objects.filter(device_id=comment.post.profile.id)
                    fb_body = {
                        'comment_reply': 'null',
                        'created_at': str(datetime.datetime.now()),
                        'post_comment': str(comment.id),
                        'type': 'CommentReaction',
                        'profile': str(profile.id),
                        'post_profile': str(comment.profile.id),
                        'text': f"{profile.user.first_name} {profile.user.last_name} reacted on your comment.",
                        'post': str(comment.post.id),
                    }
                    devices.send_message(
                        Message(
                            data=fb_body,
                            notification=FB_Notification(
                                title="Comment Reaction",
                                body=fb_body['text'],
                                image=notification_image),
                    ))
                return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'response': {'message': serializer.errors}},
                        status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            reaction = CommentReaction.objects.get(profile=profile, comment=comment)
            reaction.delete()
            comment.reactions_count -= 1
            comment.save()
            return Response({'success': True, 'response': {'message': 'Reaction deleted successfully!'}},
                    status=status.HTTP_200_OK)
        except:        
            return Response({'success': False, 'response': {'message': 'Reaction does not exist!'}},
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment_reply(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    comment = data['comment'] if 'comment' in data else None
    text = data['text'] if 'text' in data else None
    comment_image = data['comment_image'] if 'comment_image' in data else None
    comment_video = data['comment_video'] if 'comment_video' in data else None
    comment_audio = data['comment_audio'] if 'comment_audio' in data else None
    comment_gif = data['comment_gif'] if 'comment_gif' in data else None
    mentioned_profiles = data['mentioned_profiles'] if 'mentioned_profiles' in data else None

    if not comment:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if not text and not comment_image and not comment_audio and not comment_video and not comment_gif and not mentioned_profiles:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if comment:
        try:
            comment = PostComment.objects.get(id=comment, is_deleted=False)
        except:
            return Response({'success': False, 'response': {'message': 'Comment not found!'}},
                            status=status.HTTP_404_NOT_FOUND)
        reply = CommentReply(
            comment=comment,
            profile=profile,
            text=text,
        )
        reply.save()
        try:
            image = data['comment_image']
            if image is not None:    
                name = image.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    CommentReplyMedia.objects.create(comment_reply=reply, reply_image=image)
                else:
                    reply.delete()
                    return Response({'success': False, 'response': {
                                                             'message': 'Error in Comment,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}},
                                status=status.HTTP_400_BAD_REQUEST
                            )
        except:
            pass
        
    try:
        cmnt_notifiers = NotifiersList.objects.get(comment_reply=reply)
    except:
        cmnt_notifiers = NotifiersList.objects.create(comment_reply=reply)

    
    # TagUser
    try:
        mentioned_profiles = mentioned_profiles[1:-1].replace('"', '').split(',')
        if mentioned_profiles is not None:
            mention_notification = Notification(
                type='CommentReply',
                text='mentioned you in a comment reply.',
                comment_reply=reply,
                profile=profile
            )
            for pf in mentioned_profiles:
                try:
                    get_pf = Profile.objects.get(id=pf)
                    tag_user = TagUser.objects.create(
                        tagged_profile = get_pf,
                        tagged_by = profile,
                        reply_comment=reply,
                        is_mentioned=True
                    )
                    mention_notification.notifiers_list.add(get_pf)
                    cmnt_notifiers.notifiers_list.add(get_pf)
                except:
                    pass
            mention_notification.save()
            cmnt_notifiers.save()
            try:
                send_notifications_ws(mention_notification)
            except:
                pass

            # Sending Notifications to all Mentioned Users
            devices = FCMDevice.objects.filter(device_id__in=mentioned_profiles)
            fb_body = {
                'comment_reply': str(reply.id),
                'created_at': str(datetime.datetime.now()),
                'post_comment': 'null',
                'type': 'CommentReply',
                'profile': str(profile.id),
                'post_profile': str(post.profile.id),
                'text': f"{profile.user.first_name} {profile.user.last_name} mentioned you in a comment reply.",
                'post': 'null',
            }
            devices.send_message(
                Message(
                    data=fb_body,
                    notification=FB_Notification(
                        title="Post Comment",
                        body=fb_body['text'],
                        image=notification_image)
            ))
    except:
        pass
        try:
            video = data['comment_video']
            if video is not None:
                name = video.name.split('.')
                if name[-1] in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                    CommentReplyMedia.objects.create(comment_reply=reply, reply_video=video)
                else:
                    reply.delete()
                    return Response({'success': False, 'response': {
                                                             'message': 'Error in Comment Video format,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
        except:
            pass
        try:
            audio = data['comment_audio']
            if audio is not None:
                name = audio.name.split('.')
                if name[-1] in ['mp3', 'MP3']:
                    CommentReplyMedia.objects.create(comment_reply=reply, reply_audio=audio)
                else:
                    reply.delete()
                    return Response({'success': False, 'response': {
                                                             'message': 'Error in Comment Audio field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['mp3', 'MP3'])}},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
        except:
            pass
        try:
            gif = data['comment_gif']
            if gif is not None:
                CommentReplyMedia.objects.create(comment_reply=reply, reply_gif=gif)
        except:
            pass
        comment.replies_count += 1
        comment.save()
        post = comment.post
        post.comments_count += 1
        post.save()
        try:
            notifiers = NotifiersList.objects.get(post_comment=comment)
        except:
            notifiers = NotifiersList.objects.create(post_comment=comment)
        if profile != comment.profile:
            notification = Notification(
                    type = 'CommentReply',
                    profile = profile,
                    text = 'replied to your comment.',
                    comment_reply = reply,
                    post_comment = comment,
                    post = post,
                )
            notification.save()
            notification.notifiers_list.add(comment.profile)
            for i in notifiers.notifiers_list.all():
                notification.notifiers_list.add(i)
            notification.notifiers_list.remove(profile)
            notification.save()
            notifiers.notifiers_list.add(comment.profile)
            notifiers.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
            try:
                notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture.url
            except Exception as e:
                notification_image = None
            devices = FCMDevice.objects.filter(device_id=comment.profile.id)
            fb_body = {
                'comment_reply': str(reply.id),
                'created_at': str(datetime.datetime.now()),
                'post_comment': str(comment.id),
                'type': 'CommentReply',
                'profile': str(profile.id),
                'post_profile': str(comment.profile.id),
                'text': f"{profile.user.first_name} {profile.user.last_name} replied to your comment.",
                'post': str(post.id),
            }
            devices.send_message(
                Message(
                    data=fb_body,
                    notification=FB_Notification(
                        title="Comment Reply",
                        body=fb_body['text'],
                        image=notification_image),
            ))
        serializer = GetCommentReplySerializer(reply)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def create_comment_reply_reaction(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    comment = data['comment'] if 'comment' in data else None
    reaction_type = data['type'] if 'type' in data else None

    if not comment or not profile or not reaction_type:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        comment = CommentReply.objects.get(id=comment, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Comment does not exist'}},
                status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        try:
            reactions = CommentReplyReaction.objects.filter(profile=profile, comment=comment)
            for i in reactions:
                i.delete()
            comment.reactions_count -= 1
            comment.save()
            return Response({'success': True, 'response': {'message': 'Reaction removed successfully.'}},
                    status=status.HTTP_200_OK)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'POST':
        try:
            reaction = CommentReplyReaction.objects.get(profile=profile, comment=comment)
            reaction.type = reaction_type
            reaction.save()
            serializer = CommentReplyReactionSerializer(reaction)
            return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
        except:
            serializer = CommentReplyReactionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                comment.reactions_count += 1
                comment.save()
                return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'response': {'message': serializer.errors}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment_reply(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            comment = CommentReply.objects.get(id=id, profile=profile)
        except Exception as e:
            return Response({'success': False, 'response': {'message': 'Comment does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)
        parent_comment = comment.comment
        parent_comment.replies_count -= 1
        parent_comment.save()
        post = parent_comment.post
        post.comments_count -= 1
        post.save()
        comment.delete()
        return Response({'success': True, 'response': {'message': 'Comment deleted successfully!'}},
                        status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    post = request.data['post_id'] if 'post_id' in request.data else None
    if not post:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        post = Post.objects.get(id=post, is_deleted=False)
    except Exception as e:
        print(e)
        return Response({'success': False, 'response': {'message': 'Post not found!'}},
                        status=status.HTTP_404_NOT_FOUND)
    serializer = CreateSharedPostSerializer(data=request.data)
    if serializer.is_valid():
        post_obj = serializer.save()
        post_obj.normal_post = True
        post_obj.shared_post = True
        post_obj.save()
    shared_post = SharedPost.objects.create(
            profile = profile,
            shared_post = post,
            post = post_obj,
        )
    post = Post.objects.select_related(
                            'profile', 'group', 'page'
                        ).prefetch_related(
                            'postreaction_post', 'post_post', 'sub_post',
                            'albumpost_post', 'pollpost_post',
                            'taguser_post', 'sharedpost_post').get(id=post_obj.id)
    serializer = PostGetSerializer(post, context={"request": request, "profile": profile})
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_post_to_friend_timeline(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    post = request.data['post'] if 'post' in request.data else None
    friend = request.data['friend'] if 'friend' in request.data else None
    text = request.data['text'] if 'text' in request.data else None
    privacy = request.data['privacy'] if 'privacy' in request.data else 'Public'

    if not post or not friend:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            post = Post.objects.get(id=post, is_deleted=False)
        except:
            return Response({'success': False, 'response': {'message': 'Post not found!'}},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            friend = Profile.objects.get(id=friend, is_deleted=False, user__is_active=True)
        except:
            return Response({'success': False, 'response': {'message': 'Friend Profile does not exist!'}},
                            status=status.HTTP_404_NOT_FOUND)
        post_obj = Post(
                profile=profile,
                text=text,
                privacy=privacy,
                shared_post=True,
            )
        post_obj.save()
        shared_post = SharedPost.objects.create(
                profile = profile,
                shared_post = post,
                post = post_obj,
                share_choice = 'FriendTimeline',
                friend = friend,
            )
        post = Post.objects.select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post').get(id=post_obj.id)
        serializer = PostGetSerializer(post_obj, context={"request": request, "profile": profile})
        return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_post_comments(request):
    post = request.query_params.get('post')
    if not post:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            post = Post.objects.get(id=post, is_deleted=False)
        except:
            return Response({'success': False, 'response': {'message': 'The requested post does not exist!'}},
                            status=status.HTTP_404_NOT_FOUND)
        comments = PostComment.objects.filter(post=post).order_by('-created_at')
        paginator = CustomPagination()
        paginator.page_size = 15
        result_page = paginator.paginate_queryset(comments, request)
        serializer = PostCommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
        

# Saved Posts
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id
    serializer = SavedPostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'response': {'message': 'Post Saved Successfully!!'}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def un_save_post(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    post_id = request.data['post_id'] if 'post_id' in request.data else None
    try:
        post = Post.objects.get(id=post_id, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Post does not exists'}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        saved_post = SavedPost.objects.get(post=post, profile=profile)
        saved_post.delete()
        return Response({'success': True, 'response': {'message': 'Post Un-Saved Successfully!!'}},
                    status=status.HTTP_200_OK)
    except:
        return Response({'success': False, 'response': {'message': 'Saved Post does not exists'}},
                status=status.HTTP_404_NOT_FOUND)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_saved_posts(request):    
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    objs = SavedPost.objects.filter(profile=profile, post__is_deleted=False, post__is_hidden=False).values_list('post__id', flat=True)
    posts  = Post.objects.filter(id__in=objs
                ).select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post').order_by('-savedpost_post__created_at')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostGetSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_video_module_posts(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    objs = SavedPost.objects.filter(profile=profile, post__video_post=True, post__is_deleted=False, post__is_hidden=False).values_list('post__id', flat=True)
    posts  = Post.objects.filter(id__in=objs
                ).select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostGetSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_notification_choice(request):
    """
    API to turn Notifications on and off for a given post.
    """
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)

    post_id = request.data['post'] if 'post' in request.data else None
    notification_choice = request.data['notification_choice'] if 'notification_choice' in request.data else None
    post_comment = request.data['post_comment'] if 'post_comment' in request.data else None
    comment_reply = request.data['comment_reply'] if 'comment_reply' in request.data else None

    if (not post_id or not notification_choice) and not post_comment and not comment_reply:
        return Response({'success': False, 'response': {'message': 'Missing Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    notifiers = None
    resp_op = 'off'
    if post_id:
        try:
            notifiers = NotifiersList.objects.get(post__id=post_id, post__is_deleted=False)
            if notification_choice == 'turn_on':
                notifiers.notifiers_list.add(profile)
                resp_op = 'on'
            elif notification_choice == 'turn_off':
                notifiers.notifiers_list.remove(profile)
            notifiers.save()
        except:
            notifiers = None

    elif post_comment:
        try:
            notifiers = NotifiersList.objects.get(post_comment__id=post_comment, post_comment__is_deleted=False, notifiers_list=profile)
            notifiers.notifiers_list.remove(profile)
            notifiers.save()
        except:
            notifiers = None
    elif comment_reply:
        try:
            notifiers = NotifiersList.objects.get(comment_reply__id=comment_reply, comment_reply__is_deleted=False, notifiers_list=profile)
            notifiers.notifiers_list.remove(profile)
            notifiers.save()
        except:
            notifiers = None
    if notifiers is None:
        return Response({'success': True, 'response': {'message': 'Resource not found!'}},
                status=status.HTTP_404_NOT_FOUND)

    return Response({'success': True, 'response': {'message': f'Successfully Notification turned {resp_op}'}},
                status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def create_posts_reactions(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    post = data['post'] if 'post' in data else None
    video = data['video'] if 'video' in data else None
    reaction_type = data['type'] if 'type' in data else None

    if not post and not profile:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                    status=status.HTTP_400_BAD_REQUEST)

    try:
        post = Post.objects.get(id=post, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Post does not exist',}},
                status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        try:
            post_reaction = PostReaction.objects.get(post=post, profile=profile)
            post_reaction.delete()
            post.reactions_count -= 1
            post.save()
            return Response({'success': True, 'response': {'message': 'Reaction Deleted Successfully'}},
                            status=status.HTTP_200_OK)
        except:
            return Response({'success': False, 'response': {'message': 'Post Reaction does not exist'}},
                            status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        try:
            post_reaction = PostReaction.objects.get(post=post, profile=profile)
            post_reaction.type = reaction_type
            post_reaction.save()
            post.save()
        except:
            post_reaction = PostReaction.objects.create(
                post=post,
                profile=profile,
                type=reaction_type
            )
            post.reactions_count += 1
            post.save()
        if profile != post.profile:
            if post.story_post:
                text = "reacted on your story."
                notification_type = 'StoryReaction'
                title = "Story Reaction"
                story_post = post.post_profilestory.all()[0]
                story_id = post.post_profilestory.all()[0].id
            else:
                text = "reacted on your post."
                notification_type = 'PostReaction'
                title = "Post Reaction"
                story_post = None
                story_id = 'None'
            notification = Notification(
                        type = notification_type,
                        profile = profile,
                        text = text,
                        post = post,
                        story = story_post,
                    )
            notification.save()
            notification.notifiers_list.add(post.profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
            # Firebase Notification
            try:
                notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture.url
            except Exception as e:
                notification_image = None
            devices = FCMDevice.objects.filter(device_id=post.profile.id)
            if post.story_post:
                text = f"{profile.user.first_name} {profile.user.last_name} reacted on your story."
            else:
                text = f"{profile.user.first_name} {profile.user.last_name} reacted on your post."
            fb_body = {
                'comment_reply': 'null',
                'created_at': str(datetime.datetime.now()),
                'post_comment': 'null',
                'type': notification_type,
                'profile': str(profile.id),
                'post_profile': str(post.profile.id),
                'text': text,
                'post': str(post.id),
                'story_id': str(story_id),
            }
            devices.send_message(
                Message(
                    data=fb_body,
                    notification=FB_Notification(
                        title=title,
                        body=fb_body['text'],
                        image=notification_image)
            ))
    # reactions = dict()
    # reactions['type'] = post_reaction.type
    # reactions['post'] = post_reaction.post.id
    # reactions['profile'] = post_reaction.profile.id
    serializer = GetPostReactionSerializer(post_reaction, context={'user':request.user, 'post':post})
    if video == 'true':
        video = Video.objects.get(post=post, is_deleted=False)
        serializer = video_serializers.DefaultVideoSerializer(video)
        return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def total_posts_reactions(request):
    post = request.query_params.get('post')
    if not post:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)

    post_reaction = PostReaction.objects.filter(post=post).order_by('-created_at')
    serializer = TotalPostReactionSerializer(post_reaction, many=True)
    return Response({'success':True, 'response':{'message': serializer.data}},
                        status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_report_post_category(request):
    category = ReportPostCategory.objects.all()
    serializer = GetReportPostCategorySerializer(category, many=True)
    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_post(request):
    post = request.data['post'] if 'post' in request.data else None
    category = request.data['category'] if 'category' in request.data else None
    if not post or not category:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)        
    try:
        reported_by = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        request.data._mutable = True
    except:
        pass

    request.data['reported_by'] = reported_by.id
    if request.method == 'POST':
        serializer = ReportPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_package(request):
    classified = request.data.get('classified', None)
    job = request.data.get('job', None)
    automotive = request.data.get('automotive', None)
    property_object = request.data.get('property', None)
    package = request.data.get('package', None)

    if not package:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                                    status=status.HTTP_400_BAD_REQUEST)
    try:
        package = PackagePlan.objects.get(id=package)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)

    if classified:
        try:
            classified = Classified.objects.get(id=classified, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

        detail = PackagePlaneDetail.objects.create(classified=classified, packege_type='Classified', plan=package)
        return Response({"success": True, 'response': {'message': 'Package Created successfully!'}},
                                                    status=status.HTTP_400_BAD_REQUEST)
    elif job:
        try:
            job = Job.objects.get(id=job, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

        detail = PackagePlaneDetail.objects.create(job=job, packege_type='Job', plan=package)
        return Response({"success": True, 'response': {'message': 'Package Created successfully!'}},
                                                    status=status.HTTP_400_BAD_REQUEST)
    elif automotive:
        try:
            automotive = Automotive.objects.get(id=automotive, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

        detail = PackagePlaneDetail.objects.create(automotive=automotive, packege_type='Automotive', plan=package)
        return Response({"success": True, 'response': {'message': 'Package Created successfully!'}},
                                                    status=status.HTTP_400_BAD_REQUEST)
    elif property_object:
        try:
            property_object = Property.objects.get(id=property_object, is_deleted=False)

        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        detail = PackagePlaneDetail.objects.create(property=property_object, packege_type='Property', plan=package)
        return Response({"success": True, 'response': {'message': 'Package Created successfully!'}},
                                                    status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_packages(request):
    packages = PackagePlan.objects.all()
    serializer = GetPackagePlanSerializer(packages, many=True)
    return Response({'success': True, 'response': serializer.data},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def popular_category(request):
    automotive_category = AutomotiveCategory.objects.all().order_by('-view_count')[:6]
    classified_category = ClassifiedCategory.objects.all().order_by('-view_count')[:6]
    property_category = Category.objects.all().order_by('-view_count')[:6]
    job_category = JobCategory.objects.all().order_by('-view_count')[:6]

    result_list = list(chain(automotive_category, classified_category, property_category, job_category))

    my_dicts = []
    
    for i in result_list:
        new_dict = {}
        new_dict['id'] = str(i.id)
        new_dict['title'] = i.title
        new_dict['view_count'] = i.view_count
        my_dicts.append(new_dict)
    
    my_dicts.sort(key=lambda x: x['view_count'], reverse=True)

    serializer = my_dicts
    return Response({'success': True, 'response': serializer},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_deal(request):
    property_object = request.data.get('property', None)
    automotive = request.data.get('automotive', None)
    classified = request.data.get('classified', None)

    discount_percentage = request.data.get('discount_percentage', None)
    discounted_price = request.data.get('discounted_price', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    if  not discount_percentage or not discounted_price or not start_date or not end_date:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                            status=status.HTTP_400_BAD_REQUEST)

    if not property_object and not automotive and not classified:
        return Response({"success": False, 'response': {'message': 'Module ID is required!'}},
                            status=status.HTTP_400_BAD_REQUEST)

    if property_object:
        try:
            property_object = Property.objects.get(id=property_object, is_deleted=False)
            
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if automotive:
        try:
            automotive = Automotive.objects.get(id=automotive, is_deleted=False)

        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if classified:
        try:
            classified = Classified.objects.get(id=classified, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    
    serializer = DealDataSerializer(data=request.data)
    if serializer.is_valid():
        deal = serializer.save()
        deal.start_date = start_date
        deal.end_date = end_date
        deal.save()

        if property_object:
            property_object.is_deal = True
            property_object.save()
            deal.deal_property = True
            deal.save()
            
        if automotive:
            automotive.is_deal = True
            automotive.save()
            deal.deal_automotive = True
            deal.save()

        if classified:
            classified.is_deal = True
            classified.save()
            deal.deal_classified = True
            deal.save()

        return Response({'success': True, 'response': serializer.data},
            status=status.HTTP_201_CREATED)

    else:
        return Response({'success': True, 'response': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_deal(request):
    id = request.data.get('id', None)
    if not id:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        deal = DealData.objects.get(id=id, is_deleted=False, is_expired=False)
        deal.is_deleted = True
        if deal.deal_automotive:
            automotive = deal.automotive
            automotive.is_deal = False
            automotive.save()
            
        if deal.deal_property:
            property = deal.property
            property.is_deal = False
            property.save()

        if deal.deal_classified:
            classified = deal.classified
            classified.is_deal = False
            classified.save()
        deal.save()
        return Response({"success": True, 'response': {'message': 'Deal deleted successfully!'}},
                    status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_deal(request):
    id = request.data.get('id', None)
    if not id:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        deal = DealData.objects.get(id=id, is_deleted=False, is_expired=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)

    serializer = DealDataSerializer(deal, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        return Response({'success': True, 'response': serializer.data},
            status=status.HTTP_200_OK)
    else:
        return Response({'success': True, 'response': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_deal(request):
    id = request.query_params.get('id', None)
    if not id:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        deal = DealData.objects.get(id=id, is_deleted=False, is_expired=False)
        serializer = DealDataSerializer(deal)
        return Response({'success': True, 'response': serializer.data},
            status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)