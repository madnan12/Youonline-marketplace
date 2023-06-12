from django.urls import path
from . import views as property_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Property URLs
    path('get_property_categories/', property_views.get_property_categories),
    path('get_property_sub_categories/', property_views.get_property_sub_categories),
    path('get_property_sub_sub_categories/', property_views.get_property_sub_sub_categories),
    path('create_property/', property_views.create_property),
    path('update_property/', property_views.update_property),
    path('add_single_property_media/', property_views.add_single_property_media),
    path('delete_property_media/', property_views.delete_property_media),
    path('delete_property/', property_views.delete_property),
    path('get_all_properties/', property_views.get_all_properties),
    path('get_promoted_properties/', property_views.get_promoted_properties),
    path('get_popular_properties/', property_views.get_popular_properties),
    path('get_single_property/', property_views.get_single_property),
    path('verify_property/', property_views.verify_property),
    path('promote_property/', property_views.promote_property),
    path('contact_property/', property_views.contact_property),
    path('report_property/', property_views.report_property),
    path('get_my_properties/', property_views.get_my_properties),
    path('add_property_media/', property_views.add_property_media),

    # Search Filters
    path('search_properties/', property_views.search_properties),
    path('get_favourite_properties/', property_views.get_favourite_properties),
    path('recommended_properties/', property_views.recommended_properties),
    path('filtering_property/', property_views.filtering_property),

    # Landing Page URLs
    path('get_for_sale_properties/', property_views.get_for_sale_properties),
    path('get_for_rent_property/', property_views.get_for_rent_property),
    path('get_new_properties/', property_views.get_new_properties),
    # path('get_recommended_properties/', property_views.get_recommended_properties),
    path('search_landing_property/', property_views.search_landing_property),

    ############################################
    path('get_property_by_category/', property_views.get_property_by_category),
    path('filter_property/', property_views.filter_property),
    path('add_favourite_property/', property_views.add_favourite_property),
    path('total_count_properties/', property_views.total_count_properties),
    path('make_active_property/', property_views.make_active_property),
    path('get_deal_properties/', property_views.get_deal_properties),
    path('get_featured_properties/', property_views.get_featured_properties),
    path('near_property_ads/', property_views.near_property_ads),
    path('get_my_business_properties/', property_views.get_my_business_properties),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
