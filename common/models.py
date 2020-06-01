import logging

import django.utils.timezone as timezone
from django.db.models.query_utils import Q
from django.db.models import Model, AutoField, DateTimeField, IntegerField, DateField, CharField

page_size = 10
logger = logging.getLogger('common_models')


class BaseModel(Model):

    class Meta:
        abstract = True

    id = AutoField('主键', primary_key=True)
    created_time = DateTimeField('创建时间', default=timezone.now)
    updated_time = DateTimeField('更新时间', auto_now=True)

    @classmethod
    def table_columns(cls):
        return NotImplemented

    @classmethod
    def query_data(cls, query):
        return NotImplemented

    @classmethod
    def sum_pages(cls, query):
        """
        计算查询数据的总页数
        :param query: 搜索关键字
        :return:
        """
        if query is None:
            count = cls.objects.all().count()
        else:
            count = cls.query_data(query).count()
        pages = count // page_size
        if count % page_size != 0:
            pages += 1
        return pages

    @classmethod
    def find_by_page(cls, page, sort_field='id', query=None):
        """
        根据以下请求参数，查询相应的数据
        :param page: 页码，可为空，为空时默认为第一页
        :param sort_field: 排序字段名，默认正向排序，若字段名前面加'-'，则为倒序，可为空，为空时模式按主键id正向排序
        :param query: 搜素关键字，可为空，为空时模式无搜素
        :return:
        """
        page = page - 1
        page_start = page_size * page
        page_end = page_start + page_size
        sorted_columns = cls.table_columns()
        if query is None:
            query_data = cls.objects.all()
        else:
            query_data = cls.query_data(query)
        data_list = query_data.order_by(sort_field).values_list(*sorted_columns)
        return data_list[page_start: page_end]

    @classmethod
    def add(cls, data):
        """
        新增数据
        :param data:
        :return:
        """
        cls(**data).save()

    @classmethod
    def update(cls, pk, data):
        """
        更新数据
        :param pk:
        :param data:
        :return:
        """
        cls.objects.filter(id=pk).update(**data)

    @classmethod
    def remove(cls, pk):
        """
        删除数据
        :param pk:
        :return:
        """
        cls.objects.filter(id=pk).delete()


class DateClass(BaseModel):
    date = DateField('日期', unique=True)
    date_str = CharField('日期-字符串', max_length=8, unique=True)
    weekday = IntegerField('星期', default=0)
    _class = IntegerField('节日', name='class', default=0)

    class Meta:
        db_table = 'common_date'
        verbose_name = '公共时间维度表'
        verbose_name_plural = verbose_name

        permissions = (
            ('read_common_date', 'Can view common date'),
            ('write_common_date', 'Can update common date'),
        )

    @classmethod
    def table_columns(cls):
        """
        返回有序的字段名列表
        :return:
        """
        verbose_names = ['id', 'date', 'date_str', 'weekday', 'class', 'created_time', 'updated_time']
        return verbose_names

    @classmethod
    def table_names(cls):
        names = dict(
             table_name=cls._meta.db_table,
             verbose_name=cls._meta.verbose_name
        )
        return names

    @classmethod
    def query_data(cls, query):
        """
        根据搜索关键字查询数据
        :param query: 搜索关键字
        :return:
        """
        try:
            int(query)
        except (ValueError, TypeError) as e:
            logger.info(f'exception: {e}: query can not be int.')
            return cls.objects.filter(Q(date_str__contains=query))
        else:
            return cls.objects.filter(Q(date_str__contains=query) | Q(weekday=int(query)) | Q(**{'class': int(query)}))


class MobileAttributionClass(BaseModel):
    number = CharField('手机号码前7位', max_length=7, unique=True)
    short_province = CharField('号码归属地省份-简称', max_length=16)
    short_city = CharField('号码归属地城市-简称', max_length=16)
    full_province = CharField('号码归属地省份-全称', max_length=16)
    full_city = CharField('号码归属地城市-全称', max_length=16)
    phone_type = CharField('运营商', max_length=5)
    zip_code = CharField('归属地邮编', max_length=6)
    city_code = CharField('归属地区号', max_length=6)

    class Meta:
        db_table = 'common_mobile_attribution'
        verbose_name = '手机号码归属地维度表'
        verbose_name_plural = verbose_name

        permissions = (
            ('read_common_mobile_attribution', 'Can view common mobile attribution'),
            ('write_common_mobile_attribution', 'Can update common mobile attribution'),
        )

    @classmethod
    def table_columns(cls):
        """
        返回有序的字段名列表
        :return:
        """
        return ['id', 'number', 'zip_code', 'city_code', 'full_province', 'short_province',
                'full_city', 'short_city', 'phone_type', 'created_time', 'updated_time']

    @classmethod
    def table_names(cls):
        names = dict(
            table_name=cls._meta.db_table,
            verbose_name=cls._meta.verbose_name
        )
        return names

    @classmethod
    def query_data(cls, query):
        """
        根据搜索关键字查询数据
        :param query: 搜索关键字
        :return:
        """
        return cls.objects.filter(Q(number__contains=query) | Q(phone_type__contains=query) |
                                  Q(short_province__contains=query) | Q(short_city__contains=query) |
                                  Q(full_province__contains=query) | Q(full_city__contains=query) |
                                  Q(zip_code__contains=query) | Q(city_code__contains=query))


class IdAttributionClass(BaseModel):
    number = CharField('身份证号前6位', max_length=7, unique=True)
    city_code = CharField('归属地邮编', max_length=6)
    short_province = CharField('号码归属地省份-简称', max_length=16)
    short_city = CharField('号码归属地城市-简称', max_length=16)
    full_province = CharField('号码归属地省份-全称', max_length=16)
    full_city = CharField('号码归属地城市-全称', max_length=16)
    full_district = CharField('号码归属地区县-全称', max_length=16)
    short_district = CharField('号码归属地区县-简称', max_length=16)
    level = CharField('行政等级', max_length=12)

    class Meta:
        db_table = 'common_id_attribution'
        verbose_name = '身份证号码归属地维度表'
        verbose_name_plural = verbose_name

        permissions = (
            ('read_common_id_attribution', 'Can view common id attribution'),
            ('write_common_id_attribution', 'Can update common id attribution'),
        )

    @classmethod
    def table_columns(cls):
        """
        返回有序的字段名列表
        :return:
        """
        return ['id', 'number', 'city_code', 'full_province', 'short_province', 'full_city',
                'short_city', 'full_district', 'short_district', 'level', 'created_time', 'updated_time']

    @classmethod
    def table_names(cls):
        names = dict(
            table_name=cls._meta.db_table,
            verbose_name=cls._meta.verbose_name
        )
        return names

    @classmethod
    def query_data(cls, query=None):
        """
        根据搜索关键字查询数据
        :param query: 搜索关键字
        :return:
        """
        return cls.objects.filter(Q(number__contains=query) | Q(city_code__contains=query) |
                                  Q(short_province__contains=query) | Q(short_city__contains=query) |
                                  Q(full_province__contains=query) | Q(full_city__contains=query) |
                                  Q(full_district__contains=query) | Q(short_district__contains=query))





