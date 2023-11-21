# -*- coding: utf-8 -*-

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

class FTPD():
    def __init__(self):
        self.anonymous = True
        self.user = None
        self.password = None
        self.dir = None
        self.port = 21

    def start_ftpd(self):
        authorizer = DummyAuthorizer()
        if self.anonymous:
            #添加匿名用户
            authorizer.add_anonymous(self.dir,perm='elradfmwM')
        else:
            # 添加用户，需要账号和密码登录
            authorizer.add_user(self.user, self.password, self.dir, perm='elradfmwM')
        handler = FTPHandler#初始化处理客户端命令的类
        handler.encoding = 'gbk'
        handler.authorizer = authorizer#选择登录方式(是否匿名)
        address = ('0.0.0.0', int(self.port))#设置服务器的监听地址和端口
        self.server = FTPServer(address, handler)
        self.server.max_cons = 256                              #给链接设置限制
        self.server.max_cons_per_ip = 5
        self.server.serve_forever()                             # 启动FTP

    def stop_ftpd(self):
        self.server.close()
