from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter

from goods.models import SKU
from goods.serializers import HotSKUListSerialiezer

"""
列表数据
一个是热销数据
列表数据

热销数据：应该是到哪个分类 获取哪个分类的数据

1.获取分类信息id
2.根据id 获取数据 [sku,sku,sku]
3.需要将数据转换为json/字典数据
4.返回响应

GET /goods/categories/(?P<category_id>\d+)/hotskus/
"""
from rest_framework.generics import ListAPIView
class HotSKUListAPIView(ListAPIView):
    pagination_class = None
    def get_queryset(self):
        category_id=self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id).order_by('-sales')[0:2]
    serializer_class = HotSKUListSerialiezer

from rest_framework.generics import ListAPIView
class SKUListView(ListAPIView):
    serializer_class = HotSKUListSerialiezer


    # 排序
    filter_backends = [OrderingFilter]

    ordering_fields = ('create_time','price','sales')

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id)

from .serializers import SKUIndexSerializer
from drf_haystack.viewsets import HaystackViewSet

class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer


