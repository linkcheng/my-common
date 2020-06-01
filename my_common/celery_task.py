#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import logging
from celery import Celery, platforms
from my_common import settings

logger = logging.getLogger('celery_task')

# 为celery设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_common.settings')

# 创建应用
app = Celery('my_common')

platforms.C_FORCE_ROOT = True

# 配置应用
app.conf.update(
    # 本地Redis服务器
    BROKER_URL=settings.BROKER_URL,

)

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS)
