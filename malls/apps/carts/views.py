from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
import pickle
import base64
from carts.serializers import CartSerializer
from django_redis import get_redis_connection

class CartView(APIView):

    def perform_authentication(self, request):
        pass
    #post方法 添加购物车
    def post(self,request):

        # 添加购物车按钮的业务逻辑是：
        # 用户点击 添加购物车 按钮的时候 前端需要收集数据 商品id 个数 选中状态default=True
        #
        # 1.接受数据
        data = request.data
        # 2.校验数据(商品是否存在，商品的个数是否充足)
        serializer = CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取校验之后的数据
        sku_id =serializer.validated_data.get('sku_id')
        count =serializer.validated_data.get('count')
        selected =serializer.validated_data.get('selected')
        # 4.获取用户信息
        try:
            user = request.user
        except Exception as e:
            user=None
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:
            # 5.根据用户的信息进行判断是否登录
            # 6.登录用户保存在redis中
            #     6.1 链接redis
            redis_conn = get_redis_connection('cart')
            #     6.2  将数据保存在redis中的hash和set 中
            redis_conn.hset('cart_%s'%user.id,count,sku_id)
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            #     6.3返回响应
            return Response(serializer.data)
        else:
            # 7.未登录用户保存在cookie中
            #     7.1 获取cookie数据
            cart_str = request.COOKIES.get('cart')
            #     7.2判断是否存在cookie数据
            if cart_str is not None:
                #说明有数据
                #对base类型进行解码
                decode = base64.b64decode(cart_str)
                #对bytes类型进行解码转换为字典
                cookie_cart = pickle.loads(decode)
            else:
                #说明没有数据
                cookie_cart={}
            #     7.3 如果添加的购物车商品id 存在则进行商品数量的累加
            if sku_id in cookie_cart:
                #存在
                orgin_cart = cookie_cart[sku_id]['count']
                count += orgin_cart
            cookie_cart[sku_id]={
                'count':count,
                'selected':selected
            }
            #对字典数据进行处理
            # 7.5.1将字典转换为bytes类型,pickle
            dumps = pickle.loads(cookie_cart)
            # 7.5.2 将pickle二进制类进行,base64编码
            encode = base64.b64encode(dumps)
            # 7.5.3 将base64的bytes 类型转换为str
            value = encode.decode()
            #     7.3 如果添加的购物车商品id 不存在则直接添加商品信息
            #     7.5 返回响应
            response = Response(serializer.data)
            response.set_cookie('cart',value)
            return response