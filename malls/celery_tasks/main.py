from celery import Celery


"""
1.创建任务
2.创建Celery实力
3.在celery中设置任务，broker
4.worker执行任务
"""
#celery 是一个 及插即用 的任务队列
# celery 是需要和django (当前的工程) 进行交互的
# 让celery 加载当前的工程默认配置
# 第一种方法
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mall.settings")

#第二种方法
#进行Celery允许配置
# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'malls.settings'

#2.创建celery实例
# main 习惯添加celery 的文件路径
# 确保main 不出现重复
app = Celery(main = 'celery_tasks')

# 设置 borker
# 加载broker 的配置信息 参数 '路径信息'
app.config_from_object('celery_tasks.config')

# 4. 让celery自动检测
#参数：列表
#元素：任务的包路径
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.mail','celery_tasks.html'])

# 让 worker去执行任务
# 需要 在虚拟环境中执行指令
# celery -A celery实例对象路径 worker -l info
# celery -A celery_tasks.main worker -l info
