#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import logging
import pickle

from django_redis import get_redis_connection
from django.shortcuts import render as _render

from user.models import Menu, GroupMenus

logger = logging.getLogger(__name__)


class OrderedMenu:
    def __init__(self, menus: list):
        """
        原始：
        [
            {'id': 1, 'name': '数据字典', 'icon_code': 'icon fa fa-table', 'parent_id': 0, 'order': 1000, 'menu_url': '/home/'},
            {'id': 2, 'name': '公共维度', 'icon_code': '', 'parent_id': 0, 'order': 900, 'menu_url': None},
            {'id': 5, 'name': '指标定义', 'icon_code': '', 'parent_id': 0, 'order': 800, 'menu_url': '/common/index/'},
            {'id': 6, 'name': '菜单管理', 'icon_code': '', 'parent_id': 0, 'order': 700, 'menu_url': '/user/menu/'},
            {'id': 7, 'name': '操作日志', 'icon_code': '', 'parent_id': 0, 'order': 500, 'menu_url': '/user/log/'},
            {'id': 3, 'name': '时间维度', 'icon_code': '', 'parent_id': 2, 'order': 990, 'menu_url': '/common/time/'},
            {'id': 4, 'name': '区域维度', 'icon_code': '', 'parent_id': 2, 'order': 980, 'menu_url': None},
            {'id': 9, 'name': '手机号归属地', 'icon_code': '', 'parent_id': 4, 'order': 989, 'menu_url': '/common/aera/mobile/'},
            {'id': 10, 'name': '身份证归属地', 'icon_code': '', 'parent_id': 4, 'order': 988, 'menu_url': '/common/aera/id_card/'}
        ]
        :param menus:
        """
        self.menus = menus
        self.ordered_menu = []

    def order(self):
        """菜单排序
        排序后：
        [
            {'id': 1, 'name': '数据字典', 'icon_code': 'icon fa fa-table', 'parent_id': 0, 'order': 1000, 'menu_url': '/home/'},
            {
                'id': 2,
                'name': '公共维度',
                'icon_code': '',
                'parent_id': 0,
                'order': 900,
                'menu_url': None,
                'children': [
                    {'id': 3, 'name': '时间维度', 'icon_code': '', 'parent_id': 2, 'order': 990, 'menu_url': '/common/time/'},
                    {
                        'id': 4, 'name': '区域维度', 'icon_code': '', 'parent_id': 2, 'order': 980, 'menu_url': None,
                        'children': [
                                {'id': 9, 'name': '手机号归属地', 'icon_code': '', 'parent_id': 4, 'order': 989, 'menu_url': '/common/aera/mobile/'},
                                {'id': 10, 'name': '身份证归属地', 'icon_code': '', 'parent_id': 4, 'order': 988, 'menu_url': '/common/aera/id_card/'},
                        ]
                    },
                ]
            },

            {'id': 5, 'name': '指标定义', 'icon_code': '', 'parent_id': 0, 'order': 800, 'menu_url': '/common/index/'},
            {'id': 6, 'name': '菜单管理', 'icon_code': '', 'parent_id': 0, 'order': 700, 'menu_url': '/user/menu/'},
            {'id': 7, 'name': '操作日志', 'icon_code': '', 'parent_id': 0, 'order': 500, 'menu_url': '/user/log/'},
        ]

        """
        for menu in self.menus:
            if not menu['parent_id']:
                # 顶级目录
                self.ordered_menu.append(menu)
            else:
                self.insert(self.ordered_menu, menu)

        return self.ordered_menu

    def insert(self, base: list, item):
        for i in base:
            if i['id'] == item['parent_id']:
                i.setdefault('children', []).append(item)
                break
            else:
                root = i.get('children')
                if root:
                    self.insert(root, item)


def render_with_menu(request, template_name, context=None, content_type=None,
                     status=None, using=None):
    """获取菜单并做相应权限验证"""
    cxt = auth_info_required(request)
    if context is None:
        context = cxt
    else:
        context.update(cxt)
    return _render(request, template_name, context=context,
                   content_type=content_type, status=status, using=using)


def auth_info_required(request):
    user = request.user
    fields = ('id', 'name', 'icon_code', 'parent_id', 'order', 'menu_url')

    if user.is_superuser:
        menus = Menu.objects.filter(is_deleted=False).\
            order_by('parent_id', '-order').values(*fields)
    else:
        # 普通用户
        groups = user.groups.get_queryset()
        group_ids = [g.id for g in groups]

        group_menus = GroupMenus.objects.filter(
            group_id__in=group_ids).values_list('menu_id')
        menu_ids = {i[0] for i in group_menus}
        menus = Menu.objects.filter(id__in=menu_ids,
                                    is_deleted=False).values(*fields)

    om = OrderedMenu(menus)
    context = {
        'uid': user.id,
        'username': user.last_name + ' ' + user.first_name,
        'email': user.email,
        'side_menus': om.order(),
    }

    return context


def is_already_login(current_user):
    """
    判断当前用户是否已经在其他设备登陆
    :param current_user:
    :return:
    """
    redis = get_redis_connection()
    key_name_string = 'django.contrib.sessions.cache'
    for k in redis.keys():
        if key_name_string not in k.decode():
            logger.error(f"the redis key: {k} not expected!")
            continue

        user_session = pickle.loads(redis.get(k))
        try:
            user_id = int(user_session.get('_auth_user_id'))
        except (ValueError, TypeError) as e:
            logger.error(f"except-{e}, current session no _auth_user_id value!")
            continue
        if current_user.id == user_id:
            return True
    return False

