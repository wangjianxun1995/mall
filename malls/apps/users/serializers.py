import re
from rest_framework import serializers

from malls import settings
from users.models import User, Address
from django_redis import get_redis_connection

from users.untils import generic_verify_url


class RegiserUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='校验密码',allow_blank=False,allow_null=False,write_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True,max_length=6,min_length=6,allow_null=False,allow_blank=False)
    allow = serializers.CharField(label='是否同意协议',allow_blank=False,allow_null=False,write_only=True)

    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段
    class Meta:
        model = User
        fields = ['token','mobile','password','password2','username','allow','sms_code']

    #单个字段
    #手机号的验证
    def validate_mobile(self, value):
        if not re.match(r'1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号不符合规则')
        return value
    # 勾选协议的验证
    def validate_allow(self, value):
        if value !='true':
            raise serializers.ValidationError('协议未勾选')
        return value
    #多个字段
    #密码验证
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password')
        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        #短信
        #2.1 获取用户提交的验证码
        mobile = attrs.get('mobile')
        sms_code = attrs['sms_code']
        #2.2 获取redis中的验证码
        redis_conn = get_redis_connection('code')
        redis_text = redis_conn.get('sms_'+mobile)
        if redis_text is None:
            raise serializers.ValidationError('验证码失效')
        redis_conn.delete('sms_'+mobile)

        if redis_text.decode() != sms_code:
            raise serializers.ValidationError('验证码不一致')

        return attrs

    def create(self, validated_data):
        del validated_data['sms_code']
        del validated_data['allow']
        del validated_data['password2']

        user = User.objects.create(**validated_data)

        user.set_password(validated_data['password'])
        user.save()


        from rest_framework_jwt.settings import api_settings

        # 4.1 需要使用 jwt的2个方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        #4.2 让payload（载荷）放一些用户的信息
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user


class UserCenterInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email','email_active')

class UserEmaileInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        # 先把数据更新
        email = validated_data.get('email')

        instance.email = email
        instance.save

        # 在发送 邮件
        from django.core.mail import send_mail
        """
        subject, 主题
        message, 内容
        from_email, 谁发送的
        recipient_list, 收件人列表
        html_message=None  html 文件的格式

        """
        subject = '美多商城激活邮件'
        message ='内容'
        from_email =settings.EMAIL_FROM
        recipient_list=[email]
        verify_url= generic_verify_url(instance.id)
        # html_message = '<h1>叫爸爸 不打你！</h1>'
        # html_message = '<p>尊敬的用户您好！</p>' \
        #            '<p>感谢您使用美多商城。</p>' \
        #            '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #            '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message)
        from celery_tasks.mail.tasks import send_celery_email
        send_celery_email.delay(email,
                  verify_url,
                  subject,
                  message,
                  from_email,
                  recipient_list)
        return instance
class AddressSerializer(serializers.ModelSerializer):

    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')


    def create(self, validated_data):

        validated_data['user'] = self.context['request'].user

        # return Address.objects.create(**validated_data)
        return super().create(validated_data)