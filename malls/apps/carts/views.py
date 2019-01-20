from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
import pickle
import base64
from carts.serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer
from django_redis import get_redis_connection

from goods.models import SKU
from rest_framework import status

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
            redis_conn.hincrby('cart_%s'%user.id,sku_id,count)
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
            dumps =pickle.dumps(cookie_cart)
            # 7.5.2 将pickle二进制类进行,base64编码
            encode = base64.b64encode(dumps)
            # 7.5.3 将base64的bytes 类型转换为str
            value = encode.decode()
            #     7.3 如果添加的购物车商品id 不存在则直接添加商品信息
            #     7.5 返回响应
            response = Response(serializer.data)
            response.set_cookie('cart',value)
            return response

    def get(self, request):
        """
             当用户点击购物车列表的时候,前端需要发送一个get请求

             get请求的数据 需要将用户信息传递过来

             1.接收用户信息
             2.根据用户信息进行判断
             3.登陆用户从redis中获取数据
                 3.1 连接redis
                 3.2 hash        cart_userid:            {sku_id:count}
                     set         cart_selected_userid:   sku_id
                     获取hash的所有数据
                     [sku_id,sku_id]
                 3.3 根据商品id,获取商品的详细信息
                 3.4 返回相应
             4.未登陆用户从cookie中获取数据
                 4.1 先从cookie中获取数据
                 4.2 判断是否存在购物车数据
                     {sku_id:{count:xxx,selected:xxxx}}

                     [sku_id,sku_id]
                 4.3 根据商品id,获取商品的详细信息
                 4.4 返回相应


             # 1.接收用户信息
             # 2.根据用户信息进行判断
             # 3.登陆用户从redis中获取数据
             #     3.1 连接redis
             #     3.2 hash        cart_userid:            {sku_id:count}
             #         set         cart_selected_userid:   sku_id
             #         获取hash的所有数据
             #         [sku_id,sku_id]
             # 4.未登陆用户从cookie中获取数据
             #     4.1 先从cookie中获取数据
             #     4.2 判断是否存在购物车数据
             #         {sku_id:{count:xxx,selected:xxxx}}
             #
             #         [sku_id,sku_id]
             # 5 根据商品id,获取商品的详细信息
             # 6 返回相应
             """
        # 1.接收用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 2.根据用户信息进行判断
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:
            # 3.登陆用户从redis中获取数据
            #     3.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     3.2 hash        cart_userid:            {sku_id:count}
            #         set         cart_selected_userid:   sku_id
            #         获取hash的所有数据
            redis_sku_ids = redis_conn.hgetall('cart_%s' % user.id)
            #         [sku_id,sku_id]
            #         获取set数据
            redis_selected = redis_conn.smembers('cart_selected_%s'%user.id)
            cookie_cart={}
            for sku_id,count in redis_sku_ids.items():
                cookie_cart[int(sku_id)]={
                    'count':int(count),
                    'selected':sku_id in redis_selected
                }
        else:
            # 4.未登陆用户从cookie中获取数据
            #     4.1 先从cookie中获取数据
            cart_str = request.COOKIES.get('cart')
            #     4.2 判断是否存在购物车数据
            if cart_str is not None:
                #         {sku_id:{count:xxx,selected:xxxx}}
                # 有数据
                # 因为是base64所以进行解码,在转换为字典
                cookie_cart = pickle.loads(base64.b64decode(cart_str))
            else:
                cookie_cart = {}
                #         [sku_id,sku_id]
        # 5 根据商品id,获取商品的详细信息
        ids = cookie_cart.keys()
        #[1,2,3,4]
        #[sku,sku,sku]
        skus = SKU.objects.filter(pk__in=ids)
        # 对商品列表数据进行遍历，来动态的添加count和选中状态
        for sku in skus:
            sku.count = cookie_cart[sku.id]['count']
            sku.selected = cookie_cart[sku.id]['selected']
        # 6 返回相应
        serializer = CartSKUSerializer(skus,many=True)
        return Response(serializer.data)

    def put(self,request):
        data = request.data
        serializer = CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data['sku_id']
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        try:
            user = request.user
        except Exception as e:
            user = None
            # request.user.is_authenticated
        if user is not None and user.is_authenticated:
            #登录用户从redis获取数据
            redis_conn = get_redis_connection('cart')
            #管道 提升程序运行效率
            # pl = redis_conn.pipeline()
            # #更新数据
            # pl.hset('cart_%s'%user.id,sku_id,count)
            # if selected:
            #     pl.srem('cart_selected_%s'%user.id,sku_id)
            # else:
            #     pl.srem('cart_selected_%s'%user.id,sku_id)
            # pl.execute()
            #更新数据 hash
            redis_conn.hset('cart_%s'%user.id,sku_id,count)
            #set
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            else:
                redis_conn.srem('cart_selected_%s'%user.id,sku_id)

            return Response(serializer.data)
        else:
            #未登录用户cookie中获取数据
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                cart = pickle.loads(base64.b64decode(cart_str))
            else:
                cart = {}
            if sku_id in cart:
                cart[sku_id]={
                    'count':count,
                    'selected':selected
                }
            cookie_str = base64.b64encode(pickle.dumps(cart)).decode()

            response = Response(serializer.data)
            response.set_cookie('cart',cookie_str)

            return response
    def delete(self,request):
        """
               前端需要将商品id,count(个数 是采用的将最终数量提交给后端),selected提交给后端

               1.接收数据
               2.校验数据
               3.获取验证之后的数据
               4.获取用户信息
               5.根据用户的登陆状态进行判断
               6.登陆用户redis
                   6.1 连接redis
                   6.2 更新数据
                   6.3 返回相应
               7.未登录用户cookie
                   7.1 获取cookie数据
                   7.2 判断cart数据是否存在
                   7.3 更新数据
                   7.4 返回相应

               """
        # 1.接收数据
        data = request.data
        # 2.校验数据
        serializer =CartDeleteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.获取验证之后的数据
        sku_id = serializer.validated_data['sku_id']
        # 4.获取用户信息
        try:
            user = request.user
        except Exception as e:
            user = None
        # 5.根据用户的登陆状态进行判断
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:
            # 6.登陆用户redis
            #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     6.2 更新数据
            redis_conn.hdel('cart_%s'%user.id,sku_id)
            redis_conn.srem('cart_selected_%s'%user.id,sku_id)
            #     6.3 返回相应
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            # 7.未登录用户cookie
            #     7.1 获取cookie数据
            cookie_str = request.COOKIES.get('cart')
            #     7.2 判断cart数据是否存在
            if cookie_str is not None:
                cookie_cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cookie_cart={}
            #     7.3 删除数据
            if sku_id in cookie_cart:
                del cookie_cart[sku_id]
            #     7.4 返回相应
            response = Response(status=status.HTTP_204_NO_CONTENT)
            value = base64.b64encode(pickle.dumps(cookie_cart)).decode()
            response.set_cookie('cart',value)
            return response