# encoding=utf-8
__author__ = 'LiuZhe'

import paramiko,logging
from module import globals
from module.myui import mMessageBox

class sshClient():
    def __init__(self, host_ip='', port=22, username='root', password='vdiclientroot', idx=None):
        self.host = host_ip
        self.port = port
        self.username = username
        self.password = password
        self.tran = -1
        self.channel = None
        self.done = 0
        self.gauge = None
        self.console = False
        self.idx = idx
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.worker = None
        self.scp_path = None

    def connect(self, timeout=globals.timeout,server=False):
        "server是云桌面服务器"
        print("connect %s: %s %s" % (self.host, self.username, self.password))
        self.ssh.connect(self.host, username=self.username, password=self.password,timeout=timeout)
        if server:
            self.channel = self.ssh.invoke_shell()
        else:
            self.channel = self.ssh.invoke_shell(term='xterm')
            self.channel.setblocking(0)

    def server_connect(self):
        self.username = globals.vdi_user
        self.password = globals.vdi_user_pwd
        self.connect(timeout=int(globals.timeout), server=True)
        try:
            self.channel.send('su\n')
            buff = ""
            while not buff.endswith(u'：'):  # true
                resp = self.channel.recv(9999)
                buff += resp.decode('utf8')
            self.channel.send(globals.vdi_root_pwd + '\n')
            while not buff.endswith(u'：'):  # true
                resp = self.channel.recv(9999)
                buff += resp.decode('utf8')
            self.channel.send('auxo-config-controller --make_src > /root/admin.src\n')
        except Exception as e:
            mMessageBox(str(e))
            raise


    def show_process(self, curent, total):
        p = 100 * curent / total
        self.gauge.SetValue(p)

    def get_sftp_bak(self):
        self.tran = paramiko.Transport((self.host, int(self.port)))
        self.tran.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(self.tran)
        return sftp

    def get_sftp(self):
        return self.ssh.open_sftp()

    def upload(self, local, remote, gauge=False):
        sftp = self.get_sftp()
        if gauge:
            sftp.put(local, remote, callback=self.show_process)
        else:
            sftp.put(local, remote)
        sftp.close()
        self.done = 1

    def download(self, local, remote):
        sftp = self.get_sftp()
        sftp.get(remote, local)
        sftp.close()

    def send(self, command):
        self.channel.send(command + '\n')


    def send_withlog(self, command):
        logging.info('%s: %s' % (self.host, command))
        self.channel.send(command + '\n')

    def recv(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        return stdout.read().decode()

    def server_recv(self, cmd):
        c = self.ssh.invoke_shell()
        c.send('su\n')
        buff = ""
        while not buff.endswith(u'：'):  # true
            resp = c.recv(9999)
            buff += resp.decode('utf8')

        buff = ''
        c.send(globals.vdi_root_pwd + '\n')
        while not buff.endswith('# '):
            resp = c.recv(9999)
            buff += resp.decode('utf8')

        buff = ''
        c.send(cmd + '\n')
        while not buff.endswith('# '):
            resp = c.recv(9999)
            buff += resp.decode('utf8')
        c.close()
        return buff

    def close(self):
        self.channel.close()
        self.ssh.close()

    #这个方法已经无法判断，网络断开要等超时才会刷新状态
    def linkok(self):
        if not self.channel:
            return False
        if self.channel.get_transport().is_active():
            return True
        else:
            return False
