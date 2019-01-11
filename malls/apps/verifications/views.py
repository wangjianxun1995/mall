import random

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.views import APIView

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from verifications.serializers import RegisSmsSerializers


class RegisterImageCodeAPIView(APIView):
    def get(self,request,image_code_id):
        """
        通过第三方库，生成图片验证码，我们需要对验证码进行redis保存

        创建图片和验证码
        通过redis 进行保存验证码需要在设置中添加 验证码数据库选项将图片返回

        """
        # 创建图片和验证码
        text,image = captcha.generate_captcha()
        #通过redis进行保存验证码
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'%image_code_id,60,text)

        # 将图片返回
        #注意，图片是 二进制，我们通过HttpResponse返回
        return HttpResponse(image,content_type='image/jpeg')

class RegisterSmsCodeAPIView(APIView):

    def get(self,request,mobile):

        # 接收参数
        params = request.query_params
        # 校验参数 需要验证码 用户输入 的图片验证码和redis的保存是否一致
        serializer = RegisSmsSerializers(data=params)
        serializer.is_valid(raise_exception=True)
        #生成短信验证码
        sms_code ='%06d'%random.randint(0,999999)
        # 将短信保存在redis中
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_'+mobile,5*60,sms_code)
        # 使用云通讯发送短信
        # CCP.send_template_sms(mobile,[sms_code,5],1)
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code)

        # 返回相应
        return HttpResponse({'msg':'ok'})