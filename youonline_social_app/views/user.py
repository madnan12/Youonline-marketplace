from functools import partial
import profile
from ssl import VERIFY_X509_TRUSTED_FIRST
from unicodedata import category
from django.contrib.auth import authenticate, logout
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from job_app.models import Company, CompanyCoverImage, CompanyLogo
from ..custom_api_settings import CustomPagination, NewsFeedPagination
from ..constants import *
from ..decorators import *
from ..models import *
from django.db.models import Q
from ..serializers.users_serializers import *
from ..serializers.post_serializers import *
import random, string
from django.conf import settings
from twilio.rest import Client
import environ
import json
import requests
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from job_app.models import *
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from itertools import chain
from operator import attrgetter
from django.contrib.auth.hashers import make_password
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FB_Notification
from fcm_django.models import FCMDevice
from datetime import date, datetime , timedelta
from rest_framework.authtoken.models import Token
from youonline_social_app.youonline_threads import *
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from youonline_social_app.websockets.Constants import send_notifications_ws

import boto3
env = environ.Env()
environ.Env.read_env()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@api_view(['GET'])
@permission_classes([AllowAny])
def TestingRandom(request):

    return Response(
        {
            'status' : 'test',
        }
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def send_socket_notification(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'Notification-{str(request.user.profile_user.id)}',
        {
            'type' : 'chat.message',
            'message' : {'You are' : request.user.username}
        }
    )

    return Response(
        {
            'status' : 'send',
        }
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def testImageLabel(request):
    all_images = [
        'post_images/2022/04/spamImage3_bEf51d4BEC.jpeg',
        'post_images/2022/04/spamImage5_a118C7Fa24.jpeg',
        'post_images/2022/04/spamImage6_c53a0ca1a7.jpeg',
        'covers/4_1_BDD8A93A98.jpeg',
        'pictures/sanjana_kaur_712c1b6059.jpeg',
        'post_images/2022/04/Shweta_Delhi_Escort_9ACCF9A77e.jpeg',
        'covers/1300915651_1-191_nevseoboi_6d46D897B9.jpeg',
        'post_images/2022/04/Edhy2rUU4AAYrYQ_e2a7E0c517.jpeg',
        'pictures/Aisha_Bhatt_Fc08af05aF.jpeg',
        'covers/740full-marisol-yotta_1_CA1CBddc71.jpeg',
        'pictures/640full-marisol-yotta_FffeF56A7d.jpeg',
        'covers/KHALL_66a11Efa4A.jpeg',
        'pictures/khal_48b4fCE749.jpeg',
        'covers/17577-11_ddad0Ea04A.jpeg',
        'pictures/166af1_da7764ece2a54b1685b08019a5aaabe8_mv2_50f92b60d8.jpeg',
        'pictures/b3096e57523c_d0C6038c9b.jpeg',
        'covers/women-model-long-hair-closed-eyes-in-bed-smiling-275677-wallhere_7AFCc2C6F0.jpeg',
        'covers/213256415165-491_original_ECA25D061f.jpeg',
        'pictures/88fcb48b26e27593019c31267665dfec_e271914f7e.jpeg',
        'pictures/2022_04_11_18_16_17_777_E18a86b01e.jpeg',
        'covers/6_abD20CcCC6.jpeg',
        'pictures/1_3_bA4d2A4cCe.jpeg',
        'post_images/2022/04/preeti-banik-ammk_D152Cc4d62.jpeg',
        'post_images/2022/04/spamImage6_66cCEBF3fe.jpeg',
        'post_images/2022/04/spamImage7_9caC05e138.jpeg',
        'post_images/2022/04/spamImage9_b78A99Abe6.jpeg',
        'post_images/2022/04/spamImage10_7C90c36Bb2.jpeg',
        'post_images/2022/04/spamImage11_86c8346b9F.jpeg',

        'post_images/2022/04/spamImage12_Cc1165bAE5.jpeg',
        'post_images/2022/04/spamImage13_49c7Ed2eda.jpeg',
    ]


    MEDIA_URL = 'https://youonlinev2.s3.amazonaws.com/'

    session = boto3.Session(
        aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
    )
    client = session.client('rekognition', region_name='ap-southeast-1')

    all_content = {}

    global_labels = []

    for img in all_images:
        image_labels = client.detect_moderation_labels(
            Image = {
                'S3Object': {
                    'Bucket' : settings.AWS_STORAGE_BUCKET_NAME,
                    'Name' : img
                },
            },
        )
        all_labels = []
        for lb in image_labels['ModerationLabels']:
            if lb['Name'] and lb['Name'] != '':
                all_labels.append(lb['Name'])
                global_labels.append(lb['Name'])
            
            if lb['ParentName'] and lb['ParentName'] != '':
                all_labels.append(lb['ParentName'])
                global_labels.append(lb['ParentName'])

        all_labels = list(set(all_labels))
        all_content[f'{MEDIA_URL}{img}'] = all_labels

    global_labels = list(set(global_labels))



    return Response(
        {
            'global labels' : global_labels,
            'image_labels' :all_content
        }
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


def send_sms(number, code):
    account_sid = env('ACCOUNT_SID')
    auth_token = env('AUTH_TOKEN')
    phone_number = env('PHONE_NUMBER')
    client = Client(account_sid, auth_token)

    code = str(code)
    message = client.messages.create(
        body='Welcome to YouOnline! Your verification code is' + code,
        from_=phone_number,
        to=number
    )
    print(message.sid)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data
    email = request.data.get('email').lower().strip() if 'email' in data else None
    password = data['password'] if 'password' in data else None
    if not email or not password:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
			        status=status.HTTP_400_BAD_REQUEST)
    if email:
        try:
            profile = User.objects.get(email=email)
        except:
            return Response({"success": False, 'response': {'message': 'User with this email does\'nt exist.'}},
                            status=status.HTTP_401_UNAUTHORIZED)

    if email is not None:
        try:
            profile = User.objects.get(email=email, is_active=True)
            parent_username = profile.username
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Your Profile is not Active'}},
                            status=status.HTTP_404_NOT_FOUND)
        user = authenticate(username=parent_username, password=password)
        if not user:
            return Response({"success": False, 'response': {'message': 'Incorrect User Credentials!'}},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            """
            Creating new token 
            """
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=user)
            access_token = token.key
    profile = Profile.objects.get(user=user, is_deleted=False)
    context = {
        'profile': profile,
        'visited_profile': profile
    }
    profile_obj = DefaultProfileSerializer(profile, context=context).data
    try:
        LoginHistory.objects.create(
            profile = profile,
            login_at = datetime.now(),
        )
    except Exception as e:
        print(e)
    return Response({'success': True, 'response': {'profile': profile_obj, 'access_token': access_token}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    request.user.auth_token.delete()
    return Response({'success': True, 'response': {'message': 'User Logged Out Successfully'}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    visited_profile = request.query_params.get('visited_profile', None)
    if not visited_profile:
        return Response({'success': False, 'response': {'message': 'Please provide a valid ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        except Exception as e:
            profile = None

        try:
            visited_profile = Profile.objects.get(id=visited_profile, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        if profile and profile != visited_profile:
            ProfileView.objects.create(
                    profile=visited_profile,
                    viewer=profile
                )
        if profile:
            serializer = SearchUserProfileSerializer(visited_profile, many=False, context={'profile': profile, 'visited_profile':visited_profile})
        else:
            serializer = SearchUserProfileSerializer(visited_profile, many=False, context={'visited_profile':visited_profile})

        results = serializer.data
        # if visited_profile == profile:
            # notification_count = Notification.objects.filter(notifiers_list=profile).exclude(read_by=profile).count()
            # hidden_post_count = HiddenPost.objects.filter(profile=profile, post__is_deleted=False).count()
            # friend_req_count = FriendRequest.objects.filter(
            #     req_receiver=profile, 
            #     is_active=True, 
            #     status='Pending',
            #     is_read=False
            # ).count()
            # results.update({"notification_count":notification_count})
            # results.update({"hidden_post_count":hidden_post_count})
            # results.update({"friend_request_count":friend_req_count})

        return Response({'success': True, 'response':results},
                status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_user_profile(request):
#         try:
#             profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
#         except Exception as e:
#                 return Response({'success': False, 'response':{'message':str(e)}},
#                             status=status.HTTP_404_NOT_FOUND)
#         serializer = DefaultProfileSerializer(profile)
#         return Response({'success': True, 'response':serializer.data},
#                             status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    full_name = request.data['full_name'] if 'full_name' in request.data else None
    email = request.data.get('email').lower() if 'email' in request.data else None
    password = request.data['password'] if 'password' in request.data else None
    confirm_password = request.data['confirm_password'] if 'confirm_password' in request.data else None

    if not full_name:
        return Response({"success": False, 'response':{'message':'Full Name is required for Sign Up!'}},
                        status=status.HTTP_400_BAD_REQUEST)

    if not email:
        return Response({"success": False, 'response': {'message':'Email is required for Sign Up!'}},
                        status=status.HTTP_400_BAD_REQUEST)

    if not password:
        return Response({"success": False, 'response': {'message':'Password is required for Sign Up!'}},
                        status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 8:
        return Response({"success": False, 'response': {'message' :'Please enter a strong password!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    
    if password != confirm_password:
        return Response({"success": False, 'response': {'message': 'Password Not Matched!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        return Response({"success": False, 'response': {'message':'User with this email address is already registered!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    except:
        pass

    random_digits_for_code = ''.join(
        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
    verification = VerificationCode.objects.create(code=random_digits_for_code)
    html_template = render_to_string('email/u-forgot-password.html',
                                     {'code': verification.code, 'img_link': settings.DOMAIN_NAME})
    text_template = strip_tags(html_template)
    # Getting Email ready
    send_email = EmailMultiAlternatives(
        'YouOnline | Verification Code',
        text_template,
        settings.EMAIL_HOST_USER,
        [email]
    )
    send_email.attach_alternative(html_template, "text/html")
    try:
        send_email.send(fail_silently=False)
    except:
        return Response({"success": False, 'response':{'message': 'Email server failed!'}},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)

    username = email.split('@')[0]
    try:
        user = User.objects.create(
            first_name=full_name,
            email=email,
            username=username,
            is_active=False,
        )
    except:
        username_digits = ''.join(
            random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
        user = User.objects.create(
            first_name=full_name,

            email=email,
            username=username,
            is_active=False,
        )
    user.set_password(password)
    user.save()
    verification.user = user
    verification.save()
    profile = Profile.objects.create(
        user=user,
    )

    pp_album = ProfilePictureAlbum.objects.create(
        profile=profile
    )
    profile_picture = ProfilePicture.objects.create(
        album = pp_album
    )
    user_pp = UserProfilePicture.objects.create(
        profile = profile,
        picture = profile_picture
    )
    
    pc_album = ProfileCoverAlbum.objects.create(
        profile=profile
    )
    cover_picture = CoverPicture.objects.create(
        album = pc_album
    )
    user_cp = UserCoverPicture.objects.create(
        profile = profile,
        cover = cover_picture
    )
    privacy = UserPrivacySettings.objects.create(profile=profile)
    try:
        single_relationship = Relationship.objects.get(relationship_type="Single")
        relationship_status = RelationshipStatus.objects.create(
                profile=profile,
                relationship=single_relationship
            )
    except:
        relationship_status = RelationshipStatus.objects.create(profile = profile)
    # SEO Meta creation
        filename ='CSVFiles/XML/users.xml'
        open_file=open(filename,"r")
        read_file=open_file.read()
        open_file.close()
        new_line=read_file.split("\n")
        last_line="\n".join(new_line[:-1])
        open_file=open(filename,"w+")
        for i in range(len(last_line)):
            open_file.write(last_line[i])
        open_file.close()

        loc_tag=f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{user.username}</loc>\n"
        lastmod_tag=f"<lastmod>{user.date_joined}</lastmod>\n"
        priorty_tag=f"<priority>0.8</priority>\n</url>\n</urlset>"
        with open(filename, "a") as fileupdate:
            fileupdate.write(loc_tag)
            fileupdate.write(lastmod_tag)
            fileupdate.write(priorty_tag)
        # SEO Meta Close
    return Response(
        {"success": True, 'response': {'message': 'Sign Up Successful! Please verify your email to access your account!'}},
        status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data['email']
    try:
        user = User.objects.get(email=email, is_active=True)
    except ObjectDoesNotExist:
        return Response(
            {'success': False, 'response': {'message': 'User with the given email address does not exist!'}},
            status=status.HTTP_404_NOT_FOUND)
    # Generating random Code
    random_digits_for_code = ''.join(
        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
    verificaton = VerificationCode.objects.create(
        user=user,
        code=random_digits_for_code
    )
    html_template = render_to_string('email/u-forgot-password.html',
                                     {
                                         'code': verificaton.code,
                                         'img_link': settings.DOMAIN_NAME,
                                     })
    text_template = strip_tags(html_template)
    # Getting Email ready
    email = EmailMultiAlternatives(
        'YouOnline | Forgot Password',
        text_template,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(html_template, "text/html")
    try:
        email.send(fail_silently=False)
    except Exception as e:
        print(e)
        return Response({'success': False,
                         'response': {'message': 'There is an issue with Email Host Server'}},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({'success': True,
                     'response': {'message':'Verification code has been sent to your provided Email'}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    data = request.data
    try:
        user = request.user
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    old_password = data['old_password'] if 'old_password' in data else None
    password1 = data['password1'] if 'password1' in data else None
    password2 = data['password2'] if 'password2' in data else None
    if not old_password or not password1 or not password2:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if not user.check_password(old_password):
        return Response({'success': False, 'response': {'message': 'Incorrect current password!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if password1 != password2:
        return Response({'success': False, 'response': {'message': 'Password does not match'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if len(password1) < 8:
        return Response({"success": False, 'response': {'message' :'Please enter a strong password!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    user.set_password(password1)
    user.save()
    return Response({'success': True, 'response': {'message': 'Password changed successfully!'}},
                    status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    data = request.data
    email = data['email'].lower().strip() if 'email' in data else None
    password1 = data['password1'] if 'password1' in data else None
    password2 = data['password2'] if 'password2' in data else None
    code = data['code'] if 'code' in data else None

    if not email or not password2 or not password1 or not code:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if password1 != password2:
        return Response({'success': False, 'response': {'message': 'Password do not match'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email, is_active=True)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'User not found against given email!'}},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        code = VerificationCode.objects.get(user=user, code=code)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Invalid Code!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if not len(password1) < 8:
        user.set_password(password1)
        user.save()
        return Response({'success': True, 'response': {'message': 'Password reset successfully!'}},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': 'Password should be 8 letters long!'}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_code(request):
    email = request.data.get('email', None)
    if not email:
        return Response({'success': False, 'response': {'message': 'Enter your email!'}},
                status=status.HTTP_400_BAD_REQUEST)
    # Generating random Code
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Sorry! User with this email does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)

    codes = VerificationCode.objects.filter(user=user, expired=False)
    for i in codes:
        i.expired = True
        i.used = True
        i.save()

    random_digits_for_code = ''.join(
        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
    verification = VerificationCode.objects.create(user=user, code=random_digits_for_code)
    html_template = render_to_string('email/u-forgot-password.html',
                                     {'code': verification.code, 'img_link': settings.DOMAIN_NAME}
                                     )
    text_template = strip_tags(html_template)
    # Getting Email ready
    email = EmailMultiAlternatives(
        'YouOnline | Verification Code',
        text_template,
        settings.EMAIL_HOST_USER,
        [user.email]
    )
    email.attach_alternative(html_template, "text/html")
    try:
        email.send(fail_silently=False)
        return Response({'success': True, 'response': {'message': 'Verification code sent'}},
                        status=status.HTTP_201_CREATED)
    except:
        return Response({'success': False, 'response': {'message': 'There is an issue with Email Host Server'}},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    code = request.data.get('code', None)
    email = request.data.get('email', None)
    print(email)
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'requested user does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        verified = VerificationCode.objects.get(user=user, code=code, used=False, expired=False)
        # Get Profiles
        try:
            profile = Profile.objects.get(user=user)
        except Exception as e:
            print(e)
        # try:
        #     youonline_profile = Profile.objects.get(user__email='zain@youonline.online')
        # except Exception as e:
        #     youonline_profile = ''
        # # Follow Youonline Account
        # if youonline_profile:
        #     try:
        #         youonline_friends = FriendsList.objects.get(profile=youonline_profile)
        #         youonline_friends.followers.add(profile)
        #         youonline_friends.save()
        #     except Exception as e:
        #         youonline_friends = FriendsList.objects.create(profile=youonline_profile)
        #         youonline_friends.followers.add(profile)
        #         youonline_friends.save()
        #     try:
        #         profile_friends = FriendsList.objects.get(profile=profile)
        #         profile_friends.following.add(youonline_profile)
        #         profile_friends.save()
        #     except:
        #         profile_friends = FriendsList.objects.create(profile=profile)
        #         profile_friends.following.add(youonline_profile)
        #         profile_friends.save()
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'given code is invalid, already used or expired'}},
                        status=status.HTTP_404_NOT_FOUND)
    verified.expired = False
    verified.used = True
    verified.save()
    if not user.is_active:
        user.is_active = True
        user.save()
        # Send Email For Welcome.
        html_template = render_to_string('email/u-welcome-email.html', {'img_link': settings.DOMAIN_NAME, 'frontend_domain': settings.FRONTEND_SERVER_NAME})
        text_template = strip_tags(html_template)
        email = EmailMultiAlternatives(
            'Welcome to YouOnline',
            text_template,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        email.attach_alternative(html_template, "text/html")
        try:
            email.send(fail_silently=False)
        except:
            return Response({'success': False, 'response' : {'message': 'There is an issue with Email Host Server'}},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    try:
        token = Token.objects.get(user=profile.user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=profile.user)
    try:
        profile = Profile.objects.get(user=user, user__is_active=True, is_deleted=False)
        return Response({'success': True, 'response': {'data': {'id' : profile.id , 'token' : str(user.auth_token)}}},
                                status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': True, 'response': {'message': 'user is not active!'}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_phone(request):
    mobile_number = request.query_params.get('phone_number')
    username = request.query_params.get('username')
    code = request.query_params.get('code')
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'requested user does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        profile = Profile.objects.get(user=user, mobile_number=mobile_number)
    except ObjectDoesNotExist:
        return Response({'success': False, 'message': 'Sorry! Your user is not registered'},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        verified = VerificationCode.objects.get(user=user, code=code, used=False, expired=False)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'given code is invalid, already used or expired'}},
                        status=status.HTTP_404_NOT_FOUND)
    verified.used = True
    verified.save()
    user.is_active = True
    user.save()

    return Response({'success': True, 'message': 'Verification code has been sent to your phone number'},
                    status=status.HTTP_200_OK)


# Album Module Views
@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_album_media(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        media = UserAlbumMedia.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    serializer = UserAlbumMediaSerializer(media)
    return Response({'success': True, 'response': {'media': serializer.data}},
                        status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_album_media(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        media = UserAlbumMedia.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    media.is_deleted = True
    media.save()
    return Response({'success': True, 'response': {'media': 'Media deleted successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_album_media(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    album = request.data['album'] if 'album' in request.data else None
    image = request.data['image'] if 'image' in request.data else None
    video = request.data['video'] if 'video' in request.data else None
    if not album or (not image and not video):
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        album = UserAlbum.objects.get(id=album)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    if profile == album.profile:
        serializer = UserAlbumMediaSerializer(data=request.data)
        if serializer.is_valid():
            media = serializer.save()
            post = Post.objects.create(
                    profile=media.album.profile,
                    text=media.description,
                    album_post=True,
                    normal_post=True,
                    privacy=media.album.privacy,
                )
            media.post = post
            media.save()
            albumpost = AlbumPost.objects.create(
                    post=post,
                    album=media.album,
                )
            albumpost.media_posts.add(post)
            albumpost.save()
            album = UserAlbum.objects.get(id=media.album.id)
            serializer = GetUserAlbumMediaSerializer(media, context={"request": request})
            album.save()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False, 'response': 'You are not allowed to add media to this album.'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_album(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            album = UserAlbum.objects.get(id=id, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
        if not profile == album.profile:
            return Response({'success': False, 'response': {'message': 'You can only delete your own album!'}},
                        status=status.HTTP_403_FORBIDDEN)
        album.is_deleted = True
        album.save()
        album_posts = list(AlbumPost.objects.filter(album=album).values_list('post__id', flat=True))
        # Delete Album Post
        posts = Post.objects.filter(id__in=album_posts)
        for i in posts:
            i.is_deleted = True
            i.save()
        # Delete Album Media and Album Media Posts
        album_media = UserAlbumMedia.objects.filter(album=album)
        for i in album_media:
            i.is_deleted = True
            i.save()
            post = i.post
            post.is_deleted = True
            post.save()
        return Response({'success': True, 'response': {'message': 'Album deleted successfully!'}},
                        status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_album(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    album_title = request.data['album_title'] if 'album_title' in request.data else None
    if not album_title:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    request.data._mutable = True
    request.data['profile'] = profile.id
    serializer = UserAlbumSerializer(data=request.data)
    if serializer.is_valid():
        album = serializer.save()
        serializer = GetUserAlbumSerializer(album)
        return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_album(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    album_title = request.data['album_title'] if 'album_title' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    privacy = request.data['privacy'] if 'privacy' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        album = UserAlbum.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    if not album.profile == profile:
        return Response({'success': False, 'response': {'message': 'You are not allowed to updated this album'}},
                    status=status.HTTP_403_FORBIDDEN)
    album.album_title=album_title
    album.description=description
    album.privacy=privacy
    album.save()
    posts = Post.objects.filter(albumpost_post__album=album, is_deleted=False)
    for post in posts:
        post.privacy = album.privacy
        post.save()
    serializer = UserAlbumSerializer(album)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_album(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        album = UserAlbum.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    serializer = GetUserAlbumSerializer(album)
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_user_albums(request):
    try:
        visitor_profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    profile = request.query_params.get('profile')
    if not profile:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(id=profile, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    # Get Albums Based on privacy
    if profile == visitor_profile:
        albums = UserAlbum.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')
    else:
        friendship_status = check_friendship(profile, visitor_profile)
        if friendship_status['is_friend']:
            albums = UserAlbum.objects.filter(Q(profile=profile, is_deleted=False, privacy='Public') |
                                            Q(profile=profile, is_deleted=False, privacy='Friends')).order_by('-created_at')
        else:
            albums = UserAlbum.objects.filter(profile=profile, is_deleted=False, privacy='Public').order_by('-created_at')
    serializer = GetUserAlbumSerializer(albums, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
            status=status.HTTP_200_OK)


# UserFamilyMembers
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_family_member(request):
    profile = request.data['profile'] if 'profile' in request.data else None
    relation = request.data['relation'] if 'relation' in request.data else None
    family_member = request.data['family_member'] if 'family_member' in request.data else None
    if not profile or not relation or not family_member:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                status=status.HTTP_400_BAD_REQUEST)
    serializer = UserFamilyMemberSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def approve_family_member(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            relation = UserFamilyMember.objects.get(id=id, is_approved=False)
            relation.is_approved = True
            relation.save()
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'Family member does not exist!'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'success': False, 'response': {'message': 'Invalid relation ID!'}},
                    status=status.HTTP_400_BAD_REQUEST)
        new_member = UserFamilyMember.objects.create(
                profile=relation.family_member,
                family_member=relation.profile,
                relation=relation.relation,
                is_approved=True
            )
        serializer = UserFamilyMemberSerializer(new_member)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_family_member(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
            status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            relation = UserFamilyMember.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'Family member does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid family member ID!'}},
                    status=status.HTTP_400_BAD_REQUEST)
        try:
            other_relation = UserFamilyMember.objects.get(profile=relation.family_member, family_member=relation.profile)
            other_relation.delete()
            relation.delete()
        except Exception as e:
            print(e)
        return Response({'success': True, 'response': {'message': 'Family member removed successfully!'}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_family_members(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Enter profile id'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(id=id, is_deleted=False)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Profile does not exist'}},
                    status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Profile ID!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        family_members = UserFamilyMember.objects.filter(profile=profile, is_approved=True)
        serializer = UserFamilyMemberSerializer(family_members, many=True)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_workplace(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please provide a Workplace ID'}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        workplace = UserWorkPlace.objects.get(id=id, profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Workplace does not exist or you are not allowed to delete it.'}},
                status=status.HTTP_404_NOT_FOUND)
    workplace.delete()
    return Response({'success': True, 'response': {'message': 'Workplace deleted successfully!'}},
            status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_workplace(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    if request.method == 'POST':
        serializer = UserWorkPlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_workplace(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        workplace = UserWorkPlace.objects.get(id=id, profile=profile)
    except:
        return Response({'success': False, 'response': {'message': 'Workplace does not exist or you are not allowed to update it.'}},
                status=status.HTTP_404_NOT_FOUND)
    serializer = UserWorkPlaceSerializer(workplace, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_workplace(request):
    # If user sends profile id we send all the workplaces based on that profile
    # If user send workplace id we send that workplace in response.
    profile = request.query_params.get('profile')
    workplace = request.query_params.get('workplace')
    if not profile and not workplace:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    elif profile:
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        workplaces = UserWorkPlace.objects.filter(profile=profile, is_deleted=False).order_by('-start_date')
        serializer = UserWorkPlaceSerializer(workplaces, many=True)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)
    elif workplace:
        try:
            workplace = UserWorkPlace.objects.get(id=workplace, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        serializer = UserWorkPlaceSerializer(workplace)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_current_workplace(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        workplace = UserWorkPlace.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')[0]
    except:
        return Response({'success': False, 'response': {'message': 'User does not have any current workplace!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    serializer = UserWorkPlaceSerializer(workplace)
    return Response({'success': True, 'response': {'message': serializer.data}},
            status=status.HTTP_200_OK)


# UserPlacesLived
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_place_lived(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        place = UserPlacesLived.objects.get(id=id, profile=profile, is_deleted=False)
        place.is_deleted = True
        place.save()
        return Response({'success': True, 'response': {'message': 'Place deleted successfully!'}},
                status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_place_lived(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    serializer = UserPlacesLivedSerializer(data=request.data)
    if serializer.is_valid():
        place = serializer.save()
        if place.currently_living:
            places = UserPlacesLived.objects.filter(profile=place.profile).exclude(id=place.id)
            for i in places:
                i.currently_living = False
                i.save()
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_place_lived(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        place = UserPlacesLived.objects.get(id=id, profile=profile)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)},
                         'status': status.HTTP_404_NOT_FOUND})
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    serializer = UserPlacesLivedSerializer(place, data=request.data, partial=True)
    if serializer.is_valid():
        place = serializer.save()
        if place.currently_living:
            places = UserPlacesLived.objects.filter(profile=place.profile).exclude(id=place.id)
            for i in places:
                i.currently_living = False
                i.save()
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors},
                         'status': status.HTTP_400_BAD_REQUEST})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_place_lived(request):
    place_id = request.query_params.get('place_id')
    profile_id = request.query_params.get('profile_id')
    if not place_id and not profile_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    if place_id and profile_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    
    if profile_id:
        try:
            profile = Profile.objects.get(id=profile_id, is_deleted=False)
            places = UserPlacesLived.objects.filter(profile=profile, is_deleted=False).order_by('-moved_in')
            serializer = UserPlacesLivedSerializer(places, many=True)
            return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'Profile does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'success': False, 'response': {'message': 'Invalid profile ID!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    elif place_id:
        try:
            place = UserPlacesLived.objects.get(id=place_id, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'Place does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid place ID!'}},
                    status=status.HTTP_400_BAD_REQUEST)
        serializer = UserPlacesLivedSerializer(place)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Education Module
# HighSchool
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_school(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please provide a School ID'}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        school = UserHighSchool.objects.get(id=id, profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'School does not exist or you are not allowed to delete it.'}},
                status=status.HTTP_404_NOT_FOUND)
    school.delete()
    return Response({'success': True, 'response': {'message': 'School deleted successfully!'}},
            status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_school(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    if request.method == 'POST':
        serializer = UserHighSchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_school(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    school_id = request.data['id'] if 'id' in request.data else None
    if not school_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        school = UserHighSchool.objects.get(id=school_id, profile=profile)
    except:
        return Response({'success': False, 'response': {'message': 'School does not exist or you are not allowed to update it'}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    serializer = UserHighSchoolSerializer(school, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_schools(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Enter profile id'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(id=id, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Profile does not exist'}},
                    status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        schools = UserHighSchool.objects.filter(profile=profile, is_deleted=False).order_by('-start_date')
        serializer = UserHighSchoolSerializer(schools, many=True)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_single_school(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        school = UserHighSchool.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    serializer = UserUniversitySerializer(school)
    return Response({'success': True, 'response': {'message': serializer.data}},
            status=status.HTTP_200_OK)


# RelationShipStatus
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_relationship(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        relationship_obj = RelationshipStatus.objects.get(id=id, profile=profile, is_deleted=False)
        relationship_obj.is_deleted = True
        relationship_obj.save()
        return Response({'success': True, 'response': {'message': 'relationship deleted successfully!'}},
                status=status.HTTP_200_OK)
    except:
        return Response({'success': False, 'response': {'message': 'Relationship does not exist or you are not allowed to delete it.'}},
                status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_relationship(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    if request.method == 'POST':
        serializer = RelationshipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_relationship(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'please provide user id'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        relationship = RelationshipStatus.objects.get(id=id, profile=profile)
    except:
        return Response({'success': False, 'response': {'message': 'Relationship does not exist or you are not allowed to update it.'},
                         'status': status.HTTP_404_NOT_FOUND})
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    serializer = RelationshipSerializer(relationship, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_relationship(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=id, is_deleted=False)
        except:
            return Response({'success': False, 'response': {'message': 'Profile does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        try:
            relationship_obj = RelationshipStatus.objects.get(profile=profile, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
        serializer = RelationshipSerializer(relationship_obj)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_relationships(request):
    relationships = Relationship.objects.all()
    serializer = RelationshipsSerializer(relationships, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


# Get Post Album
def get_post_album(post):
    if post.album_post:
        try:
            album_post = AlbumPost.objects.get(post=post)
            return users_serializers.GetAlbumPostSerializer(album_post).data
        except Exception as e:
            return None
    else:
        return None

# Get Post Media
def get_media(post, profile):
    if post.profile_picture_post:
        media = serialized_profile_picture(post.post_profile_picture.all()[0])
    elif post.cover_post:
        media = serialized_cover_picture(post.post_cover.all()[0])
    elif post.normal_post:
        media = serilaized_post_media(post.post_post.all())
    elif post.video_post and post.media_post or (post.page_post and not post.page_banner) or (post.group_post and not post.group_banner):
        if post.post_post.all().count() > 0:
            media = serilaized_post_media(post.post_post.all())
        else:
            media = serilaized_post_media(post.sub_post.all())
    elif post.album_post:
        media = serialized_album_media(post.useralbummedia_post.all())
    elif post.video_module:
        try:
            media = GetVideoSerializer(post.videomodule_post.all(), many=True, context={"profile": profile}).data
        except:
            media = GetVideoSerializer(post.videomodule_post.all(), many=True).data
    elif post.group_banner:
        media = GetPostGroupBannerSerializer(post.groupbanner_post.all(), many=True).data
    elif post.page_banner:
        media = GetPostPageBannerSerializer(post.pagebanner_post.all(), many=True).data
    else:
        media = serilaized_post_media(post.post_post.all())
    return media

# Get Post Tags
def get_tags(post):
    tags = []
    for i in post.taguser_post.all():
        return_dict = {
            "id": i.id,
            "tagged_profile": serialized_post_profile(i.tagged_profile),
            "tagged_by": serialized_post_profile(i.tagged_by),
            "post": i.post.id,
            "created_at": i.created_at,
            "is_mentioned" : i.is_mentioned
        }
        tags.append(return_dict)
    return tags

# Get if post notifications are on
def get_notifications_on(post, profile):
    try:
        notifiers = NotifiersList.objects.get(post=post)
        if profile in notifiers.notifiers_list.all():
            notifications_on = True
        else:
            notifications_on = False
    except Exception as e:
        notifications_on = False
    return notifications_on

def get_likes(videos):
    likes =[]
    for i in PostReaction.objects.filter(post=videos.post):
        return_dict = {
            "id": i.id,
            "type": i.type,
            "react_unicode": i.react_unicode,
            "post": i.post.id,
        }
        likes.append(return_dict)
    return likes

def get_dislikes(videos):
    dislikes =[]
    for i in PostDislike.objects.filter(post=videos.post):
        return_dict = {
            "id": i.id,
            "created_at": i.created_at,
        }
        dislikes.append(return_dict)
    return dislikes

def get_comment_count(videos):
    try:
        comment_count = PostComment.objects.filter(post=videos.post).count()
        return comment_count
    except:
        comment_count = None
        return comment_count

def get_watch_later(request, videos):
    try:
        watch_later = VideoWatchLater.objects.get(video=videos, profile=request.user.profile_user)
        watch_later = True
    except:
        watch_later = False
    return watch_later


def get_channel(request, videos):
    channel = VideoChannel.objects.get(id=videos.channel.id)
    try:
        picture = ChannelPicture.objects.get(channel=channel)
        if picture.picture:
            picture = f"{settings.S3_BUCKET_LINK}{picture.picture}"
        else:
            picture = None
    except:
        picture = None
    try:
        cover = ChannelCover.objects.get(channel=channel)
        if cover.cover:
            cover = f"{settings.S3_BUCKET_LINK}{cover.cover}"
        else:
            cover = None
    except:
        cover = None
    try:
        subscribe = VideoChannelSubscribe.objects.get(profile=request.user.profile_user, channel=channel)
        is_subscribed = True
    except Exception as e:
        is_subscribed = False
    total_subscribers = VideoChannelSubscribe.objects.filter(channel=channel).count()
    total_videos = Video.objects.filter(channel=channel, is_deleted=False).count()

    return_dict = {
        'id' : channel.id,
        'slug' : channel.slug,
        'profile' :channel.profile.id,
        'name' : channel.name,
        'description' : channel.description,
        'picture' : picture,
        'cover' : cover,
        'created_at' : channel.created_at,
        'is_subscribed' : is_subscribed,
        'total_subscribers' : total_subscribers,
        'total_videos' : total_videos,
    
        }
    return return_dict


def get_video_response(request, videos):
    
    id = videos.id
    profile = videos.profile.id
    title = videos.title
    description = videos.description
    video = f"{settings.S3_BUCKET_LINK}{videos.video}"
    vid_thumbnail =  f"{settings.S3_BUCKET_LINK}{videos.vid_thumbnail}"
    short_description = videos.short_description
    youtube_link = videos.youtube_link
    if videos.category:
        category = videos.category.id
    else:
        category = None
    if videos.sub_category:
        sub_category = videos.sub_category.id
    else:
        sub_category = None
    created_at = videos.created_at
    if videos.post:
        post = videos.post.id
    else:
        post = None
    channel = get_channel(request, videos)
    slug = videos.slug
    total_views = videos.total_views
    duration = videos.duration
    likes = get_likes(videos)
    dislikes = get_dislikes(videos)
    comment_count = get_comment_count(videos)
    watch_later = get_watch_later(request, videos)

    video_post_dictionary = {
        'id' : id,
        'profile' : profile,
        'title' : title,
        'description' : description,
        'video' : video,
        'vid_thumbnail' : vid_thumbnail,
        'short_description' : short_description,
        'youtube_link' : youtube_link,
        'category' : category,
        'sub_category' : sub_category,
        'created_at' : created_at,
        'channel' : channel,
        'post' : post,
        'slug' : slug,
        'watch_later': watch_later,
        'duration': duration,
        'likes': likes,
        'dislikes': dislikes,
        'comment_count': comment_count,

        'total_views':total_views,
        

    }
    return video_post_dictionary



def get_post_response(post):
    id = post.id
    profile = serialized_post_profile(post.profile)
    feeling = {
        "feeling": post.feeling,
        "feeling_unicode": post.feeling_unicode
    }
    activity = {
        "activity": post.activity,
        "activity_unicode": post.activity_unicode
    }
    text = post.text
    created_at = post.created_at
    privacy = post.privacy
    reactions = serialized_post_reactions(post.postreaction_post.all()[:2])
    reactions_count = post.reactions_count
    comments_count = post.comments_count
    is_hidden = post.is_hidden

    media = get_media(post, profile)

    # Poll Post
    if post.poll_post:
        poll = serialized_post_poll(post.pollpost_post.all()[0])
    else:
        poll = None

    # Flags based on post type
    video_module = post.video_module
    media_post = post.media_post
    video_post = post.video_post
    profile_picture_post = post.profile_picture_post
    cover_post = post.cover_post
    normal_post = post.normal_post
    album_post = post.album_post
    group_post = post.group_post
    group_banner = post.group_banner
    page_post = post.page_post
    page_banner = post.page_banner
    is_approved = post.is_approved
    is_declined = post.is_declined

    # Get Post Group
    if post.group_post:
        group = DefaultGroupSerializer().data
    else:
        group = None

    # Get Post Page
    if post.page_post:
        page = GetPageSerializer().data
    else:
        page = None

    street_adress = post.street_adress
    longitude = post.longitude
    latitude = post.latitude

    tags = get_tags(post)

    # Get Saved Posts
    try:
        s_post = SavedPost.objects.get(profile=profile, post=post)
        saved_post = True
    except:
        saved_post = False

    notifications_on = get_notifications_on(post, profile)

    # Get Shared Post
    if post.shared_post:
        shared_post = PostGetSerializer(post.sharedpost_post.all()[0].shared_post).data
    else:
        shared_post = None

    # Get Friend
    if post.shared_post:
        friend = DefaultProfileSerializer(post.sharedpost_post.all()[0].friend).data
    else:
        friend = None
    post_album = get_post_album(post)

    post_dictionary = {
        "id": id,
        "profile": profile,
        "feeling": feeling,
        "activity": activity,
        "text": text,
        "created_at": created_at,
        "privacy": privacy,
        "reactions": reactions,
        "reactions_count": reactions_count,
        "comments_count": comments_count,
        "is_hidden": is_hidden,
        "media": media,
        "poll": poll,
        "video_module": video_module,
        "media_post": media_post,
        "video_post": video_post,
        "profile_picture_post": profile_picture_post,
        "cover_post": cover_post,
        "normal_post": normal_post,
        "album_post": album_post,
        "group_post": group_post,
        "group_banner": group_banner,
        "page_post": page_post,
        "page_banner": page_banner,
        "is_approved": is_approved,
        "is_declined": is_declined,
        "group": group,
        "page": page,
        "street_adress": street_adress,
        "longitude": longitude,
        "latitude": latitude,
        "tags": tags,
        "saved_post": saved_post,
        "notifications_on": notifications_on,
        "shared_post": shared_post,
        "friend": friend,
        "post_album": post_album,
    }
    return post_dictionary


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_newsfeed(request):
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
        posts = Post.objects.filter(Q(profile=profile, normal_post=True, is_deleted=False) |
                                    Q(group__groupmember_usergroup__profile=profile, is_deleted=False) |
                                    Q(page__pagefollower_page__profile=profile, is_deleted=False) |
                                    Q(profile__in=following_list, normal_post=True, is_deleted=False, privacy='Public') |
                                    Q(profile__in=following_list, normal_post=True, is_deleted=False, privacy='Friends')
                ).select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post').exclude(id__in=hidden_posts).exclude(id__in=report_posts).order_by('-created_at')[0:200]
    except Exception as e:
        print(e)
        
    paginator = CustomPagination()
    paginator.page_size = 20
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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_timeline(request):
    visited_profile = request.query_params.get('visited_profile')
    if not visited_profile:
        return Response({'success': False,'response': {'message': 'Please provide an ID.'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        visitor_profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        visitor_profile = None
    try:
        visited_profile = Profile.objects.get(id=visited_profile, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    if visited_profile == visitor_profile:
        posts = Post.objects.filter(Q(profile=visited_profile, normal_post=True, is_deleted=False, is_hidden=False) | 
                                    Q(taguser_post__tagged_profile=visited_profile, taguser_post__is_mentioned=False, is_deleted=False, is_hidden=False, normal_post=True)
                ).distinct().select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post').order_by('-created_at')
    else:
        if visitor_profile:
            try:
                friends = FriendsList.objects.get(profile=visitor_profile).friends.all()
                if visited_profile in friends:
                    posts = Post.objects.filter(Q(profile=visited_profile, normal_post=True, is_deleted=False, is_hidden=False, privacy='Public') |
                                                Q(profile=visited_profile, normal_post=True, is_deleted=False, is_hidden=False, privacy='Friends') |
                                                Q(taguser_post__tagged_profile=visited_profile, is_deleted=False, is_hidden=False, normal_post=True, privacy='Public')
                            ).distinct().select_related(
                                'profile', 'group', 'page'
                            ).prefetch_related(
                                'postreaction_post', 'post_post', 'sub_post',
                                'albumpost_post', 'pollpost_post',
                                'taguser_post', 'sharedpost_post').exclude(hidden_post__profile=visitor_profile).order_by('-created_at')
                else:
                    posts = Post.objects.filter(Q(profile=visited_profile, normal_post=True, is_deleted=False, is_hidden=False, privacy='Public')|
                                                Q(taguser_post__tagged_profile=visited_profile, is_deleted=False, is_hidden=False, normal_post=True, privacy='Public')
                            ).distinct().select_related(
                                'profile', 'group', 'page'
                            ).prefetch_related(
                                'postreaction_post', 'post_post', 'sub_post',
                                'albumpost_post', 'pollpost_post',
                                'taguser_post', 'sharedpost_post').exclude(hidden_post__profile=visitor_profile).order_by('-created_at')
            except:
                posts = Post.objects.filter(profile=visited_profile, normal_post=True, is_deleted=False, is_hidden=False, privacy='Public'
                            ).select_related(
                                'profile', 'group', 'page'
                            ).prefetch_related(
                                'postreaction_post', 'post_post', 'sub_post',
                                'albumpost_post', 'pollpost_post',
                                'taguser_post', 'sharedpost_post').order_by('-created_at')
        else:
            posts = Post.objects.filter(profile=visited_profile, normal_post=True, is_deleted=False, is_hidden=False, privacy='Public'
                ).select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post').order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostGetSerializer(result_page, many=True, context={"profile": visited_profile})
    return paginator.get_paginated_response(serializer.data)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_code(request):
    code = request.query_params.get('code')
    email = request.query_params.get('email')
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return Response({'success': False, 'message': 'Your requested user doesnot exist'},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        verified = VerificationCode.objects.get(user=user, code=code,
                                                used=False, expired=False)
    except ObjectDoesNotExist:
        return Response({'success': False, 'message': 'Your given code is invalid, already used or expired'},
                        status=status.HTTP_404_NOT_FOUND)
    verified.used = True
    verified.save()
    return Response({'success': True, 'message': 'Code Verified'})


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_mobile(request):
    mobile_number = request.query_params.get('mobile_number')
    email = request.query_params.get('email')
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return Response({'success': False, 'message': 'Your requested user does not exist'},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        profile = Profile.objects.get(user=user, mobile_number=mobile_number)
    except ObjectDoesNotExist:
        return Response({'success': False, 'message': 'Sorry! Your user is not registered'},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        send_sms(mobile_number)
    except:
        return Response({'success': False, 'message': 'Sorry! There is an issue with SMS Sending service'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({'success': True, 'message': 'Verification code has been sent to your phone number'},
                    status=status.HTTP_200_OK)


# Friends module views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_friend_request(request):
    try:
        req_sender = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    req_receiver = request.data['req_receiver'] if 'req_receiver' in request.data else None
    if not req_receiver:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                status=status.HTTP_400_BAD_REQUEST)
    # Verify request receiver ID.
    try:
        req_receiver = Profile.objects.get(id=req_receiver, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': 'User Profile does not exist'}},
                status=status.HTTP_404_NOT_FOUND)
    if req_sender == req_receiver:
        return Response({'success': False, 'response': {'message': 'Request sender & receiver are identical.'}},
                status=status.HTTP_400_BAD_REQUEST)
    # Check if there is already a request sent from that sender.
    try:
        obj = FriendRequest.objects.get(req_sender=req_sender,
                            req_receiver=req_receiver,
                            is_active=True,
                            status="Pending"
                    )
        return Response({'success': False, 'response': {'message': 'Invalid Request!'}},
                status=status.HTTP_400_BAD_REQUEST)
    except:
        pass
    # Check if there is already a request sent from that receiver.
    try:
        obj = FriendRequest.objects.get(req_sender=req_receiver,
                            req_receiver=req_sender,
                            is_active=True,
                            status="Pending"
                    )
        return Response({'success': False, 'response': {'message': 'Invalid Request!'}},
                status=status.HTTP_400_BAD_REQUEST)
    except:
        pass
    # Check if they are friends.
    try:
        sender_list = FriendsList.objects.get(profile=req_sender)
        if req_receiver in sender_list.friends.all():
            return Response({'success': False, 'response': {'message': 'Invalid Request!. You are already friends.'}},
                status=status.HTTP_400_BAD_REQUEST)
    # Creating objects
    except:
        sender_list = FriendsList.objects.create(profile=req_sender)
    try:
        receiver_list = FriendsList.objects.get(profile=req_receiver)
    except:
        receiver_list = FriendsList.objects.create(profile=req_receiver)

    # Adding request sender into followers list
    receiver_list.followers.add(req_sender)
    receiver_list.save()

    # Adding request receiver into request sender following list
    sender_list.following.add(req_receiver)
    sender_list.save()

    serializer = FriendRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        # Generate notification for the request.
        notification = Notification(
                type = 'FriendRequest',
                profile = req_sender,
                text = 'sent you friend request.',
            )
        notification.save()
        notification.notifiers_list.add(req_receiver)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass
        # Creating FCM Notification through Thread
        RequestSendThread(request, req_sender, req_receiver).start()
        
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friend_requests(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    friend_requests = FriendRequest.objects.filter(req_receiver=profile, is_active=True, status='Pending')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(friend_requests, request)
    serializer = RequestUserProfileSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mark_as_read_friend_requests(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    friend_requests = FriendRequest.objects.filter(
        req_receiver=profile, 
        is_active=True, 
        status='Pending',
        is_read=False
    )
    for fr_req in friend_requests:
        fr_req.is_read = True
        fr_req.save()

    return Response({'success': True,'response': {'message': 'Successfully read.'}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_friend_request(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['friend_request'] if 'friend_request' in request.data else None
    req_status = request.data['status'] if 'status' in request.data else None
    if not id and not req_status:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        friend_request = FriendRequest.objects.get(id=id, is_active=True)
    except:
        return Response({'success': False, 'response': {'message': 'Friend request does not exist'}},
                status=status.HTTP_404_NOT_FOUND)

    req_sender = friend_request.req_sender
    req_receiver = friend_request.req_receiver
    try:
        sender_list = FriendsList.objects.get(profile=req_sender)
    except:
        sender_list = FriendsList.objects.create(profile=req_sender)

    try:
        receiver_list = FriendsList.objects.get(profile=req_receiver)
    except:
        receiver_list = FriendsList.objects.create(profile=req_receiver)
    if req_status == 'Approved':
        if req_receiver != profile:
            return Response({'success': False, 'response': {'message': 'You cannot approve this request.'}},
                status=status.HTTP_403_FORBIDDEN)
        # Adding request sender into receiver friends list
        receiver_list.friends.add(req_sender)
        # Adding request sender into followers list
        receiver_list.followers.add(req_sender)
        # Adding request sender into following list
        receiver_list.following.add(req_sender)
        receiver_list.save()
        # Adding request receiver into request sender friends list
        sender_list.friends.add(req_receiver)
        # Adding request receiver into request sender followers list
        sender_list.followers.add(req_receiver)
        # Adding request receiver into request sender following list
        sender_list.following.add(req_receiver)
        sender_list.save()
        # Inactivating current friend request
        friend_request.is_active = False
        friend_request.status = 'Approved'
        friend_request.save()
        notification = Notification(
                type = 'AcceptFriendRequest',
                profile = req_receiver,
                text = 'accepted your friend request.',
            )
        notification.save()
        notification.notifiers_list.add(req_sender)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass
        # Creating FCM Notification through Thread
        RequestApproveThread(request, req_sender, req_receiver).start()
        
        return Response({'success': True, 'response': {'message': 'Approved'}},
                status=status.HTTP_200_OK)

    elif req_status == 'Cancelled':
        if req_receiver != profile and req_sender != profile:
            return Response({'success': False, 'response': {'message': 'You cannot cancel this request.'}},
                status=status.HTTP_403_FORBIDDEN)
        try:
            sender_list = FriendsList.objects.get(profile=req_sender)
        except:
            sender_list = FriendsList.objects.create(profile=req_sender)

        try:
            receiver_list = FriendsList.objects.get(profile=req_receiver)
        except:
            receiver_list = FriendsList.objects.create(profile=req_receiver)

        # Adding request sender into followers list
        receiver_list.followers.remove(req_sender)
        receiver_list.save()

        # Adding request receiver into request sender following list
        sender_list.following.remove(req_receiver)
        sender_list.save()

        friend_request.is_active = False
        friend_request.status = 'Cancelled'
        friend_request.save()
        notification = Notification(
                type = 'CancelFriendRequest',
                profile = req_receiver,
                text = 'Cancelled your friend request.',
            )
        notification.save()
        notification.notifiers_list.add(req_sender)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass
        return Response({'success': True, 'response': {'message': 'Cancelled'}},
                status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': 'Request status is not valid'}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_mutual_friends(request):
    profile1 = request.query_params.get('profile1') if 'profile1' in request.query_params else None
    profile2 = request.query_params.get('profile2') if 'profile2' in request.query_params else None
    if not profile1 and not profile2:
        return Response({'success': False, 'response': {'message': 'Input Profiles UUIds',}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        profile1 = Profile.objects.get(id=profile1)
    except:
        return Response({'success': False, 'response': {'message': 'Profile1 with this UUID does not exist'}},
            status=status.HTTP_404_NOT_FOUND)
    try:
        profile2 = Profile.objects.get(id=profile2)
    except:
        return Response({'success': False, 'response': {
            'message': 'Profile2 with this UUID does not exist',
            'status': status.HTTP_404_NOT_FOUND}
                         }, status=status.HTTP_404_NOT_FOUND)
    try:
        f1_list = FriendsList.objects.get(profile=profile1)
        friends1 = f1_list.friends.all()
    except:
        friends1 = []
    try:
        f2_list = FriendsList.objects.get(profile=profile2)
        friends2 = f2_list.friends.all()
    except:
        friends2 = []
    mutual_list = list(set(friends1).intersection(friends2))
    serializer = GetUserProfileSerializer(mutual_list, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
            status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_friends(request):
    id = request.query_params.get('id') if 'id' in request.query_params else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(id=id, is_deleted=False, user__is_active=True)
    except:
        return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        friends_list = FriendsList.objects.get(profile=profile)
        friends_list = friends_list.friends.all()
        if friends_list.count() > 0:
            serializer = GetUserProfileSerializer(friends_list, many=True)
            return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'response': {'message': 'You do not have any friends.'}},
                    status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'response': {'message': 'You do not have any friends.'}},
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow(request):
    try:
        send_profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    req_receiver = request.data['req_receiver'] if 'req_receiver' in request.data else None
    if not req_receiver:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        rec_profile = Profile.objects.get(id=req_receiver, is_deleted=False, user__is_active=True)
    except:
        return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Check if send and receiver are same.
    if send_profile == rec_profile:
        return Response({'success': False, 'response': {'message': 'Follower and receiver are identical.'}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        send_list = FriendsList.objects.get(profile=send_profile)
    except ObjectDoesNotExist:
        send_list = FriendsList.objects.create(
                profile=send_profile
            )
    try:
        rec_list = FriendsList.objects.get(profile=rec_profile)
    except ObjectDoesNotExist:
        send_list = FriendsList.objects.create(
                profile=rec_profile
            )
    send_list.following.add(rec_profile)
    send_list.save()
    rec_list.followers.add(send_profile)
    rec_list.save()
    notification = Notification(
            type = 'FollowUser',
            profile = send_profile,
            text = 'started following you.',
        )
    notification.save()
    notification.notifiers_list.add(rec_profile)
    notification.save()
    try:
        send_notifications_ws(notification)
    except:
        pass
    # FCM Notification Through Thread
    FollowUserThread(request, send_profile, rec_profile)

    return Response({'success': True, 'response': {'message': f"You are now following {rec_profile.user.username}"}},
                status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow(request):
    try:
        send_profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    req_receiver = request.data['req_receiver'] if 'req_receiver' in request.data else None
    if not req_receiver:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        rec_profile = Profile.objects.get(id=req_receiver, is_deleted=False, user__is_active=True)
    except:
        return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        send_list = FriendsList.objects.get(profile=send_profile)
    except ObjectDoesNotExist:
        send_list = FriendsList.objects.create(
                profile=send_profile
            )
    try:
        rec_list = FriendsList.objects.get(profile=rec_profile)
    except ObjectDoesNotExist:
        send_list = FriendsList.objects.create(
                profile=rec_profile
            )
    send_list.following.remove(rec_profile)
    send_list.save()
    rec_list.followers.remove(send_profile)
    rec_list.save()

    return Response({'success': True, 'response': {'message': f"You have unfollowed {rec_profile.user.username}"}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_friend(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    visited_profile = request.data['visited_profile'] if 'visited_profile' in request.data else None
    if not visited_profile:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        visited_profile = Profile.objects.get(id=visited_profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Requestee Profile does not exist'}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        obj = FriendsList.objects.get(profile=profile)
        obj.friends.remove(visited_profile)
        obj.following.remove(visited_profile)
        obj.followers.remove(visited_profile)
        for i in obj.friends.all():
            print(i)
        print("Removing friend")
        obj.save()
        print("done")
    except:
        return Response({'success': False, 'response': {'message': 'Something went wrong.'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        obj = FriendsList.objects.get(profile=visited_profile)
        obj.friends.remove(profile)
        obj.following.remove(profile)
        obj.followers.remove(profile)
        print("Removing friend")
        obj.save()
        print("done")
        return Response({'success': True, 'response': {'message': 'Removed'}},
                status=status.HTTP_200_OK)
    except:
        return Response({'success': False, 'response': {'message': 'Something went wrong.'}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ignore_suggested(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    ignored_id = request.data['ignored_id'] if 'ignored_id' in request.data else None
    ignored_object = request.data['ignored_object'] if 'ignored_object' in request.data else None
    if not ignored_id or not ignored_object:
        return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        ignored_list = IgnoredList.objects.get(profile=profile)
    except:
        ignored_list = IgnoredList.objects.create(profile=profile)
    if ignored_object == 'Profile':
        try:
            ignored = Profile.objects.get(id=ignored_id, user__is_active=True, is_deleted=False)
            ignored_list.people.add(ignored)
        except:
            return Response({'success': False, 'response': {'message': 'User profile for ignore does not exist or is inactive.'}},
                        status=status.HTTP_404_NOT_FOUND)
    elif ignored_object == 'Group':
        try:
            ignored = Group.objects.get(id=ignored_id, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        ignored_list.groups.add(ignored)
    elif ignored_object == 'Page':
        try:
            ignored = Page.objects.get(id=ignored_id, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        ignored_list.pages.add(ignored)
    elif ignored_object == 'Property':
        try:
            ignored = Property.objects.get(id=ignored_id, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        ignored_list.properties.add(ignored)
    elif ignored_object == 'Automotive':
        try:
            ignored = Automotive.objects.get(id=ignored_id, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        ignored_list.automotives.add(ignored)
    elif ignored_object == 'Classified':
        try:
            ignored = Classified.objects.get(id=ignored_id, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        ignored_list.classifieds.add(ignored)
    ignored_list.save()
    return Response({'success': True, 'response': {'message': f"{ignored_object} ignored successfully."}},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggested_people(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    context = {
        'profile': profile,
    }

    if not profile.current_city:
        return Response({'success': True, 'response': {'message': []}},
                    status=status.HTTP_200_OK)
                    
    try:
        friends = list(FriendsList.objects.get(profile=profile).friends.all())
        followers = list(FriendsList.objects.get(profile=profile).followers.all())
        following = list(FriendsList.objects.get(profile=profile).following.all())
        excluded_list = []
        for i in friends:
            excluded_list.append(i.id)
        for i in followers:
            excluded_list.append(i.id)
        for i in following:
            excluded_list.append(i.id)
        try:
            ignored_list = IgnoredList.objects.get(profile=profile)
            ignored_profiles = list(ignored_list.people.all().values_list('id', flat=True))
            for i in ignored_profiles:
                excluded_list.append(i)
        except:
            pass
        suggestions = Profile.objects.filter(
            Q(is_deleted=False, user__is_active=True, current_city__icontains=profile.current_city) |
            Q(is_deleted=False, user__is_active=True, street_adress__icontains=profile.current_city)
        ).exclude(id__in=excluded_list).exclude(id=profile.id)[0:10]
        serializer = SearchUserProfileSerializer(suggestions, many=True, context=context)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    except:
        suggestions = Profile.objects.filter(
            Q(is_deleted=False, user__is_active=True, current_city__icontains=profile.current_city) |
            Q(is_deleted=False, user__is_active=True, street_adress__icontains=profile.current_city)
        ).exclude(id=profile.id)[0:10]
        serializer = SearchUserProfileSerializer(suggestions, many=True, context=context)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


# User Profile/Timeline Module
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_profile_picture(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    picture = request.data['picture'] if 'picture' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    if not picture:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            album = ProfilePictureAlbum.objects.get(profile=profile)
        except ObjectDoesNotExist:
            album = ProfilePictureAlbum.objects.create(
                    profile = profile
                )
        except:
            return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
        # post = Post.objects.create(
        #         profile=profile,
        #         text=description,
        #         profile_picture_post=True,
        #         normal_post=True,
        #     )
    try:
        profile_picture = ProfilePicture.objects.get(profile=profile)
        profile_picture.delete()
    except:
        pass
    profile_picture = ProfilePicture(
        album = album,
        picture = picture,
        profile = profile,
    )
    profile_picture.save()

    serializer = UserProfilePictureSerializer(profile_picture)
    return Response({'success': True, 'response': {'message': serializer.data}},
            status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_picture(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    try:
        profile_picture = UserProfilePicture.objects.get(profile=profile)
        profile_picture.picture = None
        profile_picture.save()
        return Response({'success': True, 'response': {'message': 'User profile picture deleted successfully.'}},
                    status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'User does not have a profile picture.'}},
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_cover_picture(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    cover = request.data['cover'] if 'cover' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    if not cover:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        album = ProfileCoverAlbum.objects.get(profile=profile)
    except ObjectDoesNotExist:
        album = ProfileCoverAlbum.objects.create(profile=profile)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        cover_picture = CoverPicture.objects.get(profile=profile)
        cover_picture.delete()
    except:
        pass
    cover_picture = CoverPicture.objects.create(
            album = album,
            cover = cover,
            profile = profile,
        )
    cover_picture.save()
    # try:
    #     cover_obj = UserCoverPicture.objects.get(profile=profile)
    # except ObjectDoesNotExist:
    #     cover_obj = UserCoverPicture.objects.create(profile=profile)
    # cover_obj.cover = cover_picture
    # cover_obj.save()
    serializer = UserCoverPictureSerializer(cover_picture)
    return Response({'success': True, 'response': {'message': serializer.data}},
            status=status.HTTP_200_OK)
                

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cover_picture(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    try:
        cover_picture = UserCoverPicture.objects.get(profile=profile)
        cover_picture.cover = None
        cover_picture.save()
        return Response({'success': True, 'response': {'message': 'User Cover picture deleted successfully.'}},
                    status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'User does not have a cover picture.'}},
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_uploaded_pictures(request):
    profile = request.query_params.get('profile')
    if not profile:
        return Response({'success': False, 'response': {'message': 'Invalid data. Please provide an ID!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile, user__is_active=True)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid ID for User.'}},
                        status=status.HTTP_400_BAD_REQUEST)
        media_posts = PostMedia.objects.filter(Q(profile=profile, is_deleted=False, post__group__isnull=True, post__page__isnull=True) &
                                            ~Q(post_image='')).order_by('-created_at')
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(media_posts, request)
        serializer = PostMediaSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_photos_of_you(request):
    profile = request.query_params.get('profile')
    if not profile:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile, user__is_active=True)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid Profile ID.'}},
                        status=status.HTTP_400_BAD_REQUEST)
        tagged_posts = TagUser.objects.filter(tagged_profile=profile).values('post')
        media_posts = PostMedia.objects.filter(post__in=tagged_posts, post__is_deleted=False, post__is_hidden=False).exclude(post_image__exact='')
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(media_posts, request)
        serializer = PostMediaSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



@api_view(['GET'])
@permission_classes([AllowAny])
def get_prev_profile_pictures(request):
    profile = request.query_params.get('profile')
    if not profile:
        return Response({'success': False, 'response': {'message': 'Invalid data. Please provide an ID!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile, user__is_active=True, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid ID for Profile.'}},
                        status=status.HTTP_400_BAD_REQUEST)
        pictures = ProfilePicture.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')
        return_dict = []
        for i in pictures:
            url = f"{settings.S3_BUCKET_LINK}{i.picture}"
            images = {'image': url, 'post': i.post.id}
            return_dict.append(images)
        return Response({'success': True, 'response':{'message': return_dict}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_prev_cover_pictures(request):
    profile = request.query_params.get('profile')
    if not profile:
        return Response({'success': False, 'response': {'message': 'Invalid data. Please provide an ID!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile, user__is_active=True)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid ID for User.'}},
                        status=status.HTTP_400_BAD_REQUEST)
        pictures = CoverPicture.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')
        return_dict = []
        for i in pictures:
            url = f"{settings.S3_BUCKET_LINK}{i.cover}"
            images = {'image': url, 'post': i.post.id}
            return_dict.append(images)
        return Response({'success': True, 'response':{'message': return_dict}},
                    status=status.HTTP_200_OK)
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_bio(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    bio = request.data['bio'] if 'bio' in request.data else None
    if not bio:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    profile.bio = bio
    profile.save()
    serializer = GetUserProfileSerializer(profile)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    first_name = request.data['first_name'] if 'first_name' in request.data else None
    mobile_number = request.data['mobile_number'] if 'mobile_number' in request.data else None
    country = request.data['country'] if 'country' in request.data else None
    state = request.data['state'] if 'state' in request.data else None
    city = request.data['city'] if 'city' in request.data else None
    bio = request.data['bio'] if 'bio' in request.data else None
    street_adress = request.data['street_adress'] if 'street_adress' in request.data else None
    longitude = request.data['longitude'] if 'longitude' in request.data else None
    latitude = request.data['latitude'] if 'latitude' in request.data else None
    picture = request.data['picture'] if 'picture' in request.data else None
    cover = request.data['cover'] if 'cover' in request.data else None
    dial_code = request.data['dial_code'] if 'dial_code' in request.data else None

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    try:
        country = Country.objects.get(id=country)
    except Exception as e:
        country = None
    
    try:
        state = State.objects.get(id=state)
    except Exception as e:
        state = None

    try:
        city = City.objects.get(id=city)
    except Exception as e:
        city = None

    try:
        user = User.objects.get(id=profile.user.id)
    except:
        pass

    if first_name:
        user.first_name = first_name
    
    if mobile_number:
        user.mobile_number = mobile_number
    user.save()

    if country:
        profile.country = country
        
    if state:
        profile.state = state
        
    if city:
        profile.city = city
    
    if bio:
        profile.bio = bio

    if street_adress:
        profile.street_adress = street_adress

    if latitude:
        profile.latitude = latitude
    
    if longitude:
        profile.longitude = longitude
    
    if dial_code:
        profile.dial_code = dial_code
    profile.save()
    
    try:
        album = ProfilePictureAlbum.objects.get(profile=profile)
    except ObjectDoesNotExist:
        album = ProfilePictureAlbum.objects.create(
                profile = profile
            )
    if picture:
        try:
            profile_picture = ProfilePicture.objects.get(profile=profile)
            profile_picture.delete()
        except:
            pass
        profile_picture = ProfilePicture(
            album = album,
            picture = picture,
            profile = profile,
        )
        profile_picture.save()
    try:
        album = ProfileCoverAlbum.objects.get(profile=profile)
    except ObjectDoesNotExist:
        album = ProfileCoverAlbum.objects.create(profile=profile)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    if cover:
        try:
            cover_picture = CoverPicture.objects.get(profile=profile)
            cover_picture.delete()
        except:
            pass
        cover_picture = CoverPicture.objects.create(
                album = album,
                cover = cover,
                profile = profile,
            )
        cover_picture.save()
    serializer = DefaultProfileSerializer(profile)
    return Response({'success': True, 'response': serializer.data},
            status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_following_list(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=id, user__is_active=True)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = FriendsList.objects.get(profile=profile)
            following_list = obj.following.all()
            if following_list.count() > 0:
                serializer = GetUserProfileSerializer(following_list, many=True)
                return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'response': {'message': 'You are not following anyone.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'You are not following anyone.'}},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_followers_list(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=id, user__is_active=True)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User profile does not exist or is inactive.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = FriendsList.objects.get(profile=profile)
            followers_list = obj.followers.all()
            if followers_list.count() > 0:
                serializer = GetUserProfileSerializer(followers_list, many=True)
                return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'response': {'message': 'You are not followed by anyone.'}},
                            status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'You are not followed by anyone.'}},
                        status=status.HTTP_404_NOT_FOUND)       


# UserSettings APIs
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_email(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    email = request.data['email'] if 'email' in request.data else None
    if not email:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    emails = list(User.objects.all().values_list('email', flat=True))
    if email in emails:
        return Response({'success': False, 'response': {'message': 'A user with this email address already exists.'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        user = profile.user
        user.email = email
        user.save()
    return Response({'success': True, 'response': {'message': email}},
            status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_privacy_settings(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    try:
        privacy = UserPrivacySettings.objects.get(profile=profile)
    except ObjectDoesNotExist:
        privacy = UserPrivacySettings.objects.create(profile=profile)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    serializer = UserPrivacySettingsSerializer(privacy, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors},
                         'status': status.HTTP_400_BAD_REQUEST})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_privacy_settings(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    try:
        privacy = UserPrivacySettings.objects.get(profile=profile)
    except ObjectDoesNotExist:
        privacy = UserPrivacySettings.objects.create(profile=profile)
    serializer = UserPrivacySettingsSerializer(privacy)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def save_fcmdevice(request):
    name = request.data['name'] if 'name' in request.data else None
    device_id = request.data['device_id'] if 'device_id' in request.data else None
    registration_id = request.data['registration_id'] if 'registration_id' in request.data else None
    type = request.data['type'] if 'type' in request.data else None
    registration_tokens = list(FCMDevice.objects.filter(device_id=device_id).values_list('registration_id', flat=True))
    if not registration_id in registration_tokens:
        serializer = FCMDeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'success': False, 'response': {'message': 'Device already registered.'}},
                status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    notifications = Notification.objects.filter(notifiers_list=profile
                        ).order_by('-created_at')
    # Read notifications using thread.
    ReadNotificationsThread(request, profile, notifications).start()

    paginator = CustomPagination()
    paginator.page_size = 15
    result_page = paginator.paginate_queryset(notifications, request)
    serializer = NotificationSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_notification(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    notification_id =  request.data.get('notification_id', None)
    if notification_id is None:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.notifiers_list.remove(profile)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
            status=status.HTTP_400_BAD_REQUEST)
    return Response({'success': True, 'response': {'message': 'Notification Deleted Successfully'}},
                    status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def turn_of_notification(request):
    try:
        profile = Profile.objects.get(user=request.user , is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)

    post_id = request.GET.get('post' , None)
    post_comment_id = request.GET.get('post_comment', None)
    comment_reply_id = request.GET.get('comment_reply' , None)

    if post_id is None and post_comment_id is None and comment_reply_id is None:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)

    notifier = None
    if post_id:
        try:
            notifier = NotifiersList.objects.get(post__id=post_id, notifiers_list=profile)
        except:
            notifier = None

    elif post_comment_id:
        try:
            notifier = NotifiersList.objects.get(post_comment__id=post_comment_id, notifiers_list=profile)
        except:
            notifier = None

    elif comment_reply_id:
        try:
            notifier = NotifiersList.objects.get(comment_reply__id=comment_reply_id, notifiers_list=profile)
        except:
            notifier = None

    if notifier is None:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_404_NOT_FOUND)

    notifier.notifiers_list.remove(profile)
    notifier.save()
    return Response({'success': True, 'response': {'message': 'Notification turned off successfully!'}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile_id(request):
    username = request.query_params.get('username')
    if not username:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(user__username=username, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User Profile does not exist.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid Profile ID!'}},
                    status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': True, 'response': {'message': profile.id}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_profile_story(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    story_type = request.data['story_type'] if 'story_type' in request.data else 'Text'
    media_image = request.data['media_image'] if 'media_image' in request.data else None
    media_video = request.data['media_video'] if 'media_video' in request.data else None
    except_friends = request.data['except_friends'] if 'except_friends' in request.data else None

    if story_type == 'Media' and not media_video and not media_image:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    if media_image:
        if media_image.size > 20971520:
            return Response({'success': False, 'response': {'message': "Please select a smaller image. Maximum allowed size is 20mb."}},
                    status=status.HTTP_400_BAD_REQUEST)
    print(except_friends)
    
    serializer = ProfileStorySerializer(data=request.data)
    if serializer.is_valid():
        story = serializer.save()
        post = Post.objects.create(
                profile=story.profile,
                privacy=story.privacy,
                text=story.text,
                story_post=True,
            )
        story.post = post
        
        if except_friends:
            except_friends = json.loads(except_friends)
            if type(except_friends) == list:
                for u_id in except_friends:
                    try:
                        u_profile = Profile.objects.get(id=u_id)
                        story.except_friends.add(u_profile)
                    except:
                        pass

        story.save()
        serializer = GetSingleProfileStorySerializer(story)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_story(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    try:
        story = ProfileStory.objects.get(id=id, profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Story does not exist or you are not allowed to delete it.'}},
                    status=status.HTTP_404_NOT_FOUND)
    post = story.post
    try:
        post.is_deleted = True
        post.save()
    except:
        pass
    story.delete()
    return Response({'success': True, 'response': {'message': 'Story deleted successfully.'}},
            status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_story(request):
    id = request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    try:
        story = ProfileStory.objects.get(id=id, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Story does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    serializer = GetSingleProfileStorySerializer(story)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_story_view(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': e}},
                    status=status.HTTP_401_UNAUTHORIZED)
    story = request.data['story'] if 'story' in request.data else None
    if not story:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        story = ProfileStory.objects.get(id=story, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Story does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    if profile != story.profile:
        try:
            story_view = StoryView.objects.get(
                        story=story,
                        profile=profile,
                    )
            return Response({'success': True, 'response': {'message': 'Already viewed.'}},
                    status=status.HTTP_201_CREATED)
        except:
            story_view = StoryView.objects.create(
                        story=story,
                        profile=profile,
                    )
            return Response({'success': True, 'response': {'message': 'Viewed'}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': 'Cannot add view for your own story.'}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_profile_stories(request):
    profile_id = request.query_params.get('profile_id')
    try:
        user_profile = Profile.objects.get(user=request.user , is_deleted=False)
    except:
        user_profile = None
    if not profile_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile_id, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User Profile does not exist.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid Profile ID!'}},
                    status=status.HTTP_400_BAD_REQUEST)
        stories = ProfileStory.objects.filter(profile=profile, is_deleted=False).order_by("created_at")

        if user_profile and user_profile != profile:
            stories = stories.exclude(
                privacy='OnlyMe',
            )
            
        if user_profile:
            stories = stories.exclude(
                except_friends=user_profile
            )
        serializer = GetSingleProfileStorySerializer(stories, many=True)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_stories(request):
    all_profiles_list = []
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        all_profiles_list.append(profile.id)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_401_UNAUTHORIZED)
    following_list = FriendsList.objects.filter(profile=profile)
    if len(following_list) > 0:
        following_list = following_list[0].friends.values_list('id' , flat=True)
        all_profiles_list.extend(following_list)
    str_pf_ids = []
    stories = ProfileStory.objects.filter(profile__id__in=all_profiles_list, is_deleted=False).order_by('-created_at')
    def cstm_fitler(r_story):
        if r_story.privacy == 'OnlyMe' and r_story.profile != profile:
            return False
        if r_story.profile.id not in str_pf_ids and not profile in r_story.except_friends.all():
            str_pf_ids.append(r_story.profile.id)
            return True
        return False

    stories = filter(cstm_fitler , stories)
    stories = GetSingleProfileStorySerializer(stories, many=True).data
    return Response({'success': True, 'response': {'message': stories}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_social_login(request):
    email = request.data['email'] if 'email' in request.data else None
    username = request.data['username'] if 'username' in request.data else None
    first_name = request.data['first_name'] if 'first_name' in request.data else None
    mobile_number = request.data['mobile_number'] if 'mobile_number' in request.data else None
    social_id = request.data['social_id'] if 'social_id' in request.data else None
    social_platform = request.data['social_platform'] if 'social_platform' in request.data else None
    # Validation Check
    if not first_name or not social_platform:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                status=status.HTTP_400_BAD_REQUEST)
    if not email and not social_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                status=status.HTTP_400_BAD_REQUEST)
    # Generate Fake Email address if email is not provided.
    if not email:
        email = f"{social_id}@{social_platform}.com"
    username = email.split('@')[0]
    # Check if user already exists or not.
    try:
        user = User.objects.get(email=email)
        profile = Profile.objects.get(user=user)
        password = user.password
    except:
        user = User.objects.create(
                email = email,
                username = username,
                first_name = first_name,
                mobile_number = mobile_number,
                social_account = True,
                social_platform = social_platform,
                is_active = True,
            )
        # Create Fake Password
        password = 'User123$'
        user.set_password('User123$')
        user.save()

        # Create User's Profile
        profile = Profile.objects.create(
            user=user,
            gender='Male',
        )
        # Create User's Profile Picture
        pp_album = ProfilePictureAlbum.objects.create(
            profile=profile
        )
        profile_picture = ProfilePicture.objects.create(
            album = pp_album
        )
        user_pp = UserProfilePicture.objects.create(
            profile = profile,
            picture = profile_picture
        )

    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    access_token = token.key

    # Create Login History
    try:
        LoginHistory.objects.create(
            profile = profile,
            login_at = datetime.now(),
        )
    except Exception as e:
        print(e)
    profile_obj = GetUserProfileSerializer(profile).data
    return Response({'success': True, 'response': {'profile': profile_obj, 'access_token': access_token}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_activity(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success':False, 'response':{'message': str(e)}},
                                status=status.HTTP_401_UNAUTHORIZED)
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = str(profile.id)
    serializer = UserActivitySerializer(data=request.data)
    if serializer.is_valid():
        user_activity = serializer.save()
        serializer = GetUserActivitySerializer(user_activity, context={'user':request.user})
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_activity(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success':False, 'response':{'message': str(e)}},
                                status=status.HTTP_401_UNAUTHORIZED)
    user_activity = UserActivity.objects.filter(profile=profile, is_deleted=False)
    serializer = GetUserActivitySerializer(user_activity, many=True, context={'user':request.user})
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_activity(request):
    id = request.data['id'] if 'id' in request.data else None
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success':False, 'response':{'message': str(e)}}, 
                                status=status.HTTP_401_UNAUTHORIZED)
    if not id:
        return Response({'success':False, 'response':{'message':'Invalid Data!'}},
                                status=status.HTTP_400_BAD_REQUEST)
    try:
        user_activity = UserActivity.objects.get(id=id, profile=profile, is_deleted=False)
        user_activity.is_deleted = True
        user_activity.save()
        return Response({'success':True, 'response':{'message': 'User Activity Deleted Successfully!'}},
                                status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success':False, 'response':{'message': str(e)}},
                                status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_activity(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({'success':False, 'response':{'message': str(e)}},
                                status=status.HTTP_401_UNAUTHORIZED)
    try:
        user_activity = UserActivity.objects.get(profile=profile)
    except ObjectDoesNotExist:
        user_activity = UserActivity.objects.create(profile=profile)
 
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = str(profile.id)
    serializer = UserActivitySerializer(user_activity, data=request.data, partial=True)
    if serializer.is_valid():
        user_activity = serializer.save()
        serializer = GetUserActivitySerializer(user_activity, context={'user':request.user})
        return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_contact_info(request):
    alter_mobile = request.data['alter_mobile'] if 'alter_mobile' in request.data else None
    if not alter_mobile:
        return Response({'success':False, 'response':{'message':'Invalid data!'}},
                                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
        serializer = ContactInforSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            contact_info = serializer.save()
            serializer = DefaultProfileSerializer(contact_info)
            return Response({'success': True, 'response': {'message': serializer.data}},
                                status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                                status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'success':False, 'response':{'message': str(e)}},
                                status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bithday_profiles(request):
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    year, month, day = str(today).split('-')
    day = day.split(' ')
    day = day[0]

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        return Response({'success':False, 'response':{'message': str(e)}}, 
                                status=status.HTTP_401_UNAUTHORIZED)
    try:
        today_birthday = FriendsList.objects.get(profile=profile).friends.filter(
                        birth_date__day=int(day), birth_date__month=current_month)
        today_birthday = DefaultProfileSerializer(today_birthday, many=True).data
    except Exception as e:
        print("exception", e)
        today_birthday = None

    try:
        upcoming_birthday = FriendsList.objects.get(profile=profile).friends.filter(
                        birth_date__month=current_month).exclude(birth_date__day=day)
        upcoming_birthday = DefaultProfileSerializer(upcoming_birthday, many=True).data
    except:
        upcoming_birthday = None

    # Logic for next twelve months
    cur_month = current_month
    cur_year = current_year
    twelve_month_birthdays = []

    for i in range(11):
        if cur_month < 12:
            cur_month += 1
        else:
            cur_month = 1
            cur_year += 1
        try:
            one_month_birthdays = FriendsList.objects.get(profile=profile).friends.filter(
                                        birth_date__month=cur_month).order_by('birth_date')
            one_month_birthdays = DefaultProfileSerializer(one_month_birthdays, many=True).data
            new_dict = {
                'Month': cur_month,
                'Year': cur_year,
                'one_month_birthdays': one_month_birthdays
            }
            twelve_month_birthdays.append(new_dict)
        except Exception as e:
            print(e)
            one_month_birthdays = None
    
    results ={
        'today_birthday':today_birthday,
        'upcoming_birthday':upcoming_birthday,
        'twelve_month_birthdays':twelve_month_birthdays,
    }
    return Response({'success':True, 'response':{'message':results}}, 
                                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_friend_requests(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False,'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    friend_requests = FriendRequest.objects.filter(req_sender=profile, is_active=True, status='Pending')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(friend_requests, request)
    serializer = SenderUserProfileSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_report_profile_category(request):
    category = ReportProfileCategory.objects.all()
    serializer = GetReportProfileCategorySerializer(category, many=True)
    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_profile(request):
    reported_profile = request.data['reported_profile'] if 'reported_profile' in request.data else None
    category = request.data['category'] if 'category' in request.data else None
    if not reported_profile or not category:
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
        serializer = ReportProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
                        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_profile(request):
    blocked_user = request.data['blocked_user'] if 'blocked_user' in request.data else None
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED)
    if not blocked_user:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        blocked_user = Profile.objects.get(id=blocked_user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_BAD_REQUEST)

    if request.method == 'POST':
        try:
            blocked_profile = BlockProfile.objects.get(profile=profile, blocked_user=blocked_user)
            return Response({'success': True, 'response': {'message': 'Already Blocked!'}},
                        status=status.HTTP_200_OK)
        except BlockProfile.DoesNotExist:
            blocked_profile =  BlockProfile.objects.create(profile=profile, blocked_user=blocked_user)
            try:
                friend_list = FriendsList.objects.get(profile=profile)
                friend_list.friends.remove(blocked_user)
                friend_list.followers.remove(blocked_user)
                friend_list.following.remove(blocked_user)
                friend_list.save()
            except Exception as e:
                pass

            return Response({'success': True, 'response': {'message': 'User Blocked!'}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': 'Something Wrong!'}},
                status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def progress_profile(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    serializer = ProgressUserProfileSerializer(profile, many=False, context={'profile': profile})

    return Response({'success': True, 'response':serializer.data},
            status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_privacy(request):
    
    privacy = request.data.get('privacy', None)
    privacy_field = request.data.get('privacy_field', None)

    if not privacy or not privacy_field:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    
    if privacy_field == 'mobile':
        if privacy == 'Show':
            profile.mobile_privacy = 'Show'
        else:
            profile.mobile_privacy = 'Hide'

    elif privacy_field == 'special_offer':
        if privacy == 'Show':
            profile.special_offer_privacy = 'Show'
        else:
            profile.special_offer_privacy = 'Hide'

    elif privacy_field == 'recommended':
        if privacy == 'Show':
            profile.recommended_privacy = 'Show'
        else:
            profile.recommended_privacy = 'Hide'

    profile.save()

    return Response({'success': True, 'response':'Privacy Updated Successfully!'},
            status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_business_profile(request):
#     name = request.data.get('name', None)
#     about = request.data.get('about', None)
#     company_type = request.data.get('company_type', None)
#     license_number = request.data.get('license_number', None)
#     email = request.data.get('email', None)
#     phone = request.data.get('phone', None)
#     dial_code = request.data.get('dial_code', None)
#     country = request.data.get('country', None)
#     state = request.data.get('state', None)
#     city = request.data.get('city', None)
#     street_address = request.data.get('street_address', None)
#     longitude = request.data.get('longitude', None)
#     latitude = request.data.get('latitude', None)
#     logo = request.data.get('logo', None)
#     cover_image = request.data.get('cover_image', None)

#     if not name or not about or not company_type or not license_number or \
#         not email or not phone or not dial_code or not country or not state or \
#              not city or not street_address or not longitude or not latitude:
#         return Response({'success': False, 'response':'Invalid Data!'},
#             status=status.HTTP_400_BAD_REQUEST)
#     try:
#         profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
#     except Exception as e:
#         return Response({"success": False, 'response': {'message': str(e)}},
#                         status=status.HTTP_404_NOT_FOUND)
#     try:
#         company = Company.objects.get(profile=profile, company_type=company_type)
#         return Response({"success": False, 'response': {'message': 'Company is already Exists!'}},
#                 status=status.HTTP_400_BAD_REQUEST)
#     except:
#         pass
    
#     try:
#         request.data._mutable = True
#     except:
#         pass
#     request.data['profile'] = profile.id
#     serializer = CompanySerializer(data=request.data)
#     if serializer.is_valid():
#         company = serializer.save()
#         if logo:
#             try:
#                 logo = CompanyLogo.objects.get(company=company, is_deleted=False)
#                 logo.is_deleted = True
#                 logo.save()
#             except:
#                 pass
#             logo = CompanyLogo.objects.create(company=company, logo=logo, is_deleted=False)

#         if cover_image:
#             try:
#                 cover_image = CompanyCoverImage.objects.get(company=company, is_deleted=False)
#                 cover_image.is_deleted = True
#                 cover_image.save()
#             except:
#                 pass
#             cover_image = CompanyCoverImage.objects.create(company=company, cover_image=cover_image, is_deleted=False)
#         serializer = GetCompanySerializer(company)
#         return Response({"success": True, 'response': serializer.data},
#                         status=status.HTTP_200_OK)
#     else:
#         return Response({"success": False, 'response': {'message': serializer.errors}},
#                 status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_business_profile(request):
    id = request.data.get('id', None)
    company_type = request.data.get('company_type', None)

    # name = request.data.get('name', None)
    # about = request.data.get('about', None)
    # company_type = request.data.get('company_type', None)
    # license_number = request.data.get('license_number', None)
    # email = request.data.get('email', None)
    # phone = request.data.get('phone', None)
    # dial_code = request.data.get('dial_code', None)
    # country = request.data.get('country', None)
    # state = request.data.get('state', None)
    # city = request.data.get('city', None)
    # street_address = request.data.get('street_address', None)
    # longitude = request.data.get('longitude', None)
    # latitude = request.data.get('latitude', None)
    com_logo = request.data.get('logo', None)
    com_cover_image = request.data.get('cover_image', None)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    if not id or not company_type:
        return Response({'success': False, 'response':'Invalid Data!'},
            status=status.HTTP_400_BAD_REQUEST)

    try:
        company = Company.objects.get(id=id, company_type=company_type)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)

    serializer = CompanySerializer(company, data=request.data, partial=True)
    if serializer.is_valid():
        company = serializer.save()
        if com_logo:
            try:
                media = CompanyLogo.objects.get(company=company, is_deleted=False)
                media.is_deleted = True
                media.save()
            except:
                pass
            media = CompanyLogo.objects.create(company=company, logo=com_logo, is_deleted=False)

        if com_cover_image:
            try:
                media = CompanyCoverImage.objects.get(company=company, is_deleted=False)
                media.is_deleted = True
                media.save()
            except:
                pass
            media = CompanyCoverImage.objects.create(company=company, cover_image=com_cover_image, is_deleted=False)
        serializer = GetCompanySerializer(company)
        return Response({"success": True, 'response': serializer.data},
                        status=status.HTTP_200_OK)
    else:
        return Response({"success": False, 'response': {'message': serializer.errors}},
                status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    user = profile.user
    user.is_active = False
    user.save()
    profile.is_deleted = True
    profile.save()
    return Response({'success': True, 'response':'Account Deleted Successfully!'},
            status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_business_profile(request):
    name = request.data.get('name', None)
    about = request.data.get('about', None)
    company_type = request.data.get('company_type', None)
    license_number = request.data.get('license_number', None)
    email = request.data.get('email', None)
    phone = request.data.get('phone', None)
    dial_code = request.data.get('dial_code', None)
    country = request.data.get('country', None)
    state = request.data.get('state', None)
    city = request.data.get('city', None)
    street_address = request.data.get('street_address', None)
    longitude = request.data.get('longitude', None)
    latitude = request.data.get('latitude', None)
    logo = request.data.get('logo', None)
    cover_image = request.data.get('cover_image', None)

    if not name or not about or not company_type or not license_number or \
        not email or not phone or not dial_code or not country or not state or \
             not city or not street_address or not longitude or not latitude:
        return Response({'success': False, 'response':'Invalid Data!'},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
        
    try:

        company = Company.objects.get(profile=profile, company_type=company_type)
        return Response({"success": False, 'response': {'message': 'Company is already Exists!'}},
                status=status.HTTP_400_BAD_REQUEST)
    except:
        pass

    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        company = serializer.save()
        if logo:
            try:
                logo = CompanyLogo.objects.get(company=company, is_deleted=False)
                logo.is_deleted = True
                logo.save()
            except:
                pass
            logo = CompanyLogo.objects.create(company=company, logo=logo, is_deleted=False)

        if cover_image:
            try:
                cover_image = CompanyCoverImage.objects.get(company=company, is_deleted=False)
                cover_image.is_deleted = True
                cover_image.save()
            except:
                pass
            cover_image = CompanyCoverImage.objects.create(company=company, cover_image=cover_image, is_deleted=False)
        serializer = GetCompanySerializer(company)
        return Response({"success": True, 'response': serializer.data},
                        status=status.HTTP_200_OK)
    else:
        return Response({"success": False, 'response': {'message': serializer.errors}},
                status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_profile(request):

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    
    company = Company.objects.filter(profile=profile)
    serializer = GetCompanySerializer(company, many=True)
    return Response({"success": True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_profile_stats(request):
    module_name = request.query_params.get('module_name', None)
    if not module_name:
        return Response({'success': False, 'response':'Invalid Data!'},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    
    context = dict()
    active_ads = None
    total_ad_view = None
    total_profile_view = None

    if module_name == 'Property':
        active_ads = Property.objects.filter(profile=profile, business_type='Company', is_deleted=False, is_active=True).count()
        total_ad_view = sum(list(Property.objects.filter(profile=profile, is_deleted=False, is_active=True, business_type='Company').values_list('view_count', flat=True)))
        # try:
        #     company = Company.objects.get(company_type='Property', profile=profile)
        #     company.view_count = + 1
        #     company.save()
        # except:
        #     pass
        try:
            total_profile_view = Company.objects.get(company_type='Property', profile=profile).view_count
        except:
            total_profile_view = None

    if module_name == 'Classified':
        active_ads = Classified.objects.filter(profile=profile, business_type='Company', is_deleted=False, is_active=True).count()
        total_ad_view = sum(list(Classified.objects.filter(profile=profile, is_deleted=False, is_active=True, business_type='Company').values_list('view_count', flat=True)))
        # try:
        #     company = Company.objects.get(company_type='Classified', profile=profile)
        #     company.view_count = + 1
        #     company.save()
        # except:
        #     pass
        try:
            total_profile_view = Company.objects.get(company_type='Property', profile=profile).view_count
        except:
            total_profile_view = None

    if module_name == 'Job':
        active_ads = Job.objects.filter(profile=profile, business_type='Company', is_deleted=False, is_active=True).count()
        total_ad_view = sum(list(Job.objects.filter(profile=profile, is_deleted=False, is_active=True, business_type='Company').values_list('view_count', flat=True)))
        # try:
        #     company = Company.objects.get(company_type='Job', profile=profile)
        #     company.view_count = + 1
        #     company.save()
        # except:
        #     pass
        try:
            total_profile_view = Company.objects.get(company_type='Job', profile=profile).view_count
        except:
            total_profile_view = None

    if module_name == 'Automotive':
        active_ads = Automotive.objects.filter(profile=profile, business_type='Company', is_deleted=False, is_active=True).count()
        total_ad_view = sum(list(Automotive.objects.filter(profile=profile, is_deleted=False, is_active=True, business_type='Company').values_list('view_count', flat=True)))
        # try:
        #     company = Company.objects.get(company_type='Automotive', profile=profile)
        #     company.view_count = + 1
        #     company.save()
        # except:
        #     pass
        try:
            total_profile_view = Company.objects.get(company_type='Property', profile=profile).view_count
        except:
            total_profile_view = None

    context ={
        'active_ads':active_ads,
        'total_ad_view':total_ad_view,
        'total_profile_view':total_profile_view
    }
    return Response({"success": True, 'response': context},
                                            status=status.HTTP_200_OK)