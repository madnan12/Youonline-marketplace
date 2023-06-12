from django.urls import path
from ecommerce_app.views import ecommerce, ecom_admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Business Owner URLs
    path('create_business_owner/', ecommerce.create_business_owner),
    path('update_business_owner/', ecommerce.update_business_owner),
    path('get_business_owner/', ecommerce.get_business_owner),
    path('delete_business_owner/', ecommerce.delete_business_owner),

    # Business Details URLs
    path('create_business_details/', ecommerce.create_business_details),
    path('update_business_details/', ecommerce.update_business_details),
    path('get_business_details/', ecommerce.get_business_details),
    path('delete_business_details/', ecommerce.delete_business_details),
    path('active_business_detail/', ecommerce.active_business_detail),

    # Product URLs
    path('create_product/', ecommerce.create_product),
    path('get_product/', ecommerce.get_product),
    path('update_product/', ecommerce.update_product),
    path('delete_product/', ecommerce.delete_product),
    path('get_all_business_products/', ecommerce.get_all_business_products),
    path('delete_products/', ecommerce.delete_products),
    
    # Search Products URL
    path('search_products/', ecommerce.search_products),

    # Archived Product URLs
    path('add_archive_product/', ecommerce.add_archive_product),
    path('get_archive_product/', ecommerce.get_archive_product),


    # Product Category URLs
    path('get_all_product_category/', ecommerce.get_all_product_category),
    path('get_all_product_subcategory/', ecommerce.get_all_product_subcategory),

    # Collection URLs
    path('create_collection/', ecommerce.create_collection),
    path('delete_collection/', ecommerce.delete_collection),
    path('update_collection/', ecommerce.update_collection),
    path('get_my_collection/', ecommerce.get_my_collection),
    path('get_collection/', ecommerce.get_collection),

    # Business Model Admin Panel URLs
    path('get_recent_products/', ecom_admin.get_recent_products),
    path('get_business_notifications/', ecom_admin.get_business_notifications),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
