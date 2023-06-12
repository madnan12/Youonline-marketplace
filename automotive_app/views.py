from decimal import Decimal
from locale import currency
from multiprocessing import context
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
from youonline_social_app.custom_api_settings import CustomPagination
import datetime
from django.conf import settings
from youonline_social_app.youonline_threads import SendEmailThread
from automotive_app.constants import is_valid_queryparam

# Automotive Module

# Get Automotive Category API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_categories(request):
    automotives = AutomotiveCategory.objects.filter(is_deleted=False)
    serializer = AutomotiveCategorySerializer(automotives, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


# Get Automotive Make API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_make_and_models(request):
    automotive_makes = AutomotiveMake.objects.all()
    serializer = GetAutomotiveMakeAndModelSerializer(automotive_makes, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


# Get Automotive Sub Category API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_sub_categories(request):
    category = request.query_params.get('category')
    if not category:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    sub_categories = AutomotiveSubCategory.objects.filter(category=category, is_deleted=False)
    serializer = AutomotiveSubCategorySerializer(sub_categories, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


# Get Automotive Sub Sub Category API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_sub_sub_categories(request):
    sub_category = request.query_params.get('sub_category')
    if not sub_category:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    sub_sub_categories = AutomotiveSubSubCategory.objects.filter(sub_category=sub_category, is_deleted=False)
    serializer = AutomotiveSubSubCategorySerializer(sub_sub_categories, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)


# Add Single Automotive Media API
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def add_single_automotive_media(request):
#     automotive = request.query_params.get('automotive')
#     post = request.query_params.get('post')
#     try:
#         profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
#     except Exception as e:
#         return Response({"success": False, 'response': {'message': str(e)}},
#                         status=status.HTTP_404_NOT_FOUND)
#     try:
#         post = Post.objects.get(id=post)
#     except:
#         return Response({"success": False, 'response': {'message': 'Post does not exist'}},
#                         status=status.HTTP_400_BAD_REQUEST)
#     try:
#         automotive = Automotive.objects.get(id=automotive)
#     except:
#         return Response({"success": False, 'response': {'message': 'Automotive does not exist'}},
#                         status=status.HTTP_400_BAD_REQUEST)

#     if request.method == 'POST':
#         serializer = AutomotiveMediaSerializer(data=request.data)
#         if serializer.is_valid():
#             media_object = serializer.save()
#             media_object.automotive_id = automotive.id
#             media_object.profile_id = profile.id
#             media_object.post_id = post.id
#             media_object.save()
#             return Response({'success': True, 'response': serializer.data},
#                             status=status.HTTP_201_CREATED)
#         else:
#             return Response({"success": False, 'response': serializer.errors},
#                             status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_automotive_media(request):
    automotive = request.data.get('automotive', None)
    automotive_image = request.data.getlist('automotive_image', None)
    automotive_video = request.data.get('automotive_video', None)

    if not automotive or (not automotive_image and not automotive_video):
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        automotive = Automotive.objects.get(id=automotive, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    if automotive_image:
        if automotive.automotivemedia_automotive.filter(is_deleted=False).exclude(automotive_image=''):
            total_media = automotive.automotivemedia_automotive.filter(is_deleted=False).exclude(automotive_image='').count()
            my_length = total_media + len(automotive_image)
            if my_length > 20:
                return Response({"success": False, 'response': {'message': 'Maximum 20 Image allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if len(automotive_image) > 20:
                return Response({"success": False, 'response': {'message': 'Maximum 20 Image allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
    if automotive_video:
        if automotive.automotivemedia_automotive.filter(is_deleted=False).exclude(automotive_video=''):
            total_media = automotive.automotivemedia_automotive.filter(is_deleted=False).exclude(automotive_video='').count()
            my_length = total_media + len(automotive_video)
            
            if my_length > 1:
                return Response({"success": False, 'response': {'message': 'Only One Video allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if len(automotive_video) > 1:
                return Response({"success": False, 'response': {'message': 'Only One Video allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)

    if automotive_image:
        for a in automotive_image:
            media = AutomotiveMedia.objects.create(automotive=automotive, automotive_image=a, profile=profile)

    if automotive_video:
        media = AutomotiveMedia.objects.create(automotive=automotive, automotive_video=automotive_video, profile=profile)

    serializer = GetAutomotiveSerializer(automotive)
    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)


# Delete Automotive Media API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_automotive_media(request):
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
        media = AutomotiveMedia.objects.get(id=id, is_deleted=False)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Automotive Media item does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid media ID!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    media.is_deleted = True
    media.save()
    return Response({'success': True, 'response': {'message': 'Media deleted successfully!'}},
                    status=status.HTTP_200_OK)


# Get All Automotive API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_automotives(request):
    sorted_by = request.query_params.get('sorted_by', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None

    if sorted_by == 'hightolow':
        automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('-price')

    elif sorted_by == 'lowtohigh':
        automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('price')

    elif sorted_by == 'newtoold':
        automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('created_at')
    
    elif sorted_by == 'featured':
        automotives = Automotive.objects.filter(is_deleted=False, is_promoted=True, is_active=True).order_by('-created_at')
    
    elif sorted_by == 'New':
        automotives = Automotive.objects.filter(is_deleted=False, car_type__icontains='New', is_active=True).order_by('-created_at')
    
    elif sorted_by == 'Used':
        automotives = Automotive.objects.filter(is_deleted=False, car_type__icontains='Used', is_active=True).order_by('-created_at')

    else:
        automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    if profile:
        serializer = GetAutomotiveSerializer(result_page, many=True, context={'profile':profile})
    else:
        serializer = GetAutomotiveSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)



# Get All Automotive API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotives_by_category(request):
    id = request.query_params.get('id', None)
    sorted_by = request.query_params.get('sorted_by', None)

    if not id:
        return Response({"success": False, 'response': "Invalid data!"},
                        status=status.HTTP_400_BAD_REQUEST)

    if sorted_by == 'hightolow':
        automotives = Automotive.objects.filter(category=id, is_deleted=False, is_active=True).order_by('-price')

    elif sorted_by == 'lowtohigh':
        automotives = Automotive.objects.filter(category=id, is_deleted=False, is_active=True).order_by('price')

    elif sorted_by == 'newtoold':
        automotives = Automotive.objects.filter(category=id, is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        automotives = Automotive.objects.filter(category=id, is_deleted=False, is_active=True).order_by('created_at')
    
    elif sorted_by == 'featured':
        automotives = Automotive.objects.filter(category=id, is_deleted=False, is_promoted=True, is_active=True).order_by('-created_at')
    
    elif sorted_by == 'New':
        automotives = Automotive.objects.filter(category=id, is_deleted=False, car_type__icontains='New', is_active=True).order_by('-created_at')
    
    elif sorted_by == 'Used':
        automotives = Automotive.objects.filter(category=id, is_deleted=False, car_type__icontains='Used', is_active=True).order_by('-created_at')

    else:
        automotives = Automotive.objects.filter(category=id, is_deleted=False, is_active=True).order_by('-created_at')


    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    if profile:
        serializer = GetAutomotiveSerializer(result_page, many=True, context={'profile':profile})
    else:
        serializer = GetAutomotiveSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Add Favourite Automotive API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favourite_automotive(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        automotive = Automotive.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        try:
            favourite = FavouriteAutomotive.objects.get(profile=profile, automotive=automotive)
            favourite.delete()
            return Response({'success': True, 'response': {'message': "Automotive removed from favourite List"}},
                            status=status.HTTP_200_OK)
        except :
            favourite = FavouriteAutomotive.objects.create(profile=profile, automotive=automotive)
            return Response({'success': True, 'response': {'message': "Automotive added to favourite list"}},
                            status=status.HTTP_201_CREATED)



# Search Automotive API
@api_view(['GET'])
@permission_classes([AllowAny])
def search_automotives(request):
    choice = request.query_params.get('choice')
    currency = request.query_params.get('currency')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    country = request.query_params.get('country')
    state = request.query_params.get('state')
    city = request.query_params.get('city')
    street_adress = request.query_params.get('street_adress')
    category = request.query_params.get('category')
    sub_category = request.query_params.get('sub_category')
    make = request.query_params.get('make')
    model = request.query_params.get('model')
    name = request.query_params.get('name')
    body_condition = request.query_params.get('body_condition')
    inside_out = request.query_params.get('inside_out')
    transmission_type = request.query_params.get('transmission_type')
    specs = request.query_params.get('specs')
    door = request.query_params.get('door')
    power = request.query_params.get('power')
    fuel_type = request.query_params.get('fuel_type')
    year = request.query_params.get('year')
    color = request.query_params.get('color')
    warranty = request.query_params.get('warranty')
    language = request.query_params.get('language')
    city_name = request.query_params.get('city_name')

    # Get Values for the filters
    if not choice:
        choice = 'all'
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    if category:
        try:
            category = AutomotiveCategory.objects.get(id=category).title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        category = ''
    if sub_category:
        try:
            sub_category = AutomotiveSubCategory.objects.get(id=sub_category).title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        sub_category = ''
    if make:
        try:
            make = AutomotiveMake.objects.get(id=make)
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if model:
        try:
            model = AutomotiveModel.objects.get(id=model)
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
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
    if city_name:
        try:
            city = City.objects.filter(name__icontains=city_name)[0]
        except:
            return Response({'success': False, 'response': {'message': 'No record found.'}},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        city = ''
    if language:
        try:
            language = Language.objects.get(id=language)
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if not body_condition:
        body_condition = ''
    if not color:
        color = ''
    if not door:
        door = ''
    if not power:
        power = ''
    if not year:
        year = ''
    if not transmission_type:
        transmission_type = ''
    if not fuel_type:
        fuel_type = ''
    else:
        warranty = False
    # Filter Based on Choices
    if choice == 'all':
        # Search Based on Country, City and State
        if country and city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and not city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country)
        elif country and city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and not city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    country__name__icontains=country)
        elif not country and city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and not city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    state__name__icontains=state)
        elif not country and city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    city__name__icontains=city)
        elif not country and not city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    state__name__icontains=state)
        elif not country and not city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    currency=currency)
        elif not country and city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    currency=currency,
                                                    city__name__icontains=city)
        else:
            automotives = Automotive.objects.filter(is_deleted=False)
        if language:
            automotives = automotives.filter(language=language)
        # Search Based on Category, Sub Category, Make and Model
        if category and sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif category and sub_category and not make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    make=make)
        elif category and not sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category)
        elif category and sub_category and make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    make=make)
        elif category and sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and not make and not model:
            automotives = automotives.filter(category__title__icontains=category)
        elif not category and sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif not category and sub_category and make and not model:
            automotives = automotives.filter(make=make,
                                                    sub_category__title__icontains=sub_category)
        elif not category and not sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    make=make)
        elif not category and sub_category and not make and not model:
            automotives = automotives.filter(sub_category__title__icontains=sub_category)
        elif not category and not sub_category and make and not model:
            automotives = automotives.filter(make=make)
        elif not category and not sub_category and not make and model:
            automotives = automotives.filter(model=model)
        elif not category and sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    sub_category__title__icontains=sub_category)
        # Other Search attributes.
        if min_price and max_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif max_price and not min_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__gte=min_price))
        else:
            automotives = automotives.filter(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type)
    # Filter Based on Logged in User Profile
    elif choice == 'my':
        if not profile:
            return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                            status=status.HTTP_400_BAD_REQUEST)
        # Search Based on Country, City and State
        if country and city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and not city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country)
        elif country and city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and not city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    country__name__icontains=country)
        elif not country and city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and not city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state)
        elif not country and city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    city__name__icontains=city)
        elif not country and not city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    state__name__icontains=state)
        elif not country and not city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency)
        elif not country and city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    profile=profile,
                                                    currency=currency,
                                                    city__name__icontains=city)
        else:
            automotives = Automotive.objects.filter(is_deleted=False, profile=profile,)
        # Search Based on Category, Sub Category, Make and Model
        if category and sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif category and sub_category and not make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    make=make)
        elif category and not sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category)
        elif category and sub_category and make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    make=make)
        elif category and sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and not make and not model:
            automotives = automotives.filter(category__title__icontains=category)
        elif not category and sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif not category and sub_category and make and not model:
            automotives = automotives.filter(make=make,
                                                    sub_category__title__icontains=sub_category)
        elif not category and not sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    make=make)
        elif not category and sub_category and not make and not model:
            automotives = automotives.filter(sub_category__title__icontains=sub_category)
        elif not category and not sub_category and make and not model:
            automotives = automotives.filter(make=make)
        elif not category and not sub_category and not make and model:
            automotives = automotives.filter(model=model)
        elif not category and sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    sub_category__title__icontains=sub_category)
        # Other Search attributes.
        if min_price and max_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif max_price and not min_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__gte=min_price))
        else:
            automotives = automotives.filter(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type)
    elif choice == 'favourite':
        # Search Based on Country, City and State
        if not profile:
            return Response({'success': False, 'response': {'message': 'Invalid data.'}},
                            status=status.HTTP_400_BAD_REQUEST)
        if country and city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and not city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country)
        elif country and city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif country and not city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    state__name__icontains=state)
        elif country and city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    currency=currency,
                                                    country__name__icontains=country,
                                                    city__name__icontains=city)
        elif country and not city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    country__name__icontains=country)
        elif not country and city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    state__name__icontains=state,
                                                    city__name__icontains=city)
        elif not country and not city and state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    currency=currency,
                                                    state__name__icontains=state)
        elif not country and city and not state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    city__name__icontains=city)
        elif not country and not city and state and not currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    state__name__icontains=state)
        elif not country and not city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    currency=currency)
        elif not country and city and not state and currency:
            automotives = Automotive.objects.filter(is_deleted=False,
                                                    favouriteautomotive_automotive__profile=profile,
                                                    currency=currency,
                                                    city__name__icontains=city)
        else:
            automotives = Automotive.objects.filter(is_deleted=False, favouriteautomotive_automotive__profile=profile,)
        # Search Based on Category, Sub Category, Make and Model
        if category and sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif category and sub_category and not make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    make=make)
        elif category and not sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category)
        elif category and sub_category and make and not model:
            automotives = automotives.filter(category__title__icontains=category,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    make=make)
        elif category and sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    category__title__icontains=category,
                                                    sub_category__title__icontains=sub_category)
        elif category and not sub_category and not make and not model:
            automotives = automotives.filter(category__title__icontains=category)
        elif not category and sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    make=make,
                                                    sub_category__title__icontains=sub_category)
        elif not category and sub_category and make and not model:
            automotives = automotives.filter(make=make,
                                                    sub_category__title__icontains=sub_category)
        elif not category and not sub_category and make and model:
            automotives = automotives.filter(model=model,
                                                    make=make)
        elif not category and sub_category and not make and not model:
            automotives = automotives.filter(sub_category__title__icontains=sub_category)
        elif not category and not sub_category and make and not model:
            automotives = automotives.filter(make=make)
        elif not category and not sub_category and not make and model:
            automotives = automotives.filter(model=model)
        elif not category and sub_category and not make and model:
            automotives = automotives.filter(model=model,
                                                    sub_category__title__icontains=sub_category)
        # Other Search attributes.
        if min_price and max_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__gte=min_price) &
                                                    Q(price__lte=max_price))
        elif max_price and not min_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__lte=max_price))
        elif min_price and not max_price:
            automotives = automotives.filter(Q(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type) &
                                                    Q(price__gte=min_price))
        else:
            automotives = automotives.filter(body_condition__icontains=body_condition,
                                                    color__icontains=color,
                                                    door__icontains=door,
                                                    power__icontains=power,
                                                    year__icontains=year,
                                                    transmission_type__icontains=transmission_type,
                                                    fuel_type__icontains=fuel_type)
    else:
        automotives = Automotive.objects.filter(is_deleted=False)
    # Filter Logged in User's Favourite Automotives
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    if profile:
        serializer = AutomotiveListingSerializer(result_page, many=True, context={'profile': profile})
    else:
        serializer = AutomotiveListingSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Search Automotive Optimized API
@api_view(['GET'])
@permission_classes([AllowAny])
def search_automotive_optimized(request):
    choice = request.GET.get('choice' , None)
    try:
        user_profile = Profile.objects.get(user=request.user, is_deleted=False, is_active=True)
    except:
        user_profile = None
    if not choice or choice == 'all':
        all_automotives = Automotive.objects.filter(is_deleted=False)
    elif choice == 'favourite':
        all_automotives = Automotive.objects.filter(
            favouriteautomotive_automotive__profile=user_profile,
            is_deleted=False
        )
    elif choice == 'my':
        all_automotives = Automotive.objects.filter(profile=user_profile, is_deleted=False)

    all_filters = {
        'currency' : request.GET.get('currency' , None), 'min_price' : request.GET.get('min_price' , None),
        'max_price' : request.GET.get('max_price' , None), 'country' : request.GET.get('country' , None),
        'state' : request.GET.get('state' , None), 'city' : request.GET.get('city' , None),
        'category' : request.GET.get('category' , None), 'sub_category' : request.GET.get('sub_category' , None),
        'make' : request.GET.get('make' , None), 'automotive_model' : request.GET.get('automotive_model' , None),
        'language' : request.GET.get('language' , None), 'body_condition' : request.GET.get('body_condition' , None),
        'color' : request.GET.get('color' , None), 'door' : request.GET.get('door' , None),
        'power' : request.GET.get('power' , None), 'year' : request.GET.get('year' , None),
        'car_type' : request.GET.get('car_type' , None), 'transmission_type' : request.GET.get('transmission_type' , None),
        'fuel_type' : request.GET.get('fuel_type' , None),
    }
    selected_filters = list(filter(lambda q : q , all_filters.values()))
    filter_funcs = {
        'currency' : lambda user_q , r_atm : 
                            r_atm.currency and 
                            str(r_atm.currency.id) == user_q,
        'min_price' : lambda user_q , r_atm:
                            r_atm.price and
                            float(user_q) <= r_atm.price,
        'max_price' : lambda user_q , r_atm:
                            r_atm.price and
                            float(user_q) >= r_atm.price,
        'country' : lambda user_q , r_atm : 
                            r_atm.country and
                            str(r_atm.country.id) == user_q,
        'state' : lambda user_q , r_atm : 
                            r_atm.state and 
                            str(r_atm.state.id) == user_q,
        'city' : lambda user_q , r_atm : 
                            r_atm.city and 
                            str(r_atm.city.id) == user_q,
        'category' : lambda user_q , r_atm : 
                            r_atm.category and 
                            str(r_atm.category.id) == user_q,
        'sub_category' : lambda user_q , r_atm : 
                            r_atm.sub_category and 
                            str(r_atm.sub_category.id) == user_q,
        'make' : lambda user_q , r_atm : 
                            r_atm.make and 
                            str(r_atm.make.id) == user_q,
        'automotive_model' : lambda user_q , r_atm : 
                            r_atm.automotive_model and 
                            str(r_atm.automotive_model.id) == user_q,
        'language' : lambda user_q , r_atm : 
                            r_atm.language and 
                            str(r_atm.language.id) == user_q,
        'body_condition' : lambda user_q , r_atm : 
                            r_atm.body_condition and 
                            r_atm.body_condition == user_q,
        'color' : lambda user_q , r_atm : 
                            r_atm.color and 
                            r_atm.color == user_q,
        'door' : lambda user_q , r_atm : 
                            r_atm.door and 
                            r_atm.door == user_q,
        'power' : lambda user_q , r_atm : 
                            r_atm.power and 
                            r_atm.power == user_q,
        'year' : lambda user_q , r_atm : 
                            r_atm.year and 
                            r_atm.year == user_q,
        'car_type' :lambda user_q , r_atm : 
                            r_atm.car_type and 
                            r_atm.car_type == user_q,
        'transmission_type' : lambda user_q , r_atm : 
                            r_atm.transmission_type and 
                            r_atm.transmission_type == user_q,
        'fuel_type' : lambda user_q , r_atm : 
                            r_atm.fuel_type and 
                            r_atm.fuel_type == user_q,
    }
    def get_filtered_cls(r_atm):
        return_value = False
        success_q = 0
        fail_q = 0
        for k, v in all_filters.items():
            if v:
                ft_data = filter_funcs[k](v , r_atm)
                if ft_data:
                    return_value = True
                    success_q += 1
                else :
                    return_value = False
                    fail_q += 1
        if return_value and success_q == len(selected_filters) and fail_q == 0 :
            return_value = True
        else :
            return_value = False
        return return_value

    if any(selected_filters):
        all_automotives = list(filter(get_filtered_cls, all_automotives))
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(all_automotives, request)
    if user_profile:
        serializer = AutomotiveListingSerializer(result_page, many=True, context={'profile': user_profile})
    else:
        serializer = AutomotiveListingSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Verify Automotive API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def verify_automotive(request):
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
        automotive_object = Automotive.objects.get(id=id, is_deleted=False)
        automotive_object.verification_status = verification_status
        automotive_object.save()
        return Response({'success': True, 'response': {'message: Automotive Verification Done'}},
                        status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Automotive does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)


# Promote Automotive API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def promote_automotive(request):
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
        automotive_object = Automotive.objects.get(id=id, is_deleted=False)
        automotive_object.is_promoted = is_promoted
        automotive_object.save()
        return Response({'success': True, 'response': {'message: Automotive Promoted Successfully'}},
                        status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Automotive does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)


# Get Promoted Automotive API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_promoted_automotives(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    automotives = Automotive.objects.filter(is_promoted=True, is_deleted=False
                    ).select_related(
                        'currency', 'country', 'state', 'city',
                        'category', 'sub_category', 'sub_sub_category'
                    ).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    if profile:
        serializer = AutomotiveListingSerializer(result_page, many=True, context={"profile": profile})
        return paginator.get_paginated_response(serializer.data)
    else:
        serializer = AutomotiveListingSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# Contact Automotive API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_automotive(request):
    if request.method == 'POST':
        serializer = AutomotiveContactSerializer(data=request.data)
        if serializer.is_valid():
            automotive_contact = serializer.save()
            # Getting Email ready
            context = {'name': request.user.username,
                        'email': automotive_contact.email,
                        'phone': automotive_contact.phone,
                        'message': automotive_contact.message,
                        'img_link': settings.DOMAIN_NAME, 'server_url':settings.FRONTEND_SERVER_NAME,
                    }
            html_template = render_to_string('email/u-automotive-contact-email.html',context=context)
            # Email sending thread
            subject = f'Automotive | {automotive_contact.automotive.name}'
            SendEmailThread(request, subject, html_template).start()

            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


# Report Automotive API
@api_view(['POST'])
@permission_classes([AllowAny])
def report_ads(request):
    id = request.data.get('id', None)
    module_name = request.data.get('module_name', None)
    report_type = request.data.get('report_type', None)

    if not id or not module_name or not report_type:
        return Response({"success": False, 'response': 'Invalid Data!'},
                status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    request.data._mutable = True
    request.data['profile'] = profile.id

    if module_name == 'Automotive':
        request.data['automotive'] = id
        serializer = AutomotiveReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    elif module_name == 'Classified':
        request.data['classified'] = id
        serializer = ClassifiedReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    elif module_name == 'Job':
        request.data['job'] = id
        serializer = ReportJobSerializer(data=request.data)
        if serializer.is_valid():
            report_job = serializer.save()
            # # Getting Email ready
            # html_template = render_to_string('email/u-property-report-email.html',
            #                             {'email': report_property.email, 'message': report_property.message,
            #                             'url_property': settings.FRONTEND_SERVER_NAME + '/' + str(report_property.property.slug),
            #                             'img_link': settings.DOMAIN_NAME})
            # # Email sending thread
            # subject = f'Property | {report_property.property.name}'
            # SendEmailThread(request, subject, html_template).start()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    elif module_name == 'Property':
        request.data['property'] = id
        serializer = PropertyReportSerializer(data=request.data)
        if serializer.is_valid():
            report_property = serializer.save()
            # # Getting Email ready
            # html_template = render_to_string('email/u-property-report-email.html',
            #                             {'email': report_property.email, 'message': report_property.message,
            #                             'url_property': settings.FRONTEND_SERVER_NAME + '/' + str(report_property.property.slug),
            #                             'img_link': settings.DOMAIN_NAME})
            # # Email sending thread
            # subject = f'Property | {report_property.property.name}'
            # SendEmailThread(request, subject, html_template).start()
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)




# Landing Page APIs
# Get Featured Automotive API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_automotives(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    automotives = Automotive.objects.filter(is_promoted=True, is_deleted=False
                    ).select_related(
                        'currency', 'country', 'state', 'city',
                        'category', 'sub_category', 'sub_sub_category'
                    ).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    serializer = GetAutomotiveSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Get Latest Automotive API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_automotives(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    automotives = Automotive.objects.filter(is_deleted=False
                    ).select_related(
                        'currency', 'country', 'state', 'city',
                        'category', 'sub_category', 'sub_sub_category'
                    ).order_by('-created_at')
    if profile:
        serializer = AutomotiveListingSerializer(automotives, many=True, context = {'profile': profile})
    else:
        serializer = AutomotiveListingSerializer(automotives, many=True)
    return Response({"success": False, 'response': serializer.data},
                status=status.HTTP_200_OK)


# Get Automotive Comparisions API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_comparisons(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    automotives = AutomotiveComparison.objects.all().order_by('-created_at')[:5]
    if profile:
        serializer = GetAutomotiveComparisonSerializer(automotives, many=True,  context = {'profile': profile})
    else:
        serializer = GetAutomotiveComparisonSerializer(automotives, many=True)
    return Response({"success": True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Get Used Car API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_used_cars(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    automotives = list(set(AutomotiveMedia.objects.filter(is_deleted=False, automotive__is_deleted=False, automotive__category__title='Cars',
                                automotive__car_type='Used').exclude(automotive_image='').order_by('-created_at')))[:15]
    if profile:
        serializer = GetUsedCarsSerializer(automotives, many=True, context = {'profile': profile} )
    else:
        serializer = GetUsedCarsSerializer(automotives, many=True)
    return Response({"success": True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Get Automotive Video API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_videos(request):
    automotives = list(set(AutomotiveMedia.objects.filter(is_deleted=False).exclude(automotive_video='').order_by('-created_at')))
    serializer = AutomotiveMediaSerializer(automotives, many=True)
    return Response({"success": True, 'response': serializer.data},
                status=status.HTTP_200_OK)


# Search Landing Automotive API
@api_view(['GET'])
@permission_classes([AllowAny])
def search_landing_automotive(request):
    search = request.query_params.get("city_name", False)
    # will get id's
    category = request.query_params.get("category", False)
    sub_category = request.query_params.get("sub_category", False)
    brand = request.query_params.get("make", False)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None

    try:
        results = None

        if search:
               automotives = Automotive.objects.filter(is_deleted=False).filter(
                                                        Q(name__icontains=search) |
                                                        Q(country__name__icontains=search) |
                                                        Q(state__name__icontains=search) |
                                                        Q(city__name__icontains=search) |
                                                        Q(description__icontains=search)).order_by('-created_at')
               results = automotives
        else:
                automotives = Automotive.objects.filter(is_deleted=False).order_by('-created_at')

        if category and sub_category and brand:
               results = automotives.filter(category=category,sub_category=sub_category,make=brand)

        elif category and sub_category and not brand:
               results = automotives.filter(category=category,sub_category=sub_category)

        elif category and not sub_category and brand:
               results = automotives.filter(category=category,make=brand)

        elif not category and sub_category and brand:
               results = automotives.filter(sub_category=sub_category,make=brand)

        elif category and not sub_category and not brand:
                results = automotives.filter(category=category)

        elif not category and sub_category and not brand:
               results = automotives.filter(sub_category=sub_category)

        elif not category and not sub_category and brand:
               results = automotives.filter(make=brand)

        if not results:
            return Response({'success': False, 'response': {'message': "No found"}},
                            status=status.HTTP_404_NOT_FOUND)
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(results, request)
        if profile:
            serializer = AutomotiveListingSerializer(result_page, many=True, context = {'profile': profile})
        else:
            serializer = AutomotiveListingSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)


#########################################################################################################

@api_view(['GET'])
@permission_classes([AllowAny])
def filter_automotive(request):
    # try:
    #     profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    # except:
    #     profile = None
    # my_dict = dict()

    # if "automotive_type" in request.query_params !=None and "automotive_type" in request.query_params !='':
    #    my_dict["car_type"] = request.query_params.get('automotive_type')

    # if "name" in request.query_params !=None and "name" in request.query_params !='':
    #    my_dict["name__icontains"] = request.query_params.get('name')

    # if "location" in request.query_params !=None and "location" in request.query_params !='':
    #     my_dict["street_adress__icontains"] = request.query_params.get('location')

    # if "brand" in request.query_params !=None and "brand" in request.query_params !='':
    #     brand = request.query_params.get('brand')
    #     try:
    #         brand = AutomotiveMake.objects.get(id=brand)
    #     except Exception as e:
    #         print(e)

    #     my_dict["make__title__icontains"] = brand

    # if "model" in request.query_params !=None and "model" in request.query_params !='':
    #     model = request.query_params.get('model')
    #     try:
    #         model = AutomotiveModel.objects.get(id=model)
    #     except Exception as e:
    #         print(e)

    #     my_dict["automotive_model__title__icontains"] = model

    # if "min_price" in request.query_params !=None and "min_price" in request.query_params !='':
    #     my_dict["price__gte"] = request.query_params.get('min_price')

    # if "max_price" in request.query_params !=None and "max_price" in request.query_params !='':
    #     my_dict["price__lte"] = request.query_params.get('max_price')
    
    # automotives = ''
    # if is_valid_queryparam(my_dict):
    #     if len(my_dict) < 1:
    #         automotives = Automotive.objects.filter(is_deleted=False)
    #     else:
    #         automotives = Automotive.objects.filter(**my_dict, is_deleted=False).distinct()
    
    # if profile:
    #     for a in automotives:
    #         if not a.automotivesearchhistory_autotomotive.filter(profile=profile):
    #             search_history = AutomotiveSearchHistory.objects.create(
    #                                             profile=profile,
    #                                             autotomotive=a,
    #             )

    # paginator = CustomPagination()
    # paginator.page_size = 9
    # result_page = paginator.paginate_queryset(automotives, request)
    # if profile:
    #     serializer = GetAutomotiveSerializer(result_page, many=True, context={'profile': profile})
    # else:
    #     serializer = GetAutomotiveSerializer(result_page, many=True)
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
            category = AutomotiveCategory.objects.get(id=category)
            category.view_count += 1
            category.save()
            category = category.title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND
                )

    if min_price and max_price:
        automotive = Automotive.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__gte=min_price) &
                                        Q(price__lte=max_price),
                                        is_deleted=False,
                                        is_active=True)
    elif min_price and not max_price:
        automotive = Automotive.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__gte=min_price),
                                        is_deleted=False,
                                        is_active=True)
    elif max_price and not min_price:
        automotive = Automotive.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location)&
                                        Q(price__lte=max_price),
                                        is_deleted=False,
                                        is_active=True)
    else:
        automotive = Automotive.objects.filter(Q(name__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(street_adress__icontains=location),
                                        is_deleted=False,
                                        is_active=True)
    if profile:
        for a in automotive:
            if not a.automotivesearchhistory_autotomotive.filter(profile=profile):
                search_history = AutomotiveSearchHistory.objects.create(
                                                profile=profile,
                                                automotive=a,
                )

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotive, request)
    if profile:
        serializer = GetAutomotiveSerializer(result_page, many=True, context={'profile': profile})
    else:
        serializer = GetAutomotiveSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_featured_brand(request):
    brand = AutomotiveMake.objects.filter(is_featured=True)
    serializer = AutomotiveMakeSerializer(brand, many=True)
    return Response({"success": True, 'response': serializer.data},
            status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_by_brand(request):
    brand = request.query_params.get('brand', None)
    if not brand:
        return Response({"success": False, 'response': {'message':'Invalid Data!'}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        brand = AutomotiveMake.objects.get(id=brand)
    except Exception as e:
        return Response({"success": False, 'response': {'message':str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    
    automotives = Automotive.objects.filter(make=brand, verification_status='Verified', is_deleted=False)
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    serializer = GetAutomotiveSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_automotives(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None 

    automotives = ''
    if profile:
        search_history = AutomotiveSearchHistory.objects.filter(profile=profile)
        
        automotives = []
        if search_history:
            for h in search_history:
                automotive_list = Automotive.objects.filter(
                    id=h.automotive.id,
                    is_deleted=False,
                    is_active=True).distinct()
                if automotive_list:
                    for c in automotive_list:
                        automotives.append(c)
        else:
            date_from = datetime.datetime.now() - datetime.timedelta(days=3)
            automotives = Automotive.objects.filter(created_at__gte=date_from, verification_status='Verified' ,is_deleted=False)
                                        
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    serializer = GetAutomotiveSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def filtering_automotive(request):
    sorted_by = request.query_params.get('sorted_by')
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    my_dict = dict()

    if "title" in request.query_params !=None and "title" in request.query_params !='':
        my_dict["name__icontains"] = request.query_params.get('title')

    if "min_year" in request.query_params !=None and "min_year" in request.query_params !='':
        if request.query_params.get('min_year'):
            my_dict["automotive_year__gte"] = request.query_params.get('min_year')

    if "max_year" in request.query_params !=None and "max_year" in request.query_params !='':
        if request.query_params.get('max_year'):
            my_dict["automotive_year__lte"] = request.query_params.get('max_year')
    
    if "transmission_type" in request.query_params !=None and "transmission_type" in request.query_params !='':
        my_dict["transmission_type__icontains"] = request.query_params.get('transmission_type')

    if "brand" in request.query_params !=None and "brand" in request.query_params !='':
        brand = request.query_params.get('brand')
        try:
            brand = AutomotiveMake.objects.get(id=brand)
        except Exception as e:
            print(e)

        my_dict["make__title__icontains"] = brand

    if "min_price" in request.query_params !=None and "min_price" in request.query_params !='':
        if request.query_params.get('min_price'):
            my_dict["price__gte"] = request.query_params.get('min_price')

    if "max_price" in request.query_params !=None and "max_price" in request.query_params !='':
        if request.query_params.get('max_price'):
            my_dict["price__lte"] = request.query_params.get('max_price')

    if "min_km" in request.query_params !=None and "min_km" in request.query_params !='':
        if request.query_params.get('min_km'):
            my_dict["kilometers__gte"] = request.query_params.get('min_km')

    if "max_km" in request.query_params !=None and "max_km" in request.query_params !='':
        if request.query_params.get('max_km'):
            my_dict["kilometers__lte"] = request.query_params.get('max_km')

    if "fuel_type" in request.query_params !=None and "fuel_type" in request.query_params !='':
        my_dict["fuel_type__icontains"] = request.query_params.get('fuel_type')
    
    if "currency" in request.query_params !=None and "currency" in request.query_params !='':
        currency = request.query_params.get('currency')
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
            print(e)

        my_dict["currency__name__icontains"] = currency

    if "category" in request.query_params !=None and "category" in request.query_params !='':
        category = request.query_params.get('category')
        try:
            category = AutomotiveCategory.objects.get(id=category)
        except Exception as e:
            print(e)

        my_dict["category__title__icontains"] = category
    

    if "model" in request.query_params !=None and "model" in request.query_params !='':
        model = request.query_params.get('model')
        try:
            model = AutomotiveModel.objects.get(id=model)
        except Exception as e:
            print(e)

        my_dict["automotive_model__title__icontains"] = model

    if "sub_category" in request.query_params !=None and "sub_category" in request.query_params !='':
        sub_category = request.query_params.get('sub_category')
        try:
            sub_category = AutomotiveSubCategory.objects.get(id=sub_category)
        except Exception as e:
            print(e)

        my_dict["sub_category__title__icontains"] = sub_category
    
    automotives = ''
    if is_valid_queryparam(my_dict):
        if len(my_dict) < 1:
            if sorted_by == 'Old':
                automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('created_at')
            else:
                automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')
        else:
            if sorted_by == 'Old':
                automotives = Automotive.objects.filter(**my_dict, is_deleted=False, is_active=True).order_by('created_at').distinct()
            else:
                automotives = Automotive.objects.filter(**my_dict, is_deleted=False, is_active=True).order_by('-created_at').distinct()
    
    if profile:
        for a in automotives:
            if not a.automotivesearchhistory_autotomotive.filter(profile=profile):
                search_history = AutomotiveSearchHistory.objects.create(
                                                profile=profile,
                                                autotomotive=a,
                )
    min_year = request.query_params.get('min_year')
    max_year = request.query_params.get('max_year')
    automotive_inspection = request.query_params.get('automotive_inspection')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    min_km = request.query_params.get('min_km')
    max_km = request.query_params.get('max_km')
    fuel_type = request.query_params.get('fuel_type')
    brand = request.query_params.get('brand')
    transmission_type = request.query_params.get('transmission_type')
    print(min_price)
    print(max_price)

    if not profile:
        profile = ''
    
    context = {
        'min_year': min_year,
        'max_year': max_year,
        'automotive_inspection': automotive_inspection,
        'brand': brand,
        'min_price': min_price,
        'max_price': max_price,
        'min_km': min_km,
        'max_km': max_km,
        'fuel_type':fuel_type, 
        'profile':profile,
        'transmission_type':transmission_type,
        'profile':profile,
    }
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    if profile:
        serializer = GetAutomotiveSerializer(result_page, many=True, context=context)
    else:
        serializer = GetAutomotiveSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)


# Create Automotive API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_automotive(request):
    category = request.data['category'] if 'category' in request.data else None
    sub_category = request.data['sub_category'] if 'sub_category' in request.data else None
    business_type = request.data['business_type'] if 'business_type' in request.data else None
    name = request.data['name'] if 'name' in request.data else None
    price = request.data['price'] if 'price' in request.data else None
    make = request.data['make'] if 'make' in request.data else None
    automotive_model = request.data['automotive_model'] if 'automotive_model' in request.data else None
    automotive_year = request.data['automotive_year'] if 'automotive_year' in request.data else None
    kilometers = request.data['kilometers'] if 'kilometers' in request.data else None
    fuel_type = request.data['fuel_type'] if 'fuel_type' in request.data else None
    transmission_type = request.data['transmission_type'] if 'transmission_type' in request.data else None
    car_type = request.data['car_type'] if 'car_type' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    street_adress = request.data['street_adress'] if 'street_adress' in request.data else None
    longitude = request.data['longitude'] if 'longitude' in request.data else None
    latitude = request.data['latitude'] if 'latitude' in request.data else None
    mobile = request.data['mobile'] if 'mobile' in request.data else None
    automotive_image = request.data['automotive_image'] if 'automotive_image' in request.data else None
    currency = request.data['currency'] if 'currency' in request.data else None
    dial_code = request.data['dial_code'] if 'dial_code' in request.data else None
    price = Decimal(price)
    kilometers = int(kilometers)

    if not category or not sub_category or not automotive_model or not business_type\
            or not name or not automotive_year or not kilometers  or not automotive_image or not dial_code\
            or not street_adress or not longitude or not latitude or not mobile or not transmission_type \
            or not fuel_type or not price or not description or not car_type or not currency:
        return Response({"success": False, 'response': 'Invalid Data'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if not make:
        make = None

    if request.method == 'POST':
        request.data._mutable = True
        request.data['profile'] = profile.id
        serializer = AutomotiveSerializer(data=request.data)
        if serializer.is_valid():
            automotive = serializer.save()
            automotive.business_type = business_type
            automotive.is_active = True
            if longitude or latitude:
                automotive.long = Decimal(longitude)
                automotive.lat = Decimal(latitude)
            automotive.save()
            # Creating Notification for Automotive 
            notification = Notification(
            type = 'Automotive',
            profile = profile,
            text = f'Your automotive {automotive.name} is created successfully.',
            )
            notification.save()
            notification.notifiers_list.add(profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
            # End Notification
            context = {
                'request': request, 
                'profile': automotive.profile
            }
            serializer = GetAutomotiveSerializer(automotive, context=context)
            url = f'{settings.FRONTEND_SERVER_NAME}/admin/verification/automotive/' + str(automotive.id)
            html_template = render_to_string('email/u-automotive-email.html',
                                             {'id': str(automotive.slug),
                                              'url': url,
                                              'img_link': settings.DOMAIN_NAME,
                                              })
            text_template = strip_tags(html_template)
            # Sending Email to admin
            subject = 'YouOnline | Automotive Verification'
            SendEmailThread(request, subject, html_template).start()
            # SEO Meta creation
            filename ='CSVFiles/XML/automotives.xml'
            open_file=open(filename,"r")
            read_file=open_file.read()
            open_file.close()
            new_line=read_file.split("\n")
            last_line="\n".join(new_line[:-1])
            open_file=open(filename,"w+")
            for i in range(len(last_line)):
                open_file.write(last_line[i])
            open_file.close()

            loc_tag=f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{automotive.slug}</loc>\n"
            lastmod_tag=f"<lastmod>{automotive.created_at}</lastmod>\n"
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
def get_model_by_brand(request):
    brand = request.query_params.get('brand', None)
    
    if not brand:
        return Response({"success": False, 'response': 'Invalid data!'},
                    status=status.HTTP_400_BAD_REQUEST)
    
    try:
        brand = AutomotiveMake.objects.get(id=brand)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    
    automotive_models = AutomotiveModel.objects.filter(brand=brand)
    serializer = GetAutomotiveModelSerializer(automotive_models, many=True)
    return Response({'success': True, 'response': serializer.data},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_makes_by_id(request):
    sub_category = request.query_params.get('sub_category', None)
    category = request.query_params.get('category', None)
    
    if not sub_category and not category:
        return Response({"success": False, 'response': 'Invalid data!'},
                    status=status.HTTP_400_BAD_REQUEST)

    if sub_category:
        automotive_makes = AutomotiveMake.objects.filter(sub_category=sub_category)

    if category:
        automotive_makes = AutomotiveMake.objects.filter(sub_category__category__id=sub_category)

    serializer = AutomotiveMakeSerializer(automotive_makes, many=True)
    return Response({'success': True, 'response': serializer.data},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_automotive_brand(request):
    automotive_makes = AutomotiveMake.objects.all()
    serializer = AutomotiveMakeSerializer(automotive_makes, many=True)
    return Response({'success': True, 'response': serializer.data},
                status=status.HTTP_200_OK)



# Get My Automotive API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_automotives(request):
    sorted_by = request.query_params.get('sorted_by', None)
    # business_type = request.query_params.get('business_type', None)

    # if not business_type:
    #     return Response({"success": False, 'response': {'message': 'invalid data!'}},
    #                     status=status.HTTP_400_BAD_REQUEST) 
                        
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    # if business_type == 'Company':

    #     if sorted_by == 'hightolow':
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-price')
    #     elif sorted_by == 'lowtohigh':
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('price')
    #     elif sorted_by == 'newtoold':
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    #     elif sorted_by == 'oldtonew':
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('created_at')
    #     elif sorted_by == 'featured':
    #         automotives = Automotive.objects.filter(
    #                         is_deleted=False, 
    #                         profile=profile,
    #                         is_promoted=True,
    #                         business_type='Company'
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    #     elif sorted_by == 'active':
    #         automotives = Automotive.objects.filter(
    #                         is_deleted=False, 
    #                         profile=profile,
    #                         ia_active=True,
    #                         business_type='Company'

    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    #     elif sorted_by == 'inactive':
    #         automotives = Automotive.objects.filter(
    #                         is_deleted=False, 
    #                         profile=profile,
    #                         ia_active=False,
    #                         business_type='Company'
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    #     else:
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    # elif business_type == 'Individual':
    #     if sorted_by == 'hightolow':
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Individual',
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-price')
    #     elif sorted_by == 'lowtohigh':
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Individual',
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('price')
    #     elif sorted_by == 'newtoold':
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Individual',
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    #     elif sorted_by == 'oldtonew':
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Individual',
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('created_at')
    #     elif sorted_by == 'featured':
    #         automotives = Automotive.objects.filter(
    #                         is_deleted=False, 
    #                         profile=profile,
    #                         is_promoted=True, business_type='Individual',
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    #     elif sorted_by == 'active':
    #         automotives = Automotive.objects.filter(
    #                         is_deleted=False, 
    #                         profile=profile,
    #                         ia_active=True,
    #                         business_type='Individual'
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    #     elif sorted_by == 'inactive':
    #         automotives = Automotive.objects.filter(
    #                         is_deleted=False, 
    #                         profile=profile,
    #                         ia_active=False, business_type='Individual',
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')
    #     else:
    #         automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Individual',
    #                         ).select_related(
    #                             'currency',
    #                             'category', 'sub_category'
    #                         ).order_by('-created_at')

    if sorted_by == 'hightolow':
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-price')
    elif sorted_by == 'lowtohigh':
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('price')
    elif sorted_by == 'newtoold':
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    elif sorted_by == 'oldtonew':
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('created_at')
    elif sorted_by == 'featured':
        automotives = Automotive.objects.filter(
                        is_deleted=False, 
                        profile=profile,
                        is_promoted=True
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    elif sorted_by == 'active':
        automotives = Automotive.objects.filter(
                        is_deleted=False, 
                        profile=profile,
                        ia_active=True,
                        
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    elif sorted_by == 'inactive':
        automotives = Automotive.objects.filter(
                        is_deleted=False, 
                        profile=profile,
                        ia_active=False
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    else:
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    serializer = GetAutomotiveSerializer(result_page, many=True, context={'profile': profile})
    return paginator.get_paginated_response(serializer.data)


# Update Automotive API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_automotive(request):
    id = request.data['id'] if 'id' in request.data else None
    remove_media = request.data['remove_media'] if 'remove_media' in request.data else None

    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        automotive = Automotive.objects.get(id=id, is_deleted=False)
        serializer = GetAutomotiveSerializer(automotive, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if remove_media:
                media_id = remove_media[1:-1].replace('"', '').split(',')
                for i in media_id:
                    try:
                        media = AutomotiveMedia.objects.get(id=i)
                        media.is_deleted = True
                        media.save()
                    except Exception as e:
                        print(e)
            return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'response': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Automotive does not exist!'}},
                        status=status.HTTP_404_NOT_FOUND)
                        

# Delete Automotive API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_automotive(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        automotive = Automotive.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    automotive.is_deleted = True
    automotive.save()
    return Response({'success': True, 'response': {'message': 'Automotive deleted successfully!'}},
                    status=status.HTTP_200_OK)


# Get Favourite Automotive API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favourite_automotives(request):
    sorted_by = request.query_params.get('sorted_by', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    favourite_automotives = list(FavouriteAutomotive.objects.filter(profile=profile, is_deleted=False).values_list('automotive__id', flat=True))

    if sorted_by == 'hightolow':
        automotives = Automotive.objects.filter(id__in=favourite_automotives
                        ).select_related(
                            'currency','category', 
                            'sub_category'
                        ).order_by('-price')
    elif sorted_by == 'lowtohigh':
        automotives = Automotive.objects.filter(id__in=favourite_automotives
                ).select_related(
                    'currency','category', 
                    'sub_category'
                ).order_by('price')
    elif sorted_by == 'newtoold':
        automotives = Automotive.objects.filter(id__in=favourite_automotives
                ).select_related(
                    'currency','category', 
                    'sub_category'
                ).order_by('-created_at')
    elif sorted_by == 'oldtonew':
        automotives = Automotive.objects.filter(id__in=favourite_automotives
                ).select_related(
                    'currency','category', 
                    'sub_category'
                ).order_by('created_at')
    elif sorted_by == 'featured':
        automotives = Automotive.objects.filter(id__in=favourite_automotives, is_promoted=True
                ).select_related(
                    'currency','category', 
                    'sub_category'
                ).order_by('-created_at')
    else:
        automotives = Automotive.objects.filter(id__in=favourite_automotives
                ).select_related(
                    'currency','category', 
                    'sub_category'
                ).order_by('-created_at')


    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    serializer = GetAutomotiveSerializer(result_page, many=True, context={"profile": profile})
    return paginator.get_paginated_response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def make_active_automotive(request):
    id = request.data.get('id', None)
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        automotive = Automotive.objects.get(id=id)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if automotive.is_active == True:
        automotive.is_active = False
        automotive.save()
        return Response({'success': True, 'response': {'message': 'Automotive inactive successfully!'}},
                status=status.HTTP_200_OK)
    else:
        automotive.is_active = True
        automotive.save()
        return Response({'success': True, 'response': {'message': 'Automotive active successfully!'}},
                status=status.HTTP_200_OK)


# Get Single Automotive API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_automotive(request):
    automotive = request.query_params.get('automotive')
    if not automotive:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    try:
        automotive = Automotive.objects.get(slug=automotive, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if profile and profile != automotive.profile:
        automotive.view_count += 1
        automotive.save()


        # if automotive.business_type == 'Company':
        # Creating Notification for Automotive 
        notification = Notification(
        type = 'Automotive',
        profile = profile,
        automotive_id=automotive.id,
        text = f'{profile.user.first_name} has viewed your ad',
        )
        notification.save()
        notification.notifiers_list.add(automotive.profile)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass

        if automotive.view_count == 15:
            notification = Notification(
            type = 'Automotive',
            profile = profile,
            automotive_id=automotive.id,
            text = 'Your ad is getting more views and impressions. promote your ad or add special discounts to get customers.',
            )
            notification.save()
            notification.notifiers_list.add(automotive.profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
        
            # End Notification
    serializer = GetAutomotiveSerializer(automotive, context={'profile': profile})
    return Response({'success': False, 'response': serializer.data},
                    status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_deal_automotive(request):
    automotives = Automotive.objects.filter(is_deal=True, is_active=True, is_deleted=False, verification_status='Verified')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    serializer = GetAutomotiveSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def total_count_automotives(request):
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
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'CAD':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'KWD':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'AED':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'EUR':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'INR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'PKR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 500001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'GBP':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'CNH':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'OMR':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001

            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'UGX':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'ZAR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'CHF':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
        elif currency.code == 'USD':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=first_value, price__lte=second_value).count()
            second_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=second_value, price__lte=third_value).count()
            third_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=third_value, price__lte=fourth_value).count()
            fourth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=fourth_value, price__lte=fifth_value).count()
            fifth_count = Automotive.objects.filter(is_deleted=False, verification_status='Verified', currency__name__icontains=currency, price__gte=sixth_value).count()
    
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
def recently_view_ads(request):
    
    recently = ModuleViewHistory.objects.all().order_by('-created_at')[:2]
    serializer = ModuleViewHistorySerializer(recently,many=True)
    return Response({"success": True, 'response': serializer.data
    }, status=status.HTTP_200_OK)

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def 

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_deals(request):

    automotives = Automotive.objects.filter(is_deal=True, verification_status='Verified').order_by('-created_at')[:4]
    automotives = GetAutomotiveSerializer(automotives, many=True).data

    classifieds = Classified.objects.filter(is_deal=True, verification_status='Verified').order_by('-created_at')[:4]
    classifieds = ClassifiedGetSerializer(classifieds, many=True).data

    properties = Property.objects.filter(is_deal=True, verification_status='Verified').order_by('-created_at')[:4]
    properties = PropertyGetSerializer(properties, many=True).data


    result = {
        'automotives':automotives,        
        'classifieds':classifieds,
        'properties':properties        
    }
    return Response({"success": True, 'response': result
                                        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def near_automotive_ads(request):
    my_lat = request.query_params.get('lat')
    my_long = request.query_params.get('long')
    my_radius = request.query_params.get('radius')
    if my_lat or my_long:
        automotives = Automotive.objects.raw('SELECT *,  ( 6371 * acos( cos( radians('+my_lat+') ) * cos( radians( lat ) ) * cos( radians( long ) - radians('+my_long+') ) + sin( radians('+my_lat+') ) * sin( radians( lat ) ) ) ) AS distance FROM "Automotive" WHERE (6371 * acos( cos( radians('+my_lat+') ) * cos( radians(lat) ) * cos( radians(long) - radians('+my_long+') ) + sin( radians('+my_lat+') ) * sin( radians(lat) ) ) ) <= 100')

    else:
        automotives = Automotive.objects.filter(verification_status='Verified').order_by('-created_at')
    serializer = GetAutomotiveSerializer(automotives, many=True)

    return Response({"success": True, 'response': serializer.data
                                        }, status=status.HTTP_200_OK)


# Get My Automotive API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_business_automotives(request):
    sorted_by = request.query_params.get('sorted_by', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if sorted_by == 'hightolow':
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-price')
    elif sorted_by == 'lowtohigh':
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('price')
    elif sorted_by == 'newtoold':
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    elif sorted_by == 'oldtonew':
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('created_at')
    elif sorted_by == 'featured':
        automotives = Automotive.objects.filter(
                        is_deleted=False, 
                        profile=profile,
                        is_promoted=True, business_type='Company'
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    elif sorted_by == 'active':
        automotives = Automotive.objects.filter(
                        is_deleted=False, 
                        profile=profile,
                        ia_active=True, business_type='Company'

                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    elif sorted_by == 'inactive':
        automotives = Automotive.objects.filter(
                        is_deleted=False, 
                        profile=profile,
                        ia_active=False, business_type='Company'
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')
    else:
        automotives = Automotive.objects.filter(is_deleted=False, profile=profile, business_type='Company'
                        ).select_related(
                            'currency',
                            'category', 'sub_category'
                        ).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    serializer = GetAutomotiveSerializer(result_page, many=True, context={'profile': profile})
    return paginator.get_paginated_response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def view_contact_notification(request):
    module_name = request.data.get('module_name', None)
    id = request.data.get('id', None)
    
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if not module_name or not id:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    
    if module_name == 'Job':
        try:
            job = Job.objects.get(id=id, is_deleted=False, is_active=True)
            # Creating Notification for Automotive 
            if profile != job.profile: 
                notification = Notification(
                type = 'Job',
                profile = profile,
                job_id = job.id,
                text = f'{profile.user.first_name} has viewed your number on ad {job.title}.',
                )
            
                notification.save()
                notification.notifiers_list.add(job.profile)
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
            return Response({"success": True, 'response': {'message': 'Notification Created Successfuly!'}},
                        status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)

    elif module_name == 'Classified':
        try:
            classified = Classified.objects.get(id=id, is_deleted=False, is_active=True)
            # Creating Notification for Automotive
            if profile != classified.profile:
                notification = Notification(
                type = 'Classified',
                profile = profile,
                classified_id = classified.id,
                text = f'{profile.user.first_name} has viewed your number on ad {classified.name}.',
                )

                notification.save()
                notification.notifiers_list.add(classified.profile)
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
            return Response({"success": True, 'response': {'message': 'Notification Created Successfuly!'}},
                        status=status.HTTP_201_CREATED)
            # End Notification
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)    
    elif module_name == 'Property':
        try:
            property_object = Property.objects.get(id=id, is_deleted=False, is_active=True)
            # Creating Notification for Automotive 
            if profile != property_object.profile:
                notification = Notification(
                type = 'Property',
                profile = profile,
                property_id = property_object.id,
                text = f'{profile.user.first_name} has viewed your number on ad {property_object.name}.',
                )
                notification.save()
                notification.notifiers_list.add(property_object.profile)
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
            return Response({"success": True, 'response': {'message': 'Notification Created Successfuly!'}},
                        status=status.HTTP_201_CREATED)
            # End Notification
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    elif module_name == 'Automotive':
        try:
            automotive = Automotive.objects.get(id=id, is_deleted=False, is_active=True)
            # Creating Notification for Automotive
            if profile != automotive.profile:
                notification = Notification(
                type = 'Automotive',
                profile = profile,
                automotive_id = automotive.id,
                text = f'{profile.user.first_name} has viewed your number on ad {automotive.name}.',
                )
                notification.save()
                notification.notifiers_list.add(automotive.profile)
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
            return Response({"success": True, 'response': {'message': 'Notification Created Successfuly!'}},
                        status=status.HTTP_201_CREATED)
            # End Notification
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"success": False, 'response': {'message': 'Something Wrong!'}},
                        status=status.HTTP_400_BAD_REQUEST)

