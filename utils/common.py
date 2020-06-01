#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import logging
from django.http import JsonResponse
from django.utils.functional import cached_property

logger = logging.getLogger(__name__)


class Paginator:
    def __init__(self, data_size, current_page, per_page_num=12, page_count=5):
        """
        封装分页相关数据
        :param data_size: 数据总量
        :param current_page: 当前页
        :param per_page_num: 每页显示的数据条数
        :param page_count: 最多显示的页码个数
        """
        try:
            current_page = int(current_page)
        except ValueError:
            current_page = 1

        if current_page < 1:
            current_page = 1

        self.data_size = data_size
        self.per_page_num = per_page_num
        self.page_count = page_count
        self.current_page = min(current_page, self.page_total)

        # 半长
        self.half = self.page_count // 2
        self._start = self.current_page - self.half
        self._end = self.current_page + self.half

    @cached_property
    def page_total(self):
        """总的页数"""
        page_total, remainder = divmod(self.data_size, self.per_page_num)
        return page_total+1 if remainder else page_total

    @property
    def start_page(self):
        """开始页编号"""
        start = max(1, self._start)
        # 如果总页数 <= 页脚显示数，则从第一页开始
        if self.page_total <= self.page_count:
            start = 1
        # 如果总页数 < 理论右边界
        elif self.page_total < self._end:
            start = self.end_page-self.page_count+1
        return start

    @property
    def end_page(self):
        """尾页编号"""
        end = min(self.page_total, self._end)
        # 判断页脚数量与总页数
        other = min(self.page_total, self.page_count)
        return max(end, other)

    @property
    def offset(self):
        return max((self.start_page - 1) * self.per_page_num, 0)

    @property
    def limit(self):
        return self.per_page_num

    def page_range(self):
        """页脚序列"""
        return [i for i in range(self.start_page, self.end_page+1)]

    def has_previous(self):
        return self.current_page > 1

    def has_next(self):
        return self.current_page < self.page_total

    def number(self):
        return self.current_page

    def previous_page_number(self):
        return max(self.current_page-1, 1)

    def next_page_number(self):
        return min(self.current_page+1, self.page_total)


def jsonify(msg, *args, **kwargs):
    return JsonResponse(msg, *args, **kwargs)


def dict_fetchall(cr):
    """将游标返回的结果保存到一个字典对象中"""
    desc = cr.description
    return [
        dict(zip([col[0] for col in desc], row)) for row in cr.fetchall()
    ]


def s2i(val, default=None):
    """字符串转整数"""
    if val is None:
        return default

    try:
        ret = int(float(val))
    except (ValueError, TypeError):
        ret = default

    return ret


if __name__ == '__main__':
    _per_page_num = 10
    _page_count = 5

    for size in range(1, 222, 10):
        print(f'size={size}')
        for j in range(max(_page_count, size//_per_page_num+1)):
            p = Paginator(size, j+1)
            print(f'  =cur={j+1}')
            print(f'  _start={p._start}')
            print(f'  _end={p._end}')
            print(f'  page_total={p.page_total}')
            print(f'  page_count={p.page_count}')
            print(f'  start_page={p.start_page}')
            print(f'  end_page={p.end_page}')
            print(f'  page_range={p.page_range}')
