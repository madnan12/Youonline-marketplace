
from unicodedata import name
from django.urls import path
from admin_panel import views
from django.contrib.auth import views as auth_views
from admin_panel.sitemaps import ClassifiedsViewMap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'classifieds':ClassifiedsViewMap,
}


urlpatterns =[
    # Home URL
    path('', views.admin_panel_home, name="admin_panel_home"),
    path('admin_panel_login/', views.admin_panel_login, name='admin_panel_login'),
    path('admin_panel_profile/', views.admin_panel_profile, name='admin_panel_profile'),
    path('admin_panel_logout/', views.admin_panel_logout, name='admin_panel_logout'),
    path('admin_panel_update_profile/', views.admin_panel_update_profile, name='admin_panel_update_profile'),

    # Users URL
    path('admin_panel_view_users/', views.admin_panel_view_users, name="admin_panel_view_users"),
    path('admin_panel_search_user/', views.admin_panel_search_user, name='admin_panel_search_user'),
    path('admin_panel_delete_user/',views.admin_panel_delete_user, name='admin_panel_delete_user'),
    path('admin_panel_view_active_user/', views.admin_panel_view_active_user, name="admin_panel_view_active_user"),
    path('admin_panel_search_active_user/', views.admin_panel_search_active_user, name="admin_panel_search_active_user"),
    path('admin_panel_delete_active_user/', views.admin_panel_delete_active_user, name="admin_panel_delete_active_user"),
    path('admin_panel_view_inactive_user/', views.admin_panel_view_inactive_user, name="admin_panel_view_inactive_user"),
    path('admin_panel_search_inactive_user/', views.admin_panel_search_inactive_user, name="admin_panel_search_inactive_user"),
    path('admin_panel_block_user/', views.admin_panel_block_user, name="admin_panel_block_user"),
    path('admin_panel_view_album/', views.admin_panel_view_album, name='admin_panel_view_album'),
    path('admin_panel_search_album/', views.admin_panel_search_album, name='admin_panel_search_album'),
    path('admin_panel_delete_album/', views.admin_panel_delete_album, name='admin_panel_delete_album'),

    # Group URL
    path('admin_panel_view_groups/', views.admin_panel_view_groups, name="admin_panel_view_groups"),
    path('admin_panel_search_group/', views.admin_panel_search_group, name="admin_panel_search_group"),
    path('admin_panel_delete_group/',views.admin_panel_delete_group, name='admin_panel_delete_group'),
    path('admin_panel_view_unpromote_group/', views.admin_panel_view_unpromote_group, name="admin_panel_view_unpromote_group"),
    path('admin_panel_promote_group/', views.admin_panel_promote_group, name="admin_panel_promote_group"),
    path('admin_panel_search_unpromote_group/', views.admin_panel_search_unpromote_group, name="admin_panel_search_unpromote_group"),
    path('admin_panel_view_promote_group/', views.admin_panel_view_promote_group, name="admin_panel_view_promote_group"),
    path('admin_panel_search_promote_group/', views.admin_panel_search_promote_group, name="admin_panel_search_promote_group"),
    path('admin_panel_delete_promoted_group/', views.admin_panel_delete_promoted_group, name="admin_panel_delete_promoted_group"),

    # Page URL
    path('admin_panel_view_pages/', views.admin_panel_view_pages, name="admin_panel_view_pages"),
    path('admin_panel_search_page/', views.admin_panel_search_page, name="admin_panel_search_page"),
    path('admin_panel_delete_page/',views.admin_panel_delete_page, name='admin_panel_delete_page'),
    path('admin_panel_view_unpromote_page/', views.admin_panel_view_unpromote_page, name="admin_panel_view_unpromote_page"),
    path('admin_panel_search_unpromote_page/', views.admin_panel_search_unpromote_page, name="admin_panel_search_unpromote_page"),
    path('admin_panel_promote_page/', views.admin_panel_promote_page, name="admin_panel_promote_page"),
    path('admin_panel_view_promote_page/', views.admin_panel_view_promote_page, name="admin_panel_view_promote_page"),
    path('admin_panel_search_promote_page/', views.admin_panel_search_promote_page, name="admin_panel_search_promote_page"),
    path('admin_panel_delete_promoted_page/', views.admin_panel_delete_promoted_page, name="admin_panel_delete_promoted_page"),

    # Propety URL
    path('admin_panel_view_properties/', views.admin_panel_view_properties, name="admin_panel_view_properties"),
    path('admin_panel_search_property/', views.admin_panel_search_property, name="admin_panel_search_property"),
    path('admin_panel_view_unpromote_properties/', views.admin_panel_view_unpromote_properties, name="admin_panel_view_unpromote_properties"),
    path('admin_panel_search_unpromote_property/', views.admin_panel_search_unpromote_property, name="admin_panel_search_unpromote_property"),
    path('admin_panel_promote_property/', views.admin_panel_promote_property, name="admin_panel_promote_property"),
    path('admin_panel_view_promote_properties/', views.admin_panel_view_promote_properties, name="admin_panel_view_promote_properties"),
    path('admin_panel_search_promote_property/', views.admin_panel_search_promote_property, name="admin_panel_search_promote_property"),
    path('admin_panel_delete_promote_property/', views.admin_panel_delete_promote_property, name="admin_panel_delete_promote_property"),
    path('admin_panel_view_pending_properties/', views.admin_panel_view_pending_properties, name="admin_panel_view_pending_properties"),
    path('admin_panel_accept_pending_property/', views.admin_panel_accept_pending_property, name="admin_panel_accept_pending_property"),
    path('admin_panel_reject_pending_property/', views.admin_panel_reject_pending_property, name="admin_panel_reject_pending_property"),
    path('admin_panel_search_pending_property/', views.admin_panel_search_pending_property, name="admin_panel_search_pending_property"),
    path('admin_panel_delete_property/',views.admin_panel_delete_property, name='admin_panel_delete_property'),

    # Automotive URL
    path('admin_panel_view_automotives/',views.admin_panel_view_automotives, name='admin_panel_view_automotives'),
    path('admin_panel_search_automotive/', views.admin_panel_search_automotive, name="admin_panel_search_automotive"),
    path('admin_panel_view_pending_automotives/', views.admin_panel_view_pending_automotives, name="admin_panel_view_pending_automotives"),
    path('admin_panel_accept_pending_automotive/', views.admin_panel_accept_pending_automotive, name="admin_panel_accept_pending_automotive"),
    path('admin_panel_reject_pending_automotive/', views.admin_panel_reject_pending_automotive, name="admin_panel_reject_pending_automotive"),
    path('admin_panel_search_pending_automotive/', views.admin_panel_search_pending_automotive, name="admin_panel_search_pending_automotive"),
    path('admin_panel_delete_automotive/', views.admin_panel_delete_automotive, name="admin_panel_delete_automotive"),
    path('admin_panel_view_unpromoted_automotives/', views.admin_panel_view_unpromoted_automotives, name="admin_panel_view_unpromoted_automotives"),
    path('admin_panel_search_unpromote_automotive/', views.admin_panel_search_unpromote_automotive, name="admin_panel_search_unpromote_automotive"),
    path('admin_panel_promote_automotive/', views.admin_panel_promote_automotive, name="admin_panel_promote_automotive"),
    path('admin_panel_view_promoted_automotives/', views.admin_panel_view_promoted_automotives, name="admin_panel_view_promoted_automotives"),
    path('admin_panel_search_promote_automotive/', views.admin_panel_search_promote_automotive, name="admin_panel_search_promote_automotive"),
    path('admin_panel_delete_promote_automotive/', views.admin_panel_delete_promote_automotive, name="admin_panel_delete_promote_automotive"),

    # Classified URL
    path('admin_panel_view_classified/', views.admin_panel_view_classified, name="admin_panel_view_classified"),
    path('admin_panel_search_classified/', views.admin_panel_search_classified, name="admin_panel_search_classified"),
    path('admin_panel_delete_classified/', views.admin_panel_delete_classified, name="admin_panel_delete_classified"),
    path('admin_panel_view_pending_classified/', views.admin_panel_view_pending_classified, name="admin_panel_view_pending_classified"),
    path('admin_panel_search_pending_classified/', views.admin_panel_search_pending_classified, name="admin_panel_search_pending_classified"),
    path('admin_panel_accept_pending_classified/', views.admin_panel_accept_pending_classified, name="admin_panel_accept_pending_classified"),
    path('admin_panel_reject_pending_classified/', views.admin_panel_reject_pending_classified, name="admin_panel_reject_pending_classified"),
    path('admin_panel_view_unpromote_classified/', views.admin_panel_view_unpromote_classified, name="admin_panel_view_unpromote_classified"),
    path('admin_panel_search_unpromote_classified/', views.admin_panel_search_unpromote_classified, name="admin_panel_search_unpromote_classified"),
    path('admin_panel_promote_classified/', views.admin_panel_promote_classified, name="admin_panel_promote_classified"),
    path('admin_panel_view_promote_classified/', views.admin_panel_view_promote_classified, name="admin_panel_view_promote_classified"),
    path('admin_panel_delete_promote_classified/', views.admin_panel_delete_promote_classified, name="admin_panel_delete_promote_classified"),
    path('admin_panel_search_promote_classified/', views.admin_panel_search_promote_classified, name="admin_panel_search_promote_classified"),

    # User Post URL
    path('admin_panel_view_user_post/', views.admin_panel_view_user_post, name="admin_panel_view_user_post"),
    path('admin_panel_search_user_post/', views.admin_panel_search_user_post, name="admin_panel_search_user_post"),
    path('admin_panel_delete_user_post/', views.admin_panel_delete_user_post, name="admin_panel_delete_user_post"),
    path('admin_panel_view_single_user_all_post/<str:id>/', views.admin_panel_view_single_user_all_post, name="admin_panel_view_single_user_all_post"),
    path('admin_panel_delete_single_user_post/', views.admin_panel_delete_single_user_post, name="admin_panel_delete_single_user_post"),
    
    # Group Post URL
    path('admin_panel_view_group_post/<str:id>/', views.admin_panel_view_group_post, name="admin_panel_view_group_post"),
    path('admin_panel_delete_group_post/', views.admin_panel_delete_group_post, name="admin_panel_delete_group_post"),

    # Page Post URL
    path('admin_panel_view_page_post/<str:id>/', views.admin_panel_view_page_post, name="admin_panel_view_page_post"),
    path('admin_panel_search_page_post/', views.admin_panel_search_page_post, name="admin_panel_search_page_post"),
    path('admin_panel_delete_page_post/', views.admin_panel_delete_page_post, name="admin_panel_delete_page_post"),

    # Profile Story URL
    path('admin_panel_view_profile_story/', views.admin_panel_view_profile_story, name="admin_panel_view_profile_story"),
    path('admin_panel_single_profile_story/', views.admin_panel_single_profile_story, name="admin_panel_single_profile_story"),
    path('admin_panel_search_profile_story/', views.admin_panel_search_profile_story, name="admin_panel_search_profile_story"),
    path('admin_panel_delete_profile_story/', views.admin_panel_delete_profile_story, name="admin_panel_delete_profile_story"),

    # Video URL
    path('admin_panel_view_video/', views.admin_panel_view_video, name="admin_panel_view_video"),
    path('admin_panel_search_video/', views.admin_panel_search_video, name="admin_panel_search_video"),
    path('admin_panel_view_single_video/', views.admin_panel_view_single_video, name="admin_panel_view_single_video"),
    path('admin_panel_delete_video/', views.admin_panel_delete_video, name="admin_panel_delete_video"),

    # Channel URL
    path('admin_panel_view_video_channel/', views.admin_panel_view_video_channel, name="admin_panel_view_video_channel"),
    path('admin_panel_search_video_channel/', views.admin_panel_search_video_channel, name="admin_panel_search_video_channel"),
    path('admin_panel_delete_video_channel/', views.admin_panel_delete_video_channel, name="admin_panel_delete_video_channel"),

    # Job URL
    path('admin_panel_view_job/', views.admin_panel_view_job, name="admin_panel_view_job"),   
    path('admin_panel_search_job/', views.admin_panel_search_job, name="admin_panel_search_job"),
    path('admin_panel_delete_job/', views.admin_panel_delete_job, name="admin_panel_delete_job"),
    path('admin_panel_view_job_profile/', views.admin_panel_view_job_profile, name="admin_panel_view_job_profile"),
    path('admin_panel_search_job_profile/', views.admin_panel_search_job_profile, name="admin_panel_search_job_profile"),
    path('admin_panel_view_single_jobs_apply/<str:id>/', views.admin_panel_view_single_jobs_apply, name="admin_panel_view_single_jobs_apply"),
    path('admin_panel_delete_job_apply/', views.admin_panel_delete_job_apply, name="admin_panel_delete_job_apply"),
    path('admin_panel_delete_job_profile/', views.admin_panel_delete_job_profile, name="admin_panel_delete_job_profile"),

    # Blog URL
    path('admin_panel_view_blog/', views.admin_panel_view_blog, name="admin_panel_view_blog"),
    path('admin_panel_delete_blog/', views.admin_panel_delete_blog, name="admin_panel_delete_blog"),
    path('admin_panel_search_blog/', views.admin_panel_search_blog, name="admin_panel_search_blog"),
    path('admin_panel_view_unpromote_blog/', views.admin_panel_view_unpromote_blog, name="admin_panel_view_unpromote_blog"),
    path('admin_panel_search_unpromoted_blog/', views.admin_panel_search_unpromoted_blog, name="admin_panel_search_unpromoted_blog"),
    path('admin_panel_promote_blog/', views.admin_panel_promote_blog, name="admin_panel_promote_blog"),
    path('admin_panel_view_promote_blog/', views.admin_panel_view_promote_blog, name="admin_panel_view_promote_blog"),
    path('admin_panel_search_promoted_blog/', views.admin_panel_search_promoted_blog, name="admin_panel_search_promoted_blog"),

    # Business Directory URL
    path('admin_panel_view_business_directory/', views.admin_panel_view_business_directory, name='admin_panel_view_business_directory'),
    path('admin_panel_search_business_directory/', views.admin_panel_search_business_directory, name='admin_panel_search_business_directory'),
    path('admin_panel_delete_business_directory/', views.admin_panel_delete_business_directory, name='admin_panel_delete_business_directory'),
    path('admin_panel_view_pending_business_directory/', views.admin_panel_view_pending_business_directory, name='admin_panel_view_pending_business_directory'),
    path('admin_panel_search_pending_business_directory/', views.admin_panel_search_pending_business_directory, name='admin_panel_search_pending_business_directory'),
    path('admin_panel_accept_pending_business_directory/', views.admin_panel_accept_pending_business_directory, name='admin_panel_accept_pending_business_directory'),
    path('admin_panel_reject_pending_business_directory/', views.admin_panel_reject_pending_business_directory, name='admin_panel_reject_pending_business_directory'),

    path('admin_panel_view_unpromote_business_directory/', views.admin_panel_view_unpromote_business_directory, name='admin_panel_view_unpromote_business_directory'),
    path('admin_panel_search_unpromote_business_directory/', views.admin_panel_search_unpromote_business_directory, name='admin_panel_search_unpromote_business_directory'),
    path('admin_panel_promote_business_directory/', views.admin_panel_promote_business_directory, name='admin_panel_promote_business_directory'),
    path('admin_panel_view_promote_business_directory/', views.admin_panel_view_promote_business_directory, name='admin_panel_view_promote_business_directory'),
    path('admin_panel_search_promote_business_directory/', views.admin_panel_search_promote_business_directory, name='admin_panel_search_promote_business_directory'),
   
    # password reset/forget password URL
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('reset_password/',
    auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),name="reset_password"),
    path('reset_password_sent/', 
    auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"), 
    name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"), 
    name="password_reset_confirm"),
    path('reset_password_complete/', 
    auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"), 
    name="password_reset_complete"),

    # Site Map
    path('sitemap.xml', sitemap, {'sitemaps':sitemaps,}),
    path('admin_update_profile', views.admin_panel_update_profile, name="admin_update_profile"),
    path('admin_panel_update_profile_picture', views.admin_panel_update_profile_picture, name="admin_panel_update_profile_picture"),


]
