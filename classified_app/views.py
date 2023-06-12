from decimal import Decimal
from locale import currency
from unicodedata import category, name
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from . models import *
from youonline_social_app.models import *
from django.db.models import Q
from . serializers import *
from youonline_social_app.serializers.utility_serializers import *
import random, string
from django.shortcuts import render
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from firebase_admin.messaging import Notification as FB_Notification
from fcm_django.models import FCMDevice
from rest_framework import status
import datetime
import decimal
from django.db.models import F
from youonline_social_app.custom_api_settings import CustomPagination
from youonline_social_app.youonline_threads import SendEmailThread
from automotive_app.constants import is_valid_queryparam


@api_view(['GET'])
@permission_classes([AllowAny])
def get_classified_categories(request):
    # business_directory = request.query_params.get('business_directory')

    # if business_directory:
    #     if business_directory == 'true' or business_directory == 'True' :
    #         business_directory = True
    #     elif business_directory == 'false' or business_directory == 'False':
    #         business_directory = False
    # elif not business_directory:
    #     business_directory = False

    classifieds = ClassifiedCategory.objects.filter(
        is_deleted=False,
        # business_directory = business_directory
    )
    serializer = ClassifiedCategorySerializer(classifieds, many=True)
    return Response(
        {
            'success': True, 
            'response': serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_classified_sub_categories(request):
    category = request.query_params.get('category')
    if not category:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    sub_categories = ClassifiedSubCategory.objects.filter(category=category, is_deleted=False)
    serializer = ClassifiedSubCategorySerializer(sub_categories, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_classified_sub_sub_categories(request):
    sub_category = request.query_params.get('sub_category')
    if not sub_category:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    sub_sub_categories = ClassifiedSubSubCategory.objects.filter(sub_category=sub_category, is_deleted=False)
    serializer = ClassifiedSubSubCategorySerializer(sub_sub_categories, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_classified_media(request):
    classified = request.data.get('classified', None)
    classified_image = request.data.getlist('classified_image', None)
    classified_video = request.data.get('classified_video', None)

    if not classified or (not classified_image and not classified_video):
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        classified = Classified.objects.get(id=classified, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    if classified_image:
        if classified.classifiedmedia_classified.filter(is_deleted=False).exclude(classified_image=''):
            total_media = classified.classifiedmedia_classified.filter(is_deleted=False).exclude(classified_image='').count()
            my_length = total_media + len(classified_image)
            if my_length > 20:
                return Response({"success": False, 'response': {'message': 'Maximum 20 Image allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if len(classified_image) > 20:
                return Response({"success": False, 'response': {'message': 'Maximum 20 Image allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
    if classified_video:
        if classified.classifiedmedia_classified.filter(is_deleted=False).exclude(classified_video=''):
            total_media = classified.classifiedmedia_classified.filter(is_deleted=False).exclude(classified_video='').count()
            my_length = total_media + len(classified_video)
            
            if my_length > 1:
                return Response({"success": False, 'response': {'message': 'Only One Video allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if len(classified_video) > 1:
                return Response({"success": False, 'response': {'message': 'Only One Video allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)

    if classified_image:
        for c in classified_image:
            media = ClassifiedMedia.objects.create(classified=classified, classified_image=c, profile=profile)

    if classified_video:
        media = ClassifiedMedia.objects.create(classified=classified, classified_video=classified_video, profile=profile)

    serializer = ClassifiedGetSerializer(classified)
    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_classified_media(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        media = ClassifiedMedia.objects.get(id=id, is_deleted=False)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'classified Media item does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid media ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    media.is_deleted = True
    media.save()
    return Response({'success': True, 'response': {'message': 'Media deleted successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_classifieds(request):
    choice = request.query_params.get('choice')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    currency = request.query_params.get('currency')
    country = request.query_params.get('country')
    state = request.query_params.get('state')
    city = request.query_params.get('city')
    street_adress = request.query_params.get('street_adress')
    category = request.query_params.get('category')
    sub_category = request.query_params.get('sub_category')
    sub_sub_category = request.query_params.get('sub_sub_category')
    name = request.query_params.get('name')

    business_directory = request.query_params.get('business_directory' , False)

    if business_directory:
        if business_directory == 'true' or business_directory == 'True' :
            business_directory = True
        elif business_directory == 'false' or business_directory == 'False':
            business_directory = False
    elif not business_directory:
        business_directory = False

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None

    # Get Values for the filters
    if not choice:
        choice = 'all'
    if currency:
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
                return Response(
                    {
                        'success': False, 
                        'response': {
                            'message': str(e)
                        }
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
    if category:
        try:
            category = ClassifiedCategory.objects.get(id=category).title
        except Exception as e:
                return Response(
                    {
                        'success': False, 
                        'response': {
                            'message': str(e)
                        }
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
    else:
        category = ''
    if sub_category:
        try:
            sub_category = ClassifiedSubCategory.objects.get(id=sub_category).title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        sub_category = ''
    if sub_sub_category:
        try:
            sub_sub_category = ClassifiedSubSubCategory.objects.get(id=sub_sub_category).title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        sub_sub_category = ''
    if country:
        try:
            country = Country.objects.get(id=country).name
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        country = ''
    if state:
        try:
            state = State.objects.get(id=state).name
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        state = ''
    if city:
        try:
            city = City.objects.get(id=city).name
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        city = ''
    if not name:
        name = ''
    if not street_adress:
        street_adress = ''
    # Filter Based on Choices
    if choice == 'all':
        # Search Based on Country, City and State
        if country and city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        else:
            classifieds = Classified.objects.filter(is_deleted=False, business_directory=business_directory)
        # Search Based on Category, SubCategory and SubSubCategory
        if category and sub_category and sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and sub_category and not sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and not sub_category and not sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category)
        # Other search attributes.
        if min_price and max_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif max_price and not min_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress,) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress) &
                                                    Q(price__gte=min_price))
    # Filter Based on Logged in User Profile
    elif choice == 'my':
        # Search Based on Country, City and State
        if country and city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        else:
            classifieds = Classified.objects.filter(is_deleted=False, profile=profile, name__icontains=name, street_adress__icontains=street_adress , business_directory=business_directory)
        # Search Based on Category, SubCategory and SubSubCategory
        if category and sub_category and sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and sub_category and not sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and not sub_category and not sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category)
        # Other search attributes.
        if min_price and max_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif max_price and not min_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress,) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress) &
                                                    Q(price__gte=min_price))
    # Filter Logged in User's Favourite Classifieds
    elif choice == 'favourite':
        # Search Based on Country, City and State
        if country and city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    favouriteclassified_classified__profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif country and not city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    country__name__icontains=country,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and not state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and state and not currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    state__name__icontains=state,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and not city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    currency=currency,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        elif not country and city and not state and currency:
            classifieds = Classified.objects.filter(is_deleted=False,
                                                    favouriteclassified_classified__profile=profile,
                                                    currency=currency,
                                                    city__name__icontains=city,
                                                    name__icontains=name,
                                                    street_adress__icontains=street_adress,
                                                    business_directory=business_directory
                                                    )
        else:
            classifieds = Classified.objects.filter(is_deleted=False, favouriteclassified_classified__profile=profile, name__icontains=name, street_adress__icontains=street_adress, business_directory=business_directory)
        # Search Based on Category, SubCategory and SubSubCategory
        if category and sub_category and sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and sub_category and not sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and not sub_category and not sub_sub_category:
            classifieds = classifieds.filter(category__title__icontains=category)
        # Other search attributes.
        if min_price and max_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif max_price and not min_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress,) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price:
            classifieds = classifieds.filter(Q(street_adress__icontains=street_adress) &
                                                    Q(price__gte=min_price))
    else:
        classifieds = Classified.objects.filter(is_deleted=False, business_directory=business_directory)
    paginator = CustomPagination()
    paginator.page_size = 9
    result_page = paginator.paginate_queryset(classifieds, request)
    if profile:
        serializer = ClassifiedListingSerializer(result_page, many=True, context={'profile': profile})
    else:
        serializer = ClassifiedListingSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_classifieds_optimized(request):
    q_params = request.GET

    choice = q_params.get('choice' , None)
    profile_id = q_params.get('profile' , None)


    business_directory = q_params.get('business_directory' , False)

    if business_directory:
        if business_directory == 'true' or business_directory == 'True' :
            business_directory = True
        elif business_directory == 'false' or business_directory == 'False':
            business_directory = False
    elif not business_directory:
        business_directory = False

    if profile_id:
        profile = Profile.objects.get(
            user = request.user,
            is_deleted=False,
        )

    if not choice or choice == 'all':
        all_classifieds = Classified.objects.filter(
            is_deleted=False,
            business_directory=business_directory
        )

    elif choice and choice == 'my' and profile_id:
        all_classifieds = Classified.objects.filter(
            profile = profile,
            is_deleted = False,
            business_directory=business_directory
        )

    elif choice and choice == 'favourite':
        all_classifieds = Classified.objects.filter(
            is_deleted = False,
            business_directory=business_directory
            # favourite query here 
        )

    Q_FILTER_FUNC = {
        'country' : lambda itm_value, user_q : 
                                itm_value.country and 
                                itm_value.country.id and 
                                str(itm_value.country.id) == user_q,
        'state' : lambda itm_value, user_q : 
                                itm_value.state and 
                                itm_value.state.id and 
                                str(itm_value.state.id) == user_q,
        'city' : lambda itm_value, user_q :
                                itm_value.city and 
                                itm_value.city.id and 
                                str(itm_value.city.id) == user_q,
        'category' : lambda itm_value, user_q : 
                                itm_value.category and 
                                itm_value.category.id and 
                                str(itm_value.category.id) == user_q,
        'sub_category' : lambda itm_value, user_q : 
                                itm_value.sub_category and 
                                itm_value.sub_category.id and 
                                str(itm_value.sub_category.id) == user_q,
        'currency' : lambda itm_value, user_q : 
                                itm_value.currency and 
                                itm_value.currency.id and 
                                str(itm_value.currency.id) == user_q,
        'street_adress' : lambda itm_value, user_q:
                                itm_value.street_adress and
                                user_q.lower() in itm_value.street_adress.lower(),
        'name' :  lambda itm_value, user_q:
                                itm_value.name and
                                user_q.lower() in itm_value.name.lower(),
        'min_price' : lambda itm_value, user_q:
                                itm_value.price and
                                float(user_q) <= itm_value.price,
        'max_price' : lambda itm_value, user_q:
                                itm_value.price and
                                float(user_q) >= itm_value.price
    }

    ALL_FILTERS = [
        'country',
        'state',
        'city',
        'category',
        'sub_category',
        'street_adress',
        'max_price',
        'min_price',
        'name', 
        'currency',
    ]

    ALL_Q_PARAMS = [
        q_params.get('country' , None),
        q_params.get('state' , None),
        q_params.get('city' , None),
        q_params.get('category', None),
        q_params.get('sub_category', None),
        q_params.get('street_adress', None),
        q_params.get('max_price', None),
        q_params.get('min_price', None),
        q_params.get('name', None),
        q_params.get('currency', None),
    ]


    def filter_classified(itm):

        returned_value = False
        for_loop_returns = False
        success_queries = 0
        fail_queries = 0
        total_queries_len = len(list(filter(lambda x : x , ALL_Q_PARAMS)))

        for ft in ALL_FILTERS:
            q_prm_ft_key = q_params.get(ft , None) # getting query Params in User search
            # If query param exist in use search
            if q_prm_ft_key:
                get_item = Q_FILTER_FUNC.get(ft)(itm , q_prm_ft_key)
                if get_item :
                    returned_value = True
                    for_loop_returns = True
                    success_queries += 1
                else :
                    for_loop_returns = False
                    fail_queries += 1

        if success_queries == total_queries_len and fail_queries == 0 and for_loop_returns:
            returned_value = True
        else:
            returned_value = False
        
        return returned_value

    filtered_classifieds = []

    if any(ALL_Q_PARAMS):
        filtered_classifieds = list(filter(filter_classified , all_classifieds))
    else:
        filtered_classifieds = all_classifieds

    paginator = CustomPagination()
    paginator.page_size = 9
    result_page = paginator.paginate_queryset(filtered_classifieds, request)
    if profile_id:
        serializer = ClassifiedListingSerializer(result_page, many=True, context={'profile': profile})
    else:
        serializer = ClassifiedListingSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['PUT'])
@permission_classes([AllowAny])
def verify_classified(request):
    id = request.data['id'] if 'id' in request.data else None
    verification_status = request.data['verification_status'] if 'verification_status' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        classified_object = Classified.objects.get(id=id, is_deleted=False)
        classified_object.verification_status = verification_status
        classified_object.save()
        return Response({'success': True, 'response': {'message: Classified Verification Done'}},
                        status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Classified does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([AllowAny])
def promote_classified(request):
    id = request.data['id'] if 'id' in request.data else None
    promote = request.data['promote'] if 'promote' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if promote == 'true':
        is_promoted = True
    else:
        is_promoted = False
    try:
        classified_object = Classified.objects.get(id=id, is_deleted=False)
        classified_object.is_promoted = is_promoted
        classified_object.save()
        return Response({'success': True, 'response': {'message: Classified Promoted Successfully'}},
                        status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Classified does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_promoted_classifieds(request):
    business_directory = request.GET.get('business_directory' , False)
    
    if business_directory:
        if business_directory == 'true' or business_directory == 'True' :
            business_directory = True
        elif business_directory == 'false' or business_directory == 'False':
            business_directory = False
    elif not business_directory:
        business_directory = False
        
    profile = request.query_params.get('profile')
    if not profile:
        classifieds = Classified.objects.filter(
            is_promoted=True,
            is_deleted=False,
            business_directory=business_directory
        ).order_by('-created_at')
        favourite_classifieds = None
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(classifieds, request)
        serializer = ClassifiedGetSerializer(result_page,
                                               many=True,
                                               context={"profile": profile, 'favourite_classifieds': favourite_classifieds}
                                               )
        return paginator.get_paginated_response(serializer.data)
    else:
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
        except:
            return Response({'success': False, 'response': {'message': 'Profile does not exist'}},
                            status=status.HTTP_404_NOT_FOUND)
        classifieds = Classified.objects.filter(is_promoted=True, is_deleted=False).order_by('-created_at')
        favourite_classifieds = []
        favourites = FavouriteClassified.objects.filter(profile=profile, is_deleted=False)
        for favourite in favourites:
            favourite_classifieds.append(favourite.classified.id)
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(classifieds, request)
        serializer = ClassifiedGetSerializer(result_page, many=True, context={"profile": profile, 'favourite_classifieds': favourite_classifieds})
        return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_classified(request):
    if request.method == 'POST':
        serializer = ClassifiedContactSerializer(data=request.data)
        if serializer.is_valid():
            classified_contact = serializer.save()
            # Getting Email ready
            html_template = render_to_string('email/u-classified-contact-email.html',
                                         {'email': classified_contact.email, 'message': classified_contact.message, 'img_link': settings.DOMAIN_NAME})
            text_template = strip_tags(html_template)
            # Email sending thread
            subject = f'Classified | {classified_contact.classified.name}'
            SendEmailThread(request, subject, html_template).start()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def report_classified(request):
    if request.method == 'POST':
        serializer = ClassifiedReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


# Landing Page APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_classifieds(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    classifieds = Classified.objects.filter(is_promoted=True, is_deleted=False).order_by('-created_at')
    if profile:
        serializer = ClassifiedListingSerializer(classifieds, many=True, context={"profile": profile})
    else:
        serializer = ClassifiedListingSerializer(classifieds, many=True)
    return Response({"success": False, 'response': serializer.data},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_furniture_classifieds(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    print(profile)
    classifieds = Classified.objects.filter(is_promoted=True, category__title__icontains='Furniture', is_deleted=False).order_by('-created_at')
    if profile:
        serializer = ClassifiedListingSerializer(classifieds, many=True, context={"profile": profile})
    else:
        serializer = ClassifiedListingSerializer(classifieds, many=True)

    return Response({"success": False, 'response': serializer.data},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_electronic_classifieds(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    classifieds = Classified.objects.filter(is_promoted=True, category__title__icontains='Electronic', is_deleted=False).select_related(
                    'category','sub_category','sub_sub_category','profile','post',
                    'company','country','state','city','language','currency'
                                                ).order_by('-created_at')
    if profile:
        serializer = ClassifiedListingSerializer(classifieds, many=True, context={"profile": profile})
    else:
        serializer = ClassifiedListingSerializer(classifieds, many=True)
    return Response({"success": False, 'response': serializer.data},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_classifieds_by_category(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None

    category = request.query_params.get("id",None)
    sorted_by = request.query_params.get("sorted_by",None)
    if not category:
        return Response({"success": False, 'response': "Invalid data!"},
                        status=status.HTTP_400_BAD_REQUEST)
    
    if sorted_by == 'hightolow':
        classifieds = Classified.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-price')

    elif sorted_by == 'lowtohigh':
        classifieds = Classified.objects.filter(category=category, is_deleted=False, is_active=True).order_by('price')

    elif sorted_by == 'newtoold':
        classifieds = Classified.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        classifieds = Classified.objects.filter(category=category, is_deleted=False, is_active=True).order_by('created_at')

    elif sorted_by == 'featured':
        classifieds = Classified.objects.filter(category=category, is_deleted=False, is_promoted=True, is_active=True).order_by('-created_at')
    else:
        classifieds = Classified.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')
                        
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    if profile:
        serializer = ClassifiedGetSerializer(result_page, many=True, context={'profile':profile})
    else:
        serializer = ClassifiedGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)



@api_view(['GET'])
@permission_classes([AllowAny])
def search_landing_classified(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None

    # if we have category then we will not search only based on category
    category = request.query_params.get("category", False)

    search = request.query_params.get("name", False)
    # will get id's
    country = request.query_params.get("country", False)
    city = request.query_params.get("city", False)

    try:
        results = None

        if category:
               results = Classified.objects.filter(category=category)

        else:
            if search:
                classifieds = Classified.objects.filter(is_deleted=False).filter(
                    Q(name__icontains=search) |
                    Q(country__name__icontains=search) |
                    Q(state__name__icontains=search) |
                    Q(city__name__icontains=search)
                ).order_by('-created_at')
                results = classifieds
            else:
                classifieds = Classified.objects.filter(is_deleted=False).order_by('-created_at')

            if country and city:
                   results = classifieds.filter(country=country,city=city)
            elif country and not city:
                results = classifieds.filter(country=country)
            elif not country and city:
                results = classifieds.filter(city=city)

        if not results:
            return Response({'success': False, 'response': {'message': "No found"}},
                            status=status.HTTP_404_NOT_FOUND)

        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(results, request)
        if profile:
            serializer = ClassifiedListingSerializer(result_page, many=True, context={"profile": profile})
        else:
            serializer = ClassifiedListingSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)

####################################################################################################

@api_view(['GET'])
@permission_classes([AllowAny])
def filter_classifieds(request):
    name = request.query_params.get('name') if 'name' in request.query_params else None
    category = request.query_params.get('category') if 'category' in request.query_params else None
    min_price = request.query_params.get('min_price') if 'min_price' in request.query_params else None
    max_price = request.query_params.get('max_price') if 'max_price' in request.query_params else None
    location = request.query_params.get('location') if 'location' in request.query_params else None

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None

    if not name:
        name = ''
    if not category:
        category = ''
    if not location:
        location = ''
    if category:
        try:
            category = ClassifiedCategory.objects.get(id=category)
            category.view_count += 1
            category.save()
            category = category.title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND
                )

    if min_price and max_price:
        classifieds = Classified.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__gte=min_price) &
                                        Q(price__lte=max_price),
                                        is_deleted=False,
                                        is_active=True)
    elif min_price and not max_price:
        classifieds = Classified.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__gte=min_price),
                                        is_deleted=False,
                                        is_active=True)
    elif max_price and not min_price:
        classifieds = Classified.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__lte=max_price),
                                        is_deleted=False,
                                        is_active=True)
    else:
        classifieds = Classified.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location),
                                        is_deleted=False,
                                        is_active=True)
    if profile:
        for c in classifieds:
            if not c.classifiedsearchhistory_classfied.filter(profile=profile):
                search_history = ClassifiedSearchHistory.objects.create(
                                                profile=profile,
                                                classified=c,
                )

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    serializer = ClassifiedGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_deal_classifieds(request):
    classifieds = Classified.objects.filter(is_deal=True, is_active=True, is_deleted=False, verification_status='Verified')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    serializer = ClassifiedGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_classifieds(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None 
        
    classifieds = ''
    if profile:
        search_history = ClassifiedSearchHistory.objects.filter(profile=profile)

        classifieds = []
        if search_history:
            for h in search_history:
                classifieds_list = Classified.objects.filter(
                    id=h.classified.id,
                    is_deleted=False,
                    is_active=True).distinct()
                if classifieds_list:
                    for c in classifieds_list:
                        classifieds.append(c)
        else:
            date_from = datetime.datetime.now() - datetime.timedelta(days=3)
            classifieds = Classified.objects.filter(created_at__gte=date_from, verification_status='Verified' ,is_deleted=False)
                                        
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    serializer = ClassifiedGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_classified_featured_brands(request):
    brands = ClassifiedeMake.objects.filter(is_featured=True)
    serializer = ClassifiedeMakeSerializer(brands, many=True)
    return Response({"success": True, 'response': serializer.data},
                status=status.HTTP_200_OK)
            

@api_view(['GET'])
@permission_classes([AllowAny])
def get_classifieds_by_brands(request):
    brand = request.query_params.get('brand', None)
    if not brand:
        return Response({"success": False, 'response': 'Invalid Data!'},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        brand = ClassifiedeMake.objects.get(id=brand)
    except Exception as e:
        return Response({"success": False, 'response': str(e)},
            status=status.HTTP_404_NOT_FOUND)
    
    classifieds = Classified.objects.filter(make=brand, is_active=True, is_deleted=False)
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    serializer = ClassifiedGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_classifieds(request):
    sorted_by = request.query_params.get('sorted_by', None)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None


    if sorted_by == 'hightolow':
        classifieds = Classified.objects.filter(is_deleted=False, is_active=True).order_by('-price')

    elif sorted_by == 'lowtohigh':
        classifieds = Classified.objects.filter(is_deleted=False, is_active=True).order_by('price')

    elif sorted_by == 'newtoold':
        classifieds = Classified.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        classifieds = Classified.objects.filter(is_deleted=False, is_active=True).order_by('created_at')

    elif sorted_by == 'featured':
        classifieds = Classified.objects.filter(is_deleted=False, is_promoted=True, is_active=True).order_by('-created_at')
    else:
        classifieds = Classified.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    if profile:
        serializer = ClassifiedGetSerializer(result_page, many=True, context={'profile':profile})
    else:
        serializer = ClassifiedGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_classified(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)

    business_type = request.data['business_type'] if 'business_type' in request.data else None
    name = request.data['name'] if 'name' in request.data else None
    category = request.data['category'] if 'category' in request.data else None
    mobile = request.data['mobile'] if 'mobile' in request.data else None
    currency = request.data['currency'] if 'currency' in request.data else None
    price = request.data['price'] if 'price' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    c_type = request.data['type'] if 'type' in request.data else None
    sub_category = request.data['sub_category'] if 'sub_category' in request.data else None
    make = request.data['brand'] if 'brand' in request.data else None
    street_adress = request.data['street_adress'] if 'street_adress' in request.data else None
    longitude = request.data['longitude'] if 'longitude' in request.data else None
    latitude = request.data['latitude'] if 'latitude' in request.data else None
    classified_image = request.data['classified_image'] if 'classified_image' in request.data else None
    dial_code = request.data['dial_code'] if 'dial_code' in request.data else None
    price = Decimal(price)

    if not name  or not category or not price  or not sub_category \
         or not mobile or not currency  or not street_adress  or not classified_image or not business_type\
         or not description or not c_type  or not latitude or not longitude or not dial_code:
        return Response({"success": False, 'response':{'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)

    try:
        request.data._mutable = True
    except:
        pass

    if make:
        request.data['make'] = make
    elif make == '':
        request.data['make'] = None
    else:
        request.data['make'] = None
        
    request.data['profile'] = profile.id

    serializer = PostClassifiedSerializer(data=request.data)
    if serializer.is_valid():
        classified = serializer.save()
        classified.is_active=True
        if longitude or latitude:
            classified.long = Decimal(longitude)
            classified.lat = Decimal(latitude)
        classified.save()

        # creating Notification for Classifieds
        notification = Notification(
        type = 'Classified',
        profile = profile,
        text = f'Your classified {classified.name} is created successfully.',
        )
        notification.save()
        notification.notifiers_list.add(profile)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass
        # End Notifications

        classified = classified.id
        classified = Classified.objects.get(id=classified)
        serializer = ClassifiedGetSerializer(classified, context={"request": request, "profile": classified.profile})
        url = f'{settings.FRONTEND_SERVER_NAME}/admin/verification/classified/' + str(classified.id)
        html_template = render_to_string(
            'email/u-classified-email.html',
            {
                'id': str(classified.slug),
                'url': url,
                'img_link': settings.DOMAIN_NAME,
            }
        )
        text_template = strip_tags(html_template)
        # Sending Email to admin
        subject = 'YouOnline | Classified Verification'
        SendEmailThread(request, subject, html_template).start()
        # SEO Meta Creation
        filename ='CSVFiles/XML/classifieds.xml'
        open_file=open(filename,"r")
        read_file=open_file.read()
        open_file.close()
        new_line=read_file.split("\n")
        last_line="\n".join(new_line[:-1])
        open_file=open(filename,"w+")
        for i in range(len(last_line)):
            open_file.write(last_line[i])
        open_file.close()

        loc_tag=f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{classified.slug}</loc>\n"
        lastmod_tag=f"<lastmod>{classified.created_at}</lastmod>\n"
        priorty_tag=f"<priority>0.8</priority>\n</url>\n</urlset>"
        with open(filename, "a") as fileupdate:
            fileupdate.write(loc_tag)
            fileupdate.write(lastmod_tag)
            fileupdate.write(priorty_tag)
        # SEO Meta Close
        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_201_CREATED)
    else:
        print('*******', serializer.errors)
        return Response({"success": False, 'response': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_classified(request):
    id = request.data['id'] if 'id' in request.data else None
    remove_media = request.data['remove_media'] if 'remove_media' in request.data else None
    make = request.data['brand'] if 'brand' in request.data else None

    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        classified = Classified.objects.get(id=id)
        serializer = UpdateClassifiedSerializer(classified, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if remove_media:
                media_id = remove_media[1:-1].replace('"', '').split(',')
                for i in media_id:
                    try:
                        media = ClassifiedMedia.objects.get(id=i)
                        media.is_deleted = True
                        media.save()
                    except Exception as e:
                        print(e)
            serializer = ClassifiedGetSerializer(classified)
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({'success': False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_brands_by_subcategory(request):
    subcategory = request.query_params.get('subcategory', None)
    if not subcategory:
        return Response({"success": False, 'response': 'Invalid Data!'},
            status=status.HTTP_400_BAD_REQUEST)
    
    brands = ClassifiedeMake.objects.filter(subcategory=subcategory)
    serializer = ClassifiedeMakeSerializer(brands, many=True)
    return Response({"success": True, 'response': serializer.data},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def filtering_classifieds(request):

    classifieds = ''

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    my_dict = dict()

    if "title" in request.query_params !=None and "title" in request.query_params !='':
        my_dict["name__icontains"] = request.query_params.get('title')

    if "category" in request.query_params !=None and "category" in request.query_params !='':
        category = request.query_params.get('category')
        # if not category:
        #     category = ''
        try:
            category = ClassifiedCategory.objects.get(id=category)
            category.view_count += 1
            category.save()
        except Exception as e:
            print(e)

        my_dict["category__title__icontains"] = category

    if "sub_category" in request.query_params !=None and "sub_category" in request.query_params !='':
        sub_category = request.query_params.get('sub_category')
        try:
            sub_category = ClassifiedSubCategory.objects.get(id=sub_category)
        except Exception as e:
            print(e)
        my_dict["sub_category__title__icontains"] = sub_category

    if "brand" in request.query_params !=None and "brand" in request.query_params !='':
        brand = request.query_params.get('brand')
        if brand:
            try:
                brand = ClassifiedeMake.objects.get(id=brand)
            except Exception as e:
                print(e)
            my_dict["make__title__icontains"] = brand

    if "condition" in request.query_params !=None and "condition" in request.query_params !='':
       my_dict["type__icontains"] = request.query_params.get('condition')

    if "min_price" in request.query_params !=None and "min_price" in request.query_params !='':
        if request.query_params.get('min_price'):
            my_dict["price__gte"] = request.query_params.get('min_price')

    
    if "max_price" in request.query_params !=None and "max_price" in request.query_params !='':
        if request.query_params.get('max_price'):
            my_dict["price__lte"] = request.query_params.get('max_price')

    if "currency" in request.query_params !=None and "currency" in request.query_params !='':
        currency = request.query_params.get('currency')
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
            print(e)

        my_dict["currency__name__icontains"] = currency
        
    if is_valid_queryparam(my_dict):
        if len(my_dict) < 1:
            classifieds = Classified.objects.filter(is_deleted=False, is_active=True)
        else:
            classifieds = Classified.objects.filter(**my_dict, is_deleted=False, is_active=True).distinct()
    
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    serializer = ClassifiedGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_classifieds(request):
    sorted_by = request.query_params.get('sorted_by', None)
    # business_type = request.query_params.get('business_type', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
        status=status.HTTP_401_UNAUTHORIZED)

    # if not business_type:
    #     return Response({"success": False, 'response': {'message': 'invalid data!'}},
    #                     status=status.HTTP_400_BAD_REQUEST)    

    # if business_type == 'Company':
    #     if sorted_by == 'hightolow':
    #         classifieds = Classified.objects.filter(
    #                                             profile=profile,
    #                                             is_deleted=False,
    #                                             business_type='Company'
    #                                         ).order_by('-price')
    #     elif sorted_by == 'lowtohigh':
    #         classifieds = Classified.objects.filter(
    #                                     profile=profile,
    #                                     is_deleted=False,
    #                                     business_type='Company'
    #                                 ).order_by('price')
    #     elif sorted_by == 'newtoold':
    #         classifieds = Classified.objects.filter(
    #                                     profile=profile,
    #                                     is_deleted=False,
    #                                     business_type='Company'
    #                                 ).order_by('-created_at')
    #     elif sorted_by == 'oldtonew':
    #         classifieds = Classified.objects.filter(
    #                                     profile=profile,
    #                                     is_deleted=False,
    #                                     business_type='Company'
    #                                 ).order_by('created_at')
    #     elif sorted_by == 'featured':
    #         classifieds = Classified.objects.filter(
    #                                     profile=profile,
    #                                     is_promoted = True,
    #                                     is_deleted=False,
    #                                     business_type='Company'
    #                                 ).order_by('-created_at')
    #     elif sorted_by == 'active':
    #         classifieds = Classified.objects.filter(
    #                             profile=profile,
    #                             is_active = True,
    #                             is_deleted=False,
    #                             business_type='Company'
    #                         ).order_by('-created_at')
    #     elif sorted_by == 'inactive':
    #         classifieds = Classified.objects.filter(
    #                             profile=profile,
    #                             is_active = False,
    #                             is_deleted=False,
    #                             business_type='Company'
    #                         ).order_by('-created_at')
    #     else:
    #         classifieds = Classified.objects.filter(
    #             profile=profile,
    #             is_deleted=False,
    #             business_type='Company'
    #         ).order_by('-created_at')
            
    # elif business_type == 'Individual':
    #     if sorted_by == 'hightolow':
    #         classifieds = Classified.objects.filter(
    #                                             profile=profile,
    #                                             is_deleted=False,
    #                                             business_type='Individual',
    #                                         ).order_by('-price')
    #     elif sorted_by == 'lowtohigh':
    #         classifieds = Classified.objects.filter(
    #                                     profile=profile,
    #                                     is_deleted=False,
    #                                     business_type='Individual',
    #                                 ).order_by('price')
    #     elif sorted_by == 'newtoold':
    #         classifieds = Classified.objects.filter(
    #                                     profile=profile,
    #                                     is_deleted=False,
    #                                     business_type='Individual',
    #                                 ).order_by('-created_at')
    #     elif sorted_by == 'oldtonew':
    #         classifieds = Classified.objects.filter(
    #                                     profile=profile,
    #                                     is_deleted=False,
    #                                     business_type='Individual',
    #                                 ).order_by('created_at')
    #     elif sorted_by == 'featured':
    #         classifieds = Classified.objects.filter(
    #                                     profile=profile,
    #                                     is_promoted = True,
    #                                     is_deleted=False,
    #                                     business_type='Individual',
    #                                 ).order_by('-created_at')
    #     elif sorted_by == 'active':
    #         classifieds = Classified.objects.filter(
    #                             profile=profile,
    #                             is_active = True,
    #                             is_deleted=False,
    #                             business_type='Individual',
    #                         ).order_by('-created_at')
    #     elif sorted_by == 'inactive':
    #         classifieds = Classified.objects.filter(
    #                             profile=profile,
    #                             is_active = False,
    #                             is_deleted=False,
    #                             business_type='Individual',
    #                         ).order_by('-created_at')
    #     else:
    #         classifieds = Classified.objects.filter(
    #             profile=profile,
    #             is_deleted=False,
    #             business_type='Individual',
    #         ).order_by('-created_at')

    if sorted_by == 'hightolow':
        classifieds = Classified.objects.filter(
                                            profile=profile,
                                            is_deleted=False,
                                        ).order_by('-price')
    elif sorted_by == 'lowtohigh':
        classifieds = Classified.objects.filter(
                                    profile=profile,
                                    is_deleted=False,
                                ).order_by('price')
    elif sorted_by == 'newtoold':
        classifieds = Classified.objects.filter(
                                    profile=profile,
                                    is_deleted=False,
                                ).order_by('-created_at')
    elif sorted_by == 'oldtonew':
        classifieds = Classified.objects.filter(
                                    profile=profile,
                                    is_deleted=False,
                                ).order_by('created_at')
    elif sorted_by == 'featured':
        classifieds = Classified.objects.filter(
                                    profile=profile,
                                    is_promoted = True,
                                    is_deleted=False,
                                ).order_by('-created_at')
    elif sorted_by == 'active':
        classifieds = Classified.objects.filter(
                            profile=profile,
                            is_active = True,
                            is_deleted=False,
                        ).order_by('-created_at')
    elif sorted_by == 'inactive':
        classifieds = Classified.objects.filter(
                            profile=profile,
                            is_active = False,
                            is_deleted=False,
                        ).order_by('-created_at')
    else:
        classifieds = Classified.objects.filter(
            profile=profile,
            is_deleted=False,
        ).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    serializer = ClassifiedGetSerializer(result_page, many=True, context={'profile': profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_classified(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        classified = Classified.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    classified.is_deleted = True
    classified.save()
    return Response({'success': True, 'response': {'message': 'classified deleted successfully!'}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favourite_classified(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        classified = Classified.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': 'Classified does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        try:
            favourite = FavouriteClassified.objects.get(profile=profile, classified=classified)
            favourite.delete()
            return Response({'success': True, 'response': {'message': "Classified removed from favourite List"}},
                            status=status.HTTP_200_OK)
        except:
            favourite = FavouriteClassified.objects.create(profile=profile, classified=classified)
            return Response({'success': True, 'response': {'message': "classified added to favourite list"}},
                            status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favourite_classifieds(request):
    sorted_by = request.query_params.get('sorted_by', None)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response(
            {'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)

    if sorted_by == 'hightolow':

        classifieds = Classified.objects.filter(
            favouriteclassified_classified__profile=profile, 
            is_deleted=False,
            is_active=True
        ).order_by('-price')
    elif sorted_by == 'lowtohigh':

        classifieds = Classified.objects.filter(
            favouriteclassified_classified__profile=profile, 
            is_deleted=False,
            is_active=True
        ).order_by('price')
    elif sorted_by == 'newtoold':

        classifieds = Classified.objects.filter(
            favouriteclassified_classified__profile=profile, 
            is_deleted=False,
            is_active=True
        ).order_by('-created_at')
    elif sorted_by == 'oldtonew':

        classifieds = Classified.objects.filter(
            favouriteclassified_classified__profile=profile, 
            is_deleted=False,
            is_active=True
        ).order_by('created_at')
    elif sorted_by == 'featured':

        classifieds = Classified.objects.filter(
            favouriteclassified_classified__profile=profile, 
            is_deleted=False,
            is_active=True,
            is_promoted=True
        ).order_by('-created_at')
    else:

        classifieds = Classified.objects.filter(
            favouriteclassified_classified__profile=profile, 
            is_deleted=False,
            is_active=True
        ).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 6
    result_page = paginator.paginate_queryset(classifieds, request)
    serializer = ClassifiedGetSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_classified(request):
    classified = request.query_params.get('classified')
    if not classified:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        classified = Classified.objects.get(slug=classified, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    
    if profile and profile != classified.profile:
        classified.view_count += 1
        classified.save()

    # if profile or classified.business_type == 'Company':
        # Creating Notification for Automotive 
        notification = Notification(
        type = 'Classified',
        profile = profile,
        classified_id=classified.id,
        text = f'{profile.user.first_name} has viewed your ad',
        )
        notification.save()
        notification.notifiers_list.add(classified.profile)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass

        if classified.view_count == 15:
            notification = Notification(
            type = 'Classified',
            profile = profile,
            classified_id=classified.id,
            text = f'Your ad is getting more views and impressions. promote your ad or add special discounts to get customers.',
            )
            notification.save()
            notification.notifiers_list.add(classified.profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
            
    if profile:
        serializer = ClassifiedGetSerializer(classified, context={'profile': profile})    

        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_200_OK)
    else:
        serializer = ClassifiedGetSerializer(classified)
        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def make_active_classified(request):
    id = request.data.get('id', None)
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        classified = Classified.objects.get(id=id)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if classified.is_active == True:
        classified.is_active = False
        classified.save()
        return Response({'success': True, 'response': {'message': 'Classified inactive successfully!'}},
                status=status.HTTP_200_OK)
    else:
        classified.is_active = True
        classified.save()
        return Response({'success': True, 'response': {'message': 'Classified active successfully!'}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def total_count_classifieds(request):
    currency = request.query_params.get('currency', None)
    if currency:
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
            return Response({"success": False, 'response':{'message': str(e)}},
                                    status=status.HTTP_404_NOT_FOUND)

    new_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', type='New').count()
    used_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', type='Used').count()
    first_count = ''
    second_count = ''
    third_count = ''
    fourth_count = ''
    fifth_count = ''
    first_value = ''
    second_value = ''
    third_value = ''
    fourth_value = ''
    fifth_value = ''
    sixth_value = ''
    if currency:
        if currency.code == 'AUD':
            first_value = 100
            second_value = 200
            third_value = 500
            fourth_value = 1000
            fifth_value = 1500
            sixth_value = 1501
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=100, price__lte=200).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=200, price__lte=500).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=1500).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1501).count()
        elif currency.code == 'CAD':
            first_value = 100
            second_value = 200
            third_value = 500
            fourth_value = 1000
            fifth_value = 1500
            sixth_value = 1501
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=100, price__lte=200).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=200, price__lte=500).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=1500).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1501).count()
        elif currency.code == 'KWD':
            first_value = 500
            second_value = 1000
            third_value = 2000
            fourth_value = 3000
            fifth_value = 5000
            sixth_value = 5001
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=2000).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=2000, price__lte=3000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=3000, price__lte=5000).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=5001).count()
        elif currency.code == 'AED':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 150001
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=5000, price__lte=10000).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=10000, price__lte=20000).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=20000, price__lte=30000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=30000, price__lte=50000).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=50001).count()
        elif currency.code == 'EUR':
            first_value = 100
            second_value = 200
            third_value = 500
            fourth_value = 1000
            fifth_value = 1500
            sixth_value = 1501
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=100, price__lte=200).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=200, price__lte=500).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=1500).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1501).count()
        elif currency.code == 'INR':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 150001
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=5000, price__lte=10000).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=10000, price__lte=20000).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=20000, price__lte=30000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=30000, price__lte=50000).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=50001).count()
        elif currency.code == 'PKR':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=5000, price__lte=10000).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=10000, price__lte=20000).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=20000, price__lte=30000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=30000, price__lte=50000).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=50001).count()
        elif currency.code == 'GBP':
            first_value = 500
            second_value = 1000
            third_value = 2000
            fourth_value = 3000
            fifth_value = 5000
            sixth_value = 5001
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__icontains=currency, price__gte=500, price__lte=1000).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__icontains=currency, price__gte=1000, price__lte=2000).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__icontains=currency, price__gte=2000, price__lte=3000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__icontains=currency, price__gte=3000, price__lte=5000).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__icontains=currency, price__gte=5001).count()
        elif currency.code == 'CNH':
            first_value = 500
            second_value = 1000
            third_value = 2000
            fourth_value = 3000
            fifth_value = 5000
            sixth_value = 5001
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=2000).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=2000, price__lte=3000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=3000, price__lte=5000).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=5001).count()
        elif currency.code == 'OMR':
            first_value = 500
            second_value = 1000
            third_value = 2000
            fourth_value = 3000
            fifth_value = 5000
            sixth_value = 5001

            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=2000).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=2000, price__lte=3000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=3000, price__lte=5000).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=5001).count()
        elif currency.code == 'UGX':
            first_value = 100
            second_value = 200
            third_value = 500
            fourth_value = 1000
            fifth_value = 1500
            sixth_value = 1501
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=100, price__lte=200).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=200, price__lte=500).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=1500).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1501).count()
        elif currency.code == 'ZAR':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 150001
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=5000, price__lte=10000).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=10000, price__lte=20000).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=20000, price__lte=30000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=30000, price__lte=50000).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=50001).count()
        elif currency.code == 'CHF':
            first_value = 100
            second_value = 200
            third_value = 500
            fourth_value = 1000
            fifth_value = 1500
            sixth_value = 1501
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=100, price__lte=200).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=200, price__lte=500).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=1500).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1501).count()
        elif currency.code == 'USD':
            first_value = 100
            second_value = 200
            third_value = 500
            fourth_value = 1000
            fifth_value = 1500
            sixth_value = 1501
            first_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=100, price__lte=200).count()
            second_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=200, price__lte=500).count()
            third_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=500, price__lte=1000).count()
            fourth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1000, price__lte=1500).count()
            fifth_count = Classified.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=1501).count()
    
    data1 = {
        'first_value' : first_value,
        'second_value' : second_value,
        'total_count' : first_count,
    }
    data2 = {
        'first_value' : second_value,
        'second_value' : third_value,
        'total_count' : second_count,
    }

    data3 = {
        'first_value' : third_value,
        'second_value' : fourth_value,
        'total_count' : third_count,
    }

    data4 = {
        'first_value' : fourth_value,
        'second_value' : fifth_value,
        'total_count' : fourth_count,
    }

    data5 = {
        'second_value' : sixth_value,
        'total_count' : fifth_count
    }

    context = [data1, data2, data3, data4, data5]

    return Response({"success": True, 'response': context
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def near_classified_ads(request):
    my_lat = request.query_params.get('lat')
    my_long = request.query_params.get('long')
    my_radius = request.query_params.get('radius')
    if my_lat or my_long:
        classifieds = Classified.objects.raw('SELECT *,  ( 6371 * acos( cos( radians('+my_lat+') ) * cos( radians( lat ) ) * cos( radians( long ) - radians('+my_long+') ) + sin( radians('+my_lat+') ) * sin( radians( lat ) ) ) ) AS distance FROM "Classified" WHERE (6371 * acos( cos( radians('+my_lat+') ) * cos( radians(lat) ) * cos( radians(long) - radians('+my_long+') ) + sin( radians('+my_lat+') ) * sin( radians(lat) ) ) ) <= 100')
    else:
        classifieds = Classified.objects.filter(verification_status='Verified').order_by('-created_at')
    serializer = ClassifiedGetSerializer(classifieds, many=True)

    return Response({"success": True, 'response': serializer.data
                                        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_business_classifieds(request):
    sorted_by = request.query_params.get('sorted_by', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
        status=status.HTTP_401_UNAUTHORIZED)
    if sorted_by == 'hightolow':
        classifieds = Classified.objects.filter(
                                            profile=profile,
                                            is_deleted=False, business_type='Company'
                                        ).order_by('-price')
    elif sorted_by == 'lowtohigh':
        classifieds = Classified.objects.filter(
                                    profile=profile,
                                    is_deleted=False, business_type='Company'
                                ).order_by('price')
    elif sorted_by == 'newtoold':
        classifieds = Classified.objects.filter(
                                    profile=profile,
                                    is_deleted=False, business_type='Company'
                                ).order_by('-created_at')
    elif sorted_by == 'oldtonew':
        classifieds = Classified.objects.filter(
                                    profile=profile,
                                    is_deleted=False, business_type='Company'
                                ).order_by('created_at')
    elif sorted_by == 'featured':
        classifieds = Classified.objects.filter(
                                    profile=profile,
                                    is_promoted = True,
                                    is_deleted=False, business_type='Company'
                                ).order_by('-created_at')
    elif sorted_by == 'active':
        classifieds = Classified.objects.filter(
                            profile=profile,
                            is_active = True,
                            is_deleted=False, business_type='Company'
                        ).order_by('-created_at')
    elif sorted_by == 'inactive':
        classifieds = Classified.objects.filter(
                            profile=profile,
                            is_active = False,
                            is_deleted=False, business_type='Company'
                        ).order_by('-created_at')
    else:
        classifieds = Classified.objects.filter(
            profile=profile,
            is_deleted=False, business_type='Company'
        ).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(classifieds, request)
    serializer = ClassifiedGetSerializer(result_page, many=True, context={'profile': profile})
    return paginator.get_paginated_response(serializer.data)
