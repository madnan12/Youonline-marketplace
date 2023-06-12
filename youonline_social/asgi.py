
import os
import django

from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youonline_social.settings')

django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from youonline_social_app.websockets.DRF_Channels_middleware import TokenAuthMiddlewareStack


import youonline_social_app.websockets.routing

# application = get_asgi_application()


application = ProtocolTypeRouter({
    "http" : get_asgi_application(),
    "websocket" : TokenAuthMiddlewareStack(
        URLRouter(
            youonline_social_app.websockets.routing.websocket_urlpatterns 
        )
    )
})
