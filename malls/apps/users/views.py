from django.shortcuts import render

# Create your views here.
from rest_framework import request
from rest_framework import status
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from users.serializers import AddressSerializer, AddUserBrowsingHistorySerializer, SKUSeriaLizer
from users.models import User, Address
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

from rest_framework.generics import UpdateAPIView, ListAPIView


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

"""
1.后端接受数据
2.对数据进行校验
3.数据入库
4.返回响应


"""

class UserAddressAPIView(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
#
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        #由于用户的地址有存在删除的状态，所以我们需要对数据进行筛选
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self,request,*args,**kwargs):
        #保存用户地址数据
        count = request.user.addresses.count()
        if count >=20:
            return Response({'message':'保存地址数量已达上限'},status=status.HTTP_400_BAD_REQUEST)

        return super().create(request,*args,**kwargs)
############################地址列表###############################
    def list(self,request,*args,**kwargs):
        # 获取用户地址列表
        #获取所有地址
        queryset = self.get_queryset()
        # 创建序列化器
        serializer = self.get_serializer(queryset,many=True)
        user = self.request.user
        return Response({
            'user_id':user.id,
            'default_address_id':user.default_address_id,
            'limit':20,
            'addresses':serializer.data
        })
############################删除###############################
    def destory(self,*args,**kwargs):

        address = self.get_object()
        address.is_deleted=True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
from rest_framework.decorators import action
from .serializers import AddressSerializer

#修改
@action(methods=['put'], detail=True)
def title(self, request, pk=None, address_id=None):
    """
    修改标题
    """
    address = self.get_object()
    serializer = AddressSerializer(instance=address, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

#修改默认值
@action(methods=['put'], detail=True)
def status(self, request, pk=None, address_id=None):
    """
    设置默认地址
    """
    address = self.get_object()
    request.user.default_address = address
    request.user.save()
    return Response({'message': 'OK'}, status=status.HTTP_200_OK)
# from rest_framework.generics import RetrieveUpdateDestroyAPIView
# from rest_framework.generics import CreateAPIView,ListAPIView,DestroyAPIView,UpdateAPIView
# # from rest_framework.generics import GenericAPIView
# class UserAddressAPIView(CreateAPIView,ListAPIView,DestroyAPIView,UpdateAPIView):
#
#     serializer_class = AddressSerializer
#     queryset = Address.objects.all()
#
#     queryset.delete([])
from rest_framework.generics import CreateAPIView
class UserBrowsingHistoryView(CreateAPIView):
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]
from django_redis import get_redis_connection
class UserBrowsingHistoryView(CreateAPIView):
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def get(self,request):
        #获取用户信息
        user_id = request.user.id
        #1.链接redis
        redis_conn = get_redis_connection('history')
        #2.获取redis数据[sku_id,sku_id]
        history_sku_id = redis_conn.lrange('history_%s'%user_id,0,4)
        #根据history_sku_id 查询商品
        skus_list=[]
        for sku_id in history_sku_id:
            sku=SKU.objects.get(pk=sku_id)
            skus_list.append(sku)
        #序列化
        serializer = SKUSeriaLizer(skus_list,many=True)
        return Response(serializer.data)
