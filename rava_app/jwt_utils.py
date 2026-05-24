import jwt
import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.urls import reverse

User = get_user_model()

def generate_tokens(user):
    """
    Generates an access token (1 hour) and a refresh token (7 days).
    """
    access_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }
    refresh_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow(),
        'type': 'refresh'
    }
    
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
    
    return access_token, refresh_token


def decode_token(token):
    """
    Decodes the JWT token. Returns payload if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class JWTAuthenticationMiddleware:
    """
    Middleware that reads the JWT access_token from cookies, validates it,
    and sets request.user. If access_token is expired but refresh_token is valid,
    we could theoretically refresh it here, but for simplicity we'll let the user
    be Anonymous and the view (or frontend) can hit the refresh endpoint.
    However, for a pure server-rendered app, silently refreshing is better.
    Let's implement silent refresh.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        
        request.user = AnonymousUser()
        request._new_tokens = None # Flag to tell response to set new cookies

        if access_token:
            payload = decode_token(access_token)
            if payload and payload.get('type') == 'access':
                try:
                    request.user = User.objects.get(id=payload['user_id'])
                except User.DoesNotExist:
                    pass
            elif refresh_token:
                # Access token is invalid/expired, try refresh
                refresh_payload = decode_token(refresh_token)
                if refresh_payload and refresh_payload.get('type') == 'refresh':
                    try:
                        user = User.objects.get(id=refresh_payload['user_id'])
                        request.user = user
                        # Generate new tokens to be set in response
                        request._new_tokens = generate_tokens(user)
                    except User.DoesNotExist:
                        pass
        elif refresh_token:
            # No access token but we have a refresh token
            refresh_payload = decode_token(refresh_token)
            if refresh_payload and refresh_payload.get('type') == 'refresh':
                try:
                    user = User.objects.get(id=refresh_payload['user_id'])
                    request.user = user
                    request._new_tokens = generate_tokens(user)
                except User.DoesNotExist:
                    pass

        response = self.get_response(request)

        # If we silently refreshed tokens, set the new cookies on the response
        if getattr(request, '_new_tokens', None):
            new_access, new_refresh = request._new_tokens
            response.set_cookie(
                'access_token',
                new_access,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            response.set_cookie(
                'refresh_token',
                new_refresh,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            
        return response
