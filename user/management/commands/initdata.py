#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import IntegrityError
from my_common.settings import BASE_DIR

logger = logging.getLogger('initdata')


class Command(BaseCommand):
    help = """第一次使用时初始化数据。
使用方式 python manage.py initdata <App>
initdata 指令执行时，会在对应的 App 目录中寻找对应 initial.sql 文件，
然后以 ; 分割文件内容，并从上到下依次执行，请确保 SQL 顺序准确无误。
"""

    def add_arguments(self, parser):
        parser.add_argument('app', type=str, help='模块名称')

    def handle(self, *args, **options):
        app = options['app']
        init_name = 'initial.sql'
        file_name = os.path.join(BASE_DIR, app, init_name)

        with open(file_name, mode='r') as f:
            cnt = f.read()

        sql_list = cnt.split(';')
        with connection.cursor() as cr:
            for sql in sql_list:
                sql = sql.strip()
                if sql:
                    try:
                        cr.execute(sql)
                    except IntegrityError as e:
                        logger.info('#' * 40)
                        logger.info(str(e))
                        logger.info(sql)
                        logger.info('@' * 40)
                        break

        connection.close()
        logger.info('Initialize over')
