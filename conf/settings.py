#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/10 11:08
# @Author  : WangWei
# @File    : settings.py
# @Software: PyCharm

import os
import sys

# 程序目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据目录
DB_DIR = os.path.join(BASE_DIR, 'db')