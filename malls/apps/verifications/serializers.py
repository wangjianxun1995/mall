from rest_framework import serializers
from django_redis import get_redis_connection
class RegisSmsSerializers(serializers.Serializer):

    text = serializers.CharField(max_length=4,min_length=4,required=True)
    image_code_id = serializers.UUIDField(required=True)

    def validate(self, attrs):
        #1.获取用户提交的验证码
        text = attrs.get('text')
        #2.获取redis的验证码
        #2. 链接redis
        redis_conn = get_redis_connection('code')
        #2.获取数据
        image_code_id = attrs.get('image_code_id')
        redis_text =redis_conn.get('img_'+str(image_code_id))
        #2.3redis的数据有shixiao
        if redis_text is None:
            raise serializers.ValidationError('验证码已过期')
        # 比对
        if redis_text.decode().lower()!=text.lower():
            raise serializers.ValidationError('验证码不一致')
        return attrs