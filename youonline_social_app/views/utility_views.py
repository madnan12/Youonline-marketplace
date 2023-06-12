from unicodedata import name
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from blog_app.models import Blog
from ..custom_api_settings import CustomPagination
from ..constants import *
from ..decorators import *
from django.db.models import Q
from ..serializers.users_serializers import *
from ..serializers.post_serializers import *
from ..serializers.utility_serializers import *
from job_app.serializers import *
import random, string
from django.shortcuts import render
from django.conf import settings
from twilio.rest import Client
import environ
from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from itertools import chain
from operator import attrgetter
from django.contrib.auth.hashers import make_password
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FB_Notification
from fcm_django.models import FCMDevice
from ..models import *
from community_app.models import *
from video_app.models import *
from property_app.models import *
from classified_app.models import *
from automotive_app.models import *
from django.core.mail import EmailMultiAlternatives



@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_error_exceptions(request):
    all_exceptions = ExceptionRecord.objects.filter(is_resolved=False).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(all_exceptions, request)
    serializer = ExceptionRecordSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)



@api_view(['POST'])
@permission_classes([AllowAny])
def send_error_mail(request):
    error_subject = request.data['subject'] if 'subject' in request.data else None
    error_message = request.data['message'] if 'message' in request.data else None

    if error_subject is None or error_message is None:
        return Response({'success': False, 'response': {'message' : 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)

    to_list = [settings.ADMIN_EMAIL]
    if 'to' in request.data : to_list.append(request.data['to'])
    send_email = EmailMultiAlternatives(
            error_subject,
            error_message,
            settings.EMAIL_HOST_USER,
            to_list
        )
    try:
        send_email.send(fail_silently=False)
        return Response({'success': True, 'response': {'message' : 'Mail send successfuly'}},
                    status=status.HTTP_200_OK)
    except Exception as err:
        return Response({'success': False, 'response': {'message' : err}},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE)



@api_view(['GET'])
@permission_classes([AllowAny])
def get_countries(request):
    country_list = ['Australia', 'Canada', 'China', 'India', 'Kuwait', 'Oman', 'Pakistan', 
    'Saudi Arabia', 'South Africa', 'Syria', 'Uganda', 'United Arab Emirates', 'United Kingdom', 
    'United States', 'Yemen', 'Swiss franc']
    countries = []
    for c in country_list:
        try:
            country = Country.objects.get(name=c)
            countries.append(country)
        except:
            pass
    serializer = CountrySerializer(countries, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_states(request):
    country = request.query_params.get('country')
    if not country:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    states = State.objects.filter(country=country).order_by('name')
    serializer = StateSerializer(states, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cities(request):
    state = request.query_params.get('state')
    country = request.query_params.get('country')
    if not state and not country:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    if state:
        cities = City.objects.filter(state=state).order_by('name')
    elif country:
        cities = City.objects.filter(state__country__id=country).order_by('name')
    serializer = CitySerializer(cities, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_languages(request):
    languages = Language.objects.all().order_by("name")
    serializer = LanguageSerializer(languages, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_currencies(request):
    currency = Currency.objects.distinct('name').order_by('name')
    serializer = CurrencySerializer(currency, many=True)
    return Response({'success': True, 'response':  serializer.data},
                status=status.HTTP_200_OK)


# SEO APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_meta(request):
    return_dict = {}
    model_name = request.query_params.get('model_name')
    slug = request.query_params.get('slug')
    if not slug or not model_name:
        return Response({"success": False, 'response': 'Invalid Data.'},
                        status=status.HTTP_400_BAD_REQUEST)

    if model_name.lower() == 'all':
        try:
            profile = Profile.objects.get(user__username=slug, is_deleted=False, user__is_active=True)
        except Profile.DoesNotExist:
            try:
                group = Group.objects.get(slug=slug, is_deleted=False)
            except Group.DoesNotExist:
                try:
                    page = Page.objects.get(slug=slug, is_deleted=False)
                except:
                    return Response({"success": False, 'response': 'No Object Found'},
                        status=status.HTTP_404_NOT_FOUND)
                else:
                    return_dict = {
                        'name': page.name,
                        'description': page.description,
                        'type' : 'page'
                    }
            else:
                return_dict = {
                    'name': group.name,
                    'description': group.description,
                    'type' : 'group'
                }
        else:
            return_dict = {
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'bio': profile.bio,
                'id': profile.id,
                'type' : 'profile'
            }

    elif model_name == 'video':
        try:
            video = Video.objects.get(slug=slug, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        return_dict = {
            'title': video.title,
            'description': video.description,
        }
    elif model_name == 'property':
        try:
            property = Property.objects.get(slug=slug, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        return_dict = {
            'name': property.name,
            'description': property.description,
        }
    elif model_name == 'classified':
        try:
            classified = Classified.objects.get(slug=slug, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        return_dict = {
            'name': classified.name,
            'description': classified.description,
        }
    elif model_name == 'automotive':
        try:
            automotive = Automotive.objects.get(slug=slug, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        return_dict = {
            'name': automotive.name,
            'description': automotive.description,
        }
    elif model_name == 'blog':
        try:
            blog = Blog.objects.get(slug=slug, is_deleted=False)
            print()
        except Exception as e:
            return Response({"success": False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        return_dict = {
            'blog': blog.title,
            'description': blog.description,
        }
    elif model_name == 'job':
        try:
            job = Job.objects.get(slug=slug, is_deleted=False)
        except Exception as e:
            return Response({"success": False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        return_dict = {
            'Job': job.title,
            'description': job.description,
        }

    return Response({"success": True, 'response': {'message': return_dict}},
                    status=status.HTTP_200_OK)


