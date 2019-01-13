"""
Django settings for calls project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r4st3_4cyw3xgvw0pwz)-74*r0c7k8n)#e#4jp813ync4lmzpd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#让django找到 apps这个包
sys.path.insert(0,os.path.join(BASE_DIR,'apps'))

# CORS
CORS_ORIGIN_WHITELIST = (
    '127.0.0.1:8080',
    'localhost:8080',
    'www.meiduo.site:8080'
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie
#允许哪些主机访问
ALLOWED_HOSTS = ['127.0.0.1','api.meiduo.site']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'users.apps.UsersConfig',
    'corsheaders',
    'oauth.apps.OauthConfig',
    'areas.apps.AreasConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'malls.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'malls.wsgi.application'

REST_FRAMEWORK = {
    # 异常处理
    'EXCEPTION_HANDLER': 'utils.exceptions.exception_handler',
# 认证方式
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',  # 优先采用JWT认证
        'rest_framework.authentication.SessionAuthentication',           # 如果没有jwt则采用 sessison认证
        # 'rest_framework.authentication.BasicAuthentication',
    ),
}
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'root',  # 数据库用户名
        'PASSWORD': 'mysql',  # 数据库用户密码
        'NAME': 'shopping'  # 数据库名字

    }
}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    #Redis
    "code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }

}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "logs/meiduo.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],
            'propagate': True,
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'


TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'users.User'

import datetime
#设置JWT
JWT_AUTH = {

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'utils.users.jwt_response_payload_handler',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
}


#修改默认认证后端
AUTHENTICATION_BACKENDS = [
    'utils.users.UsernameMobleModelBackend',
]

# QQ登录参数
QQ_CLIENT_ID = '101474184'
QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#邮件服务器
EMAIL_HOST = 'smtp.163.com'
#smtp 默认端口号 25
EMAIL_PORT = 25
#发送邮件的邮箱
EMAIL_HOST_USER = '18846121015@163.com'
#在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = '123456abc'
#收件人看到的发件人
EMAIL_FROM = '美多商城<18846121015@163.com>'