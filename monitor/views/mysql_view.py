#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import logging
from django.views import View
from django.http.request import QueryDict
from django.db.models import Max
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from monitor.models import MySQLConnector, Database
from monitor.utils import KafkaConnector
from user.utils import render_with_menu
from utils.common import jsonify

logger = logging.getLogger(__name__)


def copy_mysql_connector(request, index):
    connector = MySQLConnector.objects.filter(id=index).first()
    databases = Database.objects.filter(is_deleted=0)
    context = {
        'connector': connector,
        'databases': databases,
        'action': 'copy',
        'action_name': '复制',
    }
    if request.user.has_perm('user.write_mysql_connector'):
        context['writable'] = '1'
    return render_with_menu(request, 'connector_detail.html', context)


def update_mysql_connector(request, index):
    connector = MySQLConnector.objects.filter(id=index).first()
    databases = Database.objects.filter(is_deleted=0)
    context = {
        'connector': connector,
        'databases': databases,
        'action': 'update',
        'action_name': '修改',
    }
    if request.user.has_perm('user.write_mysql_connector'):
        context['writable'] = '1'
    return render_with_menu(request, 'connector_detail.html', context)


class MySQLConnectorView(LoginRequiredMixin, View):

    @method_decorator(permission_required('user.read_mysql_connector', raise_exception=True))
    def get(self, request):
        connectors = MySQLConnector.objects.filter()
        context = {'connectors': connectors}
        if request.user.has_perm('user.write_mysql_connector'):
            context['writable'] = '1'
        return render_with_menu(request, 'connectors.html', context)

    @method_decorator(permission_required('user.write_mysql_connector', raise_exception=True))
    def post(self, request):
        data = request.POST
        logger.info(data)
        cid = int(data.get('cid'))
        action = data.get('action')
        db_id = data.get('database')

        fs = [
            'name', 'connector_class', 'tasks_max',
            'history_kafka_topic', 'history_kafka_servers',
            'server_id', 'server_name',
            'schema_whitelist', 'schema_blacklist',
            'table_whitelist', 'table_blacklist',
            'include_schema_changes',
            'is_deleted'
        ]
        kw = {k: data[k] for k in fs}
        kw['database_id'] = db_id

        if action == 'update':
            try:
                MySQLConnector.objects.filter(id=cid).update(**kw)
            except Exception as e:
                msg = {'status': 'failure', 'message': str(e)}
            else:
                msg = {'status': 'success'}
        elif action == 'copy':
            try:
                MySQLConnector.objects.create(**kw)
            except Exception as e:
                msg = {'status': 'failure', 'message': str(e)}
            else:
                msg = {'status': 'success'}
        else:
            msg = {'status': 'failure', 'message': 'action 不存在'}

        return jsonify(msg)

    @method_decorator(permission_required('user.write_mysql_connector', raise_exception=True))
    def put(self, request):
        data = QueryDict(request.body)
        cid = int(data.get('cid'))
        action = data.get('action')

        connector = MySQLConnector.objects.filter(id=cid, is_deleted=0).first()
        if not connector:
            msg = {'status': 'failure', 'message': '配置不存在'}
            return jsonify(msg)

        logger.info(f'action={action}, server_name={connector.server_name}')
        kc = KafkaConnector(connector)
        if action == 'resume':
            msg = kc.run()
        elif action == 'pause':
            msg = kc.pause()
        elif action == 'refresh':
            msg = kc.refresh()
        else:
            msg = {'status': 'failure', 'message': 'action 不存在'}

        return jsonify(msg)

    @method_decorator(permission_required('user.write_mysql_connector', raise_exception=True))
    def delete(self, request):
        data = QueryDict(request.body)
        cid = int(data.get('cid'))
        connector = MySQLConnector.objects.filter(id=cid).first()
        KafkaConnector.delete_connector(connector.server_name)

        try:
            ret = MySQLConnector.objects.filter(server_name=connector.server_name).aggregate(Max('is_deleted'))
            connector.is_deleted = ret.get('is_deleted__max') + 1
            connector.status = ''
            connector.save()
        except Exception as e:
            msg = {'status': 'failure', 'message': str(e)}
        else:
            msg = {'status': 'success'}

        return jsonify(msg)

