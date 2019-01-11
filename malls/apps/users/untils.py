from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from malls import settings

def generic_verify_url(user_id):
    #1.创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    #2.组织数据
    data = {
        'id':user_id
    }
    #3.对数据进行加密
    token = s.dumps(data)
    #4.拼接url


    return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()