#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import logging
import requests

from my_common.settings import KAFKA_CONNECT_URL

logger = logging.getLogger(__name__)


class KafkaConnector:
    BASE_URL = f'http://{KAFKA_CONNECT_URL}/connectors'
    TIMEOUT = 15

    def __init__(self, connector):
        self.connector = connector
        self.server_name = connector.server_name
        self.config = connector.get_config()

    def run(self):
        """运行 connector"""
        if not self.is_active():
            msg = self.active()
        else:
            msg = self.resume_connector(self.server_name)
            self.update_status()

        logger.info(msg)
        return msg

    def is_active(self):
        """是否已经激活"""
        msg = self.get_connector(self.server_name)
        logger.info(msg)

        return msg.get('status') == 'success'

    def active(self):
        """激活连接器"""
        msg = self.new_connector(self.server_name, self.config)
        logger.info(msg)

        status = msg.get('status')
        if status == 'success':
            self.update_status()
        return msg

    def pause(self):
        """暂停"""
        msg = self.pause_connector(self.server_name)
        logger.info(msg)

        self.update_status()
        return msg

    def refresh(self):
        """刷新"""
        if self.is_active():
            msg = self.update_connector(self.server_name, self.config)
            self.update_status()
        else:
            msg = self.update_status()

        logger.info(msg)
        return msg

    def update_status(self):
        """更新状态"""
        msg = self.get_connector_status(self.server_name)
        logger.info(msg)

        status = msg.get('status')
        if status == 'success':
            state = msg.get('data', {}).get('connector', {}).get('state')
        else:
            state = ''
        self.connector.status = state
        self.connector.save()
        return {'status': 'success'}

    @classmethod
    def get_connectors(cls):
        return cls.get_from_broker(cls.BASE_URL)

    @classmethod
    def get_connector(cls, connector_name):
        url = f'{cls.BASE_URL}/{connector_name}'
        return cls.get_from_broker(url)

    @classmethod
    def get_connector_status(cls, connector_name):
        url = f'{cls.BASE_URL}/{connector_name}/status'
        return cls.get_from_broker(url)

    @classmethod
    def get_connector_tasks(cls, connector_name):
        url = f'{cls.BASE_URL}/{connector_name}/tasks'
        return cls.get_from_broker(url)

    @classmethod
    def get_from_broker(cls, url):
        logger.info(f'url={url}')
        ret = requests.get(url, timeout=cls.TIMEOUT)
        logger.info(f'ret={ret}')

        if ret.status_code in (200, ):
            msg = {'status': 'success', 'data': ret.json()}
        else:
            msg = {
                'status': 'failure',
                'code': ret.status_code,
                'message': '服务器错误' if ret.status_code >= 500 else ret.json().get('message')
            }
        return msg

    @classmethod
    def new_connector(cls, name, config):
        data = {
            'name': name,
            'config': config,
        }
        logger.info(data)
        ret = requests.post(cls.BASE_URL, json=data, timeout=cls.TIMEOUT)
        logger.info(ret)

        if ret.status_code in (200, 201, ):
            msg = {'status': 'success', 'data': ret.json()}
        else:
            msg = {
                'status': 'failure',
                'code': ret.status_code,
                'message': '服务器错误' if ret.status_code >= 500 else ret.json().get('message')
            }
        return msg

    @classmethod
    def update_connector(cls, connector_name, config):
        url = f'{cls.BASE_URL}/{connector_name}/config'
        logger.info(config)
        ret = requests.put(url, json=config, timeout=cls.TIMEOUT)
        logger.info(ret)

        if ret.status_code in (200, 202, ):
            msg = {'status': 'success'}
        else:
            msg = {
                'status': 'failure',
                'code': ret.status_code,
                'message': '服务器错误' if ret.status_code >= 500 else ret.json().get('message')
            }
        return msg

    @classmethod
    def pause_connector(cls, connector_name):
        url = f'{cls.BASE_URL}/{connector_name}/pause'
        ret = requests.put(url, timeout=cls.TIMEOUT)

        if ret.status_code in (200, 202, ):
            msg = {'status': 'success'}
        else:
            msg = {
                'status': 'failure',
                'code': ret.status_code,
                'message': '服务器错误' if ret.status_code >= 500 else ret.json().get('message')
            }
        return msg

    @classmethod
    def resume_connector(cls, connector_name):
        url = f'{cls.BASE_URL}/{connector_name}/resume'
        ret = requests.put(url, timeout=cls.TIMEOUT)

        if ret.status_code in (200, 202, ):
            msg = {'status': 'success'}
        else:
            msg = {
                'status': 'failure',
                'code': ret.status_code,
                'message': '服务器错误' if ret.status_code >= 500 else ret.json().get('message')
            }
        return msg

    @classmethod
    def delete_connector(cls, connector_name):
        url = f'{cls.BASE_URL}/{connector_name}'
        ret = requests.delete(url, timeout=cls.TIMEOUT)

        if ret.status_code in (200, 202, 204):
            msg = {'status': 'success'}
        else:
            msg = {
                'status': 'failure',
                'code': ret.status_code,
                'message': '服务器错误' if ret.status_code >= 500 else ret.json().get('message')
            }
        return msg
