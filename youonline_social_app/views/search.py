
from unicodedata import category
import jwt
from django.contrib.auth import authenticate, logout
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from ..custom_api_settings import CustomPagination
from ..constants import *
from ..decorators import *
from ..models import *
from blog_app.models import *
from django.db.models import Q
from ..serializers.users_serializers import *
from ..serializers.post_serializers import *
from automotive_app.serializers import *
from classified_app.serializers import *
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from itertools import chain
from operator import attrgetter
from automotive_app.serializers import *
from classified_app.serializers import *
from property_app.serializers import *
from blog_app.serializers import *
from job_app.serializers import *
from community_app.serializers import *
from datetime import date
from django.db.models import Max

# Search APIs
@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    title = request.query_params.get('title')
    profile = request.query_params.get('profile')
    if not title or not profile:
        return Response(
            {
                'success': False, 
                'response': {
                    'message': 'Invalid Data.',
                    'error_message' : 'Please provide Title & Profile'
                    }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
        except ObjectDoesNotExist:
            return Response(
                {
                    'success': False, 
                    'response': {
                        'message': 'Profile does not exist.',
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'success': False, 
                    'response': {
                        'message': 'Invalid Profile ID.'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        private_profiles = list(UserPrivacySettings.objects.filter(search_profile_privacy='OnlyMe').values_list('profile__id', flat=True))
        friends_profiles = list(UserPrivacySettings.objects.filter(search_profile_privacy='Friends').values_list('profile__id', flat=True))
        block_profiles = list(BlockProfile.objects.filter(profile=profile).values_list('blocked_user__id', flat=True))
        try:
            friends_list = list(FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True))
        except Exception as e:
            friends_list = []
        for i in friends_profiles:
            for j in friends_list:
                if i == j:
                    friends_profiles.remove(i)
        print(title)
        people = Profile.objects.filter(
                                        # Q(user__username__icontains=title, user__is_active=True) |
                                        Q(user__first_name__icontains=title, user__is_active=True) 
                                        # Q(user__middle_name__icontains=title, user__is_active=True) |
                                        # Q(user__last_name__icontains=title, user__is_active=True) |
                                        # Q(user__name__icontains=title, user__is_active=True) |
                                        # Q(user__email__icontains=title, user__is_active=True)
                                    ).exclude(id__in=private_profiles).exclude(id__in=friends_profiles).exclude(id__in=block_profiles)
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(people, request)
        serializer = GetUserProfileSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def search_all(request):
#     title = request.query_params.get('title')
#     profile = request.query_params.get('profile')
#     if not title or not profile:
#         return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
#                         status=status.HTTP_400_BAD_REQUEST)
#     else:
#         try:
#             profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
#         except ObjectDoesNotExist:
#             return Response({'success': False, 'response': {'message': 'Profile does not exist.'}},
#                     status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'success': False, 'response': {'message': 'Invalid Profile ID.'}},
#                     status=status.HTTP_400_BAD_REQUEST)
#         private_profiles = list(UserPrivacySettings.objects.filter(search_profile_privacy='OnlyMe').values_list('profile__id', flat=True))
#         friends_profiles = list(UserPrivacySettings.objects.filter(search_profile_privacy='Friends').values_list('profile__id', flat=True))
#         try:
#             friends_list = list(FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True))
#         except Exception as e:
#             friends_list = []
#         for i in friends_profiles:
#             for j in friends_list:
#                 if i == j:
#                     friends_profiles.remove(i)
#         people = Profile.objects.filter(Q(user__username__icontains=title, user__is_active=True) |
#                                         Q(user__first_name__icontains=title, user__is_active=True) |
#                                         Q(user__middle_name__icontains=title, user__is_active=True) |
#                                         Q(user__last_name__icontains=title, user__is_active=True) |
#                                         Q(user__name__icontains=title, user__is_active=True) |
#                                         Q(user__email__icontains=title, user__is_active=True)).exclude(id__in=private_profiles).exclude(id__in=friends_profiles)[0:4]
#         people = SearchUserProfileSerializer(people, many=True, context={'profile': profile}).data
#         pages = Page.objects.filter(name__icontains=title, is_deleted=False, is_hidden=False, privacy='Public')[0:4]
#         pages = GetPageSerializer(pages, many=True, context={'profile': profile}).data
#         groups = Group.objects.filter(name__icontains=title, is_deleted=False, is_hidden=False, privacy='Public')[0:4]
#         groups = GetGroupSerializer(groups, many=True, context={'profile': profile}).data
#         properties = Property.objects.filter(name__icontains=title, is_deleted=False, privacy='Public')[0:4]
#         properties = PropertyListingSerializer(properties, many=True).data
#         automotives = Automotive.objects.filter(name__icontains=title, is_deleted=False, privacy='Public')[0:4]
#         automotives = AutomotiveListingSerializer(automotives, many=True).data
#         classifieds = Classified.objects.filter(name__icontains=title, is_deleted=False, privacy='Public')[0:4]
#         classifieds = ClassifiedListingSerializer(classifieds, many=True).data
#         posts = Post.objects.filter(text__icontains=title, is_deleted=False, is_hidden=False, privacy='Public'
#                         ).select_related(
#                             'profile', 'group', 'page'
#                         ).prefetch_related(
#                             'postreaction_post', 'post_post', 'sub_post',
#                             'albumpost_post', 'pollpost_post',
#                             'taguser_post', 'sharedpost_post')[0:4]
#         posts = PostGetSerializer(posts, many=True, context={"profile": profile}).data

#         results = {
#             'people': people,
#             'pages': pages,
#             'groups': groups,
#             'properties': properties,
#             'automotives': automotives,
#             'classifieds': classifieds,
#             'posts': posts,
#         }

#         return Response({'success': True, 'response': {'message': results}},
#                         status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_module(request):
    title = request.query_params.get('title')
    profile = request.query_params.get('profile')
    module = request.query_params.get('module')
    if not title or not profile:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'Profile does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'response': {'message': 'Invalid Profile ID.'}},
                    status=status.HTTP_400_BAD_REQUEST)
        if module == 'people':
            private_profiles = list(UserPrivacySettings.objects.filter(search_profile_privacy='OnlyMe').values_list('profile__id', flat=True))
            friends_profiles = list(UserPrivacySettings.objects.filter(search_profile_privacy='Friends').values_list('profile__id', flat=True))
            try:
                friends_list = list(FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True))
            except Exception as e:
                friends_list = []
            for i in friends_profiles:
                for j in friends_list:
                    if i == j:
                        friends_profiles.remove(i)
            people = Profile.objects.filter(Q(user__username__icontains=title, user__is_active=True) |
                                            Q(user__first_name__icontains=title, user__is_active=True) |
                                            Q(user__middle_name__icontains=title, user__is_active=True) |
                                            Q(user__last_name__icontains=title, user__is_active=True) |
                                            Q(user__name__icontains=title, user__is_active=True) |
                                            Q(user__email__icontains=title, user__is_active=True)).exclude(id__in=private_profiles).exclude(id__in=friends_profiles)
            paginator = CustomPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(people, request)
            serializer = SearchUserProfileSerializer(result_page, many=True, context={'profile': profile})
            return paginator.get_paginated_response(serializer.data)

        elif module == 'pages':
            pages = Page.objects.filter(name__icontains=title, is_deleted=False, is_hidden=False, privacy='Public')
            paginator = CustomPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(pages, request)
            serializer = GetPageSerializer(result_page, many=True, context={'profile': profile})
            return paginator.get_paginated_response(serializer.data)

        elif module == 'groups':
            groups = Group.objects.filter(name__icontains=title, is_deleted=False, is_hidden=False, privacy='Public')[0:4]
            paginator = CustomPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(groups, request)
            serializer = GetGroupSerializer(result_page, many=True, context={'profile': profile})
            return paginator.get_paginated_response(serializer.data)
        
        elif module == 'properties':
            properties = Property.objects.filter(name__icontains=title, is_deleted=False, privacy='Public')[0:4]
            paginator = CustomPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(properties, request)
            serializer = PropertyListingSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        elif module == 'automotives':
            automotives = Automotive.objects.filter(name__icontains=title, is_deleted=False, privacy='Public')[0:4]
            paginator = CustomPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(automotives, request)
            serializer = AutomotiveListingSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        elif module == 'classifieds':
            classifieds = Classified.objects.filter(name__icontains=title, is_deleted=False, privacy='Public')[0:4]
            paginator = CustomPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(classifieds, request)
            serializer = ClassifiedListingSerializer(result_page, many=True, context={'profile': profile})
            return paginator.get_paginated_response(serializer.data)
        
        elif module == 'posts':
            posts = Post.objects.filter(text__icontains=title, is_deleted=False, is_hidden=False, privacy='Public'
                ).select_related(
                    'profile', 'group', 'page'
                ).prefetch_related(
                    'postreaction_post', 'post_post', 'sub_post',
                    'albumpost_post', 'pollpost_post',
                    'taguser_post', 'sharedpost_post')[0:4]
            paginator = CustomPagination()
            paginator.page_size = 20
            result_page = paginator.paginate_queryset(posts, request)
            serializer = PostGetSerializer(result_page, many=True, context={"profile": profile})
            return paginator.get_paginated_response(serializer.data)
        
        else:
            return Response({'success': False, 'response': {'message': 'Invalid Module Name'}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_friends(request):
    title = request.query_params.get('title')
    profile = request.query_params.get('profile')
    if not title or not profile:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'Profile does not exist.'}},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'response': {'message': 'Invalid Profile ID.'}},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            friends_list = FriendsList.objects.get(profile=profile).friends.all()
            people = friends_list.filter(Q(user__username__icontains=title, user__is_active=True) |
                                            Q(user__first_name__icontains=title, user__is_active=True) |
                                            Q(user__middle_name__icontains=title, user__is_active=True) |
                                            Q(user__last_name__icontains=title, user__is_active=True) |
                                            Q(user__name__icontains=title, user__is_active=True) |
                                            Q(user__email__icontains=title, user__is_active=True))
        except:
            people = []
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(people, request)
        serializer = GetUserProfileSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

def is_valid_queryparam(*args):
    return args != '' and args is not None


@api_view(['GET'])
@permission_classes([AllowAny])
def discover_people(request):

    my_dict = dict()
    if "school" in request.query_params !=None and "school" in request.query_params !='':
        my_dict["userhighschool_profile__school_name__icontains"] = request.query_params.get('school')

    if "degree" in request.query_params != None  and "degree" in request.query_params != '' :
        my_dict["userhighschool_profile__degree__icontains"] = request.query_params.get('degree')

    if "gender" in request.query_params !=None and "gender" in request.query_params !='':
        my_dict["gender"] = request.query_params.get('gender')

    if "relationship_status" in request.query_params !=None and "relationship_status" in request.query_params !='':
        my_dict["profile_relationship__relationship__relationship_type__icontains"] = request.query_params.get('relationship_status')

    if "birthday" in request.query_params !=None and "birthday" in request.query_params !='':
        my_dict["birth_date"] = request.query_params.get('birthday')
        year, month, day = my_dict["birth_date"].split('-')
        my_dict["birth_date"] = datetime.date(int(year), int(month), int(day))

    if "interest" in request.query_params != None and "interest" in request.query_params != '':
        my_dict["useractivity_profile__interest__icontains"] = request.query_params.get('interest')

    if "country" in request.query_params !=None and "country" in request.query_params !='':
        my_dict["userplaceslived_profile__country__name__icontains"] = request.query_params.get('country')

    if "state" in request.query_params !=None and "state" in request.query_params !='':
        my_dict["userplaceslived_profile__state__name__icontains"] = request.query_params.get('state')

    if "city" in request.query_params !=None and "city" in request.query_params !='':
        my_dict["userplaceslived_profile__city__name__icontains"] = request.query_params.get('city')

    if "age" in request.query_params !=None and "age" in request.query_params !='':
        my_dict["birth_date__year__gte"] = request.query_params.get('age')
        current_year = date.today().year
        my_dict["birth_date__year__gte"] = current_year - int(my_dict["birth_date__year__gte"])
   
    profiles = ''

    if is_valid_queryparam(my_dict):
        if len(my_dict) < 1:
            profiles = Profile.objects.filter(is_deleted=False, user__is_active=True)
        else:
            profiles = Profile.objects.filter(**my_dict, is_deleted=False, user__is_active=True).distinct()
    profiles = DiscoverProfileSerializer(profiles, many=True, context={'relation': my_dict['profile_relationship__relationship__relationship_type__icontains']}).data
    results = {
        'profiles':profiles,
    }

    return Response({'success': True, 'response': {'message': results}},
                    status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def discover_communinty(request):
    module = request.query_params.get('module')
    title = request.query_params.get('title')
    if not module or not title:
        return Response({'success': False, 'response':{'message': 'Invalid Data!'}})
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({'success':False, 'response':{'message': str(e)}}, status=status.HTTP_401_UNAUTHORIZED)
    if module == 'pages':
        pages = Page.objects.filter(name__icontains=title, is_deleted=False, is_hidden=False, privacy='Public')
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page =paginator.paginate_queryset(pages, request)
        serializer = GetPageSerializer(result_page, many=True, context={'profile':profile})
        return paginator.get_paginated_response(serializer.data)
    elif module == 'groups':
        groups = Group.objects.filter(name__icontains=title, is_deleted=False, is_hidden=False, privacy='Public')
        paginator = CustomPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(groups, request)
        serializer = GetGroupSerializer(result_page, many=True, context={'profile': profile})
        return paginator.get_paginated_response(serializer.data)
   

@api_view(['GET'])
@permission_classes([AllowAny])
def search_all(request):
    title = request.query_params.get('title')
    module = request.query_params.get('module')
    sorted_by = request.query_params.get('sorted_by')

    if not title :
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    my_dict = dict()

    # my_dict['name__icontains'] = title
    
    title_automotive = Automotive.objects.filter(
        Q(name__icontains=title)|
        Q(category__title__icontains=title)|
        Q(sub_category__title__icontains=title),
        is_deleted=False, is_active=True)
    
    if "min_year" in request.query_params !=None and "min_year" in request.query_params !='':
        if request.query_params.get('min_year'):
            my_dict["automotive_year__gte"] = request.query_params.get('min_year')

    if "max_year" in request.query_params !=None and "max_year" in request.query_params !='':
        if request.query_params.get('max_year'):
            my_dict["automotive_year__lte"] = request.query_params.get('max_year')
    
    if "automotive_inspection" in request.query_params !=None and "automotive_inspection" in request.query_params !='':
        my_dict["automotive_inspection__icontains"] = request.query_params.get('automotive_inspection')

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
    
    automotives = ''
    if is_valid_queryparam(my_dict):
        if len(my_dict) < 1:
            if sorted_by == 'lowtohigh':
                automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('price')
            elif sorted_by == 'hightolow':
                automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('-price')
            else:
                automotives = Automotive.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')
        else:
            if sorted_by == 'lowtohigh':
                automotives = Automotive.objects.filter(**my_dict, is_deleted=False, is_active=True).order_by('price').distinct()
            elif sorted_by == 'hightolow':
                automotives = Automotive.objects.filter(**my_dict, is_deleted=False, is_active=True).order_by('-price').distinct()
            else:
                automotives = title_automotive.filter(**my_dict, is_deleted=False, is_active=True)
    
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
    }
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(automotives, request)
    automotive = GetAutomotiveSerializer(result_page, many=True, context=context).data
    # return paginator.get_paginated_response(serializer.data)


    # try:
    #     profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    # except:
    #     profile = None
    # my_dict = dict()

    # my_dict['name__icontains'] = title
    # if "min_price" in request.query_params !=None and "min_price" in request.query_params !='':
    #     if request.query_params.get('min_price'):
    #         my_dict["min_price__gte"] = request.query_params.get('min_price')

    # if "max_price" in request.query_params !=None and "max_price" in request.query_params !='':
    #     if request.query_params.get('max_price'):
    #         my_dict["max_price__lte"] = request.query_params.get('max_price')

    # if "area_unit" in request.query_params !=None and "area_unit" in request.query_params !='':
    #     if request.query_params.get('area_unit'):
    #         my_dict["area_unit__icontains"] = request.query_params.get('area_unit')

    # if "min_area" in request.query_params !=None and "min_area" in request.query_params !='':
    #     if request.query_params.get('min_area'):
    #         my_dict["area__gte"] = request.query_params.get('min_area')

    # if "max_area" in request.query_params !=None and "max_area" in request.query_params !='':
    #     if request.query_params.get('max_area'):
    #         my_dict["area__lte"] = request.query_params.get('max_area')

    # if "sub_category" in request.query_params !=None and "sub_category" in request.query_params !='':
    #     sub_category = request.query_params.get('sub_category')
    #     try:
    #         sub_category = SubCategory.objects.get(id=sub_category)
    #     except Exception as e:
    #         print(e)

    #     my_dict["sub_category__title__icontains"] = sub_category

    # if "currency" in request.query_params !=None and "currency" in request.query_params !='':
    #     currency = request.query_params.get('currency')
    #     try:
    #         currency = Currency.objects.get(id=currency)
    #     except Exception as e:
    #         print(e)

    #     my_dict["currency__name__icontains"] = currency

    # properties = ''
    # if is_valid_queryparam(my_dict):
    #     if len(my_dict) < 1:
    #         properties = Property.objects.filter(is_deleted=False, verification_status='Verified')
    #     else:
    #         properties = Property.objects.filter(**my_dict, is_deleted=False, is_active=True).distinct()

    # paginator = CustomPagination()
    # paginator.page_size = 8
    # result_page = paginator.paginate_queryset(properties, request)
    # property = PropertyGetSerializer(result_page, many=True).data
    # # return paginator.get_paginated_response(serializer.data)


    # classifieds = ''

    # try:
    #     profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    # except:
    #     profile = None
    # my_dict = dict()

    # my_dict['name__icontains'] = title
    # if "category" in request.query_params !=None and "category" in request.query_params !='':
    #     category = request.query_params.get('category')
    #     try:
    #         category = ClassifiedCategory.objects.get(id=category)
    #         category.view_count += 1
    #         category.save()
    #     except Exception as e:
    #         print(e)

    #     my_dict["category__title__icontains"] = category

    # if "sub_category" in request.query_params !=None and "sub_category" in request.query_params !='':
    #     sub_category = request.query_params.get('sub_category')
    #     try:
    #         sub_category = ClassifiedSubCategory.objects.get(id=sub_category)
    #     except Exception as e:
    #         print(e)
    #     my_dict["sub_category__title__icontains"] = sub_category

    # if "brand" in request.query_params !=None and "brand" in request.query_params !='':
    #     brand = request.query_params.get('brand')

    #     try:
    #         brand = ClassifiedeMake.objects.get(id=brand)
    #     except Exception as e:
    #         print(e)
    #     my_dict["make__title__icontains"] = brand

    # if "condition" in request.query_params !=None and "condition" in request.query_params !='':
    #     my_dict["type__icontains"] = request.query_params.get('condition')

    # if "min_price" in request.query_params !=None and "min_price" in request.query_params !='':
    #     min_price = request.query_params.get('min_price')
    #     if min_price:
    #         min_price.value = None

    #     my_dict["price__gte"] = request.query_params.get('min_price')

    
    # if "max_price" in request.query_params !=None and "max_price" in request.query_params !='':
    #     my_dict["price__lte"] = request.query_params.get('max_price')

    # if "currency" in request.query_params !=None and "currency" in request.query_params !='':
    #     currency = request.query_params.get('currency')
    #     try:
    #         currency = Currency.objects.get(id=currency)
    #     except Exception as e:
    #         print(e)

    #     my_dict["currency__name__icontains"] = currency
        
    # if is_valid_queryparam(my_dict):
    #     if len(my_dict) < 1:
    #         classifieds = Classified.objects.filter(is_deleted=False)
    #     else:
    #         classifieds = Classified.objects.filter(**my_dict, is_deleted=False, is_active=True).distinct()
    
    # paginator = CustomPagination()
    # paginator.page_size = 8
    # result_page = paginator.paginate_queryset(classifieds, request)
    # classified = ClassifiedGetSerializer(result_page, many=True).data
    # # return paginator.get_paginated_response(serializer.data)


    # try:
    #     profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    # except:
    #     profile = None
    # my_dict = dict()

    # my_dict['title__icontains'] = title

    # if "created_at" in request.query_params !=None and "created_at" in request.query_params !='':
    #     if request.query_params.get('created_at'):
    #         my_dict["created_at__lte"] = request.query_params.get('created_at')

    # if "salary_start" in request.query_params !=None and "salary_start" in request.query_params !='':
    #     if request.query_params.get('salary_start'):
    #         my_dict["salary_start__gte"] = request.query_params.get('salary_start')

    # if "salary_end" in request.query_params !=None and "salary_end" in request.query_params !='':
    #     if request.query_params.get('salary_end'):
    #         my_dict["salary_end__lte"] = request.query_params.get('salary_end')

    # if "job_type" in request.query_params !=None and "job_type" in request.query_params !='':
    #     my_dict["job_type__icontains"] = request.query_params.get('job_type')

    # if "position_type" in request.query_params !=None and "position_type" in request.query_params !='':
    #     my_dict["position_type__icontains"] = request.query_params.get('position_type')
    
    # if "currency" in request.query_params !=None and "currency" in request.query_params !='':
    #     currency = request.query_params.get('currency')
    #     try:
    #         currency = Currency.objects.get(id=currency)
    #     except Exception as e:
    #         print(e)

    #     my_dict["salary_currency__name__icontains"] = currency
    
    # jobs = ''
    # if is_valid_queryparam(my_dict):
    #     if len(my_dict) < 1:
    #         if sorted_by == 'lowtohigh':
    #             jobs = Job.objects.filter(is_deleted=False, is_active=True)
    #         elif sorted_by == 'hightolow':
    #             jobs = Job.objects.filter(is_deleted=False, is_active=True)
    #         else:
    #             jobs = Job.objects.filter(is_deleted=False, is_active=True)

    #     else:
    #         if sorted_by == 'lowtohigh':
    #             jobs = Job.objects.filter(**my_dict, is_deleted=False, is_active=True).distinct()
    #         elif sorted_by == 'hightolow':
    #             jobs = Job.objects.filter(**my_dict, is_deleted=False, is_active=True).distinct()
    #         else:
    #             jobs = Job.objects.filter(**my_dict, is_deleted=False, is_active=True).distinct()

    #         if profile:
    #             for j in jobs:
    #                 if not j.jobsearchhistory_job.filter(profile=profile):
    #                     try:
    #                         search_history = JobSearchHistory.objects.get(
    #                                                     profile=profile,
    #                                                     job=j,
    #                     )
    #                     except:
    #                         search_history = JobSearchHistory.objects.create(
    #                                                         profile=profile,
    #                                                         job=j,
    #                         )
    # paginator = CustomPagination()
    # paginator.page_size = 8
    # result_page = paginator.paginate_queryset(jobs, request)
    # job = GetJobSerializer(result_page, many=True).data
    result_list ={
        'automotive':automotive,
        # 'property':property,
        # 'classified':classified,
        # 'job':job,
    }
    return paginator.get_paginated_response(result_list)

    # properties = Property.objects.filter(name__icontains=title, is_deleted=False, is_active=True)
    # properties = PropertyListingSerializer(properties, many=True).data
    # automotives = Automotive.objects.filter(Q(name__icontains=title) |
    #                                         Q(category__title__icontains=title) |
    #                                         Q(make__title__icontains=title) |
    #                                         Q(automotive_model__title__icontains=title),
    #                                         is_deleted=False,
    #                                         is_active=True)
    # automotives = AutomotiveListingSerializer(automotives, many=True).data
    # classifieds = Classified.objects.filter(
    #                                         Q(name__icontains=title) |
    #                                         Q(category__title__icontains=title) , 
    #                                         is_deleted=False,
    #                                         is_active=True)
    # classifieds = ClassifiedListingSerializer(classifieds, many=True).data
    # jobs = Job.objects.filter(Q(title__icontains=title ) |
    #                                 Q(employment_type__icontains=title) |
    #                                 Q(job_type__icontains=title),
    #                                     is_deleted=False,
    #                                     is_active=True)
    # jobs = GetJobSerializer(jobs, many=True).data


    # results = {
    #     'properties': properties,
    #     'automotives': automotives,
    #     'classifieds': classifieds,
    #     'jobs': jobs,
    # }

    # return Response({'success': True, 'response': results},
    #                 status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_my_module_ads(request):
    module_name = request.query_params.get('module_name', None)
    sort_by = request.query_params.get('sort_by', None)

    if not module_name:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                        status=status.HTTP_400_BAD_REQUEST)
    
    if module_name == 'Classified':
        if sort_by == 'old':
            classifieds = Classified.objects.filter(is_deleted=False, is_active=True, verification_status='Verified').order_by('created_at')
        elif sort_by == 'new':
            classifieds = Classified.objects.filter(is_deleted=False, is_active=True, verification_status='Verified').order_by('-created_at')
        else:
            classifieds = Classified.objects.filter(is_deleted=False, is_active=True, verification_status='Verified')
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(classifieds, request)
        serializer = ClassifiedGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif module_name == 'Property':
        if sort_by == 'old':
           properties = Property.objects.filter(is_deleted=False, is_active=True, verification_status='Verified').order_by('created_at')
        elif sort_by == 'new':
            properties = Property.objects.filter(is_deleted=False, is_active=True, verification_status='Verified').order_by('-created_at')
        else:
            properties = Property.objects.filter(is_deleted=False, is_active=True, verification_status='Verified')
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(properties, request)
        serializer = PropertyGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif module_name == 'Job':
        if sort_by == 'old':
            jobs = Job.objects.filter(is_deleted=False, is_active=True, verification_status='Verified').order_by('created_at')
        elif sort_by == 'new':
            jobs = Job.objects.filter(is_deleted=False, is_active=True, verification_status='Verified').order_by('-created_at')
        else:
            jobs = Job.objects.filter(is_deleted=False, is_active=True, verification_status='Verified')   
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(jobs, request)
        serializer = GetJobSerializer(result_page, many=True, context={'profile': profile})
        return paginator.get_paginated_response(serializer.data)

    elif module_name == 'Automotive':
        if sort_by == 'old':
            automotives = Automotive.objects.filter(is_deleted=False, is_active=True, verification_status='Verified').order_by('created_at')
        elif sort_by == 'new':
            automotives = Automotive.objects.filter(is_deleted=False, is_active=True, verification_status='Verified').order_by('-created_at')
        else:
            automotives = Automotive.objects.filter(is_deleted=False, is_active=True, verification_status='Verified')
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(automotives, request)
        serializer = GetAutomotiveSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# def N_max_elements(list, N):
#     list.sort()     
#     return list[-N: ]

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_popular_categories(request):
#     classified_category = ClassifiedCategory.objects.all().order_by('-view_count')[:5]
#     property_category = Category.objects.all().order_by('-view_count')[:5]
#     automotive_category = AutomotiveCategory.objects.all().order_by('-view_count')[:5]
#     job_category = JobCategory.objects.all().order_by('-view_count')[:5]
#     category_list = []

#     for c in classified_category:
#         category_list.append(c)
#     for p in property_category:
#         category_list.append(c)
#     for a in automotive_category:
#         category_list.append(a)
#     for j in job_category:
#         category_list.append(j)

#     sorted_list = sorted(category_list('view_count'))
#     print(sorted_list)

#     return Response({'success': True, 'response': {'message': 'All Okay'}},
#                     status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def view_ads_by_profile(request):
    id = request.query_params.get('id', None)
    visitor_profile = None
    automotives = []
    properties = []
    classified = []
    jobs = []
    company = None
    if not id:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                            status=status.HTTP_400_BAD_REQUEST)
    
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None
    if id:
        try:

            visitor_profile = Profile.objects.get(id=id, is_deleted=False, user__is_active=True)
        except ObjectDoesNotExist:
            try:
                company = Company.objects.get(id=id, is_deleted=False)
            except Exception as e:
                pass
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                                                                status=status.HTTP_404_NOT_FOUND)
                                            



    # try:
    #     automotive_company = Company.objects.get(profile=visitor_profile, is_deleted=False, company_type='Automotive')
    # except:
    #     pass
    if company and company.company_type == 'Automotive':
        automotives = Automotive.objects.filter(profile=company.profile, is_deleted=False, is_active=True, business_type='Company')
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(automotives, request)
        if profile:
            automotives = GetAutomotiveSerializer(result_page, many=True, context={'profile': profile}).data
        else:
            automotives = GetAutomotiveSerializer(result_page, many=True).data
    if visitor_profile:
        automotives = Automotive.objects.filter(profile=visitor_profile, is_deleted=False, is_active=True)
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(automotives, request)
        if profile:
            automotives = GetAutomotiveSerializer(result_page, many=True, context={'profile': profile}).data
        else:
            automotives = GetAutomotiveSerializer(result_page, many=True).data

    # try:
    #     property_company = Company.objects.get(profile=visitor_profile, is_deleted=False, company_type='Property')
    # except:
    #     pass
    
    if company and company.company_type == 'Property':
        properties = Property.objects.filter(profile=company.profile, is_deleted=False, is_active=True, business_type='Company')
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(properties, request)
        if profile:
            properties = PropertyGetSerializer(result_page, many=True, context={'profile': profile}).data
        else:
            properties = PropertyGetSerializer(result_page, many=True).data
    if visitor_profile:
        properties = Property.objects.filter(profile=visitor_profile, is_deleted=False, is_active=True)
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(properties, request)
    
        if profile:
            properties = PropertyGetSerializer(result_page, many=True, context={'profile': profile}).data
        else:
            properties = PropertyGetSerializer(result_page, many=True).data

    # try:
    #     job_company = Company.objects.get(profile=visitor_profile, is_deleted=False, company_type='Job')
    # except:
    #     pass
    
    if company and company.company_type == 'Job':
        jobs = Job.objects.filter(profile=company.profile, is_deleted=False, is_active=True, business_type='Company')
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(jobs, request)
        
        if profile:
            jobs = GetJobSerializer(result_page, many=True, context={'profile': profile}).data
        else:
            jobs = GetJobSerializer(result_page, many=True).data
    if visitor_profile is not None:
        jobs = Job.objects.filter(profile=visitor_profile, is_deleted=False, is_active=True)
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(jobs, request)
        
        if profile:
            jobs = GetJobSerializer(result_page, many=True, context={'profile': profile}).data
        else:
            jobs = GetJobSerializer(result_page, many=True).data

    # try:
    #     classified_company = Company.objects.get(profile=visitor_profile, is_deleted=False, company_type='Classified')
    # except Exception as e:
    #     print(e)
    #     pass

    if company and company.company_type == 'Classified':
        classified = Classified.objects.filter(profile=company.profile, is_deleted=False, is_active=True, business_type='Company')
        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(classified, request)
        
        if profile:
            classified = ClassifiedGetSerializer(result_page, many=True, context={'profile': profile}).data
        else:
            classified = ClassifiedGetSerializer(result_page, many=True).data
    if visitor_profile:
        classified = Classified.objects.filter(profile=visitor_profile, is_deleted=False, is_active=True)

        paginator = CustomPagination()
        paginator.page_size = 8
        result_page = paginator.paginate_queryset(classified, request)
        
        if profile:
            classified = ClassifiedGetSerializer(result_page, many=True, context={'profile': profile}).data
        else:
            classified = ClassifiedGetSerializer(result_page, many=True).data

    result_list ={
        'automotive':automotives,
        'property':properties,
        'classified':classified,
        'job':jobs,
    }

    return paginator.get_paginated_response(result_list)


@api_view(['GET'])
@permission_classes([AllowAny])
def suggested_ads(request):
    category = request.query_params.get('category', None)
    module_name = request.query_params.get('module_name', None)

    if not category or not module_name:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                            status=status.HTTP_400_BAD_REQUEST)
    
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None

    if module_name == 'Automotive':
        automotives = Automotive.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')[:8]
        if profile:
            serializer = GetAutomotiveSerializer(automotives, many=True, context={'profile': profile})
        else:
            serializer = GetAutomotiveSerializer(automotives, many=True)
        return Response({'success': True, 'automotive': serializer.data},
            status=status.HTTP_200_OK)

    elif module_name == 'Property':
        properties = Property.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')[:8]
        if profile:
            serializer = PropertyGetSerializer(properties, many=True, context={'profile': profile})
        else:
            serializer = PropertyGetSerializer(properties, many=True)
        return Response({'success': True, 'property': serializer.data},
            status=status.HTTP_200_OK) 

    elif module_name == 'Job':
        jobs = Job.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')[:8]
        if profile:
            serializer = GetJobSerializer(jobs, many=True, context={'profile': profile})
        else:
            serializer = GetJobSerializer(jobs, many=True)
        return Response({'success': True, 'job': serializer.data},
            status=status.HTTP_200_OK)

    elif module_name == 'Classified':
        classified = Classified.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')[:8]
        if profile:
            serializer = ClassifiedGetSerializer(classified, many=True, context={'profile': profile})
        else:
            serializer = ClassifiedGetSerializer(classified, many=True)

        return Response({'success': True, 'classified': serializer.data},
            status=status.HTTP_200_OK)