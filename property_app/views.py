from decimal import Decimal
from multiprocessing import context
from xml.dom.minidom import Element
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from youonline_social_app.models import *
from  . models import *
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
from youonline_social_app.custom_api_settings import CustomPagination
import datetime
import xml.etree.ElementTree as ET
from django.conf import settings
from youonline_social_app.youonline_threads import SendEmailThread
from automotive_app.constants import is_valid_queryparam


@api_view(['GET'])
@permission_classes([AllowAny])
def get_property_categories(request):
    categories = Category.objects.filter(is_deleted=False)
    serializer = CategorySerializer(categories, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_property_sub_categories(request):
    category = request.query_params.get('category')
    if not category:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    sub_categories = SubCategory.objects.filter(category=category, is_deleted=False)
    serializer = SubCategorySerializer(sub_categories, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_property_sub_sub_categories(request):
    sub_category = request.query_params.get('sub_category')
    if not sub_category:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    sub_sub_categories = SubSubCategory.objects.filter(sub_category=sub_category, is_deleted=False)
    serializer = SubSubCategorySerializer(sub_sub_categories, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def verify_property(request):
    id = request.data['id'] if 'id' in request.data else None
    verification_status = request.data['verification_status'] if 'verification_status' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        property_object = Property.objects.get(id=id, is_deleted=False)
        property_object.verification_status = verification_status
        property_object.save()
        return Response({'success': True, 'response': 'message: Property Verification Done'},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'response': {'message': 'Property does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def promote_property(request):
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
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        property_object = Property.objects.get(id=id, is_deleted=False)
        property_object.is_promoted = is_promoted
        property_object.save()
        return Response({'success': True, 'response': 'message: Property Promoted Successfully'},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'response': {'message': 'Property does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property_media(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        media = PropertyMedia.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': 'Property Media item does not exist!'}},
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
def get_popular_properties(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    properties = Property.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 9
    result_page = paginator.paginate_queryset(properties, request)
    if profile:
        serializer = PropertyListingSerializer(result_page, many=True, context={'profile': profile})
        return paginator.get_paginated_response(serializer.data)
    else:
        serializer = PropertyListingSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_promoted_properties(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    properties = Property.objects.filter(is_promoted=True, is_deleted=False).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(properties, request)
    if profile:
        serializer = PropertyListingSerializer(result_page, many=True, context={"profile": profile})
        return paginator.get_paginated_response(serializer.data)
    else:
        serializer = PropertyListingSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_properties(request):
    choice = request.query_params.get('choice')
    category = request.query_params.get('category')
    sub_category = request.query_params.get('sub_category')
    sub_sub_category = request.query_params.get('sub_sub_category')
    country = request.query_params.get('country')
    state = request.query_params.get('state')
    city = request.query_params.get('city')
    currency = request.query_params.get('currency')
    language = request.query_params.get('language')
    city_name = request.query_params.get('city_name')
    street_adress = request.query_params.get('street_adress')
    min_area = request.query_params.get('min_area')
    max_area = request.query_params.get('max_area')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    beds = request.query_params.get('beds')
    baths = request.query_params.get('baths')
    # Get Values for the filters
    if not choice:
        choice = 'all'
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    if category:
        try:
            category = Category.objects.get(id=category).title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if language:
        try:
            language = Language.objects.get(id=language).name
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if sub_category:
        try:
            sub_category = SubCategory.objects.get(id=sub_category).title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if sub_sub_category:
        try:
            sub_sub_category = SubSubCategory.objects.get(id=sub_sub_category).title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if country:
        try:
            country = Country.objects.get(id=country).name
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if state:
        try:
            state = State.objects.get(id=state).name
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if city:
        try:
            city = City.objects.get(id=city).name
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        city = ''
    if city_name:
        try:
            city = City.objects.filter(name__icontains=city_name)[0]
        except:
            return Response({'success': False, 'response': {'message': 'No record found.'}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        city = ''
    if currency:
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if not street_adress:
        street_adress = ""
    if not beds:
        beds = ''    
    if not baths:
        baths = ''
    # Filter Based on Choices
    if choice == 'all':
        # Search Based on Country, City and State
        if country and city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and not city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country)
        elif country and city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and not city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    country__name__icontains=country)
        elif not country and city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and not city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    state__name__icontains=state)
        elif not country and city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    city__name__icontains=city)
        elif not country and not city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    state__name__icontains=state)
        elif not country and not city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    currency=currency)
        elif not country and city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    city__name__icontains=city)
        else:
            properties = Property.objects.filter(is_deleted=False)
        if language:
            properties = properties.filter(language__name__icontains=language)
        # Search Based on Category, SubCategory and SubSubCategory
        if category and sub_category and sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and sub_category and not sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and not sub_category and not sub_sub_category:
            properties = properties.filter(category__title__icontains=category)
        # Combinations Based on min_price
        if min_price and max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area) &
                                                    Q(area__gte=min_area))
        elif min_price and not max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price))
        elif min_price and max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__gte=min_area))
        elif min_price and not max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__lte=max_area))
        elif min_price and max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__gte=min_area))
        elif min_price and max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area))
        elif min_price and not max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__gte=min_area) &
                                                    Q(area__lte=max_area))
        # Combinations Based on max_price
        elif not min_price and max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price))
        elif not min_price and max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__gte=min_area))
        elif not min_price and max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area))
        elif not min_price and max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(price__gte=min_area) &
                                                    Q(area__lte=max_area))
        elif not min_price and not max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__gte=min_area))
        elif not min_price and not max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__gte=min_area) &
                                                    Q(area__lte=max_area))
        elif not min_price and not max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__lte=max_area))
        # Other search attributes.
        else:
            properties = properties.filter(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths)
    # Filter Logged in User's Properties
    elif choice == 'my':
        if not profile:
            return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                            status=status.HTTP_400_BAD_REQUEST)
        # Search Based on Country, City and State
        if country and city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and not city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country)
        elif country and city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and not city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country)
        elif not country and city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and not city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state)
        elif not country and city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    city__name__icontains=city)
        elif not country and not city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    state__name__icontains=state)
        elif not country and not city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency)
        elif not country and city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    city__name__icontains=city)
        else:
            properties = Property.objects.filter(is_deleted=False, profile=profile,)
        # Search Based on Category, SubCategory and SubSubCategory
        if category and sub_category and sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and sub_category and not sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and not sub_category and not sub_sub_category:
            properties = properties.filter(category__title__icontains=category)
        # Combinations Based on min_price
        if min_price and max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area) &
                                                    Q(area__gte=min_area))
        elif min_price and not max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price))
        if min_price and max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__gte=min_area))
        elif min_price and not max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__lte=max_area))
        elif min_price and max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__gte=min_area))
        elif min_price and max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area))
        elif min_price and not max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__gte=min_area) &
                                                    Q(area__lte=max_area))
        # Combinations Based on max_price
        elif not min_price and max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price))
        elif not min_price and max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__gte=min_area))
        elif not min_price and max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area))
        elif not min_price and max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(price__gte=min_area) &
                                                    Q(area__lte=max_area))
        elif not min_price and not max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__gte=min_area))
        elif not min_price and not max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__gte=min_area) &
                                                    Q(area__lte=max_area))
        elif not min_price and not max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__lte=max_area))
        # Other search attributes.
        else:
            properties = properties.filter(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths)
    # Filter Logged in User's Properties
    elif choice == 'favourite':
        if not profile:
            return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                            status=status.HTTP_400_BAD_REQUEST)
        # Search Based on Country, City and State
        if country and city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and not city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country)
        elif country and city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and not city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    country__name__icontains=country)
        elif not country and city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and not city and state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state)
        elif not country and city and not state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    city__name__icontains=city)
        elif not country and not city and state and not currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    state__name__icontains=state)
        elif not country and not city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    currency=currency)
        elif not country and city and not state and currency:
            properties = Property.objects.filter(is_deleted=False,
                                                    favouriteproperty_property__profile=profile,
                                                    currency=currency,
                                                    city__name__icontains=city)
        else:
            properties = Property.objects.filter(is_deleted=False, favouriteproperty_property__profile=profile)
        # Search Based on Category, SubCategory and SubSubCategory
        if category and sub_category and sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and sub_category and not sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and sub_sub_category:
            properties = properties.filter(category__title__icontains=category,
                                                    sub_sub_category__title__icontains=sub_sub_category,)
        elif category and not sub_category and not sub_sub_category:
            properties = properties.filter(category__title__icontains=category)
        # Combinations Based on min_price
        if min_price and max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area) &
                                                    Q(area__gte=min_area))
        elif min_price and not max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price))
        if min_price and max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__gte=min_area))
        elif min_price and not max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__lte=max_area))
        elif min_price and max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__gte=min_area))
        elif min_price and max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area))
        elif min_price and not max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__gte=min_price) &
                                                    Q(area__gte=min_area) &
                                                    Q(area__lte=max_area))
        # Combinations Based on max_price
        elif not min_price and max_price and not min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price))
        elif not min_price and max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__gte=min_area))
        elif not min_price and max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(area__lte=max_area))
        elif not min_price and max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(price__lte=max_price) &
                                                    Q(price__gte=min_area) &
                                                    Q(area__lte=max_area))
        elif not min_price and not max_price and min_area and not max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__gte=min_area))
        elif not min_price and not max_price and min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__gte=min_area) &
                                                    Q(area__lte=max_area))
        elif not min_price and not max_price and not min_area and max_area:
            properties = properties.filter(Q(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths) &
                                                    Q(area__lte=max_area))
        # Other search attributes.
        else:
            properties = properties.filter(street_adress__icontains=street_adress,
                                                    bedrooms__icontains=beds,
                                                    baths__icontains=baths)
    else:
        properties = Property.objects.filter(is_deleted=False)
    paginator = CustomPagination()
    paginator.page_size = 9
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyListingSerializer(result_page, many=True, context={'profile': profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_property(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id
    serializer = PropertyContactSerializer(data=request.data)
    if serializer.is_valid():
        property_contact = serializer.save()
        # Getting Email ready
        html_template = render_to_string('email/u-property-contact-email.html',
                                     {'email': property_contact.email, 'message': property_contact.message, 'img_link': settings.DOMAIN_NAME})
        # Email sending thread
        subject = f'Property | {property_contact.property.name}'
        SendEmailThread(request, subject, html_template).start()
        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"success": False, 'response': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_property(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id
    serializer = PropertyReportSerializer(data=request.data)
    if serializer.is_valid():
        report_property = serializer.save()
        # Getting Email ready
        html_template = render_to_string('email/u-property-report-email.html',
                                     {'email': report_property.email, 'message': report_property.message,
                                      'url_property': settings.FRONTEND_SERVER_NAME + '/' + str(report_property.property.slug),
                                      'img_link': settings.DOMAIN_NAME})
        # Email sending thread
        subject = f'Property | {report_property.property.name}'
        SendEmailThread(request, subject, html_template).start()
        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"success": False, 'response': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


# Landing Page APIs

@api_view(['GET'])
@permission_classes([AllowAny])
def get_new_properties(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    properties = Property.objects.filter(is_deleted=False).order_by('-created_at')
    if profile:
        serializer = PropertyListingSerializer(properties, many=True,  context = {'profile': profile})
    else:
        serializer = PropertyListingSerializer(properties, many=True)
    return Response({"success": True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_recommended_properties(request):
#     try:
#         profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
#     except:
#         profile = None
#     properties = Property.objects.filter(is_deleted=False, is_promoted=True).order_by('-created_at')
#     if profile:
#         serializer = PropertyListingSerializer(properties, many=True,  context = {'profile': profile})
#     else:
#         serializer = PropertyListingSerializer(properties, many=True)

#     return Response({"success": True, 'response': serializer.data},
#                     status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_landing_property(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    search = request.query_params.get("city_name", False)

    # will get id's
    category = request.query_params.get("category", False)  # category id (For Sale, For Rent)
    sub_category = request.query_params.get("sub_category", False) # property type
    sub_sub_category = request.query_params.get("sub_sub_category", False) # property sub type

    # int num of bed's/baths
    bedrooms = request.query_params.get("beds", False)
    baths = request.query_params.get("baths", False)

    if not category:
        return Response({'success': False, 'response': {'message': 'category is missing'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        results = None
        if search:
            properties = Property.objects.filter(category=category).filter(
                                                                            Q(name__icontains=search) |
                                                                            Q(country__name__icontains=search) |
                                                                            Q(state__name__icontains=search) |
                                                                            Q(city__name__icontains=search)
            ).order_by('-created_at')
            results = properties
        else:
            properties = Property.objects.filter(is_deleted=False).order_by('-created_at')




        try:

            if sub_category and sub_sub_category:
                   results = properties.filter(sub_sub_category=sub_sub_category,sub_category=sub_category)

            elif not sub_category and sub_sub_category:
                   results = properties.filter(sub_sub_category=sub_sub_category)

            elif sub_category and not sub_sub_category:
                   results = properties.filter(sub_category=sub_category)

            if not results:
                return Response({'success': False, 'response': {'message': "No found"}},
                                status=status.HTTP_404_NOT_FOUND)
            else:
                results = results.filter(Q(baths=baths) | Q(bedrooms=bedrooms))

            paginator = CustomPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(results, request)
            if profile:
                serializer = PropertyListingSerializer(result_page, many=True,  context = {'profile': profile})
            else:
                serializer = PropertyListingSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_400_BAD_REQUEST)



############################################## NEW APIS ############################################

@api_view(['GET'])
@permission_classes([AllowAny])
def get_for_sale_properties(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    properties = Property.objects.filter(is_deleted=False, category__title__icontains='Sale').order_by('-created_at')
    if profile:
        serializer = PropertyGetSerializer(properties, many=True,  context = {'profile': profile})
    else:
        serializer = PropertyGetSerializer(properties, many=True)
    return Response({"success": True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_for_rent_property(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    properties = Property.objects.filter(is_deleted=False, category__title__icontains='Rent').order_by('-created_at')
    if profile:
        serializer = PropertyGetSerializer(properties, many=True,  context = {'profile': profile})
    else:
        serializer = PropertyGetSerializer(properties, many=True)
    return Response({"success": True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_property_by_category(request):
    category = request.query_params.get("id", False) 
    sorted_by = request.query_params.get("sorted_by", False) 
    if not category:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    
    try:
        category = Category.objects.get(id=category, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                                status=status.HTTP_404_NOT_FOUND)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None

    if sorted_by == 'hightolow':
        properties = Property.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-price')

    elif sorted_by == 'lowtohigh':
        properties = Property.objects.filter(category=category, is_deleted=False, is_active=True).order_by('price')

    elif sorted_by == 'newtoold':
        properties = Property.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        properties = Property.objects.filter(category=category, is_deleted=False, is_active=True).order_by('created_at')

    elif sorted_by == 'featured':
        properties = Property.objects.filter(category=category, is_deleted=False, is_promoted=True, is_active=True).order_by('-created_at')

    elif sorted_by == 'Rent':
        properties = Property.objects.filter(category=category, is_deleted=False, property_type__icontains='Rent', is_active=True).order_by('-created_at')

    elif sorted_by == 'Sale':
        properties = Property.objects.filter(category=category, is_deleted=False, property_type__icontains='Sale', is_active=True).order_by('-created_at')
    else:
        properties = Property.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(properties, request)
    if profile:
        serializer = PropertyGetSerializer(result_page, many=True, context={'profile':profile})
    else:
        serializer = PropertyGetSerializer(result_page, many=True)    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def filter_property(request):
    # try:
    #     profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    # except:
    #     profile = None
    # my_dict = dict()

    # if "property_type" in request.query_params !=None and "property_type" in request.query_params !='':
    #     property_type = request.query_params.get('property_type')
    #     print(property_type)
    #     try:
    #         property_type = Category.objects.get(id=property_type, is_deleted=False)
    #         my_dict["category__title__icontains"] = property_type
    #     except Exception as e:
    #         property_type = ''

    # if "location" in request.query_params !=None and "location" in request.query_params !='':
    #     my_dict["street_adress__icontains"] = request.query_params.get('location')

    # if "min_price" in request.query_params !=None and "min_price" in request.query_params !='':
    #     my_dict["price__gte"] = request.query_params.get('min_price')

    # if "max_price" in request.query_params !=None and "max_price" in request.query_params !='':
    #     my_dict["price__lte"] = request.query_params.get('max_price')

    
    # if "min_area" in request.query_params !=None and "min_area" in request.query_params !='':
    #     my_dict["area__gte"] = request.query_params.get('min_area')

    # if "max_area" in request.query_params !=None and "max_area" in request.query_params !='':
    #     my_dict["area__lte"] = request.query_params.get('max_area')
    
    # properties = ''

    # if is_valid_queryparam(my_dict):
    #     if len(my_dict) < 1:
    #         properties = Property.objects.filter(is_deleted=False)
    #     else:
    #         properties = Property.objects.filter(**my_dict, is_deleted=False).distinct()

    # if profile:
    #     for p in properties:
    #         if not p.propertysearchhistory_property.filter(profile=profile):
    #             search_history = PropertySearchHistory.objects.create(
    #                                             profile=profile,
    #                                             property=p,
    #             )
    # paginator = CustomPagination()
    # paginator.page_size = 9
    # result_page = paginator.paginate_queryset(properties, request)
    # if profile:
    #     serializer = PropertyListingSerializer(result_page, many=True, context={'profile': profile})
    # else:
    #     serializer = PropertyListingSerializer(result_page, many=True)
    # return paginator.get_paginated_response(serializer.data)

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
            category = Category.objects.get(id=category)
            category.view_count += 1
            category.save()
            category = category.title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND
                )

    if min_price and max_price:
        properties = Property.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__gte=min_price) &
                                        Q(price__lte=max_price),
                                        is_deleted=False,
                                        is_active=True)
    elif min_price and not max_price:
        properties = Property.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__gte=min_price),
                                        is_deleted=False,
                                        is_active=True)
    elif max_price and not min_price:
        properties = Property.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__lte=max_price),
                                        is_deleted=False,
                                        is_active=True)
    else:
        properties = Property.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location),
                                        is_deleted=False,
                                        is_active=True)
    if profile:
        for p in properties:
            if not p.propertysearchhistory_property.filter(profile=profile):
                search_history = PropertySearchHistory.objects.create(
                                                profile=profile,
                                                property=p,
                )

    paginator = CustomPagination()
    paginator.page_size = 9
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_properties(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None 
    properties = ''
    if profile:
        search_history = PropertySearchHistory.objects.filter(profile=profile)
        
        properties = []
        if search_history:
            for h in search_history:
                property_list = Property.objects.filter(
                    id=h.property.id,
                    is_active=True,
                    is_deleted=False)
                if property_list:
                    for c in property_list:
                        properties.append(c)
        else:
            date_from = datetime.datetime.now() - datetime.timedelta(days=3)
            properties = Property.objects.filter(created_at__gte=date_from, verification_status='Verified' ,is_deleted=False)
                                        
    paginator = CustomPagination()
    paginator.page_size = 9
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_property(request):
    business_type = request.data['business_type'] if 'business_type' in request.data else None

    name = request.data['name'] if 'name' in request.data else None
    price = request.data['price'] if 'price' in request.data else None
    furnished = request.data['furnished'] if 'furnished' in request.data else None
    category = request.data['category'] if 'category' in request.data else None
    sub_category = request.data['sub_category'] if 'sub_category' in request.data else None
    bedrooms = request.data['bedrooms'] if 'bedrooms' in request.data else None
    baths = request.data['baths'] if 'baths' in request.data else None
    area_unit = request.data['area_unit'] if 'area_unit' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    street_adress = request.data['street_adress'] if 'street_adress' in request.data else None
    longitude = request.data['longitude'] if 'longitude' in request.data else None
    latitude = request.data['latitude'] if 'latitude' in request.data else None
    property_image = request.data['property_image'] if 'property_image' in request.data else None
    mobile = request.data['mobile'] if 'mobile' in request.data else None
    property_type = request.data['property_type'] if 'property_type' in request.data else None
    currency = request.data['currency'] if 'currency' in request.data else None
    dial_code = request.data['dial_code'] if 'dial_code' in request.data else None
    price = Decimal(price)

    if not name or not price or not sub_category or not category  or not property_image  or not currency\
    or not furnished or not bedrooms or not baths or not area_unit  or not mobile  or not property_type  or not dial_code\
     or not description or not street_adress or not street_adress or not longitude or not latitude or not business_type:
        return Response({"success": False, 'response': 'Invalid Data.'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    request.data._mutable = True
    request.data['profile'] = profile.id
    serializer = PostPropertySerializer(data=request.data)
    if serializer.is_valid():
        property_object = serializer.save()
        property_object.business_type = business_type
        property_object.is_active = True
        if longitude or latitude:
            property_object.long = Decimal(longitude)
            property_object.lat = Decimal(latitude)
        property_object.save()
        # Creating Notification for Property
        notification = Notification(
        type = 'Property',
        profile = profile,
        text = f'You Property {property_object.name} is created successfully.',
        )
        notification.save()
        notification.notifiers_list.add(profile)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass
        # End Notification
        property_object = property_object.id
        property_object = Property.objects.get(id=property_object)
        serializer = PropertyGetSerializer(property_object, context={"request": request, "profile": property_object.profile})
        url = f'{settings.FRONTEND_SERVER_NAME}/admin/verification/property/' + str(property_object.id)
        html_template = render_to_string('email/u-property-email.html',
                                         {'id': str(property_object.slug),
                                          'url': url,
                                          'img_link': settings.DOMAIN_NAME,
                                          })
        text_template = strip_tags(html_template)
        # Sending Email to admin
        subject = 'YouOnline | Property Verification'
        SendEmailThread(request, subject, html_template).start()
        # SEO Meta creation
        filename ='CSVFiles/XML/propertys.xml'
        open_file=open(filename,"r")
        read_file=open_file.read()
        open_file.close()
        new_line=read_file.split("\n")
        last_line="\n".join(new_line[:-1])
        open_file=open(filename,"w+")
        for i in range(len(last_line)):
            open_file.write(last_line[i])
        open_file.close()

        loc_tag=f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{property_object.slug}</loc>\n"
        lastmod_tag=f"<lastmod>{property_object.created_at}</lastmod>\n"
        priorty_tag=f"<priority>0.8</priority>\n</url>\n</urlset>"
        with open(filename, "a") as fileupdate:
            fileupdate.write(loc_tag)
            fileupdate.write(lastmod_tag)
            fileupdate.write(priorty_tag)
        # SEO Meta Close
        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"success": False, 'response': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def filtering_property(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    my_dict = dict()

    if "title" in request.query_params !=None and "title" in request.query_params !='':
        my_dict["name__icontains"] = request.query_params.get('title')
        
    if "min_price" in request.query_params !=None and "min_price" in request.query_params !='':
        if request.query_params.get('min_price'):
            my_dict["price__gte"] = request.query_params.get('min_price')

    if "max_price" in request.query_params !=None and "max_price" in request.query_params !='':
        if request.query_params.get('max_price'):
            my_dict["price__lte"] = request.query_params.get('max_price')

    if "area_unit" in request.query_params !=None and "area_unit" in request.query_params !='':
        if request.query_params.get('area_unit') != 'All':
            my_dict["area_unit__icontains"] = request.query_params.get('area_unit')

    if "min_area" in request.query_params !=None and "min_area" in request.query_params !='':
        if request.query_params.get('min_area'):
            my_dict["area__gte"] = request.query_params.get('min_area')

    if "max_area" in request.query_params !=None and "max_area" in request.query_params !='':
        if request.query_params.get('max_area'):
            my_dict["area__lte"] = request.query_params.get('max_area')

    if "category" in request.query_params !=None and "category" in request.query_params !='':
        # category = request.query_params.get('category')
        # try:
        #     category = Category.objects.get(id=category)
        # except Exception as e:
        #     print(e)

        my_dict["category__title__icontains"] = request.query_params.get('category')

    if "sub_category" in request.query_params !=None and "sub_category" in request.query_params !='':
        sub_category = request.query_params.get('sub_category')
        try:
            sub_category = SubCategory.objects.get(id=sub_category)
        except Exception as e:
            print(e)

        my_dict["sub_category__title__icontains"] = sub_category

    if "currency" in request.query_params !=None and "currency" in request.query_params !='':
        currency = request.query_params.get('currency')
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
            print(e)

        my_dict["currency__name__icontains"] = currency
    
    if "furnished" in request.query_params !=None and "furnished" in request.query_params !='':
        my_dict["furnished__icontains"] = request.query_params.get('furnished')

    if "baths" in request.query_params !=None and "baths" in request.query_params !='':
        my_dict["baths__icontains"] = request.query_params.get('baths')

    if "bedrooms" in request.query_params !=None and "bedrooms" in request.query_params !='':
        my_dict["bedrooms__icontains"] = request.query_params.get('bedrooms')

    properties = ''
    if is_valid_queryparam(my_dict):
        if len(my_dict) < 1:
            properties = Property.objects.filter(is_deleted=False, verification_status='Verified')
        else:
            properties = Property.objects.filter(**my_dict, is_deleted=False, is_active=True).distinct()

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favourite_property(request):
    id = request.data['id'] if 'id' in request.data else None

    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        try:
            favourite = FavouriteProperty.objects.get(profile=profile, property_id=id)
            favourite.delete()
            return Response({'success': True, 'response': {'message': "Property removed from favourite List"}},
                            status=status.HTTP_200_OK)
        except:
            favourite = FavouriteProperty.objects.create(profile=profile, property_id=id)
            return Response({'success': True, 'response': {'message': "Property added to favourite list"}},
                        status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favourite_properties(request):
    sorted_by = request.query_params.get('sorted_by', None)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    favourite_properties = list(FavouriteProperty.objects.filter(profile=profile).values_list('property__id', flat=True))
    

    if sorted_by == 'hightolow':
        properties = Property.objects.filter(id__in=favourite_properties, is_deleted=False, is_active=True).order_by('-price')
    elif sorted_by == 'lowtohigh':
        properties = Property.objects.filter(id__in=favourite_properties, is_deleted=False, is_active=True).order_by('price')
    elif sorted_by == 'newtoold':
        properties = Property.objects.filter(id__in=favourite_properties, is_deleted=False, is_active=True).order_by('-created_at')
    elif sorted_by == 'oldtonew':
        properties = Property.objects.filter(id__in=favourite_properties, is_deleted=False, is_active=True).order_by('created_at')
    elif sorted_by == 'featured':
        properties = Property.objects.filter(id__in=favourite_properties, is_promoted=True, is_deleted=False, is_active=True).order_by('-created_at')
    else:
        properties = Property.objects.filter(id__in=favourite_properties, is_deleted=False, is_active=True).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyGetSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_properties(request):

    properties = Property.objects.filter(is_promoted=True, is_deleted=False)
    paginator = CustomPagination()
    paginator.page_size = 6
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyGetSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_properties(request):
    sorted_by = request.query_params.get('sorted_by', None)
    # business_type = request.query_params.get('business_type', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
                        
    # if not business_type:
    #     return Response({"success": False, 'response': {'message': 'invalid data!'}},
    #                     status=status.HTTP_400_BAD_REQUEST)

    # if business_type == 'Company':
    #     if sorted_by == 'hightolow':
    #         properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('-price')
    #     elif sorted_by == 'lowtohigh':
    #         properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('price')
    #     elif sorted_by == 'newtoold':
    #         properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('-created_at')
    #     elif sorted_by == 'oldtonew':
    #         properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('created_at')
    #     elif sorted_by == 'featured':
    #         properties = Property.objects.filter(profile=profile, is_promoted=True, is_deleted=False, business_type='Company').order_by('-created_at')
    #     elif sorted_by == 'active':
    #         properties = Property.objects.filter(profile=profile, is_active=True, is_deleted=False, business_type='Company').order_by('-created_at')
    #     elif sorted_by == 'inactive':
    #         properties = Property.objects.filter(profile=profile, is_active=False, is_deleted=False, business_type='Company').order_by('-created_at')
    #     else:
    #         properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('-created_at')
            
    # elif business_type == 'Individual':

        # if sorted_by == 'hightolow':
        #     properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('-price')
        # elif sorted_by == 'lowtohigh':
        #     properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('price')
        # elif sorted_by == 'newtoold':
        #     properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('-created_at')
        # elif sorted_by == 'oldtonew':
        #     properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('created_at')
        # elif sorted_by == 'featured':
        #     properties = Property.objects.filter(profile=profile, is_promoted=True, is_deleted=False, business_type='Individual').order_by('-created_at')
        # elif sorted_by == 'active':
        #     properties = Property.objects.filter(profile=profile, is_active=True, is_deleted=False, business_type='Individual').order_by('-created_at')
        # elif sorted_by == 'inactive':
        #     properties = Property.objects.filter(profile=profile, is_active=False, is_deleted=False, business_type='Individual').order_by('-created_at')
        # else:
        #     properties = Property.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('-created_at')
        
    if sorted_by == 'hightolow':
        properties = Property.objects.filter(profile=profile, is_deleted=False).order_by('-price')
    elif sorted_by == 'lowtohigh':
        properties = Property.objects.filter(profile=profile, is_deleted=False).order_by('price')
    elif sorted_by == 'newtoold':
        properties = Property.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')
    elif sorted_by == 'oldtonew':
        properties = Property.objects.filter(profile=profile, is_deleted=False).order_by('created_at')
    elif sorted_by == 'featured':
        properties = Property.objects.filter(profile=profile, is_promoted=True, is_deleted=False).order_by('-created_at')
    elif sorted_by == 'active':
        properties = Property.objects.filter(profile=profile, is_active=True, is_deleted=False).order_by('-created_at')
    elif sorted_by == 'inactive':
        properties = Property.objects.filter(profile=profile, is_active=False, is_deleted=False).order_by('-created_at')
    else:
        properties = Property.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyGetSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        property_object = Property.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    property_object.is_deleted = True
    property_object.save()
    return Response({'success': True, 'response': {'message': 'Property deleted successfully!'}},
                    status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def make_active_property(request):
    id = request.data.get('id', None)
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        property_object = Property.objects.get(id=id)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if property_object.is_active == True:
        property_object.is_active = False
        property_object.save()
        return Response({'success': True, 'response': {'message': 'Property inactive successfully!'}},
                status=status.HTTP_200_OK)
    else:
        property_object.is_active = True
        property_object.save()
        return Response({'success': True, 'response': {'message': 'Property active successfully!'}},
                status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_property(request):
    id = request.data['id'] if 'id' in request.data else None
    feature = request.data['feature'] if 'feature' in request.data else None
    remove_media = request.data['remove_media'] if 'remove_media' in request.data else None

    if not id:
        return Response({'success': False, 'response': {'message': 'Please give an ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        property_object = Property.objects.get(id=id, is_deleted=False)
        # add_features = property_object.feature.all()
        # add_features.delete()
        # items = json.loads(feature)
        # for i in range(len(items)):
        #     property_feature = PropertyFeatures.objects.create(
        #         name=items[i]
        #     )
        #     property_object.feature.add(property_feature)
        #     property_object.save()
        try:
            profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
        request.data._mutable = True
        request.data['profile'] = profile.id
        serializer = PropertyGetSerializer(property_object, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if remove_media:
                media_id = remove_media[1:-1].replace('"', '').split(',')
                for i in media_id:
                    try:
                        media = PropertyMedia.objects.get(id=i)
                        media.is_deleted = True
                        media.save()
                    except Exception as e:
                        print(e)
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'response': {'message': 'Property does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_single_property_media(request):
    property_id = request.data.get('property', None)
    property_img = request.data.get('property_image', None)
    if not property_id:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        property_object = Property.objects.get(id=property_id)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    
    #media.save()
    if property_img:
        for p in property_img:
            media = PropertyMedia.objects.create(property_image=p, property=property_object)

            

    # request.data._mutable = True
    # request.data['profile'] = profile.id
    # if request.method == 'POST':
    serializer = PropertyMediaSerializer(media, many=True)
        # if serializer.is_valid():
        #     media_object = serializer.save()
        #     media_object.property = property_object
        #     media_object.profile__id = profile.id
        #     media_object.save()
    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        # else:
        #     return Response({"success": False, 'response': serializer.errors},
        #                     status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_property(request):
    property = request.query_params.get('property')
    if not property:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    try:
        property = Property.objects.get(slug=property, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Property does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)


    if profile and profile != property.profile:
        property.view_count += 1
        property.save()

    # if profile or property.business_type == 'Company':
        # Creating Notification for Property 
        notification = Notification(
        type = 'Property',
        profile = profile,
        property_id=property.id,
        text = f'{profile.user.first_name} has viewed your ad',
        )
        notification.save()
        notification.notifiers_list.add(property.profile)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass
        if property.view_count == 15:
            notification = Notification(
            type = 'Property',
            profile = profile,
            property_id=property.id,
            text = 'Your ad is getting more views and impressions. promote your ad or add special discounts to get customers.',
            )
            notification.save()
            notification.notifiers_list.add(property.profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
    if profile:
        serializer = PropertyGetSerializer(property, context={'profile': profile})
        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_200_OK)
    else:
        serializer = PropertyGetSerializer(property)
        return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_properties(request):
    sorted_by = request.query_params.get('sorted_by', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None
        
    # property_type = request.query_params.get('property_type', None)
    # if property_type == 'Rent':
    #     properties = Property.objects.filter(is_deleted=False, is_active=True, property_type='Rent').order_by('-created_at')

    # elif property_type == 'Sale':
    #     properties = Property.objects.filter(is_deleted=False, is_active=True, property_type='Sale').order_by('-created_at')
    
    # elif property_type == 'Commercial':
    #     properties = Property.objects.filter(is_deleted=False, is_active=True, category__title='Commercial').order_by('-created_at')

    # elif property_type == 'Residential':
    #     properties = Property.objects.filter(is_deleted=False, is_active=True, category__title='Residential').order_by('-created_at')

    # else:
    #     properties = Property.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    if sorted_by == 'hightolow':
        properties = Property.objects.filter(is_deleted=False, is_active=True).order_by('-price')

    elif sorted_by == 'lowtohigh':
        properties = Property.objects.filter(is_deleted=False, is_active=True).order_by('price')

    elif sorted_by == 'newtoold':
        properties = Property.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        properties = Property.objects.filter(is_deleted=False, is_active=True).order_by('created_at')

    elif sorted_by == 'featured':
        properties = Property.objects.filter(is_deleted=False, is_promoted=True, is_active=True).order_by('-created_at')

    elif sorted_by == 'Rent':
        properties = Property.objects.filter(is_deleted=False, property_type__icontains='Rent', is_active=True).order_by('-created_at')

    elif sorted_by == 'Sale':
        properties = Property.objects.filter(is_deleted=False, property_type__icontains='Sale', is_active=True).order_by('-created_at')
    else:
        properties = Property.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')



    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(properties, request)
    if profile:
        serializer = PropertyGetSerializer(result_page, many=True, context={'profile':profile})
    else:
        serializer = PropertyGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_deal_properties(request):
    properties = Property.objects.filter(is_deal=True, is_active=True, is_deleted=False, verification_status='Verified')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def total_count_properties(request):
    currency = request.query_params.get('currency', None)
    if currency:
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
            return Response({"success": False, 'response':{'message': str(e)}},
                                    status=status.HTTP_404_NOT_FOUND)

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
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'CAD':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'KWD':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'AED':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'EUR':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'INR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'PKR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 500001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'GBP':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'CNH':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'OMR':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001

            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'UGX':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'ZAR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'CHF':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'USD':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Property.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
    
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_property_media(request):
    property_object = request.data.get('property', None)
    property_image = request.data.getlist('property_image', None)
    property_video = request.data.get('property_video', None)

    if not property_object or (not property_image and not property_video):
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        property_object = Property.objects.get(id=property_object, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    if property_image:
        if property_object.propertymedia_set.filter(is_deleted=False).exclude(property_image=''):
            total_media = property_object.propertymedia_set.filter(is_deleted=False).exclude(property_image='').count()
            my_length = total_media + len(property_image)
            if my_length > 20:
                return Response({"success": False, 'response': {'message': 'Maximum 20 Image allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if len(property_image) > 20:
                return Response({"success": False, 'response': {'message': 'Maximum 20 Image allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
    if property_video:
        if property_object.propertymedia_set.filter(is_deleted=False).exclude(property_video=''):
            total_media = property_object.propertymedia_set.filter(is_deleted=False).exclude(property_video='').count()
            my_length = total_media + len(property_video)
            
            if my_length > 1:
                return Response({"success": False, 'response': {'message': 'Only One Video allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if len(property_video) > 1:
                    return Response({"success": False, 'response': {'message': 'Only One Video allowed!'}},
                                    status=status.HTTP_400_BAD_REQUEST)

    if property_image:
        for a in property_image:
            media = PropertyMedia.objects.create(property=property_object, property_image=a, profile=profile)

    if property_video:
        media = PropertyMedia.objects.create(property=property_object, property_video=property_video, profile=profile)

    serializer = PropertyGetSerializer(property_object)
    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def near_property_ads(request):
    my_lat = request.query_params.get('lat')
    my_long = request.query_params.get('long')
    my_radius = request.query_params.get('radius')
    if my_lat or my_long:
        property_objects = Property.objects.raw('SELECT *,  ( 6371 * acos( cos( radians('+my_lat+') ) * cos( radians( lat ) ) * cos( radians( long ) - radians('+my_long+') ) + sin( radians('+my_lat+') ) * sin( radians( lat ) ) ) ) AS distance FROM "Property" WHERE (6371 * acos( cos( radians('+my_lat+') ) * cos( radians(lat) ) * cos( radians(long) - radians('+my_long+') ) + sin( radians('+my_lat+') ) * sin( radians(lat) ) ) ) <= 100')
    else:
        property_objects = Property.objects.filter(verification_status='Verified').order_by('-created_at')
    
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(property_objects, request)
    serializer = PropertyGetSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_business_properties(request):
    sorted_by = request.query_params.get('sorted_by', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    if sorted_by == 'hightolow':
        properties = Property.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('-price')
    elif sorted_by == 'lowtohigh':
        properties = Property.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('price')
    elif sorted_by == 'newtoold':
        properties = Property.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('-created_at')
    elif sorted_by == 'oldtonew':
        properties = Property.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('created_at')
    elif sorted_by == 'featured':
        properties = Property.objects.filter(profile=profile, is_promoted=True, is_deleted=False, business_type="Company").order_by('-created_at')
    elif sorted_by == 'active':
        properties = Property.objects.filter(profile=profile, is_active=True, is_deleted=False, business_type="Company").order_by('-created_at')
    elif sorted_by == 'inactive':
        properties = Property.objects.filter(profile=profile, is_active=False, is_deleted=False, business_type="Company").order_by('-created_at')
    else:
        properties = Property.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertyGetSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)