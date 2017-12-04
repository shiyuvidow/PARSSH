#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/10 11:07
# @Author  : WangWei
# @File    : fabric.py
# @Software: PyCharm

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core import main

if __name__ == '__main__':
    main.Fabric()