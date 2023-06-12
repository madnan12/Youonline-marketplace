from django.urls import path
from .import views  as classified
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create_classified/', classified.create_classified), 
    path('get_classified_categories/', classified.get_classified_categories),
    path('get_classified_sub_categories/', classified.get_classified_sub_categories),
    path('get_classified_sub_sub_categories/', classified.get_classified_sub_sub_categories),
    path('get_single_classified/', classified.get_single_classified),
    path('add_classified_media/', classified.add_classified_media),

    path('search_classifieds/', classified.search_classifieds),
    # path('search_classifieds/', classified.search_classifieds_optimized),
    path('search_classifieds_optimized/', classified.search_classifieds_optimized),
    path('get_all_classifieds/', classified.get_all_classifieds),
    path('get_favourite_classifieds/', classified.get_favourite_classifieds),
    path('get_my_classifieds/', classified.get_my_classifieds),
    path('get_promoted_classifieds/', classified.get_promoted_classifieds),
    path('verify_classified/', classified.verify_classified),
    path('promote_classified/', classified.promote_classified),
    path('contact_classified/', classified.contact_classified),
    path('report_classified/', classified.report_classified),
    path('update_classified/', classified.update_classified),
    path('delete_classified_media/', classified.delete_classified_media),
    path('delete_classified/', classified.delete_classified),
    path('add_favourite_classified/', classified.add_favourite_classified),
    path('get_all_classifieds/', classified.get_all_classifieds),

    path('get_classified_featured_brands/', classified.get_classified_featured_brands),
    path('get_classifieds_by_brands/', classified.get_classifieds_by_brands),
    path('make_active_classified/', classified.make_active_classified),

    # Landing Page URLs
    path('get_featured_classifieds/', classified.get_featured_classifieds),
    path('get_furniture_classifieds/', classified.get_furniture_classifieds),
    path('get_electronic_classifieds/', classified.get_electronic_classifieds),
    path('search_landing_classified/', classified.search_landing_classified),
    path('get_classifieds_by_category/', classified.get_classifieds_by_category),

    ######## NEW API URL #############
    path('filter_classifieds/', classified.filter_classifieds),
    path('get_deal_classifieds/', classified.get_deal_classifieds),
    path('recommended_classifieds/', classified.recommended_classifieds),
    path('get_brands_by_subcategory/', classified.get_brands_by_subcategory),
    path('filtering_classifieds/', classified.filtering_classifieds),
    path('total_count_classifieds/', classified.total_count_classifieds),
    path('near_classified_ads/', classified.near_classified_ads),
    path('get_my_business_classifieds/', classified.get_my_business_classifieds),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
