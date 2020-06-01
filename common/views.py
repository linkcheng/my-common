import logging

from django.views import View
from django.http.request import QueryDict
from django.shortcuts import redirect
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

from user.utils import render_with_menu
from utils.common import jsonify
from common.models import DateClass, IdAttributionClass, MobileAttributionClass


logger = logging.getLogger('common_views')


class CommonView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    common模块的通用views，根据path的信息，判断处理哪一个model
    三个model通用了get post put delete方法
    """
    login_url = '/user/login/'
    permission_required = ['common.read_common_date', 'common.read_common_id_attribution',
                           'common.read_common_mobile_attribution']

    location2model = dict(
        date=DateClass,
        idAttribution=IdAttributionClass,
        mobileAttribution=MobileAttributionClass
    )

    @classmethod
    def get_path(cls, request):
        """
        从请求对象中获取path
        :param request:
        :return:
        """
        return request.get_full_path().split('?')[0]

    @classmethod
    def current_model(cls, request):
        """
        根据path找到对应的model
        :param request:
        :return:
        """
        location = cls.get_path(request).split('/')[2]
        return cls.location2model.get(location)

    @classmethod
    def has_write_perm(cls, request):
        model = cls.current_model(request)
        current_user = request.user
        table_name = model.table_names()['table_name']
        return current_user.has_perm(f"common.write_{table_name}")

    def get(self, request):
        """
        根据以下请求参数，查询相应的数据并响应页面
        page: int， 页码，可为空，为空时默认为第一页
        sort_field: str 排序字段名，默认正向排序，若字段名前面加'-'，则为倒序，可为空，为空时模式按主键id正向排序
        query: str，搜素关键字，可为空，为空时模式无搜素
        :param request:
        :return:
        """
        # TODO 处理 table_data.html 中date表新增字段的weekday的相关更新
        query = request.GET.get('query')
        path = self.get_path(request)
        model = self.current_model(request)

        if query == '':
            return redirect(path)

        cxt = dict()
        page = int(request.GET.get('page', 1))

        sort_field = request.GET.get('sort_field', 'id')
        if sort_field[0] == '-':
            sort_ = {'field': sort_field[1:], 'order': '-alt', 'next_order': ''}
        else:
            sort_ = {'field': sort_field, 'order': '', 'next_order': '-'}
        sort_['sort_field'] = sort_field

        sum_pages = model.sum_pages(query)
        cxt['table_names'] = model.table_names()
        cxt['page_data'] = model.find_by_page(page, query=query, sort_field=sort_field)
        cxt['verbose_columns'] = model.table_columns()
        cxt['pages'] = make_page_info(page, sum_pages)
        cxt['write_perm'] = self.has_write_perm(request)
        cxt['sort'] = sort_
        cxt['path'] = path

        if query is not None:
            cxt['query'] = query

        return render_with_menu(request, 'table_data.html', cxt)

    def post(self, request):
        """
        接受post请求的新数据，插入表中
        :param request:
        :return:
        """
        model = self.current_model(request)
        data = request.POST.dict()
        logger.info(f"POST-model: {model}-data: {data}")
        for k in data.keys():
            if data[k] == '':
                del data[k]
        model.add(data)
        return jsonify({'status': 'success'})

    def put(self, request, index):
        """
        接受put请求的更新数据，更新表
        :param request:
        :param index: 数据主键id
        :return:
        """
        data = QueryDict(request.body).dict()
        model = self.current_model(request)
        logger.info(f"PUT-model: {model}-index: {index}-data: {data}")
        for k in data.keys():
            if data[k] == '':
                del data[k]
        model.update(index, data)
        return jsonify({'status': 'success'})

    def delete(self, request):
        """
        接受delete请求的主键id，并删除表中对应的数据
        :param request:
        :return:
        """
        pk = QueryDict(request.body).dict().get('id')
        model = self.current_model(request)
        logger.info(f"DELETE-model: {model}-pk: {pk}")
        model.remove(pk)
        return jsonify({'status': 'success'})


def make_page_info(page, sum_pages):
    """
    生成分页相关信息，以及页面中需要点击的翻页按钮的相关信息
    :param page: 当前页码
    :param sum_pages: 总页数
    :return:
    """
    pages = dict()
    pages['sum_pages'] = sum_pages
    pages['has_previous'] = True if page > 1 else False
    pages['has_next'] = True if page < sum_pages else False
    pages['previous_page'] = page - 1
    pages['next_page'] = page + 1
    pages['page_number'] = page
    pages['page_range'] = create_page_range(page, 5, sum_pages)
    pages['show_first_page'] = True if pages['page_range'][0] != 1 else False
    pages['show_last_page'] = True if pages['page_range'][-1] < sum_pages else False
    return pages


def create_page_range(page, length, sum_pages):
    """
    根据当前页码，显示的页码个数，总页码数，确定页面中的翻页按钮应该显示哪些页码
    :param page: 当前页码
    :param length: 需要显示的页码个数
    :param sum_pages: 总的页码数量
    :return:
    """
    page_list = []
    length_mid = length // 2

    if sum_pages < length:
        page_range = range(sum_pages)
        base_number = 1
    # 前length页
    elif page <= length_mid + 1:
        page_range = range(length)
        base_number = 1
    # 后length页
    elif page + length_mid > sum_pages:
        page_range = range(sum_pages-length, sum_pages)
        base_number = 1
    # 中间页
    else:
        page_range = range(-length_mid, length-length_mid)
        base_number = page

    for i in page_range:
        page_list.append(base_number + i)
    if len(page_list) == 0:
        page_list = [1]
    return page_list

