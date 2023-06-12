from django.urls import path
from blog_app import views

urlpatterns = [
    path('get_all_blog_categories/', views.get_all_blog_categories),
    path('create_blog/', views.create_blog),
    
    path('get_blogs/', views.get_blogs),
    path('get_all_blogs/', views.get_all_blogs),
    path('get_single_blog/', views.get_single_blog),
    path('search_blogs/', views.search_blogs),
    path('latest_blog/', views.latest_blog),
    path('get_my_blogs/', views.get_my_blogs),
    path('get_trending_blogs/', views.get_trending_blogs),
    path('blog_add_to_watched/', views.blog_add_to_watched),
    path('add_featured_blog/', views.add_featured_blog),
    path('get_featured_blogs/', views.get_featured_blogs),
    path('delete_blog/', views.delete_blog),
    path('update_blog/', views.update_blog),
    path('search_blog_by_category/', views.search_blog_by_category),
    path('apply_blog_author/', views.apply_blog_author),
    path('get_blog_author/', views.get_blog_author),



]
