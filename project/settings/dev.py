from .base import *
import datetime
import os
from decouple import config
from corsheaders.defaults import default_headers 

DEBUG = True
# ALLOWED_HOSTS = ['192.168.1.44', 'localhost']
# CORS_ORIGIN_ALLOW_ALL = False

# CORS_ORIGIN_WHITELIST = (
#     'http://192.168.1.44:8000',
#     'http://localhost:3000'
# )

ALLOWED_HOSTS=['*']
CORS_ORIGIN_ALLOW_ALL = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'), 
        'USER': config('DB_USER'),  
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'), 
        'PORT': config('DB_PORT'),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')#os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')#os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    ),
}

AUTHENTICATION_BACKENDS = (
    # Google OAuth2
    'social_core.backends.google.GoogleOAuth2',
    
    'django.contrib.auth.backends.ModelBackend', # To keep the Browsable API
    'oauth2_provider.backends.OAuth2Backend',
)

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'}
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '286763141053-6obqmg3ql3jt90j4a1siu5qkrqk4jlaa.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

# Define SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE to get extra permissions from Google.
# SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
#     'https://www.googleapis.com/auth/userinfo.email',
#     'https://www.googleapis.com/auth/userinfo.profile',
# ]

# JWT_AUTH = {
#     'JWT_ENCODE_HANDLER':
#     'rest_framework_jwt.utils.jwt_encode_handler',

#     'JWT_DECODE_HANDLER':
#     'rest_framework_jwt.utils.jwt_decode_handler',

#     'JWT_PAYLOAD_HANDLER':
#     'rest_framework_jwt.utils.jwt_payload_handler',

#     'JWT_PAYLOAD_GET_USER_ID_HANDLER':
#     'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

#     'JWT_RESPONSE_PAYLOAD_HANDLER':
#     'rest_framework_jwt.utils.jwt_response_payload_handler',

#     'JWT_SECRET_KEY': SECRET_KEY,
#     'JWT_GET_USER_SECRET_KEY': None,
#     'JWT_PUBLIC_KEY': None,
#     'JWT_PRIVATE_KEY': None,
#     'JWT_ALGORITHM': 'HS256',
#     'JWT_VERIFY': True,
#     'JWT_VERIFY_EXPIRATION': True,
#     'JWT_LEEWAY': 0,
#     'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
#     'JWT_AUDIENCE': None,
#     'JWT_ISSUER': None,

#     'JWT_ALLOW_REFRESH': False,
#     'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

#     'JWT_AUTH_HEADER_PREFIX': 'JWT',
#     'JWT_AUTH_COOKIE': None,
# }

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=7),
    # 'ROTATE_REFRESH_TOKENS': False,
    # 'BLACKLIST_AFTER_ROTATION': False,
    # 'UPDATE_LAST_LOGIN': False,

    # 'ALGORITHM': 'HS256',
    # 'SIGNING_KEY': SECRET_KEY,
    # 'VERIFYING_KEY': None,
    # 'AUDIENCE': None,
    # 'ISSUER': None,
    # 'JWK_URL': None,
    # 'LEEWAY': 0,

    # 'AUTH_HEADER_TYPES': ('Bearer',),
    # 'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    # 'USER_ID_FIELD': 'id',
    # 'USER_ID_CLAIM': 'user_id',
    # 'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    # 'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    # 'TOKEN_TYPE_CLAIM': 'token_type',
    # 'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    # 'JTI_CLAIM': 'jti',

    # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # 'SLIDING_TOKEN_LIFETIME': datetime.timedelta(minutes=5),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': datetime.timedelta(days=1),
}