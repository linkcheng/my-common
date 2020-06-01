import os
import sys
import time
import logging
import datetime

import numpy as np
import pandas as pd
from django.db.utils import OperationalError

from my_common.settings import GAODE_KEY, JUHE_KEY
from my_common.celery_task import app
from common.utils import simplify_name, is_valid_phone, is_valid_phone_7, execute_sql, query_fmt

logger = logging.getLogger('common_tasks')


class CommonBase:
    table_name = None

    @classmethod
    def make_data(cls):
        return NotImplemented

    @classmethod
    def splice_insert_sql(cls, table_name, df):
        """
        拼接插入语句sql
        :param table_name: 表名
        :param df: dataframe格式的数据
        :return:
        """
        value_fmt = ",".join(['{0}'] * len(df.columns)).format("'{}'")
        sql = f"insert into {table_name}({','.join(df.columns)}) values"
        value_list = [f"({value_fmt.format(*data)})" for data in df.values]
        sql += ','.join(value_list)
        sql = sql.replace("'nan'", 'null')
        sql = sql.replace("'None'", 'null')
        return sql

    @classmethod
    def splice_truncate_sql(cls, table_name):
        """
        生成删除数据 重置表的sql
        :param table_name: 表名
        :return:
        """
        return f"truncate table {table_name}"

    @classmethod
    def insert(cls, initial=False):
        """
        向表中插入数据
        :param initial: 是否先格式化表
        :return:
        """
        try:
            logger.info(f"start update {cls.table_name}'s data.")
            if initial:
                execute_sql(cls.splice_truncate_sql(cls.table_name))

            df = cls.make_data()

            if df is None:
                return

            logger.info(f"find {cls.table_name}'s {df.shape[0]} records")
            if df.shape[0] == 0:
                return

            sql = cls.splice_insert_sql(cls.table_name, df)
            execute_sql(sql)
        except OperationalError as e:
            logger.error(f"Due to exception: {e}, this task failed!")
        else:
            logger.info(f'{cls.table_name} insert {df.shape[0]} records')


class CommonDate(CommonBase):
    table_name = 'common_date'
    days = 10

    @classmethod
    def _last_date(cls):
        """
        获取common_date表中最近的一条记录的date
        :return: date格式的日期
        """
        sql = "select date from common_date order by date desc limit 1"
        data = execute_sql(sql, dict_cursor=True)
        if len(data) == 0:
            return
        return data[0].get('date')

    @classmethod
    def _get_class(cls, date_string, slow=True):
        """
        向www.easybots.cn发送请求获取指定日期的节假日信息
        :param date_string: 时间字符串，类似于 '20100101'这样的格式
        :param slow: 是否控制请求速度，默认是
        :return: 节假日等级
        """
        if slow:
            time.sleep(1)
        url = 'http://www.easybots.cn/api/holiday.php'
        params = {'d': date_string}
        json_data = query_fmt(url, params)
        data = json_data.get(date_string)
        if not data:
            logger.error(f'url:{url}-params:{params}-value:{json_data}')
            raise ValueError('The value of class cannot be None!')
        return data

    @classmethod
    def _init_data(cls):
        """
        从 my_user_profile.DateClass 中拉取历史common_date数据
        :return:
        """
        sql = "select distinct date as date_str, class from DateClass"
        data = execute_sql(sql, db='my_user_profile', dict_cursor=True)

        df = pd.DataFrame(data)
        df.drop_duplicates(subset=['date_str'], inplace=True)
        df['date'] = df['date_str'].apply(lambda x: datetime.date(int(x[:4]), int(x[4:6]), int(x[6:])))
        df['weekday'] = df['date'].apply(lambda x: x.weekday())
        return df

    @classmethod
    def _update_date(cls, start_date):
        """
        根据common_data表中最新的last_date，向前更新cls.days天的数据，
        :param start_date: common_data表中最新的last_date
        :return:
        """
        now = datetime.datetime.now()
        if now.year - start_date.year < -1:
            return
        if now.year - start_date.year == -1 and now.month < 12:
            return

        end_date_unc = start_date + datetime.timedelta(days=cls.days)
        if end_date_unc.year == now.year:
            end_date = end_date_unc
        else:
            deadline = datetime.date(now.year + 1, 12, 31)
            end_date = min(end_date_unc, deadline)

        start_date += datetime.timedelta(days=1)
        logger.info(f"start_date: {start_date}, end_date: {end_date}")

        if start_date == end_date:
            logger.info(f"The update of {cls.table_name} table is completed.")
            return

        date_range = pd.date_range(start=start_date, end=end_date, freq='d')
        df = date_range.to_frame(index=False, name='date')
        df['date_str'] = df['date'].astype(str).str.replace('-', '')

        try:
            df['class'] = df['date_str'].apply(cls._get_class)
            df['weekday'] = df['date'].apply(lambda x: x.weekday())
        except ValueError:
            logger.error(f"The value of class is None, this task failed!")
            return

        return df

    @classmethod
    def make_data(cls):
        """
        生成插入common_date表中dataframe格式的数据
        :return:
        """
        start_date = cls._last_date()

        if start_date is None:
            df = cls._init_data()
        else:
            df = cls._update_date(start_date)

        return df


class CommonMobile(CommonBase):
    table_name = 'common_mobile_attribution'

    @classmethod
    def _phone_query(cls, number):
        """
        请求聚合api，得到手机号码归属地
        :param number: 手机号前7位
        :return:
        """
        url = 'http://apis.juhe.cn/mobile/get'
        params = {
            'phone': number,
            'key': JUHE_KEY,
        }

        value = query_fmt(url, params)
        result_code = value.get('resultcode')
        if result_code == '200':
            result = value.get('result')
            data = {
                'province': result.get('province'),
                'city': result.get('city'),
                'phone_type': result.get('company'),
                'city_code': result.get('areacode'),
                'zip_code': result.get('zip'),
            }
        else:
            data = {}
            logger.error(f'url:{url}-params:{params}'
                         f'-value:{value}')

        r = f"{data.get('area_code')}|{data.get('zip_code')}|{data.get('province')}|" \
            f"{data.get('city')}|{data.get('phone_type')}"

        return r

    @classmethod
    def _id_df(cls):
        """
        读取common_id_attribution表中的数据，并转成dataframe格式
        :return:
        """
        sql = "select * from common_id_attribution"
        data = execute_sql(sql, dict_cursor=True)
        if len(data) <= 1:
            logger.info(f'common_id_attribution table is empty, initial data of it.')
            CommonId.insert(initial=True)
            logger.info(f'common_id_attribution table initial data success.')

        df = pd.DataFrame(data)
        df.drop(['id', 'created_time', 'updated_time'], axis=1, inplace=True)

        def zhi_xia_city(name):
            if name is None:
                return name
            if name[:2] in ('北京', '上海', '天津', '重庆'):
                return name[:2] + '市'
            return name

        df['full_city'] = df['full_city'].apply(zhi_xia_city)
        return df

    @classmethod
    def _match_full_place(cls, name, place, id_df):
        """
        根据id_df，匹配province-简称的province-全称，city-简称的city-全称
        :param name: 'province'，或者 'city'
        :param place: 对应name的 province-简称，或者 city-简称
        :param id_df: common_id_attribution表数据的dataframe格式
        :return:
        """
        # 地名类型不是str
        if type(place) != str:
            return

        # 地名为空字符串
        if len(place) < 1:
            return

        def is_in(area, b):
            if b is None:
                return False
            return area in b

        equal_df = id_df[id_df[f"short_{name}"] == place]
        if equal_df.shape[0] > 0:
            return equal_df[f"full_{name}"].values[0]

        similar_df = id_df[id_df[f"full_{name}"].apply(lambda x: is_in(place, x))]
        if similar_df.shape[0] > 0:
            return similar_df[f"full_{name}"].values[0]

    @classmethod
    def _exist_numbers(cls):
        """
        读取已存在common_mobile_attribution表中的所有手机号码（前7位），用于新插入数据的去重
        :return:
        """
        number_sql = "select number from common_mobile_attribution"
        number_data = execute_sql(number_sql, dict_cursor=True)
        number_set = set(pd.DataFrame(number_data)['number'].to_list())
        return number_set

    @classmethod
    def _last_time(cls):
        """
        获取common_mobile_attribution表中最新一条数据的插入时间
        :return: datetime
        """
        last_date_sql = "select max(created_time) as last_time from common_mobile_attribution"
        last_date_data = execute_sql(last_date_sql, dict_cursor=True)
        if len(last_date_data) == 0:
            return
        last_time = last_date_data[0].get('last_time')
        if last_time is None:
            return
        return last_time.date()

    @classmethod
    def _update_user_mobile(cls):
        """
        从 my_v2.credit_user表中读取最新一天的用户手机号（前7位）数据，去重过滤后，标注归属地信息
        :return: dateframe格式的数据
        """
        end = datetime.datetime.now().date()
        start = end - datetime.timedelta(days=1)
        sql = f"select distinct mobile as number from credit_user where created_time between '{start}' and '{end}'"
        data = execute_sql(sql, db='my_v2', dict_cursor=True)

        if len(data) == 0:
            logger.info(f'Not add any new user between {start} and {end} in credit_user table')
            return

        df = pd.DataFrame(data)
        df = df[df['number'].apply(is_valid_phone)]
        df['number'] = df['number'].apply(lambda x: x[:7])
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)

        exist_numbers = cls._exist_numbers()
        df = df[df['number'].apply(lambda x: x not in exist_numbers)]
        logger.info(f"New unique numbers: {df.values.tolist()} between {start} and {end}")

        if df.shape[0] == 0:
            logger.info(f"No valid update data for {cls.table_name} table!")
            return

        df['phone_info'] = df['number'].apply(cls._phone_query)
        pdf = df['phone_info'].str.split('|', expand=True)
        df['city_code'], df['zip_code'], df['short_province'] = pdf[0], pdf[1], pdf[2]
        df['short_city'], df['phone_type'] = pdf[3], pdf[4]
        df.drop(columns=['phone_info'], axis=1, inplace=True)
        return df

    @classmethod
    def _init_data(cls):
        """
        从 my_user_profile.PhoneCity表中读取历史数据，转为dataframe格式
        :return:
        """
        sql = "select distinct code, province, city, corporation, area_code, zip_code from PhoneCity"
        data = execute_sql(sql, db='my_user_profile', dict_cursor=True)

        df = pd.DataFrame(data)
        df.rename(columns={'code': 'number', 'corporation': 'phone_type', 'area_code': 'city_code'}, inplace=True)
        df.rename(columns={'province': 'short_province', 'city': 'short_city'}, inplace=True)
        df = df[df['number'].apply(is_valid_phone_7)]
        df.replace('', np.nan, inplace=True)
        return df

    @classmethod
    def make_data(cls):
        """
        生成手机号归属地相关dataframe格式的数据，并匹配地名全称
        :return:
        """
        last_date = cls._last_time()
        if last_date is None:
            df = cls._init_data()
        else:
            df = cls._update_user_mobile()

        if df is None:
            return

        id_df = cls._id_df()
        province_df = id_df[['full_province', 'short_province']].drop_duplicates()
        city_df = id_df[['full_city', 'short_city']].drop_duplicates()

        df['full_province'] = df['short_province'].apply(lambda x: cls._match_full_place('province', x, province_df))
        df['full_city'] = df['short_city'].apply(lambda x: cls._match_full_place('city', x, city_df))
        return df


class CommonId(CommonBase):
    table_name = 'common_id_attribution'

    @classmethod
    def existed_id(cls):
        sql = "select * from common_id_attribution"
        data = execute_sql(sql, dict_cursor=True)
        return data


    @classmethod
    def make_data(cls):
        """
        请求高德api获取身份证号归属地数据，转为dataframe格式
        :return:
        """
        if len(cls.existed_id()) > 0:
            logger.info(f"Due to {cls.table_name} table already available, this task will not update the table. "
                        f"if you need force update it completely, please set 'initial=True' in keyword arguments")
            return

        url = "https://restapi.amap.com/v3/config/district?parameters"
        params = {
            "key": GAODE_KEY,
            "keywords": "中国",
            "subdistrict": 3
        }
        common_columns = ['adcode', 'citycode', 'name', 'level']

        res_data = query_fmt(url, params)

        try:
            province_data = res_data['districts'][0]['districts']
            province_df = pd.DataFrame(province_data)[common_columns]
        except BaseException:
            logger.error(f'url:{url}-params:{params}-value:{res_data}-except-{sys.exc_info()}')
            return

        # province level 的数据
        province_df.rename(columns={'name': 'full_province', 'adcode': 'number'}, inplace=True)
        province_df['citycode'] = province_df['citycode'].apply(lambda x: x if x != [] else np.nan)

        # city level 的数据
        city_data = []
        for p in province_data:
            city_data.extend(p['districts'])
        city_df = pd.DataFrame(city_data)[common_columns]
        city_df = city_df[city_df['level'] == 'city']
        # HangKong Macao 过滤香港和澳门的district
        # district_df_patch = city_df[city_df['level'] == 'district']
        city_df.rename(columns={'name': 'full_city', 'adcode': 'number'}, inplace=True)

        # district level 的数据
        district_data = []
        for c in city_data:
            district_data.extend(c['districts'])
        district_df = pd.DataFrame(district_data)[common_columns]
        district_df = district_df[district_df['level'] == 'district']
        district_df.rename(columns={'name': 'full_district', 'adcode': 'number'}, inplace=True)

        # 身份证号前两位确定province，取number的前两位数做关联，合并province和city，生成新的city level 数据
        province_df['number_2'] = province_df['number'].apply(lambda x: x[:2])
        city_df['number_2'] = city_df['number'].apply(lambda x: x[:2])
        new_city_df = pd.merge(left=province_df[['full_province', 'number_2']],
                               right=city_df, on='number_2', how='right')

        # 身份证号前四位确定city，取number的前四位数做关联，合并新city和district，生成新的district level 数据
        new_city_df['number_4'] = new_city_df['number'].apply(lambda x: x[:4])
        district_df['number_4'] = district_df['number'].apply(lambda x: x[:4])
        new_district_df = pd.merge(left=new_city_df[['full_province', 'full_city', 'number_4']],
                                   right=district_df, on='number_4', how='right')

        # 删除多余数据
        province_df.drop(['number_2'], axis=1, inplace=True)
        new_city_df.drop(['number_2', 'number_4'], axis=1, inplace=True)
        new_district_df.drop(['number_4'], axis=1, inplace=True)

        # 合并province，新的city，新的district 的数据
        df = pd.concat([province_df, new_city_df, new_district_df], sort=True)
        df.rename(columns={'citycode': 'city_code'}, inplace=True)

        # 添加地名简称
        df['short_province'] = df['full_province'].apply(simplify_name)
        df['short_city'] = df['full_city'].apply(simplify_name)
        df['short_district'] = df['full_district'].apply(simplify_name)
        return df


@app.task
def update_common_date(initial=False, days=10):
    """
    更细common_date表的celery任务
    :param initial: 是否重置，默认不重置
    :param days: 一次更新多少天
    :return:
    """
    CommonDate.days = days
    CommonDate.insert(initial=initial)


@app.task
def update_common_mobile(initial=False):
    """
    更细common_mobile_attribution表的celery任务
    :param initial: 是否重置，默认不重置
    :return:
    """
    CommonMobile.insert(initial=initial)


@app.task
def update_common_id(initial=False):
    """
    更细common_id_attribution表的celery任务
    :param initial: 是否重置，默认不重置
    :return:
    """
    CommonId.insert(initial=initial)


if __name__ == '__main__':
    # CommonId.existed_id()
    # CommonDate.insert()
    # CommonMobile.insert()
    pass

