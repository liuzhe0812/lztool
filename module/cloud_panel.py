# -*- coding: utf-8 -*-
import logging

import wx.grid, wx.aui, webbrowser, pyperclip, base64
from .myui import *
from module import mysql, ssh, methods, dialogs, globals
from wx.html2 import WebView


class login_panel(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        self.vdi_conn = parent.vdi_conn
        self.vdi_db = parent.vdi_db
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.creaPanel()

    def creaPanel(self):
        self.SetBackgroundColour(globals.bgcolor)

        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc_server = mInput(self, st_label='主控IP', tc_size=(120, 23), st_size=(80, 23))
        self.bt_connect = mButton(self, '连接', color='blue', size=(45, 23), font_size=10)
        self.bt_connect.Bind(wx.EVT_BUTTON, self.on_connect)
        self.tc_server.tc.SetValue('172.31.13.51')
        bSizer1.Add(self.tc_server, 0, wx.LEFT | wx.TOP, 50)
        bSizer1.Add((0, 10), 0)
        bSizer1.Add(self.bt_connect, 0, wx.TOP, 50)

        self.SetSizer(bSizer1)
        self.Centre(wx.BOTH)
        self.Layout()

    def on_connect(self, evt):
        host = self.tc_server.GetValue()
        self.vdi_conn.password = globals.vdi_user_pwd
        self.vdi_conn.host = host
        self.vdi_db.host = host
        try:
            self.vdi_db.connect()
            self.vdi_conn.server_connect()
        except Exception as e:
            mMessageBox(str(e))
            return
        self.parent.server_panel.refresh(None)
        self.Hide()
        self.parent.lb.Show()
        self.parent.Layout()


class vdi_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.vdi_db = mysql.vdi_db()
        self.vdi_conn = ssh.sshClient()
        self.creaPanel()

    def creaPanel(self):
        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)
        bSizer2.Add((0, 5))

        self.log_panel = vdi_log_panel(self)
        self.log = self.log_panel.log

        self.login_panel = login_panel(self)
        self.server_panel = vdi_server_panel(self)
        self.image_panel = vdi_image_panel(self)
        self.vm_panel = vdi_vm_panel(self)
        self.network_panel = vdi_network_panel(self)

        images = ['node.png', 'image.png', 'vm.png', 'vdi_network.png', 'vdi_log.png']
        panels = [self.server_panel, self.image_panel, self.vm_panel, self.network_panel, self.log_panel]
        labels = ['服务器', '模板', '桌面', '网络', '日志']
        self.lb = mLabelBook(self, labels, panels, images)
        self.lb.Hide()
        self.lb.Bind(LB.EVT_IMAGENOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        bSizer1.Add(self.login_panel, 0, wx.EXPAND)
        bSizer1.Add(self.lb, 1, wx.EXPAND)

        self.SetSizer(bSizer1)

    def OnPageChanged(self, evt):
        obj = evt.GetEventObject()
        page = obj.GetCurrentPage()
        page.Layout()
        if evt.GetSelection() != 4:
            page.refresh(None)


class vdi_server_panel(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        self.vdi_conn = parent.vdi_conn  # 此时还未连接
        self.vdi_db = parent.vdi_db
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.compute_conn_dic = {}
        self.console_is_compute = None
        self.creaPanel()

    def creaPanel(self):
        self.SetBackgroundColour(globals.bgcolor)

        bSizerall = wx.BoxSizer(wx.VERTICAL)
        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # bt_time = mButton(self, '时间同步', 'blue', font_size=10, size=(60, 23))
        # bt_time.Bind(wx.EVT_BUTTON, self.on_bt_time)
        # bSizer1.Add(bt_time, 0, wx.LEFT, 5)
        bSizer1.Add((0, 0), 1)

        self.bt_refresh = mButton(self, '刷新', color='blue', size=(40, 23), font_size=10)
        self.bt_refresh.Bind(wx.EVT_BUTTON, self.refresh)
        bSizer1.Add(self.bt_refresh, 0, wx.LEFT, 5)

        self.bt_disconnect = mButton(self, '断开', color='red', size=(40, 23), font_size=10)
        self.bt_disconnect.Bind(wx.EVT_BUTTON, self.on_disconnect)
        bSizer1.Add(self.bt_disconnect, 0, wx.LEFT | wx.RIGHT, 5)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        # 服务器列表
        sizer_servers = wx.BoxSizer(wx.VERTICAL)
        self.lc_server = mULC_Report(self)
        self.lc_server.create(['ip', '主机名', 'UUID', '任务', '操作'])
        self.lc_server.setColumnWidth([120, 100, 260, 80, 120], autofill=4)
        sizer_servers.Add(self.lc_server, 1, wx.EXPAND)

        bSizer2.Add(sizer_servers, 1, wx.EXPAND)

        bSizerall.Add((0, 10))
        bSizerall.Add(bSizer1, 0, wx.EXPAND | wx.LEFT, 5)
        bSizerall.Add((0, 5))
        bSizerall.Add(bSizer2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.SetSizer(bSizerall)
        self.Centre(wx.BOTH)
        self.Layout()

    def get_all_servers_conn(self):
        if self.console_is_compute:
            conn_list = list(self.compute_conn_dic.values())
        else:
            conn_list = [self.console_conn] + list(self.compute_conn_dic.values())
        return conn_list

    def get_selected_servers_conn(self):
        conn_list = []
        ids = self.lc_server.get_selected_item()
        for conn in self.get_all_servers_conn():
            if conn.idx in ids:
                conn_list.append(conn)
        return conn_list


    def set_server_task_state(self, idx, state):
        self.lc_server.SetStringItem(idx, 3, state)

    def on_disconnect(self, evt):
        if self.vdi_conn.linkok():
            self.vdi_conn.close()
        self.vdi_db.disconnect()
        self.compute_conn_dic = {}
        self.lc_server.DeleteAllItems()

        self.parent.lb.Hide()
        self.parent.login_panel.Show()
        self.parent.Layout()

    def refresh(self, evt):
        "包括控制节点"
        self.lc_server.DeleteAllItems()
        self.compute_conn_dic.clear()

        # 获取主控IP，如果有主控HA，排除浮动IP
        try:
            re = self.vdi_db.cmd(
                "select ip,name,uuid from auxo.nodes where deleted=0 and role='controller' order by id")
        except Exception as e:
            mMessageBox(str(e))
            return
        console_item = re[0]
        console_ip = re[0][0]

        # 查询所有计算节点
        re = self.vdi_db.cmd(
            "select ip,name,uuid from auxo.nodes where deleted=0 and role='compute' group by ip order by id")

        if re[0][0] == console_ip:
            self.console_is_compute = True
        else:
            self.console_is_compute = False
            idx = self.lc_server.insert(console_item)
            self.lc_server.SetStringItem(idx, 3, '无')
            btp = BTPanel(self.lc_server,size=(-1,30))
            btp.add_bitmap_button(bmp_path='bitmaps/console.png', tooltip='控制台',
                                  onclick_method=self.on_ssh)
            btp.add_bitmap_button(bmp_path='bitmaps/moniter.png', tooltip='系统监测',
                                  onclick_method=self.on_moniter)
            btp.SetSize(btp.GetBestSize())
            ulcitem = self.lc_server.GetItem(idx, 4)
            ulcitem.SetWindow(btp)
            self.lc_server.SetItem(ulcitem)

            self.console_conn = ssh.sshClient(host_ip=console_item[0])
            self.console_conn.idx = idx
            btp.conn = self.console_conn

        for item in re:
            idx = self.lc_server.insert(item)
            self.lc_server.SetStringItem(idx, 3, '无')
            btp = BTPanel(self.lc_server,size=(-1,30))
            btp.SetBackgroundColour('white')
            btp.add_bitmap_button(bmp_path='bitmaps/console.png', tooltip='控制台',size=(23,23),
                                  onclick_method=self.on_ssh)
            btp.add_bitmap_button(bmp_path='bitmaps/moniter.png', tooltip='系统监测',size=(23,23),
                                  onclick_method=self.on_moniter)
            btp.SetSize(btp.GetBestSize())
            ulcitem = self.lc_server.GetItem(idx, 4)
            ulcitem.SetWindow(btp)
            self.lc_server.SetItem(ulcitem)

            conn = ssh.sshClient(host_ip=item[0])
            conn.idx = idx
            conn.username = globals.vdi_user
            conn.password = globals.vdi_user_pwd

            self.compute_conn_dic[item[0]] = conn
            btp.conn = conn

    def on_ssh(self, evt):
        item = evt.GetEventObject()
        conn = item.Parent.conn
        dlg = wx.Frame(self)
        dlg.__init__(None, -1, title="connect to %s" % conn.host, size=(800, 600))
        dlg.SetIcon(wx.Icon('bitmaps/console.png'))
        p = server_shell_panel(dlg, conn)
        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(p, 1, wx.EXPAND)
        dlg.SetSizer(bsizer)
        dlg.Show()

    def on_moniter(self, evt):
        item = evt.GetEventObject()
        conn = item.Parent.conn
        dialogs.get_info_dlg(conn).Show()


# 服务器控制台弹出窗口
class server_shell_panel(wx.Panel):
    def __init__(self, parent, conn):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(globals.bgcolor)

        self.browser = WebView.New(self, backend=wx.html2.WebViewBackendEdge)
        self.conn = conn
        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(self.browser, 1, wx.EXPAND)

        self.SetSizer(bsizer)
        self.refresh()

    def refresh(self):
        passwd_base64 = base64.b64encode(self.conn.password.encode())
        url = "http://127.0.0.1:%s/?hostname=%s&username=%s&password=%s" % (
            globals.wssh_port, self.conn.host, self.conn.username, passwd_base64.decode())
        self.browser.LoadURL(url)



class vdi_image_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(globals.panel_bgcolor)
        self.vdi_db = parent.vdi_db
        self.vdi_conn = parent.vdi_conn
        self.creaPanel()

    def creaPanel(self):
        bSizerall = wx.BoxSizer(wx.VERTICAL)

        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.bt_refresh = mButton(self, '刷新', color='blue', size=(40, 23), font_size=10)
        self.bt_refresh.Bind(wx.EVT_BUTTON, self.refresh)
        bSizer1.Add((0, 0), 1)
        bSizer1.Add(self.bt_refresh, 0, wx.LEFT | wx.TOP, 5)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.lc_image_panel = mPanel(self, '模板列表')
        bSizer2.Add(self.lc_image_panel, 0, wx.EXPAND | wx.BOTTOM, 5)

        self.lc_image = mListCtrl(self.lc_image_panel, ['id', '模板名', '类型'], border=False,
                                  method=self.on_image_popmenu, popupmemu=['重置状态'])
        self.lc_image.SetColumnWidth(0, 40)
        self.lc_image.SetColumnWidth(1, 120)
        self.lc_image.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_image_select)

        self.lc_image_panel.Add(self.lc_image, 1, wx.EXPAND)

        linebt = wx.BoxSizer(wx.HORIZONTAL)
        self.bt_reset = mButtonSimple(self.lc_image_panel, '重置状态', globals.panel_bgcolor, (60, 25))
        self.bt_reset.Bind(wx.EVT_BUTTON, self.on_reset)
        linebt.Add(self.bt_reset, 0, wx.EXPAND)
        self.lc_image_panel.Add(linebt)

        bSizer3 = wx.BoxSizer(wx.VERTICAL)
        bSizer2.Add(bSizer3, 1, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

        self.base_panel = mPanel(self, 'base文件信息')
        bSizer3.Add(self.base_panel, 1, wx.EXPAND)

        line1 = wx.BoxSizer(wx.HORIZONTAL)
        self.base_panel.sizer.Add(line1, 0, wx.EXPAND | wx.RIGHT | wx.TOP | wx.LEFT, 10)

        st = wx.StaticText(self.base_panel, label='模板名：')
        st.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        self.choice_image = wx.StaticText(self.base_panel)
        self.choice_image.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        line1.Add(st, 0)
        line1.Add(self.choice_image, 1)

        line2 = wx.BoxSizer(wx.HORIZONTAL)
        bs_base0 = wx.BoxSizer(wx.VERTICAL)
        bs_base1 = wx.BoxSizer(wx.VERTICAL)
        self.base_panel.sizer.Add(line2, 1, wx.EXPAND | wx.ALL, 10)
        self.lc_base0 = mListCtrl(self.base_panel, ['计算节点', 'UUID'], editable=True)
        self.lc_base1 = mListCtrl(self.base_panel, ['计算节点', 'UUID'], editable=True)

        st_base0 = wx.StaticText(self.base_panel, label='系统盘')
        st_base1 = wx.StaticText(self.base_panel, label='数据盘')

        st_base0.SetFont(wx.Font(10, 70, 90, 90, False, "微软雅黑"))
        st_base0.SetForegroundColour('grey')
        st_base1.SetFont(wx.Font(10, 70, 90, 90, False, "微软雅黑"))
        st_base1.SetForegroundColour('grey')

        bs_base0.Add(st_base0, 0)
        bs_base0.Add(self.lc_base0, 1, wx.EXPAND)

        bs_base1.Add(st_base1, 0)
        bs_base1.Add(self.lc_base1, 1, wx.EXPAND)

        line2.Add(bs_base0, 1, wx.EXPAND | wx.RIGHT, 10)
        line2.Add(bs_base1, 1, wx.EXPAND)

        self.lc_inst_panel = vdi_instance_panel(self)
        bSizer3.Add(self.lc_inst_panel, 0, wx.EXPAND | wx.TOP, 5)

        bSizerall.Add(bSizer1, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, 5)
        staticline1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizerall.Add(staticline1, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        bSizerall.Add(bSizer2, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)

        self.SetSizer(bSizerall)
        self.Layout()

    def refresh(self, evt):
        self.lc_image.DeleteAllItems()
        try:
            data = self.vdi_db.cmd(
                'select id,name,type_code from thor_console.images where deleted=0 and type_code<5 order by id')
        except Exception as e:
            mMessageBox(str(e))
            return
        for item in data:
            item = list(item)
            if item[2] == 1:
                item[2] = '教学'
            elif item[2] == 2:
                item[2] = '个人'
            elif item[2] == 4:
                item[2] = '系统桌面'
            self.lc_image.addRow(item)

    def on_image_popmenu(self, evt):
        item = self.lc_image.popupmenu.FindItemById(evt.GetId())
        text = item.GetItemLabel()
        if text == '重置状态':
            self.on_reset(None)

    def on_reset(self, evt):
        dlg = mWarnDlg('是否要重置数据库模板状态？')
        if dlg.ShowModal() == wx.ID_OK:
            image = self.lc_image.getItemData(1)
            cmd = "update thor_console.images set status='alive' where name='%s'" % image
            logging.info(f'数据库:{cmd}')
            self.vdi_db.cmd(cmd)
            self.vdi_db.conn.commit()
            mMessageBox('重置成功！')
        dlg.Destroy()

    def on_image_select(self, evt):
        self.image_name = self.lc_image.getItemData(1)
        self.choice_image.SetLabel(self.image_name)
        self.lc_inst_panel.inst_list.DeleteAllItems()
        id = evt.GetText()
        data = self.vdi_db.cmd(
            "select b.instance_id from thor_console.images as a INNER JOIN thor_console.instance_extra as b where a.id=b.image_id and b.graphic_type='vnc' and b.deleted=0 and a.id=%s" % id)
        if data:
            inst_id = data[0][0]
        else:
            mMessageBox('error: no data')
            return
        inst_info = self.vdi_db.get_inst_info(inst_id)
        self.lc_inst_panel.inst_list.addRow(inst_info)

        # 获取base
        image0 = inst_info[5]
        base0 = self.vdi_db.get_base_from_imageID(image0)
        self.lc_base0.DeleteAllItems()
        for item in base0:
            host = item[0].split('@')[0]
            self.lc_base0.addRow([host, item[1]])

        image1 = inst_info[6]
        self.lc_base1.DeleteAllItems()
        if image1:
            base1 = self.vdi_db.get_base_from_imageID(image1)
            for item in base1:
                host = item[0].split('@')[0]
                self.lc_base1.addRow([host, item[1]])


class vdi_instance_panel(mPanel):
    def __init__(self, parent):
        mPanel.__init__(self, parent, '关联桌面')
        self.SetBackgroundColour(globals.panel_bgcolor)
        self.vdi_db = parent.vdi_db
        self.vdi_conn = parent.vdi_conn

        self.inst_list = mListCtrl(self,
                                   ['名称', 'UUID', '宿主机', '系统盘', '数据盘', '系统盘模板', '数据盘模板'],
                                   border=False, editable=True,
                                   method=self.on_inst_popmenu, popupmemu=['查看桌面', 'xml配置', 'qemu日志'])
        self.inst_list.SetColumnWidth(0, 120)
        self.inst_list.SetColumnWidth(1, 270)
        self.inst_list.SetColumnWidth(2, 100)

        self.sizer.Add(self.inst_list, 1, wx.EXPAND)

        bt_line = wx.BoxSizer(wx.HORIZONTAL)
        bt_view = mButtonSimple(self, '查看桌面', globals.panel_bgcolor, (60, 25))
        bt_view.Bind(wx.EVT_BUTTON, self.view_inst)
        bt_line.Add(bt_view, 0)

        bt_xml = mButtonSimple(self, 'xml配置', globals.panel_bgcolor, (60, 25))
        bt_xml.Bind(wx.EVT_BUTTON, self.view_xml)
        bt_line.Add(bt_xml, 0)

        bt_qemulog = mButtonSimple(self, 'qemu日志', globals.panel_bgcolor, (70, 25))
        bt_qemulog.Bind(wx.EVT_BUTTON, self.view_qemulog)
        bt_line.Add(bt_qemulog, 0)

        self.Add(bt_line, 0)

    def on_inst_popmenu(self, evt):
        item = self.inst_list.popupmenu.FindItemById(evt.GetId())
        text = item.GetItemLabel()
        if text == '查看桌面':
            self.view_inst(None)
        if text == 'xml配置':
            self.view_xml(None)
        if text == 'qemu日志':
            self.view_qemulog(None)

    def view_inst(self, evt):
        inst_id = self.inst_list.getItemData(1)
        host, qemu_id = self.check(inst_id)
        if host == self.vdi_conn.host:
            conn = self.vdi_conn
        else:
            conn = ssh.sshClient()
            conn.host = host
            try:
                conn.server_connect()
            except:
                mMessageBox('无法连接节点%s' % conn.host)
        # 查vnc密码
        try:
            re = conn.server_recv('cat /etc/libvirt/qemu/%s.xml | grep vnc' % qemu_id)
        except Exception as e:
            mMessageBox(str(e))
        re = re.split('passwd=')[1]
        password = re.split('\'')[1]
        pyperclip.copy(password)
        mMessageBox('VNC密码：%s，已复制到剪切板' % password)

        # 查URL
        re = self.vdi_conn.server_recv('source /root/admin.src; nova get-vnc-console %s novnc | grep novnc' % inst_id)
        re = re.split('http://')[1]
        url = re.split(' ')[0]
        webbrowser.open_new('http://' + url)

        if conn != self.vdi_conn:
            conn.close()

    def view_xml(self, evt):
        inst_id = self.inst_list.getItemData(1)
        host, qemu_id = self.check(inst_id)
        conn = self.get_agent_conn(host)

        file_path = '/etc/libvirt/qemu/%s.xml' % qemu_id

        dlg = dialogs.xml_viewer(file_path)
        dlg.m_button1.Hide()
        dlg.m_button2.Hide()
        data = conn.server_recv('cat %s' % file_path)
        dlg.data.SetValue(data)
        if dlg.ShowModal() == wx.ID_OK:
            pass
        if conn != self.vdi_conn:
            conn.close()
        dlg.Destroy()

    def view_qemulog(self, evt):
        inst_id = self.inst_list.getItemData(1)
        host, qemu_id = self.check(inst_id)
        conn = self.get_agent_conn(host)

        file_path = '/var/log/libvirt/qemu/%s.log' % qemu_id

        dlg = dialogs.xml_viewer(file_path)
        dlg.m_button1.Hide()
        dlg.m_button2.Hide()
        data = conn.server_recv('cat %s' % file_path)
        dlg.data.SetValue(data)
        if dlg.ShowModal() == wx.ID_OK:
            pass
        if conn != self.vdi_conn:
            conn.close()
        dlg.Destroy()

    # 查询宿主机ip和qemu-id
    def check(self, inst_id):
        re = self.vdi_db.cmd("select ip, hostname from auxo.nodes where deleted=0 and role='compute'")
        hosts = {}
        for host in re:
            hosts[host[1]] = host[0]
        re = self.vdi_conn.server_recv('source /root/admin.src; nova show %s | grep ATTR' % inst_id)
        re = re.split('\n')
        hostname = re[1].split('|')
        hostname = hostname[2].strip()
        qemu_id = re[3].split('|')
        qemu_id = qemu_id[2].strip()
        return hosts[hostname], qemu_id

    # 获取宿主机会话
    def get_agent_conn(self, host):
        conn = ssh.sshClient()
        if host == self.vdi_conn.host:
            conn = self.vdi_conn
        else:
            conn.host = host
            try:
                conn.server_connect()
            except:
                mMessageBox('无法连接节点%s' % conn.host)
        return conn


class vdi_vm_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(globals.panel_bgcolor)
        self.vdi_db = parent.vdi_db
        self.vdi_conn = parent.vdi_conn

        bSizerall = wx.BoxSizer(wx.VERTICAL)
        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer1.Add((0, 0), 1, wx.EXPAND, 0)
        self.radio = mRadio(self, ['个人', '教学'], method=self.refresh)
        bSizer1.Add(self.radio, 0, wx.EXPAND | wx.RIGHT, 5)

        self.list_panel = mPanel(self, '用户列表')
        self.personal_list = mListCtrl(self.list_panel, ['id', '用户名', '姓名'], border=False,
                                       method=self.on_plist_popmenu, popupmemu=['重置密码'])
        self.personal_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_left_list_selected)
        self.personal_list.SetColumnWidth(0, 40)
        self.personal_list.SetColumnWidth(1, 80)
        self.teaching_list = mListCtrl(self.list_panel, ['id', '场景名'], border=False,
                                       method=self.on_tlist_popmenu, popupmemu=['修改教室'])
        self.teaching_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_left_list_selected)
        self.teaching_list.SetColumnWidth(0, 50)
        self.teaching_list.SetColumnWidth(1, 120)
        self.list_panel.sizer.Add(self.personal_list, 1, wx.EXPAND)
        self.list_panel.sizer.Add(self.teaching_list, 1, wx.EXPAND)

        list_panel_bt = wx.BoxSizer(wx.HORIZONTAL)
        self.bt_chClass = mButtonSimple(self.list_panel, '修改教室', globals.panel_bgcolor, (60, 25))
        self.bt_chClass.Bind(wx.EVT_BUTTON, self.on_chClass)
        self.bt_chClass.Hide()
        self.bt_chPasswd = mButtonSimple(self.list_panel, '重置密码', globals.panel_bgcolor, (60, 25))
        self.bt_chPasswd.Bind(wx.EVT_BUTTON, self.on_chPasswd)
        self.bt_chPasswd.Hide()
        list_panel_bt.Add(self.bt_chClass, 0, wx.EXPAND)
        list_panel_bt.Add(self.bt_chPasswd, 0, wx.EXPAND)

        self.list_panel.Add(list_panel_bt, 0, wx.EXPAND)
        bSizer2.Add(self.list_panel, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

        inst_panel = vdi_instance_panel(self)
        self.inst_list = inst_panel.inst_list

        bSizer2.Add(inst_panel, 1, wx.EXPAND | wx.LEFT | wx.BOTTOM, 5)

        bSizerall.Add(bSizer1, 0, wx.EXPAND | wx.LEFT | wx.TOP, 5)
        staticline1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizerall.Add(staticline1, 0, wx.EXPAND | wx.ALL, 5)
        bSizerall.Add(bSizer2, 1, wx.EXPAND | wx.RIGHT, 5)
        self.SetSizer(bSizerall)
        self.Centre(wx.BOTH)

        self.radio.setFoces(0)
        self.teaching_list.Hide()
        self.Layout()

    def on_tlist_popmenu(self, evt):
        item = self.teaching_list.popupmenu.FindItemById(evt.GetId())
        text = item.GetItemLabel()
        if text == '修改教室':
            self.on_chClass(None)

    def on_plist_popmenu(self, evt):
        item = self.personal_list.popupmenu.FindItemById(evt.GetId())
        text = item.GetItemLabel()
        if text == '重置密码':
            self.on_chPasswd(None)

    def on_chClass(self, evt):
        try:
            poolname = self.teaching_list.getItemData(1)
            re = self.vdi_db.cmd("select name from thor_console.pool where deleted=0")
            pools = []
            for item in re:
                pools.append(item[0])
            dlg = dialogs.vdi_chClass(poolname, pools)
            if dlg.ShowModal() == wx.ID_OK:
                poolname = dlg.choice.GetStringSelection()
                re = self.vdi_db.cmd(
                    "select id from thor_console.pool where deleted=0 and name='%s'" % poolname)
                pool_id = re[0][0]
                cmd = "update thor_console.mode set pool_id=%s where deleted=0 and name='%s'" % (
                    pool_id, self.teaching_list.getItemData(1))
                self.vdi_db.cmd(cmd)
                self.vdi_db.conn.commit()
                logging.info(f'数据库：{cmd}')
                mMessageBox('修改成功！')
            dlg.Destroy()
        except Exception as e:
            mMessageBox(str(e))

    def on_chPasswd(self, evt):
        username = self.personal_list.getItemData(1)
        try:
            dlg = mWarnDlg('是否要将用户%s密码重置为oseasy?' % username)
            if dlg.ShowModal() == wx.ID_OK:
                cmd = "update thor_console.user_edu set password='f4e282a29388abe98e784113dcddf0f0' where name='%s'" % username
                self.vdi_db.cmd(cmd)
                self.vdi_db.conn.commit()
                logging.info(f'数据库：{cmd}')
                mMessageBox('重置成功！')
            dlg.Destroy()
        except Exception as e:
            mMessageBox(str(e))

    def refresh(self, evt):
        self.hide_left_list()
        self.inst_list.DeleteAllItems()
        self.personal_list.DeleteAllItems()
        self.teaching_list.DeleteAllItems()
        if not self.radio.focus:
            return
        elif self.radio.focus == '个人':
            self.personal_list.Show()
            self.bt_chClass.Hide()
            self.bt_chPasswd.Show()
            self.Layout()
            try:
                data = self.vdi_db.cmd(
                    'select id,name,real_name from thor_console.user_edu where deleted=0 and role<3 order by id DESC')
            except Exception as e:
                mMessageBox(str(e))
                return
            for item in data:
                self.personal_list.addRow(item)

        elif self.radio.focus == '教学':
            self.teaching_list.Show()
            self.bt_chPasswd.Hide()
            self.bt_chClass.Show()
            self.Layout()
            try:
                data = self.vdi_db.cmd(
                    'select id,name from thor_console.mode where deleted=0 and product_type="vdi" order by id DESC')
            except Exception as e:
                mMessageBox(str(e))
                return
            for item in data:
                self.teaching_list.addRow(item)

    def hide_left_list(self):
        self.personal_list.Hide()
        self.teaching_list.Hide()

    def on_left_list_selected(self, evt):
        self.inst_list.DeleteAllItems()
        key_id = evt.GetText()

        if self.radio.focus == '个人':
            self.list_panel.title.SetLabel('用户列表')
            self.list_panel.Layout()
            try:
                data = self.vdi_db.get_inst_UUID_from_userID(key_id)
            except Exception as e:
                mMessageBox(e)
            for inst in data:
                inst_id = inst[0]
                inst_info = self.vdi_db.get_inst_info(inst_id)
                self.inst_list.addRow(inst_info)

        elif self.radio.focus == '教学':
            self.list_panel.title.SetLabel('场景列表')
            self.list_panel.Layout()
            try:
                data = self.vdi_db.cmd(
                    "select b.instance_id from thor_console.mode as a INNER JOIN thor_console.instance_extra as b where b.mode_id=a.id and b.deleted=0 and a.id=%s ORDER BY b.id desc" % key_id)
            except Exception as e:
                mMessageBox(e)
            if data:
                for inst in data:
                    inst_id = inst[0]
                    inst_info = self.vdi_db.get_inst_info(inst_id)
                    self.inst_list.addRow(inst_info)


class vdi_network_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(globals.panel_bgcolor)
        self.vdi_db = parent.vdi_db
        self.vdi_conn = parent.vdi_conn
        bSizerall = wx.BoxSizer(wx.VERTICAL)

        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.bt_refresh = mButton(self, '刷新', color='blue', size=(40, 23), font_size=10)
        self.bt_refresh.Bind(wx.EVT_BUTTON, self.refresh)
        bSizer1.Add((0, 0), 1)
        bSizer1.Add(self.bt_refresh, 0, wx.LEFT, 5)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        p1 = mPanel(self, '数据网络')
        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(p1, wx.ID_ANY, "修改子网掩码"), wx.VERTICAL)
        p1.Add(sbSizer1, 0, wx.EXPAND | wx.ALL, 5)

        self.lc_subnet = mListCtrl(p1, ['uuid', 'name', 'cidr'], border=False,
                                   method=self.on_subnet_popmenu, popupmemu=['修改子网'])
        self.lc_subnet.SetColumnWidth(0, 120)
        self.lc_subnet.SetColumnWidth(2, 120)
        sbSizer1.Add(self.lc_subnet, 1, wx.EXPAND)
        bSizer2.Add(p1, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT, 5)

        bSizerall.Add(bSizer1, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, 5)
        staticline1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizerall.Add(staticline1, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        bSizerall.Add(bSizer2, 1, wx.TOP | wx.LEFT | wx.RIGHT, 5)

        self.SetSizer(bSizerall)
        self.Layout()

    def refresh(self, evt):
        self.lc_subnet.DeleteAllItems()
        try:
            re = self.vdi_db.cmd('select uuid,name,cidr from thor_console.subnets where deleted=0')
        except Exception as e:
            mMessageBox(str(e))
            return
        for item in re:
            self.lc_subnet.addRow(item)

    def on_subnet_popmenu(self, evt):
        item = self.lc_subnet.popupmenu.FindItemById(evt.GetId())
        text = item.GetItemLabel()
        if text == '修改子网':
            self.on_bt_chsubnet(None)

    def on_bt_chsubnet(self, evt):
        cidr = self.lc_subnet.getItemData(2)
        name = self.lc_subnet.getItemData(1)
        uuid = self.lc_subnet.getItemData(0)
        dlg = dialogs.vdi_chSubnet(name)
        if dlg.ShowModal() == wx.ID_OK:
            mask = dlg.mask.GetValue()
            if not methods.checkmask(mask):
                mMessageBox('无效的mac地址')
                dlg.Destroy()
                return
            maskint = methods.mask_to_int(mask)
            cidr = cidr.split('/')[0] + '/' + str(maskint)
            cmd = 'update thor_console.subnets set netmask="%s",cidr="%s" where uuid="%s"' % (mask, cidr, uuid)
            self.vdi_db.cmd(cmd)
            logging.info(f'数据库：{cmd}')
            cmd = 'update neutron.subnets set cidr="%s" where id="%s"' % (cidr, uuid)
            self.vdi_db.cmd(cmd)
            self.vdi_db.conn.commit()
            logging.info(f'数据库：{cmd}')
            self.refresh(None)
            mMessageBox('修改成功')
        dlg.Destroy()


class vdi_log_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(globals.panel_bgcolor)
        bSizerall = wx.BoxSizer(wx.VERTICAL)

        self.log_tc = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(200, -1),
                                  wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER)
        self.log_tc.SetBackgroundColour(globals.bgcolor)
        self.log_clean = mButton(self, '清空记录', 'red', size=(60, 23), font_size=10)
        self.log_clean.Bind(wx.EVT_BUTTON, self.clean_log)

        bSizerall.Add(self.log_clean, 0, wx.LEFT | wx.TOP, 10)
        staticline1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizerall.Add((0, 2))
        bSizerall.Add(staticline1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        bSizerall.Add(self.log_tc, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        self.SetSizer(bSizerall)
        self.Layout()

    def log(self, info):
        self.log_tc.AppendText(info + '\n')

    def clean_log(self, evt):
        self.log_tc.Clear()
