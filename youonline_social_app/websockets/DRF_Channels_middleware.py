from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async



@database_sync_to_async
def get_user(token_key):
    try:
        user = Token.objects.get(key=token_key).user
        return user
    except:
        return AnonymousUser()

class TokenAuthMiddleware:
    
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token = None
        if len(scope['query_string']) > 0:
            queries = (scope['query_string']).decode('utf-8').split('&')
            all_queries = {}
            for query in queries:
                sp_query = query.split('=')
                all_queries[sp_query[0]] = sp_query[1]

            try:
                token = all_queries['token']
            except:
                token = None

        if token is not None:
            scope['user'] = await get_user(token)
        else:
            scope['user'] = AnonymousUser()

        # headers = dict(scope['headers'])
        # if b'authorization' in headers:
        #     try:
        #         token_name, token_key = headers[b'authorization'].decode().split()
        #         if token_name == 'Token':
        #             scope['user'] = await get_user(token_key)
        #     except Token.DoesNotExist:
        #         scope['user'] = AnonymousUser()
        return await self.inner(scope, receive, send)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))