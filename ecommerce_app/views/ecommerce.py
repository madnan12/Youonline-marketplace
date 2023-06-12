import collections
from functools import partial
from django.core.exceptions import ObjectDoesNotExist
from requests import request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from ecommerce_app. models import *
from ecommerce_app. serializers import *
from youonline_social_app.custom_api_settings import CustomPagination
from youonline_social_app.models import Profile


# Business Owner CRUDs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_business_owner(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Add the user profile id to the request.data
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = profile.id
    serializer = BusinessOwnerSerializer(data=request.data)
    if serializer.is_valid():
        business_owner = serializer.save()
        serializer = GetBusinessOwnerSerializer(business_owner)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_owner(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Update the request data for profile
    try:
        request.data._mutable = True
    except:
        pass
    id = request.data['id'] if request.data['id'] else None
    # Check data validation
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Get the record before updating
    try:
        business_owner = BusinessOwner.objects.get(id=id, profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Owner does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Update the record partially
    serializer = BusinessOwnerSerializer(business_owner, data=request.data, partial=True)
    if serializer.is_valid():
        business_owner = serializer.save()
        serializer = GetBusinessOwnerSerializer(business_owner)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_owner(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    id = request.query_params['id'] if request.query_params['id'] else None
    # Check data validation
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Get the record
    try:
        business_owner = BusinessOwner.objects.get(id=id, profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Owner does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Serialize the given record
    serializer = GetBusinessOwnerSerializer(business_owner)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_owner(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    id = request.query_params['id'] if 'id' in request.query_params else None
    # Check data validation
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Get the record
    try:
        business_owner = BusinessOwner.objects.get(id=id, profile=profile, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': 'Business Owner does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Soft delete the record partially
    business_owner.is_deleted = True
    business_owner.save()
    return Response({'success': True, 'response': {'message': 'Business owner removed successfully.'}},
                status=status.HTTP_200_OK)


# Business Details CRUDs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_business_details(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Check for the data in request.data
    page = request.data['page'] if 'page' in request.data else None
    owner = request.data['owner'] if 'owner' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    checkout_option = request.data['checkout_option'] if 'checkout_option' in request.data else None
    # Get a comma separted list of countries and convert it to a python list
    countries = request.data['countries'] if 'countries' in request.data else None
    countries = countries[2:-2].split("','")

    if not owner or not page or not description or not checkout_option:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the business owner exists and belongs to the requesting user.
    try:
        bus_owner = BusinessOwner.objects.get(id=owner, profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Owner does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # check for the page if it exists and is created by requesting user.
    try:
        business_page = Page.objects.get(id=page, created_by=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Page does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    serializer = BusinessDetailsSerializer(data=request.data)
    if serializer.is_valid():
        countries_obj = list(set(Country.objects.filter(id__in=countries).values_list('name', flat=True)))
        business_detials = serializer.save(countries = countries_obj)
        # Save the page as business page.
        business_page.business_page = True
        business_page.save()
        serializer = GetBusinessDetailsSerializer(business_detials)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_details(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Check the request body for validation
    id = request.data['id'] if 'id' in request.data else None
    page = request.data['page'] if 'page' in request.data else None
    owner = request.data['owner'] if 'owner' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Do not allow to update the page of the business owner.
    if page or owner:
        return Response({'success': False, 'response': {'message': 'Page or Owner cannot be updated.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the business detials exists and belongs to the requesting user.
    try:
        business_details = BusinessDetails.objects.get(id=id, owner__profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Details does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Update the record partially.
    serializer = BusinessDetailsSerializer(business_details, data=request.data, partial=True)
    if serializer.is_valid():
        business_details = serializer.save()
        serializer = GetBusinessDetailsSerializer(business_details)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def active_business_detail(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        business_detail = BusinessDetails.objects.get(id=id, owner__profile=profile, is_deleted=False)
        business_detail.is_approved = True
        business_detail.save()
        return Response({'success': False, 'response': {'message': 'Business Details Approved.'}},
                    status=status.HTTP_201_CREATED)
    except:
        return Response({'success': False, 'response': {'message': 'Business Details does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_details(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Check for the data in request.query_params for validation
    id = request.query_params['id'] if 'id' in request.query_params else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the business details exists and belongs to the requesting user.
    try:
        business_details = BusinessDetails.objects.get(id=id, owner__profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Details does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    serializer = GetBusinessDetailsSerializer(business_details)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_details(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Check for the data in request.query_params for validation
    id = request.query_params['id'] if 'id' in request.query_params else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the business details exists and belongs to the requesting user.
    try:
        business_details = BusinessDetails.objects.get(id=id, owner__profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Details does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Soft Delete the record.
    business_details.is_deleted = True
    business_details.save()
    return Response({'success': True, 'response': {'message': 'Business Details deleted successfully.'}},
                status=status.HTTP_200_OK)


# Product CRUDs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Check for the data in request.data for validation
    business_details = request.data['business_details'] if 'business_details' in request.data else None
    title = request.data['title'] if 'title' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    category = request.data['category'] if 'category' in request.data else None
    brand = request.data['brand'] if 'brand' in request.data else None
    images = request.data['images'] if 'images' in request.data else None
    schedule_time = request.data['schedule_time'] if 'schedule_time' in request.data else None
    quantity = request.data['quantity'] if 'quantity' in request.data else None
    cost_price = request.data['cost_price'] if 'cost_price' in request.data else None
    sale_price = request.data['sale_price'] if 'sale_price' in request.data else None

    if not business_details or not title or not description\
        or not category or not brand or not images\
        or not quantity or not cost_price or not sale_price:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)

    # Check if cost price is greater than sale price.
    if int(cost_price) > int(sale_price):
        return Response({'success': False, 'response': {'message': 'Cost price cannot be greater than sale price.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if quantity is greater than 0.
    if int(quantity) <= 0:
        return Response({'success': False, 'response': {'message': 'Quantity cannot be less than or equal to 0.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the business details exists and belongs to the requesting user.
    try:
        business_details = BusinessDetails.objects.get(id=business_details, owner__profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Details does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Create the record.
    serializer = ProductSerializer(data=request.data, context = {'profile': profile.id, 'schedule_time': schedule_time})
    if serializer.is_valid():
        product = serializer.save()
        serializer = GetProductSerializer(product)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Check for the data in request.data for validation
    id = request.data['id'] if 'id' in request.data else None
    schedule_time = request.data['schedule_time'] if 'schedule_time' in request.data else None
    # Check if the product exists and belongs to the requesting user.
    try:
        product = Product.objects.get(id=id, business_details__owner__profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Product does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Update the record.
    # Populate request body
    try:
        request.data._mutable = True
    except:
        pass
    request.data['business_details'] = product.business_details.id
    serializer = ProductSerializer(product, data=request.data, context = {'profile': profile.id, 'schedule_time': schedule_time})
    if serializer.is_valid():
        product = serializer.save()
        serializer = GetProductSerializer(product)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_product(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        profile = None
    url = request.query_params['url'] if 'url' in request.query_params else None
    if not url:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the product exists.
    try:
        product = Product.objects.get(url=url, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Product does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    serializer = GetProductSerializer(product)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    url = request.query_params['url'] if 'url' in request.query_params else None
    if not url:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the product exists and belongs to the requesting user.
    try:
        product = Product.objects.get(url=url, business_details__owner__profile=profile, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    product.is_deleted = True
    product.save()
    for i in product.productmedia_product.all():
        i.is_deleted = True
        i.save()
    return Response({'success': True, 'response': {'message': 'Product deleted scuccessfully.'}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_business_products(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        profile = None
    id = request.query_params['id'] if 'id' in request.query_params else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the business details exists
    try:
        business_details = BusinessDetails.objects.get(id=id, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Details does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Check if the product exists.
    try:
        products = Product.objects.filter(business_details=business_details, is_deleted=False
            ).prefetch_related(
                'productmedia_product',
            ).order_by('-created_at')
    except:
        return Response({'success': False, 'response': {'message': 'Product does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(products, request)
    serializer = GetProductSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_product_category(request):
    categorys = ProductCategory.objects.all()
    serializer = ProductCategorySerializer(categorys, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_product_subcategory(request):
    subcategorys = ProductSubCategory.objects.all()
    serializer = ProductSubCategorySerializer(subcategorys, many=True)
    return Response({'success':True, 'response':{'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    title = request.query_params.get('title')
    category = request.query_params.get('category')
    condition = request.query_params.get('condition')
    product_status = request.query_params.get('status')
    brand = request.query_params.get('brand')
    all_product = request.query_params.get('all_product')
    from_price = request.query_params.get('from_price')
    to_price = request.query_params.get('to_price')

    if not title and not all_product and not category and not condition and not product_status and not from_price and not to_price and not brand:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}
                             }, status=status.HTTP_400_BAD_REQUEST)
    if not title:
        title = ''
    try:
        category = ProductCategory.objects.get(id=category)
    except:
        category = ''

    if not condition:
        condition = ''
    
    if not product_status:
        product_status = ''
    
    if not brand:
        brand = ''
    
    if all_product == 'True':
        product = Product.objects.filter(is_deleted=False)
    else:
        if from_price and not to_price:
            product = Product.objects.filter(
                                    cost_price__gte=from_price, 
                                    title__icontains=title, 
                                    category__title__icontains=category, 
                                    condition__icontains=condition,
                                    status__icontains=product_status,
                                    brand__icontains=brand
                                    )
        if to_price and not from_price:
            product = Product.objects.filter(
                                    cost_price__lte=to_price, 
                                    title__icontains=title, 
                                    category__title__icontains=category, 
                                    condition__icontains=condition,
                                    status__icontains=product_status,
                                    brand__icontains=brand
                                    )
        if from_price and to_price:
            product = Product.objects.filter(
                                    cost_price__gte=from_price,
                                    cost_price__lte=to_price,
                                    title__icontains=title, 
                                    category__title__icontains=category, 
                                    condition__icontains=condition,
                                    status__icontains=product_status,
                                    brand__icontains=brand
                                    )
        if not from_price and not to_price:
            product = Product.objects.filter(
                                    title__icontains=title, 
                                    category__title__icontains=category, 
                                    condition__icontains=condition,
                                    status__icontains=product_status,
                                    brand__icontains=brand
                                    )

    serializer=GetProductSerializer(product, many=True)
    return Response({'success': True, 'response': {
                'message': serializer.data}
                             }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_archive_product(request):
    product = request.data['product'] if 'product' in request.data else None
    if not product:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}
                             }, status=status.HTTP_400_BAD_REQUEST)
    try:
        product = Product.objects.get(id=product, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        archive_product = ArchivedProduct.objects.get(product=product)
        archive_product.delete()
        return Response({'success': True, 'message': {"message": 'Product removed from archived list!'}},
                    status=status.HTTP_200_OK)
    except ArchivedProduct.DoesNotExist:
        archive_product = ArchivedProduct.objects.create(
                        product=product
                    )
        serializer = ArchivedProductSerializer(archive_product)
        return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_archive_product(request):
    business_detail = request.query_params['business_detail']
    if not business_detail:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}
                             }, status=status.HTTP_400_BAD_REQUEST)
    try:
        business_detail = BusinessDetails.objects.get(id=business_detail)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    archive_product = ArchivedProduct.objects.filter(product__business_details=business_detail.id)
    serializer = GetArchivedProductSerializer(archive_product, many=True)
    return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_products(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)

    id = id[1:-1].replace('"', '').split(',')
    for i in id:
        try:
            p = Product.objects.get(id=i)
            p.is_deleted = True
            p.save()
            return Response({"success": True, 'response': {'message': 'Product deleted successfully!!'}},
                status=status.HTTP_200_OK)
        except Exception as e:
            pass

@api_view(['POST'])
@permission_classes([AllowAny])
def create_collection(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)

    title = request.data['title'] if 'title' in request.data else None
    product = request.data['product'] if 'product' in request.data else None
    owner = request.data['owner'] if 'owner' in request.data else None
    if not title or not owner:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        bus_owner = BusinessOwner.objects.get(id=owner, profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Owner does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    product = product[1:-1].replace('"', '').split(',')
    request.data._mutable = True
    serializer = CollectionProductSerializer(data=request.data)
    if serializer.is_valid():
        collection = serializer.save()
        for p in product:
            try:
                pro = Product.objects.get(id=p)
                collection.product.add(pro)
            except Exception as e:
                print(e)
        collection.save()
        serializer = GetCollectionProductSerializer(collection)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_collection(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    id = request.query_params['id'] if 'id' in request.query_params else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        collection = CollectionProduct.objects.get(id=id, owner__profile=profile, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    collection.is_deleted = True
    collection.save()
    return Response({'success': True, 'response': {'message': 'Collection deleted scuccessfully.'}},
                status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_collection(request):
    id = request.data['id'] if 'id' in request.data else None
    deleted_product = request.data['deleted_product'] if 'deleted_product' in request.data else None
    added_product = request.data['added_product'] if 'added_product' in request.data else None
    owner = request.data['owner'] if 'owner' in request.data else None
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        bus_owner = BusinessOwner.objects.get(id=owner, profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Owner does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        collection = CollectionProduct.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    
    request.data._mutable = True
    serializer = CollectionProductSerializer(collection, data=request.data, partial=True)
    if serializer.is_valid():
        collection = serializer.save()

        if added_product:
            added_product = added_product[1:-1].replace('"', '').split(',')
            for p in added_product:
                try:
                    pro = Product.objects.get(id=p)
                    collection.product.add(pro)
                except Exception as e:
                    pass
        if deleted_product:
            deleted_product = deleted_product[1:-1].replace('"', '').split(',')
            for p in deleted_product:
                try:
                    pro = Product.objects.get(id=p)
                    collection.product.remove(pro)
                except Exception as e:
                    pass
        collection.save()
        serializer = GetCollectionProductSerializer(collection)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_collection(request):
    owner = request.query_params['owner']
    if not owner:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        owner = BusinessOwner.objects.get(id=owner, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    collections = CollectionProduct.objects.filter(owner=owner, is_deleted=False)
    serializer = GetCollectionProductSerializer(collections, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_collection(request):
    id = request.query_params['id']
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        collection = CollectionProduct.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    serializer = GetCollectionProductSerializer(collection)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)
