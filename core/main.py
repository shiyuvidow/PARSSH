#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/10 11:09
# @Author  : WangWei
# @File    : main.py
# @Software: PyCharm

from optparse import OptionParser
from common import load_host_info
import paramiko
import threading


class Fabric(object):
    def __init__(self):
        # 读取输入参数
        # 主机标志位
        self.hosts_flag = 0
        self.hosts = None
        self.exec_flag = 0
        self.exec_operation = {
            1: 'show_host_info',
            2: 'exec_module',
            3: 'exec_module',
        }
        self.module_list = ['cmd', 'put', 'get']
        self.resource = None
        self.parser = OptionParser()
        self.parser.add_option("-g", "--group", dest='group', help="fabric group")
        self.parser.add_option("-i", "--hosts", dest='hosts', help="fabric hosts")
        self.parser.add_option("-m", "--module", dest='module', help="fabric module, choice: cmd,put,get")
        self.parser.add_option("-a", "--args", dest='args', help="fabric args, uesd in concert with module cmd")
        self.parser.add_option("-s", "--source", dest='source', help="fabric file source, uesd in concert with module "
                                                                     "put or get")
        self.parser.add_option("-d", "--dest", dest='dest', help="fabric file dest, uesd in concert with module put"
                                                                 "or get")
        (self.options, self.args) = self.parser.parse_args()
        self.verify_args()
        if not self.exec_flag:
            exit("invalid cmd")
        self.exec_fabric()

    def verify_args(self):
        # 主机组和主机不能同时存在
        if self.options.group and self.options.hosts:
            exit("group and hosts can't exists together")
        self.hosts = self.options.group or self.options.hosts
        if not self.hosts:
            exit("group or hosts need be required")
        # 主机组标志位1主机标志位2
        self.hosts_flag = 1 if self.options.group else 2
        if self.hosts == 'list':
            self.exec_flag = 1
            return
        if not self.options.module:
            exit("module need be required")
        if self.options.module not in self.module_list:
            exit("unknown module, valid choice: cmd,put,get")
        if self.options.module == 'cmd' and self.options.args:
            self.exec_flag = 2
            return
        if self.options.module == 'put' and self.options.source and self.options.dest:
            self.exec_flag = 3
            return
        if self.options.module == 'get' and self.options.source and self.options.dest:
            self.exec_flag = 3
            return

    def exec_fabric(self):
        # 加载主机信息
        self.resource = load_host_info()
        func_args = self.exec_operation[self.exec_flag]
        if hasattr(self, func_args):
            func = getattr(self, func_args)
            func()
        else:
            self.parser.print_help()

    def show_host_info(self):
        # 主机组标志位1
        if self.hosts_flag == 1:
            print """-------- Fabric GROUP INFO --------"""
            for group in self.resource:
                print(
                    "\033[33;1m{}\033[0m".format(group))
        # 主机标志位2
        if self.hosts_flag == 2:
            for group in self.resource:
                print(
                    "\033[33;1m[{}]\033[0m".format(group))
                for host in self.resource.get(group):
                    print(host)

    def exec_module(self):
        t_obj = []
        # 执行命令2传输文件3
        target = self.transfer_files_single if self.exec_flag == 3 else self.exec_cmd_single
        # 主机组
        if self.hosts_flag == 1:
            if self.hosts in self.resource:
                exec_group_list = self.resource[self.hosts]
                for hostname in exec_group_list:
                    host = exec_group_list[hostname]
                    # print hostname, host.get('username', ''), host.get('password', ''), int(host.get('port', 22))
                    # print self.options.args
                    t = threading.Thread(target=target, args=(
                        hostname, int(host.get('port', 22)), host.get('username', ''), host.get('password', '')
                    ))
                    t.start()
                    # 为了不阻塞后面线程的启动，不在这里join, 先把线程实例放到一个列表
                    t_obj.append(t)
            else:
                exit("unknown group, please check file hosts")

        # 主机组
        if self.hosts_flag == 2:
            exec_white_list = []
            exec_host_list = self.hosts.split(',')
            for group in self.resource:
                for hostname in self.resource[group]:
                    if hostname in exec_host_list and hostname not in exec_white_list:
                        host = self.resource[group][hostname]
                        # print hostname, host.get('username', ''), host.get('password', ''), int(host.get('port', 22))
                        # print self.options.args
                        exec_white_list.append(hostname)
                        t = threading.Thread(target=target, args=(
                            hostname, int(host.get('port', 22)), host.get('username', ''), host.get('password', '')
                        ))
                        t.start()
                        # 为了不阻塞后面线程的启动，不在这里join, 先把线程实例放到一个列表
                        t_obj.append(t)

        active_threads = threading.active_count()
        if active_threads:
            print("----all threads has running...", active_threads)
            # 主线程与子线程是并行的
            # 循环线程实例列表，等待所有线程结束
            for obj in t_obj:
                obj.join()

    def exec_cmd_single(self, hostname, port, username, password):
        # 创建SSH对象
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # 使用用户名密码连接服务器
            ssh.connect(hostname=hostname, port=port, username=username, password=password)
            # 执行命令
            stdin, stdout, stderr = ssh.exec_command(self.options.args)
            result = stdout.read() or stderr.read()
        except Exception as e:
            result = e.message
        finally:
            print """
            ----------HOST %s----------
            %s
            """ % (hostname, result)
            # 关闭结果
            ssh.close()

    def transfer_files_single(self, hostname, port, username, password):
        # 创建Transport对象
        transport = paramiko.Transport((hostname, port))
        try:
            # 使用用户名密码登录
            transport.connect(username=username, password=password)
            # 创建SFTP实例
            sftp = paramiko.SFTPClient.from_transport(transport)
            if self.options.module == 'put':
                # 将本地文件上传至服务器/tmp/test
                sftp.put(self.options.source, self.options.dest)
            if self.options.module == 'get':
                # 将服务器文件下载到本地
                sftp.get(self.options.source, self.options.dest)
            result = """
            ----------HOST %s----------
            Method: %s SRC: %s DEST: %s
            """ % (hostname, self.options.module, self.options.source, self.options.dest)
        except Exception as e:
            result = """
            ----------HOST %s----------
            %s
            """ % (hostname, e.message)
        finally:
            print result
            transport.close()