from django.urls import path
from job_app import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Company/Industry URLs
    path('get_all_industries/', views.get_all_industries),
    path('create_company/', views.create_company),
    path('get_all_companies/', views.get_all_companies),
    path('get_my_company/', views.get_my_company),
    path('update_company/', views.update_company),
    path('delete_company/', views.delete_company),
    
    # Job URLs
    path('create_job/', views.create_job),
    path('get_all_jobs/', views.get_all_jobs),
    path('get_single_job/', views.get_single_job),
    path('update_job/', views.update_job),
    path('delete_job/', views.delete_job),
    path('get_my_jobs/', views.get_my_jobs),
    path('add_favourite_job/', views.add_favourite_job),
    path('get_favorite_jobs/', views.get_favorite_jobs),
    path('get_recent_job/', views.get_recent_job),
    path('search_jobs/', views.search_jobs),
    path('apply_job/', views.apply_job),
    path('recommended_job/', views.recommended_job),
    path('get_apply_single_job/', views.get_apply_single_job),
    path('get_my_apply_on_jobs/', views.get_my_apply_on_jobs),
    path('similar_jobs/', views.similar_jobs),
    path('get_job_categories/', views.get_job_categories),
    path('get_job_by_category/', views.get_job_by_category),
    path('filtering_job/', views.filtering_job),
    path('total_count_jobs/', views.total_count_jobs),
    path('make_active_job/', views.make_active_job),
    path('get_featured_jobs/', views.get_featured_jobs),
    path('add_job_media/', views.add_job_media),
    path('upload_resume/', views.upload_resume),
    path('get_my_resume/', views.get_my_resume),
    path('delete_resume/', views.delete_resume),


    # Job Profile URLs
    path('create_job_profile/', views.create_job_profile),
    path('update_job_profile/', views.update_job_profile),
    path('update_jobprofile_skills/', views.update_jobprofile_skills),
    path('get_job_profile/', views.get_job_profile),

    
    # Project URLs
    path('create_job_project/', views.create_job_project),
    path('get_job_project/', views.get_job_project),
    path('get_single_job_project/', views.get_single_job_project),
    path('delete_job_project/', views.delete_job_project),
    path('update_job_project/', views.update_job_project),
    path('create_job_project_media/', views.create_job_project_media),
    path('create_job_project_media/', views.create_job_project_media),
    path('get_job_project_media/', views.get_job_project_media),
    path('delete_job_project_media/', views.delete_job_project_media),

    # Job Story URLs
    path('create_job_story/', views.create_job_story),
    path('delete_job_story/', views.delete_job_story),
    path('get_all_job_profile_stories/', views.get_all_job_profile_stories),
    
    # Job Notification URLs
    path('get_job_notification/', views.get_job_notification),
    path('get_skill/', views.get_skill),
    path('add_job_endoresements/', views.add_job_endoresements),
    path('get_job_endoresements/', views.get_job_endoresements),
    path('delete_job_endoresements/', views.delete_job_endoresements),
    path('get_job_search_history/', views.get_job_search_history),
    path('near_job_ads/', views.near_job_ads),
    path('get_my_business_jobs/', views.get_my_business_jobs),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
