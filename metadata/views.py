import json
import logging
from operator import itemgetter
from itertools import groupby
from django.views import View
from django.db import connection
from django.http.request import QueryDict
from django.contrib.auth.mixins import LoginRequiredMixin

from user.utils import render_with_menu
from metadata.models import Comment
from utils.common import (
    Paginator,
    dict_fetchall,
    s2i,
    jsonify
)

logger = logging.getLogger(__name__)


class SearchEngine:
    # 表的描述信息
    table_desc = (
        'table_schema',
        'table_name',
        'table_comment',
        'create_time',
        'update_time'
    )
    # 列的描述信息
    column_desc = (
        'column_name',
        'column_type',
        'is_nullable',
        'column_default',
        'extra',
        'column_comment',
    )
    # 索引的描述信息
    statistics_desc = (
        'index_name',
        'column_name',
        'seq_in_index',
        'index_type',
        'index_comment',
    )
    # 评论的描述信息
    comment_desc = (
        'id',
        'content',
        'updated_time',
        'parent_id',
        'user_id',
        'user_name',
    )

    def get_all_db(self):
        sql = f"""
        select  `schema_name` from metadata_schema_config GROUP BY `schema_name` """
        return self.get_tuple(sql)

    def get_table_names(self, key):
        """查询可能的表名"""
        sql = f"""
            SELECT
                distinct e.table_name 
            FROM
                metadata_column_info e 
            WHERE
                e.column_name like '{key}%' 
                AND 
                ( 
                    SELECT count(1) FROM metadata_column_info 
                    WHERE column_name = e.column_name AND e.created_time < created_time 
                ) < 1
            UNION ALL
            SELECT
                e.table_name
            FROM
                metadata_table_info e 
            WHERE
                e.table_name like '{key}%' 
                AND 
                ( 
                    SELECT count(1) FROM metadata_table_info 
                    WHERE table_name = e.table_name AND e.created_time < created_time 
                ) < 1
        """
        return self.get_tuple(sql)

    def get_table_names_by_table(self, tab, table_schema=None):
        schema = f"AND e.table_schema like '%{table_schema}%'" if table_schema else ''
        sql = f"""
            SELECT
                distinct e.table_name
            FROM
                metadata_table_info e 
            WHERE
                e.table_name like '{tab}%' 
                {schema}
                AND 
                ( 
                    SELECT count(1) FROM metadata_table_info 
                    WHERE table_name = e.table_name AND e.created_time < created_time 
                ) < 1
        """
        return self.get_tuple(sql)

    def get_table_names_by_column(self, col, tab=None, table_schema=None):
        schema = f"AND e.table_schema like '%{table_schema}%'" if table_schema else ''
        table = f"AND e.table_name like '{tab}%'" if tab else ''
        sql = f"""
            SELECT
                distinct e.table_name 
            FROM
                metadata_column_info e 
            WHERE
                
                e.column_name like '{col}%' 
                {table}
                {schema}
                AND 
                ( 
                    SELECT count(1) FROM metadata_column_info 
                    WHERE column_name = e.column_name AND e.created_time < created_time 
                ) < 1
        """
        return self.get_tuple(sql)

    def get_tuple(self, sql):
        cr = connection.cursor()
        cr.execute(sql)
        return tuple(set([i[0] for i in cr.fetchall()]))

    def get_column_info(self, table_schema=None, tab=None, col=None):
        """根据表名查询所有对应的字段"""

        if table_schema is None:
            schema = f"AND t.table_schema in (select `schema_name` from metadata_schema_config)"
        else:
            schema = f"AND t.table_schema='{table_schema}'"
        if tab is not None:
            table_names = f"t.table_name like '{tab}%'"
        else:
            table_names = f"c.column_name like '{col}%'"

        sql = f"""
            SELECT
                t.table_schema, t.table_name, t.table_comment, t.create_time
                ,ifnull(t.update_time, '') AS update_time
                ,c.column_name, c.column_type, c.is_nullable, c.column_default
                ,c.extra, c.column_comment, c.ordinal_position 
            FROM  
                metadata_table_info t
            INNER JOIN  
                metadata_column_info c
            ON 
                t.table_schema=c.table_schema AND t.table_name=c.table_name
            WHERE
                {table_names}
                {schema}
                AND 
                ( 
                    SELECT count(1) 
                    FROM metadata_table_info 
                    WHERE table_name = t.table_name
                        AND t.created_time < created_time 
                ) < 1
                AND
                ( 
                    SELECT count(1) 
                    FROM metadata_column_info 
                    WHERE table_name = c.table_name
                        AND c.created_time < created_time 
                ) < 1
            ORDER BY t.table_name ASC, t.created_time DESC
        """
        return self.get_info(sql, 'column_info', self.column_desc)

    def get_statistics_info(self, table_schema=None, tab=None):
        """根据表名查询所有对应的索引"""
        if not tab:
            return []

        if table_schema is None:
            return []

        schema = f"AND t.table_schema ='{table_schema}'"
        table_name = f"s.table_name = '{tab}'"

        sql = f"""
            SELECT
                t.table_schema, t.table_name, t.table_comment, t.create_time
                ,ifnull(t.update_time, '') AS update_time
                ,s.index_name, s.column_name, s.seq_in_index, s.index_type
                ,s.index_comment
            FROM  
                metadata_table_info t
            INNER JOIN 
                metadata_statistics_info s
            ON 
                t.table_schema=s.table_schema AND t.table_name=s.table_name
            WHERE
                {table_name}
                {schema}
                AND 
                ( 
                    SELECT count(1) 
                    FROM metadata_table_info 
                    WHERE table_name = t.table_name
                        AND t.created_time < created_time 
                ) < 1
                AND
                ( 
                    SELECT count(1) 
                    FROM metadata_statistics_info 
                    WHERE table_name = s.table_name
                        AND s.created_time < created_time 
                ) < 1
            ORDER BY t.table_name ASC, t.created_time DESC
        """
        return self.get_info(sql, 'statistics_info', self.statistics_desc)

    def get_comment(self, table_names, table_schema=None):
        """根据表名查询所有对应的评论"""
        if not table_names:
            return []

        if not isinstance(table_names, (list, tuple)):
            table_names = (table_names, '')
        schema = f"AND t.table_schema='{table_schema}'" if table_schema else ''

        sql = f"""
            SELECT
                t.table_schema, t.table_name, t.table_comment, t.create_time
                ,ifnull(t.update_time, '') AS update_time
                ,m.id, m.content, m.updated_time, m.parent_id, m.user_id
                ,concat(u.last_name, ' ', u.first_name) AS user_name
            FROM  
               metadata_comment m
            INNER JOIN  
                metadata_table_info t
            ON 
                m.table_schema=t.table_schema AND m.table_name=t.table_name
            INNER JOIN 
                auth_user u
            ON 
                m.user_id=u.id
            WHERE
                t.table_name IN {table_names}
                {schema}
                AND 
                ( 
                    SELECT count(1) 
                    FROM metadata_table_info 
                    WHERE table_name = t.table_name
                       AND t.created_time < created_time 
                ) < 1
            ORDER BY t.table_name ASC, t.created_time DESC
        """
        return self.get_info(sql, 'comment', self.comment_desc)

    def get_info(self, sql, data_type='column_info', data_desc=None):
        cr = connection.cursor()
        cr.execute(sql)
        data = dict_fetchall(cr)
        return self.rebuilt(data, data_type, data_desc)

    def rebuilt(self, data, data_type='column_info', data_desc=None):
        """重新组合数据结果
        把对应表的
            字段信息放入 column_info 中
            索引信息放入 statistics_info 中
            评论信息放入 comment 中
        最终结构为
        [
            {
                'table_schema': 'statistics',
                'table_name': 'StarUser',
                'table_comment': '',
                'create_time': datetime.datetime(2019, 6, 11, 15, 41, 52),
                'update_time': '',
                'column_info': [
                    {
                        'column_name': 'id',
                        'column_type': 'bigint(20) unsigned',
                        'column_comment': '用户id'
                    },
                ],
            },
        ]
        或者
        [
            {
                'table_schema': 'statistics',
                'table_name': 'StarUser',
                'table_comment': '',
                'create_time': datetime.datetime(2019, 6, 11, 15, 41, 52),
                'update_time': '',
                'statistics_info': [
                    {
                        'index_name': 'PRIMARY',
                        'column_name': 'id',
                        'seq_in_index': 1，
                    },
                ],
            },

        ]
        """
        if not data_desc:
            data_desc = self.column_desc

        def f(arg):
            table_info, rows = arg
            item = dict(zip(self.table_desc, table_info))
            item[data_type] = [
                {desc: row[desc] for desc in data_desc} for row in rows
            ]
            return item

        return list(map(f, groupby(data, key=itemgetter(*self.table_desc))))


class GetDB(LoginRequiredMixin, View):
    engine = SearchEngine()

    def get(self, request):
        res = self.engine.get_all_db()
        return jsonify({"res": [{"id": res.index(item), "dbName": item} for item in res]})


class SearchView(LoginRequiredMixin, View):
    engine = SearchEngine()

    def get(self, request):
        key = request.GET.get('key')
        db_name = request.GET.get('dbName')
        db_name = None if db_name in ("全库检索", 'None') else db_name
        type_ = request.GET.get('type')  # 表名 内容

        if not key:
            return render_with_menu(request, 'search.html')
        else:
            cur_page = int(request.GET.get('p', 1))
            return self.search(request, key, s2i(cur_page, 1), db_name=db_name, type_=type_)

    def search(self, request, key, cur_page, db_name=None, type_=None):
        if key == '':
            return render_with_menu(request, 'search.html')

        pri, *other = key.split()
        if type_ == "表名":
            search_info = self.engine.get_column_info(table_schema=db_name, tab=pri)

        elif type_ == "内容":
            if other:
                base_info = other
            else:
                base_info = pri
            search_info = self.engine.get_column_info(table_schema=db_name, col=base_info)

        else:
            return render_with_menu(request, 'result.html', {})

        per_page_num = 12
        paginator = Paginator(len(search_info), cur_page, per_page_num)
        context = {
            'key': key,
            'dbName': db_name,
            'SType': type_,
            'search_list': search_info[(cur_page - 1) * per_page_num:cur_page * per_page_num],
            'paginator': paginator,
        }
        return render_with_menu(request, 'result.html', context)


class DetailView(LoginRequiredMixin, View):
    engine = SearchEngine()

    def get(self, request, table_schema, table_name):
        column_info = self.engine.get_column_info(table_schema=table_schema, tab=table_name)
        statistics_info = self.engine.get_statistics_info(table_schema=table_schema, tab=table_name)
        comment = self.engine.get_comment(table_name, table_schema)

        if column_info and statistics_info:
            column_info[0]['statistics_info'] = statistics_info[0].get('statistics_info')

        if column_info and comment:
            column_info[0]['comment'] = comment[0].get('comment')

        return render_with_menu(request, 'detail.html', {'details': column_info})


class CommentView(LoginRequiredMixin, View):
    def post(self, request):
        comment = dict(
            table_schema=request.POST.get('table_schema'),
            table_name=request.POST.get('table_name'),
            content=request.POST.get('content', ''),
            user_id=request.user.id,
        )

        try:
            Comment.objects.create(**comment)
        except Exception as e:
            logger.error(str(e))
            msg = {'status': 'failure', 'message': str(e)}
        else:
            msg = {'status': 'success'}

        return jsonify(msg)

    def put(self, request):
        data = QueryDict(request.body)

        user_id = request.user.id
        cid = data.get('cid')
        content = data.get('content', '')

        obj = Comment.objects.get(id=cid)
        obj.content = content
        obj.user_id = user_id
        try:
            obj.save()
        except Exception as e:
            logger.error(str(e))
            msg = {'status': 'failure', 'message': str(e)}
        else:
            msg = {'status': 'success'}

        return jsonify(msg)
