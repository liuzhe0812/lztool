# -*- coding: utf-8 -*-
import logging
import socket, os, threadpool, wx.grid, _thread, struct, wx.aui, threading, wmi
from _thread import start_new_thread, allocate_lock
from .myui import *
from functools import reduce
from module import dhcp, mysql, ftp, globals


class dhcp_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.dhcpd = dhcp.DHCPD()
        self.isDHCP = False

    def creaPanel(self):
        box1 = mStaticBox(self, '地址池配置')
        bSizer11 = wx.BoxSizer(wx.VERTICAL)
        box1.Add(bSizer11)

        box2 = wx.BoxSizer(wx.HORIZONTAL)

        boxall = wx.BoxSizer(wx.VERTICAL)
        boxall.Add(box1, 0, wx.ALL | wx.EXPAND, 10)
        boxall.Add(box2, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(boxall)

        # func1
        self.nic_list = {}
        self.wmiService = wmi.WMI()
        for nic in self.wmiService.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            name = nic.Caption.split(']')[1].strip()
            self.nic_list[name] = nic
        self.cb_nic = mChoice(self, st_label='选择网卡', choice=list(self.nic_list.keys())[::-1], st_size=(80, -1))
        self.cb_nic.choice.Bind(wx.EVT_CHOICE, self.on_nic_sel)
        self.line1 = mInput(self, st_label='起始IP', tc_label='', st_size=(80, 25),
                            tc_size=(150, 25))
        self.line2 = mInput(self, st_label='结束IP', tc_label='', st_size=(80, 25),
                            tc_size=(150, 25))
        self.line3 = mInput(self, st_label='子网掩码', tc_label='', st_size=(80, 25),
                            tc_size=(150, 25))
        self.line4 = mInput(self, st_label='网关', tc_label='', st_size=(80, 25),
                            tc_size=(150, 25))
        self.line5 = mInput(self, st_label='DNS', tc_label='114.114.114.114', st_size=(80, 25),
                            tc_size=(150, 25))

        self.pxe_server = mInput(self, st_label='服务器IP', tc_label='', st_size=(80, 25),
                                 tc_size=(150, 25))
        self.pxe_server.tc.Disable()

        self.cb = wx.CheckBox(self, wx.ID_ANY, "PXE服务器", wx.DefaultPosition, wx.DefaultSize, 0)
        self.cb.Bind(wx.EVT_CHECKBOX, self.on_cb)

        bSizer11.Add(self.cb_nic, 0, wx.TOP, 5)
        bSizer11.Add(self.line1, 0, wx.TOP, 5)
        bSizer11.Add(self.line2, 0, wx.TOP, 5)
        bSizer11.Add(self.line3, 0, wx.TOP, 5)
        bSizer11.Add(self.line4, 0, wx.TOP, 5)
        bSizer11.Add(self.line5, 0, wx.TOP, 5)
        bSizer11.Add(self.cb, 0, wx.TOP, 5)
        bSizer11.Add(self.pxe_server, 0, wx.TOP, 5)

        # func2

        s_dhcp = wx.StaticText(self, -1, "DHCP服务状态")
        s_dhcp.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        s_dhcp.SetForegroundColour((44, 94, 250))

        self.bt_switch = switch(self, key=self.isDHCP)
        self.bt_switch.Bind(wx.EVT_BUTTON, self.on_switch)

        box2.Add(s_dhcp, 0)
        box2.Add(self.bt_switch, 0, wx.LEFT, 20)
        self.on_nic_sel(None)

    def on_switch(self, evt):
        if not self.isDHCP:
            if self.line1.GetValue() and self.line2.GetValue() and self.line3.GetValue() and self.line4.GetValue():
                self.dhcpd.offer_from = self.line1.GetValue()
                self.dhcpd.offer_to = self.line2.GetValue()
                self.dhcpd.subnet_mask = self.line3.GetValue()
                self.dhcpd.router = self.line4.GetValue()
                self.dhcpd.dns_server[0] = self.line5.GetValue()
                self.dhcpd.file_server = self.pxe_server.GetValue()
                self.dhcpd.start_dhcpd()
                self.isDHCP = True
                self.bt_switch.key = True
            else:
                mMessageBox('请完善地址池信息！')
        else:
            self.dhcpd.stop_dhcpd()
            self.isDHCP = False
            self.bt_switch.key = False

    def on_cb(self, evt):
        if self.cb.GetValue():
            self.pxe_server.tc.Enable()
            self.dhcpd.pxe = True
        else:
            self.dhcpd.pxe = False
            self.pxe_server.tc.Disable()

    def on_nic_sel(self, evt):
        nic = self.nic_list[self.cb_nic.GetStringSelection()]
        ip = nic.IPAddress[0]
        ip_header = '.'.join(ip.split('.')[:3])
        start_ip = ip_header + '.101'
        end_ip = ip_header + '.200'
        self.dhcpd.ip = ip
        netmask = nic.IPSubnet[0]
        self.line1.SetValue(start_ip)
        self.line2.SetValue(end_ip)
        self.line3.SetValue(netmask)
        if nic.DefaultIPGateway:
            gw = nic.DefaultIPGateway[0]
            self.line4.SetValue(gw)
        else:
            self.line4.SetValue(ip)


class scan_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.count = -1
        self.scan_ip = ''
        self.lock = allocate_lock()
        self.left = 0
        self.total = 0

    def creaPanel(self):
        panel1 = wx.Panel(self)  # IP
        panel2 = wx.Panel(self)  # 端口
        panel1.SetBackgroundColour(self.parent.GetBackgroundColour())
        panel2.SetBackgroundColour(self.parent.GetBackgroundColour())

        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        bSizer1.Add(panel1, 1, wx.EXPAND)
        bSizer2 = wx.BoxSizer(wx.VERTICAL)
        bSizer2.Add(panel2, 1, wx.EXPAND)
        bSizer11 = wx.BoxSizer(wx.VERTICAL)
        bSizer21 = wx.BoxSizer(wx.VERTICAL)

        box1 = mStaticBox(panel1, 'IP扫描')
        box1.Add(bSizer11, 1, wx.EXPAND)
        box2 = mStaticBox(panel2, '端口扫描')
        box2.Add(bSizer21, 1, wx.EXPAND)
        panel1.SetSizer(box1)
        panel2.SetSizer(box2)

        line1 = wx.BoxSizer(wx.HORIZONTAL)
        line1.Add(bSizer1, 1, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 10)
        line1.Add(bSizer2, 1, wx.EXPAND | wx.ALL, 10)
        bSizerALL = wx.BoxSizer(wx.HORIZONTAL)
        bSizerALL.Add(line1, 0, wx.EXPAND)
        self.SetSizer(bSizerALL)

        # IP
        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)
        self.start_ip = mInput(panel1, st_label='IP范围')
        bSizer6.Add(self.start_ip, 1)

        self.end_ip = mInput(panel1, st_label='至')
        bSizer6.Add(self.end_ip, 1)
        self.bt1 = mButton(panel1, "开始", size=(-1, 23), color='deepgreen')
        bSizer6.Add(self.bt1, 0)

        bSizer11.Add(bSizer6, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        bSizer11.Add((0, 5))

        self.ip_list = mListCtrl(panel1, colnames=['IP', 'Ping', 'Hostname'], border=False)
        self.ip_list.SetColumnWidth(0, 150)
        self.il = wx.ImageList(16, 16, True)
        self.greenball = wx.Bitmap('bitmaps/greenball.png', wx.BITMAP_TYPE_PNG)
        self.redball = wx.Bitmap('bitmaps/redball.png', wx.BITMAP_TYPE_PNG)
        self.il.Add(self.redball)
        self.il.Add(self.greenball)
        self.ip_list.AssignImageList(self.il, wx.IMAGE_LIST_SMALL)

        bSizer11.Add(self.ip_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # 端口
        bSizer16 = wx.BoxSizer(wx.HORIZONTAL)

        self.start_port = mInput(panel2, st_label='端口范围')
        bSizer16.Add(self.start_port, 0, wx.ALL, 0)

        self.end_port = mInput(panel2, st_label='至')
        bSizer16.Add(self.end_port, 0, wx.ALL, 0)

        bSizer18 = wx.BoxSizer(wx.HORIZONTAL)

        self.d_ip = mInput(panel2, st_label='目标IP', tc_size=(120, -1))
        bSizer18.Add(self.d_ip, 0, wx.ALL, 0)
        bSizer18.Add((0, 0), 1, wx.EXPAND, 5)

        self.bt2 = mButton(panel2, "开始", size=(-1, 25), color='deepgreen')
        bSizer18.Add(self.bt2, 0, wx.ALIGN_CENTER, 0)

        bSizer21.Add(bSizer16, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        bSizer21.Add(bSizer18, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.port_result = wx.TextCtrl(panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER)
        bSizer21.Add(self.port_result, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.bt1.Bind(wx.EVT_BUTTON, lambda evt, method=self.ip_scan: self.new_thread(method))
        self.bt2.Bind(wx.EVT_BUTTON, lambda evt, method=self.port_scan: self.new_thread(method))

    def new_thread(self, method):
        start_new_thread(method, ())

    def ip_scan(self):
        # globals.status.show_gauge()
        self.ip_list.DeleteAllItems()
        ip_list = []
        start_ip = self.start_ip.GetValue()
        self.start_num = reduce(lambda x, y: (x << 8) + y, list(map(int, start_ip.split('.'))))
        end_ip = self.end_ip.GetValue()
        end_num = reduce(lambda x, y: (x << 8) + y, list(map(int, end_ip.split('.'))))
        self.count = end_num - self.start_num + 1
        self.left = end_num - self.start_num + 1
        if not self.count < 0:
            for i in range(end_num - self.start_num + 1):
                num2ip = lambda x: '.'.join([str(x // (256 ** i) % 256) for i in range(3, -1, -1)])
                cur_ip = num2ip((self.start_num + i))
                ip_list.append(cur_ip)
            # globals.status.SetStatusText('扫描中...', 1)
            try:
                n = 0
                for ip in ip_list:
                    self.ip_list.addRow([ip, '', ''])
                    _thread.start_new_thread(self.ping, (ip,))
                    n += 1
            except Exception as e:
                logging.error(e)
        else:
            mMessageBox.log('IP输入有误!')

    def ping(self, ip):
        output = list(os.popen('ping %s -n 1' % ip).readlines())
        flag = False
        delay = None
        for line in output:
            if not line:
                continue
            if str(line).upper().find("TTL") >= 0:
                flag = True
                delay = str(line).split()[-2]
                a = delay.split('=')
                if len(a) == 2:
                    delay = a[1]
                else:
                    delay = '<1ms'
                break
        self.lock.acquire()
        num = reduce(lambda x, y: (x << 8) + y, list(map(int, ip.split('.'))))
        index = num - self.start_num
        if flag:
            self.ip_list.SetItem(index, 1, delay)
            self.ip_list.SetItemImage(index, 1, 1)
            self.total += 1
            _thread.start_new_thread(self.get_host_name, (ip, index))
        else:
            self.ip_list.SetItemImage(index, 0, 0)
            self.ip_list.SetItem(index, 1, '非活动')
        self.left -= 1
        per = (self.count - self.left) * 100 // self.count
        # globals.status.gauge.SetValue(per)
        # globals.status.SetStatusText('%s%%' % per, 2)
        if self.left == 0:
            self.TopLevelParent.Message('扫描范围：%s - %s\n'
                                        '共扫描IP：%s\n'
                                        '活动主机：%s' % (
                                            self.start_ip.GetValue(), self.end_ip.GetValue(), self.count, self.total))
            self.total = 0
        self.lock.release()

    def get_host_name(self, ip, index):
        output = os.popen('ping -a %s -n 1' % ip).readlines()
        if len(output[1].split(' ')) == 7:
            host = output[1].split(' ')[2]
            self.ip_list.SetItem(index, 2, host)
        else:
            self.ip_list.SetItem(index, 2, 'N/A')

    def port_scan(self):
        port_list = []
        start_port = int(self.start_port.GetValue())
        end_port = int(self.end_port.GetValue())
        self.left = self.count = end_port - start_port + 1
        self.scan_ip = self.d_ip.GetValue()
        # globals.status.gauge.Show()
        # globals.status.Layout()
        if not self.count < 0:
            for i in range(end_port - start_port + 1):
                port_list.append(start_port + i)
            self.bt2.Disable()
            pool = threadpool.ThreadPool(700)
            requests = threadpool.makeRequests(self.socket_port, port_list)
            [pool.putRequest(req) for req in requests]
            pool.wait()
            self.bt2.Enable()
        else:
            mMessageBox('端口输入有误')

    def socket_port(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex((self.scan_ip, port))
            s.close()
        except:
            self.port_result.AppendText('端口扫描异常\n')
        self.lock.acquire()
        if result == 0:
            self.port_result.AppendText(self.scan_ip + ': ' + str(port) + ' 端口开放\n')
            self.total += 1
        self.left -= 1
        per = (self.count - self.left) * 100 // self.count
        # globals.status.gauge.SetValue(per)
        # globals.status.SetStatusText('%s%%' % per, 1)
        if self.left == 0:
            self.port_result.AppendText('**** 扫描完成，总数为: %s ****' % self.total)
            self.total = 0
        self.lock.release()


class wol_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.parent = parent

    def creaPanel(self):
        panel1 = wx.Panel(self)
        panel2 = wx.Panel(self)
        panel3 = wx.Panel(self)
        panel1.SetBackgroundColour(self.parent.GetBackgroundColour())
        panel2.SetBackgroundColour(self.parent.GetBackgroundColour())
        panel3.SetBackgroundColour(self.parent.GetBackgroundColour())

        box1 = mStaticBox(panel1, label='批量唤醒')
        box2 = mStaticBox(panel2, label='终端唤醒')
        box3 = mStaticBox(panel3, label='唤醒信息')
        panel1.SetSizer(box1)
        panel2.SetSizer(box2)
        panel3.SetSizer(box3)

        bSizer11 = wx.BoxSizer(wx.VERTICAL)
        bSizer21 = wx.BoxSizer(wx.VERTICAL)
        bSizer31 = wx.BoxSizer(wx.VERTICAL)
        box1.Add(bSizer11, 0, wx.EXPAND)
        box2.Add(bSizer21, 1, wx.EXPAND)
        box3.Add(bSizer31, 1, wx.EXPAND)

        col1 = wx.BoxSizer(wx.VERTICAL)
        col2 = wx.BoxSizer(wx.VERTICAL)
        col1.Add(panel1, 0, wx.EXPAND | wx.LEFT, 10)
        col1.Add((0, 20))
        col1.Add(panel2, 0, wx.EXPAND | wx.LEFT, 10)
        col2.Add(panel3, 1, wx.EXPAND | wx.LEFT, 10)

        bSizerAll = wx.BoxSizer(wx.HORIZONTAL)
        bSizerAll.Add(col1, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        bSizerAll.Add(col2, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        self.SetSizer(bSizerAll)

        # func1
        bSizer7 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText1 = wx.StaticText(panel1, wx.ID_ANY, "起始MAC地址：", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        bSizer7.Add(self.m_staticText1, 0, wx.ALIGN_CENTER, 5)

        self.mac1 = wx.TextCtrl(panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(25, -1),
                                0)
        bSizer7.Add(self.mac1, 0, wx.ALL, 5)

        self.m_staticText2 = wx.StaticText(panel1, wx.ID_ANY, "-", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText2.Wrap(-1)
        bSizer7.Add(self.m_staticText2, 0, wx.ALIGN_CENTER, 5)

        self.mac2 = wx.TextCtrl(panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(25, -1),
                                0)
        bSizer7.Add(self.mac2, 0, wx.ALL, 5)

        self.m_staticText3 = wx.StaticText(panel1, wx.ID_ANY, "-", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText3.Wrap(-1)
        bSizer7.Add(self.m_staticText3, 0, wx.ALIGN_CENTER, 5)

        self.mac3 = wx.TextCtrl(panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(25, -1),
                                0)
        bSizer7.Add(self.mac3, 0, wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(panel1, wx.ID_ANY, "-", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText4.Wrap(-1)
        bSizer7.Add(self.m_staticText4, 0, wx.ALIGN_CENTER, 5)

        self.mac4 = wx.TextCtrl(panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(25, -1),
                                0)
        bSizer7.Add(self.mac4, 0, wx.ALL, 5)

        self.m_staticText5 = wx.StaticText(panel1, wx.ID_ANY, "-", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText5.Wrap(-1)
        bSizer7.Add(self.m_staticText5, 0, wx.ALIGN_CENTER, 5)

        self.mac5 = wx.TextCtrl(panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(25, -1),
                                0)
        bSizer7.Add(self.mac5, 0, wx.ALL, 5)

        self.m_staticText6 = wx.StaticText(panel1, wx.ID_ANY, "-", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText6.Wrap(-1)
        bSizer7.Add(self.m_staticText6, 0, wx.ALIGN_CENTER, 5)

        self.mac6 = wx.TextCtrl(panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(25, -1),
                                0)
        bSizer7.Add(self.mac6, 0, wx.TOP | wx.LEFT, 5)

        bSizer11.Add(bSizer7, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        bSizer8 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText15 = wx.StaticText(panel1, wx.ID_ANY, "数量：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        bSizer8.Add(self.m_staticText15, 0, wx.ALIGN_CENTER, 5)

        self.num = wx.TextCtrl(panel1)
        bSizer8.Add(self.num, 0, wx.ALIGN_CENTER, 5)
        bSizer8.Add((0, 0), 1, wx.EXPAND, 5)
        self.bt_wake = mButton(panel1, "唤醒", color='deepgreen', size=(-1, 25))
        self.bt_wake.Bind(wx.EVT_BUTTON, self.multi_wake)
        bSizer8.Add(self.bt_wake, 0, wx.LEFT | wx.ALIGN_CENTER, 5)

        bSizer11.Add(bSizer8, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # func2
        bSizer4 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText16 = wx.StaticText(panel2, wx.ID_ANY, "主控IP：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_staticText16.Wrap(-1)
        bSizer4.Add(self.m_staticText16, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.consoleIP = wx.TextCtrl(panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                     wx.DefaultSize, 0)
        bSizer4.Add(self.consoleIP, 1, wx.ALIGN_CENTER, 5)
        bSizer4.Add((0, 0), 1, wx.EXPAND)
        self.bt_getData = mButton(panel2, "获取数据", color='deepgreen', size=(-1, 25))
        self.bt_getData.Bind(wx.EVT_BUTTON, self.get_data)
        bSizer4.Add(self.bt_getData, 0, wx.LEFT, 5)

        bSizer21.Add(bSizer4, 0, wx.TOP | wx.RIGHT | wx.EXPAND, 5)

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = mListCtrl(panel2, ['教室'])
        self.listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.choice)
        bSizer5.Add(self.listCtrl, 1, wx.ALL | wx.EXPAND, 5)

        bSizer21.Add(bSizer5, 1, wx.EXPAND, 5)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText17 = wx.StaticText(panel2, wx.ID_ANY, "当前选中：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_staticText17.Wrap(-1)
        bSizer6.Add(self.m_staticText17, 0, wx.ALIGN_CENTER, 5)

        self.classroom = wx.StaticText(panel2, wx.ID_ANY, "无", wx.DefaultPosition, wx.DefaultSize,
                                       0 | wx.SIMPLE_BORDER)
        self.classroom.Wrap(-1)
        bSizer6.Add(self.classroom, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        bSizer6.Add((0, 0), 1, wx.EXPAND, 5)

        self.bt_vdi_wake = mButton(panel2, "唤醒", color='deepgreen', size=(-1, 25))
        self.bt_vdi_wake.Bind(wx.EVT_BUTTON, self.vdi_wake)
        bSizer6.Add(self.bt_vdi_wake, 0, 0, 5)

        bSizer21.Add(bSizer6, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.result = wx.TextCtrl(panel3, style=wx.TE_MULTILINE | wx.TE_READONLY)
        bSizer31.Add(self.result, 1, wx.ALL | wx.EXPAND, 5)

    def choice(self, evt):
        self.pool_name = evt.GetText()
        self.classroom.SetLabel(self.pool_name)

    def get_data(self, evt):
        host = self.consoleIP.GetValue()
        self.db = mysql.vdi_db()
        self.db.host = host
        try:
            self.db.connect()
        except Exception as e:
            mMessageBox(str(e))
        num = self.db.cur.execute('select name from thor_console.pool where deleted=0')
        data = self.db.cur.fetchall()
        for i in range(num):
            id = self.listCtrl.InsertItem(0, data[i][0])

    def multi_wake(self, evt):
        num = int(self.num.GetValue())
        mac = self.mac1.GetValue() + self.mac2.GetValue() + self.mac3.GetValue() + self.mac4.GetValue() + self.mac5.GetValue() + self.mac6.GetValue()
        for i in range(num):
            tmp = int(mac, 16) + i
            mac_addr = str(hex(tmp))[-12:]
            self.WOL(mac_addr)
            self.result.AppendText('wake up %s\n' % mac_addr)
        self.result.AppendText('finish!')

    def vdi_wake(self, evt):
        self.db.cur.execute(
            'select client_name,client_mac from thor_console.client_edu as c INNER JOIN thor_console.pool as p where c.pool_id=p.id and p.name="%s"' % self.pool_name)
        data = self.db.cur.fetchall()
        for i in data:
            mac = i[1].replace(':', '')
            self.WOL(mac)
            self.result.AppendText('wake up %s(%s)\n' % (i[1], i[0]))

    def WOL(self, macaddress):
        if len(macaddress) == 12:
            pass
        elif len(macaddress) == 12 + 5:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, '')
        else:
            raise ValueError('Incorrect MAC address format')
        data = ''.join(['FFFFFFFFFFFF', macaddress * 16])
        send_data = b''
        for i in range(0, len(data), 2):
            byte_dat = struct.pack('B', int(data[i: i + 2], 16))
            send_data = send_data + byte_dat
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(send_data, ('255.255.255.255', 7))
        sock.close()


class ftp_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.ftpd = ftp.FTPD()

    def creaPanel(self):
        boxall = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(boxall)

        box1 = mStaticBox(self, 'FTP服务器')
        boxall.Add(box1, 0, wx.TOP | wx.LEFT, 10)

        panel1 = wx.Panel(self)
        panel1.SetBackgroundColour(self.parent.GetBackgroundColour())
        box1.Add(panel1, 1, wx.EXPAND)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        panel1.SetSizer(sizer1)

        self.cb = wx.CheckBox(panel1, -1, '使用账户密码登录', pos=(20, 20), size=(200, -1))
        self.cb.Bind(wx.EVT_CHECKBOX, self.on_cb)
        sizer1.Add(self.cb, 0, wx.EXPAND | wx.LEFT | wx.TOP, 5)

        font = wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL)
        userlabel = wx.StaticText(panel1, label="用户名:", pos=(35, 45))
        userlabel.SetFont(font)
        self.usertext = wx.TextCtrl(panel1, -1, 'user', size=(95, 20), pos=(90, 42), style=wx.TE_READONLY)
        passlabel = wx.StaticText(panel1, label="密码:", pos=(195, 45))
        passlabel.SetFont(font)
        self.passtext = wx.TextCtrl(panel1, -1, '123456', size=(95, 20), pos=(235, 42))
        self.passtext.SetEditable(False)
        sizer12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer12.Add(userlabel, 0, wx.CENTER)
        sizer12.Add(self.usertext, 1)
        sizer12.Add(passlabel, 0, wx.CENTER | wx.LEFT, 5)
        sizer12.Add(self.passtext, 1)
        sizer1.Add(sizer12, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, 5)

        dirlabel = wx.StaticText(panel1, label="FTP目录:")
        dirlabel.SetFont(font)
        self.dirPicker = wx.DirPickerCtrl(panel1, wx.ID_ANY, wx.EmptyString, "选择FTP目录",
                                          style=wx.DIRP_DEFAULT_STYLE | wx.NO_BORDER | wx.DIRP_SMALL)
        sizer13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer13.Add(dirlabel, 0, wx.CENTER)
        sizer13.Add(self.dirPicker, 1)
        sizer1.Add(sizer13, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)

        sizer14 = wx.BoxSizer(wx.HORIZONTAL)
        portlabel = wx.StaticText(panel1, label="FTP端口:")
        portlabel.SetFont(font)
        self.porttext = wx.TextCtrl(panel1, -1, '21')
        sizer14.Add(portlabel, 0, wx.CENTER)
        sizer14.Add(self.porttext, 0)
        sizer1.Add(sizer14, 0, wx.TOP | wx.LEFT | wx.EXPAND | wx.RIGHT, 5)

        self.bt_start = mButton(panel1, '启动FTP', 'deepgreen')
        self.bt_start.Bind(wx.EVT_BUTTON, self.on_bt_start)
        sizer1.Add(self.bt_start, 0, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, 5)

        self.urllabel = wx.StaticText(panel1, label="")
        self.urllabel.SetFont(font)
        self.urllabel.SetForegroundColour('red')
        sizer1.Add(self.urllabel, 1, wx.ALL, 5)

    def on_cb(self, event):
        self.usertext.SetEditable(event.IsChecked())
        self.passtext.SetEditable(event.IsChecked())

    def on_bt_start(self, evt):
        if not self.dirPicker.GetPath():
            mMessageBox('请选择FTP目录')
            return
        if self.bt_start.GetLabel() == '启动FTP':
            self.bt_start.SetLabel('关闭FTP')
            # 创建线程启动FTP
            self.ftpd.port = self.porttext.GetValue()
            self.ftpd.user = self.usertext.GetValue()
            self.ftpd.password = self.passtext.GetValue()
            self.ftpd.anonymous = bool(1 - self.cb.GetValue())
            self.ftpd.dir = self.dirPicker.GetPath()
            t = threading.Thread(target=self.ftpd.start_ftpd)
            t.setDaemon(True)
            t.start()
            iplist = socket.gethostbyname_ex(socket.gethostname())[2]
            ftpurl = ''
            if iplist:
                for ip in iplist:
                    ftpurl += 'FTP地址:ftp://' + ip + ':' + self.porttext.GetValue() + '\n'
            self.urllabel.SetLabel(ftpurl)
            self.urllabel.SetSize(self.urllabel.GetBestSize())
            self.SetSize(self.GetBestSize())
        else:
            dlg1 = wx.MessageDialog(None, "FTP正在运行，确认退出吗？", "退出", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dlg1.ShowModal() == wx.ID_YES:
                self.bt_start.SetLabel('启动FTP')
                self.urllabel.SetLabel('')
                self.urllabel.SetSize(self.urllabel.GetBestSize())
                self.SetSize(self.GetBestSize())
                self.ftpd.stop_ftpd()


class tool_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        bSizerAll = wx.BoxSizer(wx.HORIZONTAL)

        p1 = dhcp_panel(self)
        p2 = scan_panel(self)
        p3 = wol_panel(self)
        p4 = ftp_panel(self)
        panels = [p1, p2, p3, p4]
        for p in panels:
            p.creaPanel()

        labels = ['DHCP服务', '网络扫描', '网络唤醒', 'FTP服务']
        self.lb = mLabelBook(self, labels, panels)
        self.lb.SetFontBold(True)
        bSizerAll.Add(self.lb, 1, wx.EXPAND)
        self.SetSizer(bSizerAll)
        self.Layout()

