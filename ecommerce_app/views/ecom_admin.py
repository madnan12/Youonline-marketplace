from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from ecommerce_app.models import *
from ecommerce_app.serializers import *
from django.conf import settings
from youonline_social_app.custom_api_settings import CustomPagination
from youonline_social_app.youonline_threads import ReadNotificationsThread
from youonline_social_app.serializers.users_serializers import NotificationSerializer
from youonline_social_app.models import Profile, Notification
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_recent_products(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        profile = None
    # Check for the id in request.query_params for validation
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
    # Get recent products based on Business Details
    products = Product.objects.filter(business_details=business_details, is_deleted=False
        ).prefetch_related(
            'productmedia_product',
        ).order_by('-created_at')[:30]
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(products, request)
    serializer = GetProductSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_notifications(request):
    # Check for token
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        return Response({'success': False, 'response': {'message': 'Invalid Token'}},
                    status=status.HTTP_401_UNAUTHORIZED)
    # Check for the id in request.query_params for validation
    id = request.query_params['id'] if 'id' in request.query_params else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                    status=status.HTTP_400_BAD_REQUEST)
    # Check if the business details exists
    try:
        business_details = BusinessDetails.objects.get(id=id, owner__profile=profile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Business Details does not exist.'}},
                    status=status.HTTP_404_NOT_FOUND)
    # Get Notifications based on Business Details Page.
    notifications = Notification.objects.filter(page=business_details.page
                        ).select_related('page').order_by('-created_at')
    # Read notifications using thread.
    ReadNotificationsThread(request, profile, notifications).start()

    # Return the paginated response.
    paginator = CustomPagination()
    paginator.page_size = 15
    result_page = paginator.paginate_queryset(notifications, request)
    serializer = NotificationSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
