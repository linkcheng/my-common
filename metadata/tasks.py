#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import logging
import pymysql
from django.db import connection
from pymysql.err import Error
from django.db.utils import IntegrityError

from my_common.celery_task import app
from utils.encryptor import des_encryptor
from utils.common import dict_fetchall

logger = logging.getLogger('load_metadata')


@app.task
def load_metadata():
    """根据 metadata_database_config 与 metadata_schema_config 的配置
    从不同数据库实例拉取表、字段以及索引信息"""
    sql = """
        SELECT 
            a.id
            ,a.host
            ,a.port
            ,a.username
            ,a.password
            ,group_concat(b.schema_name) schema_names
        FROM metadata_database_config a
        INNER JOIN metadata_schema_config b
        ON a.id = b.database_id
        WHERE 
            a.is_deleted = 0
            AND b.is_deleted = 0
        GROUP BY 
            a.id
            ,a.host
            ,a.port
            ,a.username
            ,a.password
        ;
    """
    with connection.cursor() as cr:
        try:
            cr.execute(sql)
            items = dict_fetchall(cr)
        except IntegrityError as e:
            logger.error(str(e))
            items = []

        sql_fmt = "insert into {table} ({columns}) values ({placeholders})"

        for item in items:
            item['password'] = des_encryptor.decrypt(item['password'])
            meta = Metadata(**item)
            result = meta.read()
            for table, data in result.items():
                columns = ','.join(Metadata.columns[table])
                placeholders = ','.join(['%s'] * len(Metadata.columns[table]))
                _sql = sql_fmt.format(table=table, columns=columns, placeholders=placeholders)
                try:
                    cr.executemany(_sql, data)
                except IntegrityError as e:
                    logger.error(str(e))


class Metadata:
    columns = {
        'metadata_table_info': (
            'table_schema',
            'table_name',
            'table_comment',
            'table_collation',
            'row_format',
            'create_time',
            'update_time',
        ),
        'metadata_column_info': (
            'table_schema',
            'table_name',
            'column_name',
            'column_type',
            'is_nullable',
            'column_default',
            'extra',
            'column_comment',
            'ordinal_position',
            'character_set_name',
            'collation_name',
        ),
        'metadata_statistics_info': (
            'table_schema',
            'table_name',
            'index_name',
            'column_name',
            'seq_in_index',
            'index_type',
            'index_comment',
        ),
    }

    sql_list = {
        'metadata_table_info': """
            select
                {column_list}
            from `information_schema`.tables
            where table_schema in {schema_names}
        """,
        'metadata_column_info': """
            select
                {column_list}
            from `information_schema`.columns
            where table_schema in {schema_names}
        """,
        'metadata_statistics_info': """
            select
                {column_list}
            from `information_schema`.statistics
            where table_schema in {schema_names}
        """

    }

    def __init__(self, schema_names, host, port, username, password,
                 charset='utf8', *args, **kwargs):
        self.config = {
            'host': host,
            'port': port,
            'user': username,
            'password': password,
            'charset': charset,
            'autocommit': True,
        }
        if isinstance(schema_names, (str,)):
            schema_names = schema_names.split(',')
        if len(schema_names) < 2:
            schema_names = list(schema_names)
            schema_names.append('')
            schema_names = tuple(schema_names)
        self.schema_names = tuple(set(schema_names))

        self.conn = pymysql.connect(**self.config)
        self.cr = self.conn.cursor()

    def __del__(self):
        self.close()

    def read(self):
        ret = {}
        for key, sql in Metadata.sql_list.items():
            column_list = ','.join(Metadata.columns[key])
            query_sql = sql.format(column_list=column_list, schema_names=self.schema_names)
            logging.info(query_sql)
            try:
                self.cr.execute(query_sql)
                ret[key] = self.cr.fetchall()
            except Exception as e:
                logger.error(str(e))

        return ret

    def close(self):
        try:
            self.cr.close()
            self.conn.close()
        except Error as e:
            logging.error(str(e))


@app.task
def del_metadata():
    with connection.cursor() as cr:
        sql = "DELETE from {table} where `created_time` <= date_sub(CURRENT_DATE(),interval 1 week) "
        for key in Metadata.sql_list:
            _sql = sql.format(table=key)
            try:
                cr.execute(_sql)
                connection.commit()
            except IntegrityError as e:
                logger.error(str(e))


if __name__ == '__main__':
    del_metadata()
