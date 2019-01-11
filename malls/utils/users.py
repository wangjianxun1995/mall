import re

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    #token,   jwt 生成的token
    # user=None,  jwt 验证成功之后的user
    # request=None  请求
    return {
        'token': token,
        'user_id':user.id,
        'username':user.username
    }

def get_user_by_account(username):
    try:
        if re.match(r'1[3-9]\d{9}', username):
            # 手机号
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    return user
from django.contrib.auth.backends import ModelBackend


class UsernameMobleModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # try:
        #     if re.match(r'1[3-9]\d{9}',username):
        #         user = User.objects.get(mobile=username)
        #     else:
        #         user= User.objects.get(username=username)
        # except User.DoesNotExist:
        #     user=None
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
        return None
