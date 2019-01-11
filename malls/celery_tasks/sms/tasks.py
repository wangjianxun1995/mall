"""
1.创建任务
2.创建Celery实例
3.在celery中设置任务，broker
4.worker

"""

#任务 就是普通的函数
#1.这个普通的函数必须要被celery 实例对象的task 装时期装饰
# 2.这个任务需要celery 自己去检测

from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def send_sms_code(mobile,sms_code):
    CCP().send_template_sms(mobile,[sms_code,5],1)