from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import RegiserUserSerializer, UserCenterInfoSerializer, UserEmaileInfoSerializer
from users.untils import check_token


class RegisterUsernameCountAPIView(APIView):
    def get(self,request,username):
        #通过模型查询，获取用户名的个数
        count = User.objects.filter(username=username).count()
        #组织数据
        context = {
            'count':count,
            'username':username
        }
        return Response(context)

class RegisterPhoneCountAPIView(APIView):
    def get(self,request,mobile):
        # 通过模型查询获取手机号个数
        count = User.objects.filter(mobile=mobile).count()
        #组织 数据
        context = {
            'count':count,
            'phone':mobile
        }
        return Response(context)

class RegiserUserAPIView(APIView):
    def post(self,request):
        #1.接收参数
        data = request.data
        #校验参数
        serializer = RegiserUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        #数据入库
        serializer.save()
        #返回响应
        return Response(serializer.data)

"""
个人中心的信息展示
必须是登录用户才可以访问
1.让前端传递用户信息
2.我们根据用户的信息来获取user
3.将对象转换为字典数据

GET   /user/infos/

"""
from rest_framework.permissions import IsAuthenticated
class UserCenterInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 必须认证才可以获取用户信息

    def get(self,request):
        #1.获取用户信息
        user = request.user
        #2.将模型转换为字典（json）
        serializer = UserCenterInfoSerializer(user)
        # 3. 返回响应
        return Response(serializer.data)
# from rest_framework.generics import RetrieveAPIView
# from rest_framework.permissions import IsAuthenticated
# from .serializers import UserCenterInfoSerializer
# class UserCenterInfoAPIView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]
#
#     serializer_class = UserCenterInfoSerializer
#
#       #已经有的父类 无法满足我们的需求 我们从写
#     def get_object(self):
#         return self.request.user


'''
当用户 输入邮箱之后，点击保存的时候，
1.我们需要将 邮箱内容发送给后端，后端需要更新制定用户的email字段
2.同时后端需要给这个邮箱发送一个激活链接
3.当用户点击激活链接的时候改变布尔值email_active状态

'''
# class UserEmaileInfoAPIView(APIView):
#
#     permission_classes = [IsAuthenticated]
#     def put(self,request):
#         #1.接受数据
#         data = request.data
#         #2.校验
#         serializer = UserEmaileInfoSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         #3.更新数据
#         serializer.save()
#         #4.返回响应
#         return Response(serializer.data)

from rest_framework.generics import UpdateAPIView

class UserEmaileInfoAPIView(UpdateAPIView):
    #必须认证登录信息
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmaileInfoSerializer
    #从写父类的get_objects方法

    def get_object(self):
        return self.request.user

'''
激活需求：
    当用户点击激活链接的时候，需要让前端接受到 token信息
    然后让前端发送 一个请求 包含token信息

1.接受token信息
2.对token进行解析
3.解析获取user_id 之后 进行查询
4.修改状态
5.返回响应

GET   /users/emails/verification/

'''
class UserEMailVerificationAPIView(APIView):
    def get(self,request):

        # 1.接受token信息
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2.对token进行解析
        user_id = check_token(token)
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3.解析获取user_id 之后 进行查询
        user = User.objects.get(pk=user_id)
        # 4.修改状态
        user.email_active=True
        user.save()
        # 5.返回响应
        return Response({'msg':'OK'})

