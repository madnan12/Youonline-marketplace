from django.urls import path
from . import views as automotive
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('get_automotive_categories/', automotive.get_automotive_categories),
    path('get_automotive_sub_categories/', automotive.get_automotive_sub_categories),
    path('get_automotive_sub_sub_categories/', automotive.get_automotive_sub_sub_categories),
    path('get_automotive_make_and_models/', automotive.get_automotive_make_and_models),

    path('create_automotive/', automotive.create_automotive),
    path('get_single_automotive/', automotive.get_single_automotive),
    path('get_all_automotives/', automotive.get_all_automotives),
    path('get_favourite_automotives/', automotive.get_favourite_automotives),
    path('get_my_automotives/', automotive.get_my_automotives),
    path('search_automotives/', automotive.search_automotives),
    path('search_automotives_optimized/', automotive.search_automotive_optimized),
    path('add_automotive_media/', automotive.add_automotive_media),

    path('verify_automotive/', automotive.verify_automotive),
    path('get_promoted_automotives/', automotive.get_promoted_automotives),
    path('promote_automotive/', automotive.promote_automotive),
    path('contact_automotive/', automotive.contact_automotive),
    path('report_ads/', automotive.report_ads),
    path('update_automotive/', automotive.update_automotive),
    path('delete_automotive_media/', automotive.delete_automotive_media),
    path('delete_automotive/', automotive.delete_automotive),
    path('get_makes_by_id/', automotive.get_makes_by_id),
    path('recently_view_ads/', automotive.recently_view_ads),

    path('add_favourite_automotive/', automotive.add_favourite_automotive),
    path('get_automotive_featured_brand/', automotive.get_automotive_featured_brand),
    path('get_automotive_by_brand/', automotive.get_automotive_by_brand),
    path('recommended_automotives/', automotive.recommended_automotives),
    
    # Landing Page URLs
    path('get_featured_automotives/', automotive.get_featured_automotives),
    path('get_latest_automotives/', automotive.get_latest_automotives),
    path('get_automotive_comparisons/', automotive.get_automotive_comparisons),
    path('get_automotive_videos/', automotive.get_automotive_videos),
    path('search_landing_automotive/', automotive.search_landing_automotive),
    path('get_used_cars/', automotive.get_used_cars),

    ################################################################
    path('filter_automotive/', automotive.filter_automotive),
    path('filtering_automotive/', automotive.filtering_automotive),
    path('get_model_by_brand/', automotive.get_model_by_brand),
    path('get_automotive_brand/', automotive.get_automotive_brand),
    path('total_count_automotives/', automotive.total_count_automotives),
    path('make_active_automotive/', automotive.make_active_automotive),
    path('get_deal_automotive/', automotive.get_deal_automotive),
    path('get_all_deals/', automotive.get_all_deals),
    path('near_automotive_ads/', automotive.near_automotive_ads),
    path('get_my_business_automotives/', automotive.get_my_business_automotives),
    path('get_automotives_by_category/', automotive.get_automotives_by_category),
    path('view_contact_notification/', automotive.view_contact_notification),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

