#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import base64
from pyDes import des, PAD_PKCS5, ECB
from my_common.settings import DES_KEY


class DESEncrypt:
    def __init__(self, key, iv, padding_mode=PAD_PKCS5):
        self.mode = ECB
        self.padding_mode = padding_mode
        self.key = bytes(key, encoding='utf-8')
        self.iv = iv

    def encrypt(self, text):
        """
        DES 加密
        :param text: 原始字符串
        :return: 加密后字符串
        """
        secret_key = self.key
        k = des(secret_key, self.mode, self.iv, pad=None, padmode=self.padding_mode)
        en = k.encrypt(bytes(text, encoding='utf-8'), padmode=PAD_PKCS5)
        ret = base64.encodebytes(en)
        return str(ret, encoding='utf-8')

    def decrypt(self, text):
        """
        DES 解密
        :param text: 密文
        :return:  解密后的字符串
        """
        secret_key = self.key
        k = des(secret_key, self.mode, pad=None, padmode=self.padding_mode)

        if isinstance(text, str):
            text = bytes(text, encoding='utf-8')
        de = k.decrypt(base64.decodebytes(text), padmode=self.padding_mode)
        return str(de, encoding='utf-8')


des_encryptor = DESEncrypt(key=DES_KEY, iv='11223344')


if __name__ == '__main__':
    base = DESEncrypt(key=DES_KEY, iv='11223344')
    data = "123456"
    print(base.encrypt(data))
    print(base.decrypt(base.encrypt(data)))
    print(base.decrypt(bytes('DROrgEhWkYo=', encoding='utf-8')))
    print(base.decrypt('DROrgEhWkYo=\n'))
