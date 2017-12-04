#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/10 14:24
# @Author  : WangWei
# @File    : common.py
# @Software: PyCharm

import ConfigParser
import os
from conf import settings


# 加载主机信息
def load_host_info():
    all_info = {}
    host_file = os.path.join(settings.DB_DIR, 'hosts')
    conf = ConfigParser.ConfigParser()
    conf.read(host_file)
    for group in conf.sections():
        host_info = {}
        for key, value in conf.items(group):
            user, passwd, port = value.split('|')
            host_info.update({
                key: {
                    'username': user,
                    'password': passwd,
                    'port': port
                }
            })
        group_info = {group: host_info}
        all_info.update(group_info)
    return all_info

