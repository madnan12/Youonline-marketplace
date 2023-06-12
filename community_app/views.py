import datetime
from fileinput import filename
import json
from tokenize import group
import jwt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from . models import *
from youonline_social_app.models import *
from . import serializers as community_serializers
from django.db.models import Q
from youonline_social_app.decorators import *
from youonline_social_app.constants import *
from youonline_social_app.custom_api_settings import CustomPagination
from youonline_social_app.serializers import post_serializers
from itertools import chain
from operator import attrgetter
from moviepy.editor import VideoFileClip
import random, string
from django.conf import settings
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FB_Notification
from fcm_django.models import FCMDevice
from django.views.decorators.csrf import csrf_exempt
from youonline_social_app.websockets.Constants import send_notifications_ws


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_page(request):
    name = request.data['name'] if 'name' in request.data else None
    category = request.data['category'] if 'category' in request.data else None
    try:
        created_by = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        return Response({"success": False, 'response': 'Invalid User Profile'},
                    status=status.HTTP_401_UNAUTHORIZED)
    if not name or not category:
        return Response({"success": False, 'response': 'Invalid Data. Missing required fields.'},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            request.data._mutable = True
        except:
            pass
        request.data['created_by'] = created_by.id
        serializer = community_serializers.PageSerializer(data=request.data)
        if serializer.is_valid():
            page = serializer.save()
            PageFollower.objects.create(
                profile=page.created_by,
                page=page,
                is_administrator=True
            )
            serializer = community_serializers.GetPageSerializer(page, context={'profile': page.created_by})
            # SEO Meta Creation
            filename ='CSVFiles/XML/pages.xml'
            open_file = open(filename,"r")
            read_file = open_file.read()
            open_file.close()
            new_line = read_file.split("\n")
            last_line = "\n".join(new_line[:-1])
            open_file = open(filename,"w+")
            for i in range(len(last_line)):
                open_file.write(last_line[i])
            open_file.close()

            loc_tag = f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{page.slug}</loc>\n"
            lastmod_tag = f"<lastmod>{page.created_at}</lastmod>\n"
            priorty_tag = f"<priority>0.8</priority>\n</url>\n</urlset>"
            with open(filename, "a") as fileupdate:
                fileupdate.write(loc_tag)
                fileupdate.write(lastmod_tag)
                fileupdate.write(priorty_tag)
            # SEO Meta Close
            return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_page(request):
    page_id = request.data['id'] if 'id' in request.data else None
    page_slug = request.data['slug'] if 'slug' in request.data else None
    if not page_id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
            
        try:
            page = Page.objects.get(id=page_id, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Page does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)

        if page_slug:
            try:
                get_page = Page.objects.get(slug=page_slug)
                return Response({'success': True, 'response': {'message': 'Slug already exist! Try another'}},
                            status=status.HTTP_302_FOUND) 
            except:
                pass

        serializer = community_serializers.PageSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            serializer = community_serializers.GetPageSerializer(page, context={'profile': page.created_by})
            return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_page(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    if not page_id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        administrator = PageFollower.objects.get(page=page, profile=profile, is_administrator=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': 'You are not allowed to delete this page.'}},
                status=status.HTTP_403_FORBIDDEN)
    page.is_deleted = True
    page.save()
    posts = Post.objects.filter(page=page)
    for i in posts:
        i.is_deleted = True
        i.save()
    return Response({'success': True, 'response': {'message': 'Page deleted successfuly!'}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_page(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False)
    except:
        profile = None
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({"success": False, 'response': 'Invalid Data. Data Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(slug=page_id, is_deleted=False, is_hidden=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    if profile:
        serializer = community_serializers.GetPageSerializer(page, context={'profile': profile})
    else:
        serializer = community_serializers.GetPageSerializer(page)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_page(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    if not page_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        # Page Check
        try:
            page = Page.objects.get(id=page_id, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        # Profile Check
        try:
            obj = PageFollower.objects.create(
                    profile=profile,
                    page=page,
                )
            return Response({"success": True, 'response': {'message': 'Now you are following this page.'}},
                        status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_followed_pages(request):
    profile = request.query_params.get('profile')
    if not profile:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Profile does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        page_ids = PageFollower.objects.filter(profile=profile).values_list('page__id', flat=True)
        pages = Page.objects.filter(id__in=page_ids, is_deleted=False, is_hidden=False)
        serializer = community_serializers.DefaultPageSerializer(pages, context={'profile': profile}, many=True)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_page_admin(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    if not page_id:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        # Page Check
        try:
            page = Page.objects.get(id=page_id, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        # Admin Check
        try:
            admin = PageFollower.objects.get(profile=profile, page=page, is_admin=True)
        except:
            return Response({"success": False, 'response': {'message': "You don't have the permissions to make someone admin."}},
                    status=status.HTTP_403_FORBIDDEN)
        # Member Check
        try:
            member = PageFollower.objects.get(profile=profile, page=page, is_admin=False)
        except:
            return Response({"success": False, 'response': {'message': 'User is not following the page or user is admin already.'}},
                    status=status.HTTP_404_NOT_FOUND)
        member.is_admin = True
        member.save()
        return Response({"success": True, 'response': {'message': 'Adminship confirmed successfuly!'}},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_page(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    if not page_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        # Member Check
        try:
            follower = PageFollower.objects.get(profile=profile, page__id=page_id)
        except:
            return Response({"success": False, 'response': {'message': 'User is not following this page.'}},
                    status=status.HTTP_404_NOT_FOUND)
        follower.delete()
        return Response({"success": True, 'response': {'message': 'Unfollowed Page Successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_page_members(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)

    members = PageFollower.objects.filter(page=page)
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(members, request)
    serializer = community_serializers.PageFollowerSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_page_members_ids(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        friends = list(FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True))
    except Exception as e:
        friends = None
    page_members = list(PageFollower.objects.filter(profile__id__in=friends, page=page).values_list('profile__id', flat=True))
    return Response({"success": True, 'response': {'message': page_members}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_page_member_role(request):
    page_id = request.data['page'] if 'page' in request.data else None
    profile_id = request.data['profile'] if 'profile' in request.data else None
    role = request.data['role'] if 'role' in request.data else None
    make_options = ['administrator' , 'editor']
    try:
        user_profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)

    if page_id is None or profile_id is None or role is None or role not in make_options:
        return Response({"success": True, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
        profile = Profile.objects.get(id=profile_id, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success" : False,"response" : {"message" : str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        user_follower = PageFollower.objects.get(
            Q(page=page, profile=user_profile, is_admin=True) |
            Q(page=page, profile=user_profile, is_administrator=True)
            )
    except:
        return Response({"status" : False,"response" : {"message" : 'You are not allowed to change the role.'}},
                status=status.HTTP_403_FORBIDDEN)
    try:
        follower = PageFollower.objects.get(page=page, profile=profile)
    except:
        follower = PageFollower.objects.create(page=page, profile=profile)
    
    # if role == 'admin':
    #     follower.make_admin()
    if role == 'administrator':
        follower.make_administrator()
    elif role == 'editor':
        follower.make_editor()
    # Send Notification For Page Invite
    notification = Notification(
            type = f'your role is changed as {role}',
            profile = profile,
            text = f'for the page {page.name}',
            page = page,
        )
    notification.save()
    notification.notifiers_list.add(profile)
    notification.save()
    try:
        send_notifications_ws(notification)
    except:
        pass

    follower.save()
    return Response({"status" : True,"response" : {"message" : 'Role Updated Successfully'}},
            status=status.HTTP_200_OK)


# Page Rules Cruds
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_page_rule(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        admin = PageFollower.objects.get(page=page, profile=profile, is_admin=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': "You don't have the permissions to write this page rules."}},
                status=status.HTTP_403_FORBIDDEN)
    serializer = community_serializers.PageRuleSerializer(data=request.data)
    if serializer.is_valid():
        rule = serializer.save()
        serializer = community_serializers.PageRuleSerializer(rule)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({"success": False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_page_rule(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        admin = PageFollower.objects.get(page=page, profile=profile, is_admin=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': "You don't have the permissions to update this page rules."}},
                status=status.HTTP_403_FORBIDDEN)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            rule = PageRule.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Rule does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
    serializer = community_serializers.PageRuleSerializer(rule, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        serializer = community_serializers.PageRuleSerializer(rule)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    else:
        return Response({"success": False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_page_rule(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        admin = PageFollower.objects.get(page=page, profile=profile, is_admin=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': "You don't have the permissions to delete this page rules."}},
                status=status.HTTP_403_FORBIDDEN)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            rule = PageRule.objects.get(id=id)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        rule.delete()
        return Response({"success": True, 'response': {'message': 'Rule deleted successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_page_rules(request):
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            page = Page.objects.get(id=page_id, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Page does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        rules  = PageRule.objects.filter(page=page)
        serializer = community_serializers.PageRuleSerializer(rules, many=True)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def discover_pages(request):
    profile = request.query_params.get('profile')
    if not profile:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        user_pages = PageFollower.objects.filter(profile=profile).values_list('page__id', flat=True)
        pages = Page.objects.filter(is_deleted=False, is_hidden=False).exclude(id__in=user_pages)[:20]
        serializer = community_serializers.DefaultPageSerializer(pages, many=True, context={'profile': profile})
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_page_invite(request):
    try:
        invited_by = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    profiles = request.data['profiles'] if 'profiles' in request.data else None
    try:
        request.data._mutable = True
    except:
        pass
    request.data['invited_by'] = invited_by.id
    if not page_id or not profiles:
        return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except:
        return Response({"success": False, 'response': {'message': 'Page does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    members = profiles[1:-1].replace('"', "").split(',')
    for i in members:
        try:
            profile = Profile.objects.get(id=i, is_deleted=False, user__is_active=True)
            PageInvite.objects.create(
                    profile = profile,
                    page = page,
                    invited_by = invited_by,
                )
            # Send Notification For Page Invite
            notification = Notification(
                    type = 'PageInvite',
                    profile = invited_by,
                    text = f'invited you to the page {page.name}',
                    page = page,
                )
            notification.save()
            notification.notifiers_list.add(profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
            # Firebase FCM Notification
            try:
                notification_image = UserProfilePicture.objects.get(profile=invited_by).picture.picture.url
                notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
            except:
                notification_image = None
            try:
                devices = FCMDevice.objects.filter(device_id=profile.id)
                fb_body = {
                    'created_at': str(datetime.datetime.now()),
                    'type': 'PageInvite',
                    'profile': str(profile.id),
                    'invited_by': str(invited_by.id),
                    'text': f"{invited_by.user.first_name} {invited_by.user.last_name} invited you to the page {page.name}.",
                    'page': str(page.id),
                }
                devices.send_message(
                    Message(
                        data=fb_body,
                        notification=FB_Notification(
                            title="Page Invite",
                            body=fb_body['text'],
                            image=notification_image)
                ))
            except:
                pass
        except:
            pass
    return Response({"success": True, 'response': {'message': 'Invite Sent'}},
                    status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def cancel_page_invite(request):
    profile = request.data['profile'] if 'profile' in request.data else None
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    if not page_id or not profile:
        return Response({"success": False, 'response': {'message': 'Invalid data.'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        invitation = PageInvite.objects.get(profile__id=profile, page__id=page_id, is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
    invitation.delete()
    return Response({"success": True, 'response': {'message': 'Invitation cancelled successfuly!!'}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_page_invites(request):
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except:
        return Response({"success": False, 'response': {'message': 'Page does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    invited_list = list(PageInvite.objects.filter(page=page, is_active=True).values_list('profile__id', flat=True))
    return Response({"success": True, 'response': {'message': invited_list}},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_page_invite_profiles(request):
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except:
        return Response({"success": False, 'response': {'message': 'Page does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    invited_list = list(PageInvite.objects.filter(page=page, is_active=True).values_list('profile__id', flat=True))
    profiles = Profile.objects.filter(id__in=invited_list, is_deleted=False, user__is_active=True)
    serializer = post_serializers.DefaultProfileSerializer(profiles, many=True)
    return Response({"success": True, 'response': {'message': serializer.data}},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_page_invites(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    invitations = PageInvite.objects.filter(profile=profile, is_active=True)
    serializer = community_serializers.GetPageInviteSerializer(invitations, many=True, context={"profile": profile})
    return Response({"success": True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Page Post Views
@api_view(['GET'])
@permission_classes([AllowAny])
def get_page_posts(request):
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        except:
            profile = None
        if profile:
            try:
                hidden_posts = HiddenPost.objects.filter(profile=profile).values_list('post__id', flat=True)
                posts = Post.objects.filter(page__id=page_id, is_deleted=False, is_hidden=False).exclude(id__in=hidden_posts).order_by('-created_at')
            except Exception as e:
                return Response({"success": False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            posts = Post.objects.filter(page__id=page_id, is_deleted=False, is_hidden=False).order_by('-created_at')
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(posts, request)
        if profile:
            serializer = post_serializers.PostGetSerializer(result_page, many=True, context = {'profile': profile})
        else:
            serializer = post_serializers.PostGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_pages_feed(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    pages = PageFollower.objects.filter(profile=profile).values_list('page__id', flat=True)
    hidden_posts = HiddenPost.objects.filter(profile=profile).values_list('post__id', flat=True)
    posts = Post.objects.filter(page__id__in=pages, is_deleted=False, is_hidden=False
                ).select_related(
                    'profile', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'pollpost_post', 'taguser_post', 'sharedpost_post'
                ).exclude(id__in=hidden_posts).order_by('-create_at')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(posts, request)
    serializer = post_serializers.PostGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Page Banner Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_page_banner(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    banner = request.data['banner'] if 'banner' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    # Updating request variables
    try:
        request.data._mutable = True
    except:
        pass
    request.data['page'] = page_id
    request.data['uploaded_by'] = profile.id
    if not page_id or not banner:
        return Response({"success": False, 'response': {'message': 'Missing Field. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        auth_user = PageFollower.objects.get(
            Q(page=page, profile=profile, is_admin=True) |
            Q(page=page, profile=profile, is_administrator=True) |
            Q(page=page, profile=profile, is_editor=True)
        )
    except:
        return Response({"success": False, 'response': {'message': 'You are not allowed to change this page banner'}},
                    status=status.HTTP_403_FORBIDDEN)
    serializer = community_serializers.PageBannerSerializer(data=request.data)
    if serializer.is_valid():
        banner = serializer.save()
        post = Post.objects.create(
                profile=profile,
                page=banner.page, 
                text=description,
                page_post=True,
                page_banner=True,
                normal_post=False,
            )
        banner.post = post
        banner.save()
        try:
            cur_banner = PageCurrentBanner.objects.get(page=banner.page)
            cur_banner.banner=banner
            cur_banner.save()
        except:
            PageCurrentBanner.objects.create(
                    page=banner.page,
                    uploaded_by=profile,
                    banner=banner
                )
        serializer = post_serializers.PostGetSerializer(post)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({"success": False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)

# Page Banner Views
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_page_banner(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    added_banner = request.data['added_banner'] if 'added_banner' in request.data else None
    deleted_banner = request.data['deleted_banner'] if 'deleted_banner' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    # Updating request variables
    try:
        request.data._mutable = True
    except:
        pass
    request.data['page'] = page_id
    request.data['uploaded_by'] = profile.id
    if not page_id or not added_banner or not deleted_banner:
        return Response({"success": False, 'response': {'message': 'Missing Field. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        auth_user = PageFollower.objects.get(
            Q(page=page, profile=profile, is_administrator=True) |
            Q(page=page, profile=profile, is_editor=True)
        )
    except:
        return Response({"success": False, 'response': {'message': 'You are not allowed to change this page banner'}},
                    status=status.HTTP_403_FORBIDDEN)
    try:
        deleted_banner = PageBanner.objects.get(page=page, id=deleted_banner, is_deleted=False)
        deleted_banner.delete()
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
            status=status.HTTP_404_NOT_FOUND)
    added_banner = PageBanner.objects.create(page=page,
                                            banner=added_banner,
                                            uploaded_by=profile)

    post = Post.objects.create(
            profile=profile,
            page=added_banner.page, 
            text=description,
            page_post=True,
            page_banner=True,
            normal_post=False,
        )
    added_banner.post = post
    added_banner.save()
    try:
        cur_banner = PageCurrentBanner.objects.get(page=added_banner.page)
        cur_banner.banner=added_banner
        cur_banner.save()
    except:
        PageCurrentBanner.objects.create(
                page=added_banner.page,
                uploaded_by=profile,
                banner=added_banner
            )
    serializer = post_serializers.PostGetSerializer(post)
    return Response({"success": True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)

# Page Logo Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_page_logo(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    logo = request.data['logo'] if 'logo' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    # Updating request variables
    try:
        request.data._mutable = True
    except:
        pass
    request.data['page'] = page_id
    request.data['uploaded_by'] = profile.id
    if not page_id or not logo:
        return Response({"success": False, 'response': {'message': 'Missing Field. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        auth_user = PageFollower.objects.get(
            Q(page=page, profile=profile, is_admin=True) |
            Q(page=page, profile=profile, is_administrator=True) |
            Q(page=page, profile=profile, is_editor=True)
        )
    except:
        return Response({"success": False, 'response': {'message': 'You are not allowed to change this page banner'}},
                    status=status.HTTP_403_FORBIDDEN)
    serializer = community_serializers.PageLogoSerializer(data=request.data)
    if serializer.is_valid():
        logo = serializer.save()
        post = Post.objects.create(
                profile=profile,
                page=logo.page, 
                text=description,
                page_post=True,
                page_logo=True,
                normal_post=False,
            )
        logo.post = post
        logo.save()
        try:
            cur_logo = PageCurrentLogo.objects.get(page=logo.page)
            cur_logo.logo=logo
            cur_logo.save()
        except:
            PageCurrentLogo.objects.create(
                    page=logo.page,
                    uploaded_by=profile,
                    logo=logo
                )
        serializer = post_serializers.PostGetSerializer(post)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({"success": False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def page_image_posts(request):
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            page = Page.objects.get(id=page_id, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Page does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        media_posts = PostMedia.objects.filter(post__page=page, is_deleted=False, post__is_deleted=False, post__is_hidden=False).exclude(post_image='').order_by('-created_at')
        posts_list = []
        for i in media_posts:
            if i.sub_post:
                posts_list.append(str(i.sub_post.id))
            else:
                posts_list.append(str(i.post.id))
        posts = Post.objects.filter(id__in=posts_list)
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(posts, request)
        serializer = post_serializers.PostGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def page_video_posts(request):
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            page = Page.objects.get(id=page_id, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Page does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        media_posts = PostMedia.objects.filter(post__page=page, is_deleted=False, post__is_deleted=False, post__is_hidden=False).exclude(post_video='').order_by('-created_at')
        posts_list = []
        for i in media_posts:
            if i.sub_post:
                posts_list.append(str(i.sub_post.id))
            else:
                posts_list.append(str(i.post.id))
        posts = Post.objects.filter(id__in=posts_list)
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(posts, request)
        serializer = post_serializers.PostGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
        

# Group Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_group_categories(request):
    categories = GroupCategory.objects.all()
    serializer = community_serializers.GroupCategorySerializer(categories, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = request.data['name'] if 'name' in request.data else None
    privacy = request.data['privacy'] if 'privacy' in request.data else None
    if not name and privacy:
        return Response({"success": False, 'response': 'Name and Privacy is required to create a group'},
                        status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        request.data._mutable = True
        try:
            request.data._mutable = True
        except:
            pass
        request.data['created_by'] = Profile.objects.get(user=request.user).id
        serializer = community_serializers.GroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            GroupMember.objects.create(
                profile=group.created_by,
                group=group,
                is_admin=True
            )
            serializer = community_serializers.GetGroupSerializer(group, context={'profile': group.created_by})
            # SEO Meta Creation
            filename ='CSVFiles/XML/groups.xml'
            open_file = open(filename,"r")
            read_file = open_file.read()
            open_file.close()
            new_line = read_file.split("\n")
            last_line = "\n".join(new_line[:-1])
            open_file = open(filename,"w+")
            for i in range(len(last_line)):
                open_file.write(last_line[i])
            open_file.close()

            loc_tag = f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{group.slug}</loc>\n"
            lastmod_tag = f"<lastmod>{group.created_at}</lastmod>\n"
            priorty_tag = f"<priority>0.8</priority>\n</url>\n</urlset>"
            with open(filename, "a") as fileupdate:
                fileupdate.write(loc_tag)
                fileupdate.write(lastmod_tag)
                fileupdate.write(priorty_tag)
            # SEO Meta Close

            return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_group(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(id=id, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Group does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        serializer = community_serializers.GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            serializer = community_serializers.GetGroupSerializer(group, context={'profile': group.created_by})
            return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_group(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        group = Group.objects.get(id=id, is_deleted=False)
    except ObjectDoesNotExist:
        return Response({"success": False, 'response': {'message': 'Group does not exist.'}},
                status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST)
    group.is_deleted = True
    group.save()
    posts = Post.objects.filter(group=group)
    for i in posts:
        i.is_deleted = True
        i.save()
    return Response({'success': True, 'response': {'message': 'Group deleeted successfuly!'}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_group(request):
    group = request.query_params.get('group')
    if not group:
        return Response({"success": False, 'response': 'Invalid Data. Data Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(slug=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        try:
            profile = Profile.objects.get(user=request.user)
        except:
            profile = None
        if profile:
            serializer = community_serializers.GetGroupSerializer(group, context={'profile': profile})
        else:
            serializer = community_serializers.GetGroupSerializer(group)

        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_user_groups(request):
    profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    groups = Group.objects.filter(groupmember_usergroup__profile=profile, is_deleted=False)
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(groups, request)
    serializer = community_serializers.DefaultGroupSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def group_join_request(request):
    group = request.data['group'] if 'group' in request.data else None
    if not group:
        return Response({'success': False, 'response': {'message': 'Missing fields Profile or Group ID. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        # Group Check
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        # Profile Check
        profile = Profile.objects.get(user=request.user)
        try:
            request.data._mutable = True
        except:
            pass
        request.data['profile'] = profile.id
        # Request Check
        try:
            req = GroupRequest.objects.get(profile=profile, group=group, status='Pending', is_active=True)
            return Response({'success': False, 'response': {'message': 'Request sent already.'}},
                        status=status.HTTP_400_BAD_REQUEST)
        except:
            serializer = community_serializers.GroupRequestSerializer(data=request.data)
            if serializer.is_valid():
                req = serializer.save()
                group_invite = GroupInvite.objects.filter(group=group, profile=profile)
                for i in group_invite:
                    i.delete()
                # Send Notification For Page Invite
                notification = Notification(
                        type = 'GroupJoinRequest',
                        profile = profile,
                        text = f'Sent Group Join request to {group.name}',
                        group = group,
                    )
                notification.save()
                group_admins = GroupMember.objects.filter(group=group, is_admin=True)
                group_admins_ids = list(group_admins.values_list('profile__id', flat=True))
                for i in group_admins:
                    notification.notifiers_list.add(i.profile)
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
                try:
                    notification_image = GroupCurrentBanner.objects.get(group=group).banner.banner.url
                    notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
                except:
                    notification_image = None
                try:
                    devices = FCMDevice.objects.filter(device_id__in=group_admins_ids)
                    fb_body = {
                        'created_at': str(datetime.datetime.now()),
                        'type': 'GroupJoinRequest',
                        'profile': str(profile.id),
                        'text': f"{profile.user.first_name} {profile.user.last_name} requested to join {group.name}.",
                        'group': str(group.id),
                    }
                    devices.send_message(
                        Message(
                            data=fb_body,
                            notification=FB_Notification(
                                title="Group Join Request",
                                body=fb_body['text'],
                                image=notification_image)
                    ))
                except Exception as e:
                    print("Firebase exception in group join", e)
                serializer = community_serializers.GetGroupRequestSerializer(req)
                return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'response': {'message': serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_group_join_request(request):
    group = request.data['group'] if 'group' in request.data else None
    profile = request.data['profile'] if 'profile' in request.data else None
    req_status = request.data['req_status'] if 'req_status' in request.data else None
    if not group or not profile or not req_status:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        # Group Check
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        # Profile Check
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        # Request Check
        try:
            req = GroupRequest.objects.get(profile=profile, group=group, status='Pending', is_active=True)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        approved_by = Profile.objects.get(user=request.user)
        # Approver Admin Check
        if approved_by != profile:
            try:
                admin = GroupMember.objects.get(profile=approved_by, group=group, is_admin=True)
            except Exception as e:
                return Response({"success": False, 'response': {'message': 'Non admin users cannot approve a group request'}},
                        status=status.HTTP_403_FORBIDDEN)
            # Cancel Request
            if req_status == "Cancelled":
                req.status = 'Cancelled'
                req.is_active = False
                req.delete()
                return Response({"success": True, 'response': {'message': 'Request cancelled successfuly!'}},
                        status=status.HTTP_200_OK)
            # Approve Request
            elif req_status == "Approved":
                req.status = 'Approved'
                req.is_active = False
                req.delete()
                try:
                    member = GroupMember.objects.create(
                            profile=profile,
                            group=group,
                            approved_by=admin.profile
                        )
                    # Send Notification For Group Request Confirm
                    notification = Notification(
                            type = 'ConfirmGroupJoinRequest',
                            profile = profile,
                            text = f'Your request to join {group.name} group was approved by {admin.profile.user.first_name} {admin.profile.user.last_name}',
                            group = group,
                        )
                    notification.save()
                    notification.notifiers_list.add(profile)
                    notification.save()
                    try:
                        send_notifications_ws(notification)
                    except:
                        pass
                    try:
                        notification_image = GroupCurrentBanner.objects.get(group=group).banner.banner.url
                        notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
                    except:
                        notification_image = None
                    try:
                        devices = FCMDevice.objects.filter(device_id=profile.id)
                        fb_body = {
                            'created_at': str(datetime.datetime.now()),
                            'type': 'ConfirmGroupJoinRequest',
                            'profile': str(profile.id),
                            'text': f'Your request to join {group.name} group was approved by {admin.profile.user.first_name} {admin.profile.user.last_name}',
                            'group': str(group.id),
                        }
                        devices.send_message(
                            Message(
                                data=fb_body,
                                notification=FB_Notification(
                                    title="Confirm Group Join Request",
                                    body=fb_body['text'],
                                    image=notification_image)
                        ))
                    except Exception as e:
                        print("Firebase exception in group join", e)
                    return Response({"success": True, 'response': {'message': 'Request approved successfuly!'}},
                            status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"success": False, 'response': {'message': str(e)}},
                            status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, 'response': {'message': 'Invalid Request Status!'}},
                        status=status.HTTP_400_BAD_REQUEST)
        else:
            if req_status == "Cancelled":
                req.status = 'Cancelled'
                req.is_active = False
                req.delete()
                return Response({"success": True, 'response': {'message': 'Request cancelled successfuly!'}},
                        status=status.HTTP_200_OK)
            else:
                return Response({"success": False, 'response': {'message': 'Invalid Choice'}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_group_admin(request):
    group = request.data['group'] if 'group' in request.data else None
    profile = request.data['profile'] if 'profile' in request.data else None
    if not group or not profile:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        # Group Check
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        # Profile Check
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        # Admin Check
        admin = Profile.objects.get(user=request.user)
        try:
            admin = GroupMember.objects.get(profile=admin, group=group, is_admin=True)
        except Exception as e:
            return Response({"success": False, 'response': {'message': 'User is not Admin'}},
                    status=status.HTTP_403_FORBIDDEN)
        # Member Check
        try:
            member = GroupMember.objects.get(profile=profile, group=group)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        member.is_admin = True
        member.save()
        return Response({"success": True, 'response': {'message': 'Adminship confirmed successfuly!'}},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member(request):
    group = request.data['group'] if 'group' in request.data else None
    profile = request.data['profile'] if 'profile' in request.data else None
    if not group or not profile:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        # Admin Check
        admin = Profile.objects.get(user=request.user)
        try:
            admin = GroupMember.objects.get(profile=admin, group__id=group, is_admin=True)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Admin is not an admin'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        # Member Check
        try:
            member = GroupMember.objects.get(profile__id=profile, group__id=group)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'User does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        member.delete()
        return Response({"success": True, 'response': {'message': 'Member removed successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def leave_group(request):
    group = request.data['group'] if 'group' in request.data else None
    if not group:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        try:
            member = GroupMember.objects.get(profile=profile, group__id=group)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'User does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        member.delete()
        return Response({"success": True, 'response': {'message': 'Group left successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_group_requests(request):
    group = request.query_params.get('group')
    if not group:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Group does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        reqs = GroupRequest.objects.filter(group=group, status='Pending', is_active=True).order_by('-created_at')
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(reqs, request)
        serializer = community_serializers.GetGroupRequestSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_group_admins(request):
    group = request.query_params.get('group')
    if not group:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Group does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        reqs = GroupMember.objects.filter(group=group, is_admin=True)
        serializer = community_serializers.GroupMemberSerializer(reqs, many=True)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_group_members(request):
    group = request.query_params.get('group')
    if not group:
        return Response({'success': False, 'response': {'message': 'Missing fields. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Group does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        reqs = GroupMember.objects.filter(group=group)
        serializer = community_serializers.GroupMemberSerializer(reqs, many=True)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_group_members_ids(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    group = request.query_params.get('group')
    if not group:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        group = Group.objects.get(id=group, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        friends = list(FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True))
    except Exception as e:
        friends = None
    group_members = list(GroupMember.objects.filter(profile__id__in=friends, group=group).values_list('profile__id', flat=True))
    return Response({"success": True, 'response': {'message': group_members}},
                status=status.HTTP_200_OK)


# Group Rules Cruds
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group_rule(request):
    serializer = community_serializers.GroupRuleSerializer(data=request.data)
    if serializer.is_valid():
        rule = serializer.save()
        serializer = community_serializers.GroupRuleSerializer(rule)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({"success": False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_group_rule(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            rule = GroupRule.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Rule does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
    serializer = community_serializers.GroupRuleSerializer(rule, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        serializer = community_serializers.GroupRuleSerializer(rule)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    else:
        return Response({"success": False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_group_rule(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            rule = GroupRule.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Rule does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        rule.delete()
        return Response({"success": True, 'response': {'message': 'Rule deleted successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_group_rules(request):
    group = request.query_params.get('group')
    if not group:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Group does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        rules  = GroupRule.objects.filter(group=group)
        print(rules)
        serializer = community_serializers.GroupRuleSerializer(rules, many=True)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def discover_groups(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    # Category Based Suggestions
    try:
        friends = FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True)
    except Exception as e:
        print(e)
        friends = None
    if friends:
        groups = Group.objects.filter(is_deleted=False, is_hidden=False).exclude(groupmember_usergroup__profile=profile).exclude(groupmember_usergroup__profile__id__in=friends).exclude(grouprequest_usergroup__status='Pending', grouprequest_usergroup__profile=profile)
    else:
        groups = Group.objects.filter(is_deleted=False, is_hidden=False).exclude(groupmember_usergroup__profile=profile).exclude(grouprequest_usergroup__status='Pending', grouprequest_usergroup__profile=profile)[:20]
    serializer = community_serializers.DefaultGroupSerializer(groups, many=True)
    return Response({"success": True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends_groups(request):
    profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    try:
        friends = FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True)
    except Exception as e:
        print(e)
        friends = None
    if friends:
        groups = Group.objects.filter(is_deleted=False, is_hidden=False, groupmember_usergroup__profile__id__in=friends).exclude(groupmember_usergroup__profile=profile).exclude(grouprequest_usergroup__status='Pending', grouprequest_usergroup__profile=profile)
    else:
        groups = []
        return Response({"success": True, 'response': {'message': groups}},
                status=status.HTTP_200_OK)
    serializer = community_serializers.DefaultGroupSerializer(groups, many=True)
    return Response({"success": True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group_invite(request):
    group = request.data['group'] if 'group' in request.data else None
    profiles = request.data['profiles'] if 'profiles' in request.data else None
    if not group or not profiles:
        return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        group = Group.objects.get(id=group, is_deleted=False)
    except:
        return Response({"success": False, 'response': {'message': 'Group does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    invited_by = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    members = profiles[1:-1].replace('"', "").split(',')
    for i in members:
        try:
            profile = Profile.objects.get(id=i, is_deleted=False, user__is_active=True)
            try:
                member = GroupMember.objects.get(profile=profile, group=group)
            except:
                GroupInvite.objects.create(
                        profile = profile,
                        group = group,
                        invited_by = invited_by,
                    )
                # Send Notification For Group Invite
                notification = Notification(
                        type = 'GroupInvite',
                        profile = invited_by,
                        text = f'invited you to the group {group.name}',
                        group = group,
                    )
                notification.save()
                notification.notifiers_list.add(profile)
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
                try:
                    notification_image = UserProfilePicture.objects.get(profile=invited_by).picture.picture.url
                    notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
                except:
                    notification_image = None
                try:
                    devices = FCMDevice.objects.filter(device_id=profile.id)
                    fb_body = {
                        'created_at': str(datetime.datetime.now()),
                        'type': 'GroupInvite',
                        'profile': str(profile.id),
                        'invited_by': str(invited_by.id),
                        'text': f"{invited_by.user.first_name} {invited_by.user.last_name} invited you to the group {group.name}.",
                        'group': str(group.id),
                    }
                    devices.send_message(
                        Message(
                            data=fb_body,
                            notification=FB_Notification(
                                title="Group Invite",
                                body=fb_body['text'],
                                image=notification_image)
                    ))
                except:
                    pass
        except:
            pass
    return Response({"success": True, 'response': {'message': 'Invite Sent'}},
                    status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_group_invite(request):
    group = request.data['group'] if 'group' in request.data else None
    profile = request.data['profile'] if 'profile' in request.data else None
    if not group or not profile:
        return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        group = Group.objects.get(id=group, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        invitation = GroupInvite.objects.get(profile=profile, group=group, is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    invitation.delete()
    return Response({"success": True, 'response': {'message': 'Invitation cancelled successfuly!!'}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_group_invites(request):
    group = request.query_params.get('group')
    if not group:
        return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        group = Group.objects.get(id=group, is_deleted=False)
    except:
        return Response({"success": False, 'response': {'message': 'Group does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    invited_list = list(GroupInvite.objects.filter(group=group, is_active=True).values_list('profile__id', flat=True))
    return Response({"success": True, 'response': {'message': invited_list}},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_group_invite_profiles(request):
    group = request.query_params.get('group')
    if not group:
        return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        group = Group.objects.get(id=group, is_deleted=False)
    except:
        return Response({"success": False, 'response': {'message': 'Group does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    invited_list = list(GroupInvite.objects.filter(group=group, is_active=True).values_list('profile__id', flat=True))
    profiles = Profile.objects.filter(id__in=invited_list, is_deleted=False, user__is_active=True)
    serializer = post_serializers.DefaultProfileSerializer(profiles, many=True)
    return Response({"success": True, 'response': {'message': serializer.data}},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_group_invites(request):
    profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    try:
        invitations = GroupInvite.objects.filter(profile=profile, is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
    serializer = community_serializers.GetGroupInviteSerializer(invitations, many=True, context={"profile": profile})
    return Response({"success": True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Group Post Views
@api_view(['GET'])
@permission_classes([AllowAny])
def get_group_posts(request):
    group = request.query_params.get('group')
    if not group:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        except:
            profile = None
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        if profile:
            try:
                hidden_posts = HiddenPost.objects.filter(profile=profile, post__group=group).values_list('post__id', flat=True)
                posts = Post.objects.filter(group=group, is_deleted=False, is_hidden=False).exclude(id__in=hidden_posts).order_by('-created_at')
            except Exception as e:
                return Response({"success": False, 'response': {'message': str(e)}},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            posts = Post.objects.filter(group=group, is_deleted=False, is_hidden=False).order_by('-created_at')
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(posts, request)
        if profile:
            serializer = post_serializers.PostGetSerializer(result_page, many=True, context={'profile': profile})
        else:
            serializer = post_serializers.PostGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_groups_feed(request):
    profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    groups = GroupMember.objects.filter(profile=profile).values_list('group__id', flat=True)
    hidden_posts = HiddenPost.objects.filter(profile=profile).values_list('post__id', flat=True)
    posts = Post.objects.filter(group__id__in=groups, is_deleted=False, is_hidden=False
                ).select_related(
                    'profile', 'group'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'pollpost_post', 'taguser_post', 'sharedpost_post'
                ).exclude(id__in=hidden_posts).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(posts, request)
    serializer = post_serializers.PostGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Group Banner Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_group_banner(request):
    group = request.data['group'] if 'group' in request.data else None
    banner = request.data['banner'] if 'banner' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    if not group or not banner:
        return Response({"success": False, 'response': {'message': 'Missing Field. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        try:
            request.data._mutable = True
        except:
            pass
        request.data['uploaded_by'] = profile.id
        serializer = community_serializers.GroupBannerSerializer(data=request.data)
        if serializer.is_valid():
            banner = serializer.save()
            post = Post.objects.create(
                    profile=profile,
                    group=banner.group, 
                    text=description,
                    group_post=True,
                    group_banner=True,
                    normal_post=False,
                )
            banner.post = post
            banner.save()
            try:
                cur_banner = GroupCurrentBanner.objects.get(group=banner.group)
                cur_banner.banner=banner
                cur_banner.save()
            except:
                GroupCurrentBanner.objects.create(
                        group=banner.group,
                        uploaded_by=profile,
                        banner=banner
                    )
            context = {
                'profile': profile
            }
            serializer = post_serializers.PostGetSerializer(post, context=context)
            return Response({"success": True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': {'message': serializer.errors}},
                        status=status.HTTP_400_BAD_REQUEST)

# Group Logo Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_group_logo(request):
    group = request.data['group'] if 'group' in request.data else None
    logo = request.data['logo'] if 'logo' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    if not group or not logo:
        return Response({"success": False, 'response': {'message': 'Missing Field. Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        try:
            request.data._mutable = True
        except:
            pass
        request.data['uploaded_by'] = profile.id
        serializer = community_serializers.GroupLogoSerializer(data=request.data)
        if serializer.is_valid():
            logo = serializer.save()
            post = Post.objects.create(
                    profile=profile,
                    group=logo.group, 
                    text=description,
                    group_post=True,
                    group_logo=True,
                    normal_post=False,
                )
            logo.post = post
            logo.save()
            try:
                cur_logo = GroupCurrentLogo.objects.get(group=logo.group)
                cur_logo.logo=logo
                cur_logo.save()
            except:
                GroupCurrentLogo.objects.create(
                        group=logo.group,
                        uploaded_by=profile,
                        logo=logo
                    )
            context = {
                'profile': profile
            }
            serializer = post_serializers.PostGetSerializer(post, context=context)
            return Response({"success": True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': {'message': serializer.errors}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def group_image_posts(request):
    group = request.query_params.get('group')
    if not group:
        return Response({"success": False, 'response': 'Invalid Data. ID Missing.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        try:
            profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        except:
            profile = None
        media_posts = PostMedia.objects.filter(post__group=group, is_deleted=False, post__is_deleted=False, post__is_hidden=False).exclude(post_image='').order_by('-created_at')
        posts_list = []
        for i in media_posts:
            if i.sub_post:
                posts_list.append(str(i.sub_post.id))
            else:
                posts_list.append(str(i.post.id))
        posts = Post.objects.filter(id__in=posts_list)
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(posts, request)
        if profile:
            serializer = post_serializers.PostGetSerializer(result_page, many=True, context={'profile': profile})
        else:
            serializer = post_serializers.PostGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def group_video_posts(request):
    group = request.query_params.get('group')
    if not group:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        try:
            profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        except:
            profile = None
        media_posts = PostMedia.objects.filter(post__group=group, is_deleted=False, post__is_deleted=False, post__is_hidden=False).exclude(post_video='').order_by('-created_at')
        posts_list = []
        for i in media_posts:
            if i.sub_post:
                posts_list.append(str(i.sub_post.id))
            else:
                posts_list.append(str(i.post.id))
        posts = Post.objects.filter(id__in=posts_list)
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(posts, request)
        if profile:
            serializer = post_serializers.PostGetSerializer(result_page, many=True, context={'profile': profile})
        else:
            serializer = post_serializers.PostGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_pending_posts(request):
    group = request.query_params.get('group')
    if not group:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(user=request.user)
        posts = Post.objects.filter(group=group, is_deleted=True, is_declined=False,
                                    is_hidden=False, is_approved=False).order_by('-created_at')
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(posts, request)
        context = {
            'profile': profile
        }
        serializer = post_serializers.PostGetSerializer(result_page, many=True, context=context)
        return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_pending_group_post(request):
    post = request.data['post'] if 'post' in request.data else None
    group = request.data['group'] if 'group' in request.data else None
    approval_status = request.data['approval_status'] if 'approval_status' in request.data else 'Approved'
    if not post or not group:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        # Check if Group exists
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        # Check if Post Exists
        try:
            post = Post.objects.get(id=post, is_approved=False, group=group)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(user=request.user)
        # Check if user is the group admin
        try:
            group_admin = GroupMember.objects.get(group=group, profile=profile, is_admin=True)
        except:
            return Response({"success": False, 'response': {'message': 'Members that are not admin cannot approve a group post.'}},
                    status=status.HTTP_403_FORBIDDEN)
        if approval_status == 'Approved':
            post.is_approved = True
            post.is_deleted = False
            post.is_declined = False
            post.save()
            # Send Notification For Page Invite
            notification = Notification(
                    type = 'GroupPostApproved',
                    profile = profile,
                    text = f'Approved your post to the Group {group.name}',
                    group = group,
                )
            notification.save()
            notification.notifiers_list.add(post.profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
            try:
                notification_image = GroupCurrentBanner.objects.get(group=group).banner.banner.url
                notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
            except:
                notification_image = None
            try:
                devices = FCMDevice.objects.filter(device_id=post.profile)
                fb_body = {
                    'created_at': str(datetime.datetime.now()),
                    'type': 'GroupPostApproved',
                    'profile': str(profile.id),
                    'text': f"{profile.user.first_name} {profile.user.last_name} approved your to post to the group {group.name}.",
                    'group': str(group.id),
                }
                devices.send_message(
                    Message(
                        data=fb_body,
                        notification=FB_Notification(
                            title="Group Post Approved",
                            body=fb_body['text'],
                            image=notification_image)
                ))
            except Exception as e:
                print("Firebase exception in group post approve", e)
            return Response({"success": True, 'response': {'message': 'Post approved to be added to the Group'}},
                    status=status.HTTP_200_OK)
        elif approval_status == 'Cancelled':
            post.is_approved = False
            post.is_declined = True
            post.is_deleted = True
            post.save()
            # Send Notification For Page Invite
            notification = Notification(
                    type = 'GroupPostDeclined',
                    profile = profile,
                    text = f'Declined your post to the Group {group.name}',
                    group = group,
                )
            notification.save()
            notification.notifiers_list.add(post.profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
            try:
                notification_image = GroupCurrentBanner.objects.get(group=group).banner.banner.url
                notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
            except:
                notification_image = None
            try:
                devices = FCMDevice.objects.filter(device_id=post.profile)
                fb_body = {
                    'created_at': str(datetime.datetime.now()),
                    'type': 'GroupPostDeclined',
                    'profile': str(profile.id),
                    'text': f"{profile.user.first_name} {profile.user.last_name} declined your to post to the group {group.name}.",
                    'group': str(group.id),
                }
                devices.send_message(
                    Message(
                        data=fb_body,
                        notification=FB_Notification(
                            title="Group Post Declined",
                            body=fb_body['text'],
                            image=notification_image)
                ))
            except Exception as e:
                print("Firebase exception in group post decline", e)
            return Response({"success": True, 'response': {'message': 'Post declined to be added to the Group'}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_all_pending_group_posts(request):
    group = request.data['group'] if 'group' in request.data else None
    approval_status = request.data['approval_status'] if 'approval_status' in request.data else 'Approved'
    if not group:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        # Check if Group exists
        try:
            group = Group.objects.get(id=group, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(user=request.user)
        # Check if user is the group admin
        try:
            group_admin = GroupMember.objects.get(group=group, profile=profile, is_admin=True)
        except:
            return Response({"success": False, 'response': {'message': 'Members that are not admin cannot approve a group post.'}},
                    status=status.HTTP_403_FORBIDDEN)
        posts = Post.objects.filter(group=group, is_approved=False, is_declined=False)
        if approval_status == 'Approved':
            for post in posts:
                post.is_approved = True
                post.is_deleted = False
                post.is_declined = False
                post.save()
                # Send Notification For Page Invite
                notification = Notification(
                        type = 'GroupPostApproved',
                        profile = profile,
                        text = f'Approved your post to the Group {group.name}',
                        group = group,
                    )
                notification.save()
                notification.notifiers_list.add(post.profile)
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
                try:
                    notification_image = GroupCurrentBanner.objects.get(group=group).banner.banner.url
                    notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
                except:
                    notification_image = None
                try:
                    devices = FCMDevice.objects.filter(device_id=post.profile)
                    fb_body = {
                        'created_at': str(datetime.datetime.now()),
                        'type': 'GroupPostApproved',
                        'profile': str(profile.id),
                        'text': f"{profile.user.first_name} {profile.user.last_name} approved your to post to the group {group.name}.",
                        'group': str(group.id),
                    }
                    devices.send_message(
                        Message(
                            data=fb_body,
                            notification=FB_Notification(
                                title="Group Post Approved",
                                body=fb_body['text'],
                                image=notification_image)
                    ))
                except Exception as e:
                    print("Firebase exception in group post approve", e)
            return Response({"success": True, 'response': {'message': 'All Posts approved to be added to the Group'}},
                    status=status.HTTP_200_OK)
        elif approval_status == 'Cancelled':
            for post in posts:    
                post.is_approved = False
                post.is_declined = True
                post.is_deleted = True
                post.save()
                # Send Notification For Page Invite
                notification = Notification(
                        type = 'GroupPostDeclined',
                        profile = profile,
                        text = f'Declined your post to the Group {group.name}',
                        group = group,
                    )
                notification.save()
                notification.notifiers_list.add(post.profile)
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
                try:
                    notification_image = GroupCurrentBanner.objects.get(group=group).banner.banner.url
                    notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
                except:
                    notification_image = None
                try:
                    devices = FCMDevice.objects.filter(device_id=post.profile)
                    fb_body = {
                        'created_at': str(datetime.datetime.now()),
                        'type': 'GroupPostDeclined',
                        'profile': str(profile.id),
                        'text': f"{profile.user.first_name} {profile.user.last_name} declined your to post to the group {group.name}.",
                        'group': str(group.id),
                    }
                    devices.send_message(
                        Message(
                            data=fb_body,
                            notification=FB_Notification(
                                title="Group Post Declined",
                                body=fb_body['text'],
                                image=notification_image)
                    ))
                except Exception as e:
                    print("Firebase exception in group post decline", e)
            return Response({"success": True, 'response': {'message': 'All Posts declined to be added to the Group'}},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_page_logo(request):
    id = request.data['id'] if 'id' in request.data else None
    page_id = request.data['page_id'] if 'page_id' in request.data else None
    if not id and not page_id:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': 'Invalid User Profile'},
                    status=status.HTTP_401_UNAUTHORIZED)
    try:
        page = Page.objects.get(id=page_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': str(e)},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        auth_user = PageFollower.objects.get(
            Q(page=page, profile=profile, is_admin=True) |
            Q(page=page, profile=profile, is_administrator=True) |
            Q(page=page, profile=profile, is_editor=True)
        )
    except:
        return Response({"success": False, 'response': {'message': 'You are not allowed to change this page banner'}},
                    status=status.HTTP_403_FORBIDDEN)

    try:
        logo = PageLogo.objects.get(id=id, is_deleted=False)
        logo.is_deleted=True
        logo.save()
        return Response({"success": False, 'response': {'message': 'Page Logo deleted successfully'}},
            status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_group_logo(request):
    id = request.data['id'] if 'id' in request.data else None
    group_id = request.data['group_id'] if 'group_id' in request.data else None
    if not id and not group_id:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': 'Invalid User Profile'},
                    status=status.HTTP_401_UNAUTHORIZED)
    try:
        group = Group.objects.get(id=group_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': str(e)},
                    status=status.HTTP_404_NOT_FOUND)

    try:
        logo = GroupLogo.objects.get(id=id, uploaded_by=profile, is_deleted=False, group=group)
        logo.is_deleted=True
        logo.save()
        return Response({"success": False, 'response': {'message': 'Group Logo deleted successfully'}},
            status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def accept_group_invite(request):
    group_id =  request.data['group_id'] if 'group_id' in request.data else None
    if not group_id:
        return Response({"success": False, 'response': 'Invalid Data'},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': str(e)},
            status=status.HTTP_401_UNAUTHORIZED)
    try:
        group = Group.objects.get(id=group_id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': str(e)},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        invite = GroupInvite.objects.get(group=group, profile=profile)
        invite.is_active = False
        invite.save()
        return Response({"success": True, 'response': 'Request accepted successfully!'},
                            status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"success": False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

