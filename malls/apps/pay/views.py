from django.shortcuts import render

# Create your views here.
"""
1.第一步：创建应用（appid）
2.第二步：配置密钥（一共两对，我们的服务器一对，支付宝的一对）
3.第三步：搭配和配置从开发环境（下载/安装 SDK）(SDK 就是 支付宝封装好的库)
    pip install python-alipay-sdk --upgrade
4.第四步：接口调用（开发，看支付宝的API（接口文档））
商家帐号runvmo3496@sandbox.com
买家帐号xflosy4381@sandbox.com
登录密码 111111

"""
"""
 该接口必须是登录用户
1.接收订单id
2.根据订单id查询订单
3.生成alipay实例对象
4.调用支付接口
5.拼接url
6.返回url

请求方式： GET/orders/(?P<order_id>\d+)/payment/
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from orders.models import OrderInfo
from rest_framework import status
from alipay import AliPay
from malls import settings

# Create your views here.

class PaymentView(APIView):
    """
    支付
    GET /pay/orders/(?P<order_id>)\d+/

    必须登录

    思路:
    判断订单是否正确
    创建支付对象
    调用支付对象生成 order_string
    构造支付地址
    返回响应
    """

    def get(self,request,order_id):
        user = request.user
        # 判断订单是否正确
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message':'订单信息有误'},status=status.HTTP_400_BAD_REQUEST)
        # 创建支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None, # 默认回调url
            app_private_key_path=settings.APP_PRIVATE_KEY_PATH,
            alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,
            sign_type='RSA2', # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG
        )
        # 调用支付对象生成order_string

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            # 将浮点数(decimal)转换为字符串
            total_amount=str(order.total_amount),
            subject='测试订单',
            return_url='http://www.meiduo.site:8080/pay_success.html',
        )
        # 构造支付地址
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        # 返回响应
        return Response({'alipay_url':alipay_url})