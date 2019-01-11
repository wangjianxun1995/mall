from QQLoginTool.QQtool import OAuthQQ
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from malls import settings

# 获取code
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.unitls import generic_open_id


class OAuthQQURLAPIView(APIView):
    """
    提供QQ登录页面网址

    """
    def get(self, request):

        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        # state= request.query_params.get('state')
        # if not state:
        # state= '/'

        # 获取QQ登录页面网址
        # client_id=None,
        # client_secret=None,
        # redirect_uri=None,
        # state=None
        state='/'
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)
        login_url = oauth.get_qq_url()

        return Response({'auth_url':login_url})

from rest_framework import status
#获取token
class OAuthQQUserAPIView(APIView):
    def get(self,request):
        params = request.query_params
        code = params.get('code')
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        )
        token = oauth.get_access_token(code)
        #获取openid
        openid = oauth.get_open_id(token)
        try:
            # 根据openid 查询数据库
            qquser =OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #不存在
            # s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
            #
            # data = {
            #     'openid': openid
            # }
            #
            # token = s.dumps(data)
            token = generic_open_id(openid)
            return Response({'access_token':token})

        else:
            #存在  直接登录

            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(qquser.user)
            token = jwt_encode_handler(payload)
            return Response({
                'token':token,
                'username':qquser.user.username,
                'user_id':qquser.user.id,

            })


    def post(self,request):

        data = request.data

        serializer = OAuthQQUserSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        qquser = serializer.save()

        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(qquser.user)
        token = jwt_encode_handler(payload)
        return Response({
            'token': token,
            'username': qquser.user.username,
            'user_id': qquser.user.id,

        })


# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from malls import settings
# #secret_key,  秘钥
# # expires_in=None   过期时间 单位秒
# # 创建序列化器
# s =  Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
#
# data = {
#     'openid':'123456789'
# }
#
# token = s.dumps(data)
#
# s.loads(token)
