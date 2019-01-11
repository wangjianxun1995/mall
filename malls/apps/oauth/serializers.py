from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser
from oauth.unitls import check_access_token
from users.models import User


class OAuthQQUserSerializer(serializers.Serializer):
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')


    def validate(self, attrs):
        access_token = attrs.get('access_token')
        openid = check_access_token(access_token)
        if openid is None:
            raise serializers.ValidationError('openid不存在')

        attrs['openid']=openid

        # 对短信验证码进行校验
        # 2.1 获取用户提交的
        mobile = attrs.get('mobile')
        sms_code = attrs['sms_code']
        # 2.2 获取 redis
        redis_conn = get_redis_connection('code')

        redis_code = redis_conn.get('sms_' + mobile)

        if redis_code is None:
            raise serializers.ValidationError('短信验证码已过期')

        # 最好删除短信
        redis_conn.delete('sms_' + mobile)
        # 2.3 比对
        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('验证码不一致')
        #对手机号进行校验
        try:
            user = User.objects.get(mobile =mobile)
        except User.DoesNotExist:
            pass
        else:
            # 说明注册过
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码不正确')
            attrs['user'] = user

        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        if user is None:
            #创建user
            user = User.objects.create(
                mobile=validated_data.get('mobile'),
                username=validated_data.get('mobile'),
                password=validated_data.get('password')
            )
            user.set_password(validated_data['password'])
            user.save()

        qquser = OAuthQQUser.objects.create(
            user=user,
            openid=validated_data.get('openid'),
        )
        return qquser