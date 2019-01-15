from fdfs_client.client import Fdfs_client
from django.utils.deconstruct import deconstructible
from django.core.files.storage import Storage
#您的存储类必须是可解构的， 以便在迁移中的字段上使用它时可以对其进行序列化。
# 只要您的字段具有可自行序列化的参数，就 可以使用
# django.utils.deconstruct.deconstructible类装饰器（这就是Django在FileSystemStorage上使用的）。

#1.您的自定义存储系统必须是以下子类 django.core.files.storage.Storage：
@deconstructible
class MyStorage(Storage):
    # 2.Django必须能够在没有任何参数的情况下实例化您的存储系统。
    # 这意味着任何设置都应该来自django.conf.settings：
    # def __init__(self, option=None):
    #     if not option:
    #         option = settings.CUSTOM_STORAGE_OPTIONS
    pass
#3.您的存储类必须实现_open()和_save() 方法以及适用于
    # 您的存储类的任何其他方法。

    #open 打开
    # 因为我们的 Fdfs 是通过http来获取图片的所以我们 不需要打开方法
    def _open(self, name, mode='rb'):

        pass

    def _save(self, name, content, max_length=None):
        #name,  文件的名字 我们不能通过名字获取文件的完整路径
        # content,  content 内容就是上传的内容 二进制
        # max_length=None

    #1. 创建 Fdfs的客户端，让客户端加载配置文件
        client = Fdfs_client('utils/fastdfs/client.conf')
    #2.获取上传的文件
        # 是读取 content 的内容
        # content.read()
        #读取的是二进制
        file_data = content.read()
    #3.上传图片，并获取 返回内容
        #upload_by_buffer 上传二进制流
        result = client.append_by_buffer(file_data)
    #4. 根据返回内容 获取 remote file_id
        """
        {'Group name': 'group1',
         'Local file name': '/home/python/Pictures/hu.jpeg',
         'Remote file_id': 'group1/M00/00/00/wKgsgFw9mYyAVfk7AAC02lJVkUQ88.jpeg',
         'Status': 'Upload successed.',
         'Storage IP': '192.168.44.128',
         'Uploaded size': '45.00KB'}

        """
        if result['Status']=='Upload successed.':
            # 上传成功
            file_id = result['Remote file_id']
        else:
            raise Exception('上传失败')

        #需要把file_id 返回回去
        return file_id
    #exists 存在
    #Fdfs 做了重名的处理我们只需要上传就可以
    def exists(self, name):
        return False

    def url(self, name):
        return 'http://192.168.44.128:8888/' + name