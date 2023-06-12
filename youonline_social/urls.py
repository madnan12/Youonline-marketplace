from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('youonline_social_app.urls')),
    path('api/', include('community_app.urls')),
    path('api/', include('video_app.urls')),
    path('api/', include('property_app.urls')),
    path('api/', include('automotive_app.urls')),
    path('api/', include('classified_app.urls')),
    path('api/', include('job_app.urls')),
    path('api/chat/', include('chat_app.urls')),
    path('api/ecommerce/', include('ecommerce_app.urls')),
    path('admin_panel/', include('admin_panel.urls')),
    path('api/', include('blog_app.urls')),
    path('api/api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

handler404 = 'admin_panel.custom_error_handler.error_404'
handler500 = 'admin_panel.custom_error_handler.error_500'
handler403 = 'admin_panel.custom_error_handler.error_403'


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

