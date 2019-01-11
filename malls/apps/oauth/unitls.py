from rest_framework.response import Response
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature

from malls import settings


def generic_open_id(openid):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

    data = {
        'openid': openid
    }

    token = s.dumps(data)

    return token.decode()

def check_access_token(access_token):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    try:
        data = s.loads(access_token)
    except BadSignature:
        return None
    return data['openid']