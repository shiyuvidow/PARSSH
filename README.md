# PARSSH

Version: 2.7

类 Fabric 主机管理程序PARSSH开发：
1. 列出主机组或者主机列表, 主机数据储存在db目录下的hosts文件中，形式如：ip=username|password|port
2. 指定主机或者主机组执行命令
3. 指定主机或者主机组传输文件（上传/下载）
4. 使用多线程
5. 不同主机的用户名密码、端口可以不同

参数说明：

```
# -h或者--help，帮助说明
# -g或--group，主机组
# -i或--hosts，主机
# -m或--module， 模块，可选cmd,put,get
# -a或--args，执行命令，与模块cmd配合使用
# -s或--source， 文件源路径，与模块put或get配合使用
# -d或--dest， 文件目标路径，与模块put或get配合使用
```

使用说明：
```进到PARSSH的bin目录
# 进到PARSSH的bin目录下
# 显示所有主机组
python fabric.py -g list
# 显示所有主机
python fabric.py -i list
# 主机组执行命令，命令请用双引号引起来，否则不识别
python fabric.py -g group1 -m cmd -a "pwd"
# 主机执行命令
python fabric.py -i 172.30.150.30,172.30.150.33 -m cmd -a "ps -ef|grep nginx"
# 上传文件
python fabric.py -g group2 -m put -s "E:/test" -d "/tmp/test"
# 下载文件
python fabric.py -i 172.30.150.29 -m get -s "/tmp/test" -d "test"
```