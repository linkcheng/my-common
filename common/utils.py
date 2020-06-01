import re
import sys
import logging
from json import JSONDecodeError

import jieba
import requests
import numpy as np

from requests.exceptions import RequestException, ConnectTimeout, ReadTimeout
from django.db import connection, connections
from django.db.utils import OperationalError


logger = logging.getLogger('common_utils')


def is_valid_phone(number):
    """
    简单判断是否是手机号
    :return:
    """
    return bool(re.match(r'1[3-9]\d{9}', number))


def is_valid_phone_7(number):
    """
    简单判断是否是手机号前7位
    :return:
    """
    if type(number) != str:
        return False
    return bool(re.match(r'1[3-9]\d{5}', number))


def execute_sql(sql, db=None, dict_cursor=False):
    """
    执行sql语句
    :param sql: sql语句
    :param db: 指定数据库
    :param dict_cursor: 是否返回dict格式的数据
    :return:
    """
    if db is None:
        conn = connection
    else:
        conn = connections[db]

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            data = cur.fetchall()
            if dict_cursor:
                data = [dict(zip([c[0] for c in cur.description], row)) for row in data]
            connection.close()
    except OperationalError:
        logger.error(f"SQL: {sql} execute failed! "
                     f"exception- {sys.exc_info()}")
        raise OperationalError
    return data


def simplify_name(name):
    """
    简化地名全称
    1，去掉地区级别名称，如，省/市/县等等
    2，去掉自治地方民族名后缀，如，都安瑶族自治县，要先去掉自治县，再去掉瑶族
    3，特别的，如果地名只有两个字，不做简化，直接返回
    :param name: 地名
    :return:
    """
    onw_word = ('省', '市', '区', '县', '盟', '旗')
    two_words = ('新区', '左旗', '右旗', '地区', '林区', '前旗', '中旗', '后旗')
    add_words = ('自治区', '自治县', '自治州', '自治旗')

    minorities = ('壮族', '回族', '满族', '维吾尔族', '苗族', '彝族', '土家族', '藏族', '蒙古族', '侗族', '布依族', '瑶族',
                  '白族', '朝鲜族', '哈尼族', '黎族', '哈萨克族', '傣族', '畲族', '傈僳族', '东乡族', '仡佬族', '拉祜族',
                  '佤族', '水族', '纳西族', '羌族', '土族', '仫佬族', '锡伯族', '柯尔克孜族', '景颇族', '达斡尔族', '撒拉族',
                  '布朗族', '毛南族', '塔吉克族', '普米族', '阿昌族', '怒族', '鄂温克族', '京族', '基诺族', '德昂族', '保安族',
                  '俄罗斯族', '裕固族', '乌孜别克族', '门巴族', '鄂伦春族', '独龙族', '赫哲族', '高山族', '珞巴族', '塔塔尔族')
    del_words = ('山区', '海区', '东区', '西区', '北区', '南区')

    special_area = {'万柏林区': '万柏林', '博尔塔拉蒙古自治州': '博尔塔拉', '内蒙古自治区': '内蒙古',
                    '巴音郭楞蒙古自治州': '巴音郭楞', '积石山保安族东乡族撒拉族自治县': '积石山',
                    '前郭尔罗斯蒙古族自治县': '前郭尔罗斯', '镇沅彝族哈尼族拉祜族自治县': '镇沅',
                    '孟连傣族拉祜族佤族自治县': '孟连', '耿马傣族佤族自治县': '耿马',
                    '黔西南布依族苗族自治州': '黔西南', '和布克赛尔蒙古自治县': '和布克赛尔',
                    '塔什库尔干塔吉克自治县': '塔什库尔干', '道真仡佬族苗族自治县': '道真',
                    '彭水苗族土家族自治县': '彭水', '金秀瑶族自治县': '金秀', '都安瑶族自治县': '都安',
                    '龙胜各族自治县': '龙胜', '阿克塞哈萨克族自治县': '阿克塞', '张家川回族自治县': '张家川',
                    '元江哈尼族彝族傣族自治县': '元江'}

    for minority in minorities + add_words:
        jieba.add_word(minority, freq=200000)

    for word in del_words:
        jieba.del_word(word)

    if name is np.nan:
        return name

    if special_area.get(name):
        return special_area.get(name)

    if len(name) < 3:
        return name

    if name[-4:] in ('特别行政区',):
        return name[:-5]

    if name[-2:] in ('联合旗',):
        return name[:-3]

    if len(name) > 3 and name[-2:] in two_words:
        return name[:-2]

    if name[-1] in onw_word and '自治' not in name:
        return name[:-1]

    new_names = jieba.lcut(name, cut_all=True)
    simple_name = new_names[0]

    return simple_name


def query_fmt(url, params):
    """
    通用请求处理格式
    :param url: 链接
    :param params: 参数
    :return:
    """
    result = dict()

    try:
        ret = requests.get(url, params, timeout=15)
    except ConnectTimeout as e:
        logger.error(f'ConnectTimeout url:{url}-params:{params}-exp:{e}')
    except ReadTimeout as e:
        logger.error(f'ReadTimeout url:{url}-params:{params}-exp:{e}')
    except RequestException as e:
        logger.error(f'RequestException url:{url}-params:{params}-exp:{e}')
    else:
        if ret.status_code == 200:
            try:
                result = ret.json()
                logger.info(f'url:{url}-params:{params}-result:{result}{type(result)}')
            except JSONDecodeError as e:
                logger.error(f'url:{url}-params:{params}'
                             f'-msg:{ret.text}-exp:{e}')
        else:
            logger.info(f'[ERROR requests]url:{url}-params:{params}'
                        f'-msg:{ret.text}-status_code:{ret.status_code}')

    return result

