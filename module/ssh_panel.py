# -*- coding: utf-8 -*-
import logging,shutil,winreg
import threadpool, wx.grid, wx.aui, pyperclip, base64,  stat,configparser,os,re
from _thread import start_new_thread
from .myui import *
from functools import reduce
from module import methods, dialogs, globals,ssh
from wx.html2 import WebView
from module.dialogs import add_cmd_dlg, file_chmod, file_edit, file_choice, sshclient_list
from module.methods import getLabelFromEVT, bytes2human
from module.widgets import sshNotebook as SNB
import wx.lib.agw.flatnotebook as FNB

backends = [wx.html2.WebViewBackendEdge, wx.html2.WebViewBackendIE]
BACKEND = None
for id in backends:
    if WebView.IsBackendAvailable(id) and BACKEND is None:
        if id == wx.html2.WebViewBackendIE:
            key_path = r"Software\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BROWSER_EMULATION"
            methods.check_and_create_registry_key(key_path, 'lztool.exe', 11000)
            WebView.MSWSetEmulationLevel(wx.html2.WEBVIEWIE_EMU_IE11)
        BACKEND = id


class ssh_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.new_thread = methods.new_thread
        self.link_ok = 0  # 连接成功数
        self._PageCount = 0
        self._IsMulti = True
        self.sftp_status = False
        self.is_conecting = False  # 用来处理default page
        globals.multi_ssh_conn = {}  # host : {'conn','gauge'}
        self.treeNode_dict = {}  # host : child_id
        self.shellpage_dic = {}  # host : shell_panel
        self.__init__ui()
        self.__evt_bind()

    def __init__ui(self):
        bSizerAll = wx.BoxSizer(wx.VERTICAL)
        bSizer0 = wx.BoxSizer(wx.HORIZONTAL)
        bSizer1 = wx.BoxSizer(wx.VERTICAL)  # 会话树
        bSizer2 = wx.BoxSizer(wx.VERTICAL)  # SHELL界面

        bSizer11 = wx.BoxSizer(wx.VERTICAL)
        bSizer12 = wx.BoxSizer(wx.VERTICAL)

        self.panel11 = wx.Panel(self, size=(231, -1))  # 批量连接设置
        self.panel12 = wx.Panel(self, size=(231, -1))  # 连接列表

        bSizerInfo = wx.BoxSizer(wx.VERTICAL)
        self.panel11.SetSizer(bSizerInfo)
        info_label = wx.StaticText(self.panel11, label='批量连接', size=(-1, 25), style=wx.ALIGN_CENTER)
        info_label.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        info_label.SetBackgroundColour('#95a5a6')
        info_label.SetForegroundColour('#ffffff')
        self.num = mInput(self.panel11, st_label='数量', tc_label='2', st_size=(60, 25), font_size=12)
        self.host = mInput(self.panel11, st_label='起始IP', tc_label='172.31.13.240', st_size=(60, 25), font_size=12)
        self.port = mInput(self.panel11, st_label='端口', tc_label='22', st_size=(60, 25), font_size=12)
        self.username = mInput(self.panel11, st_label='用户名', tc_label='root', st_size=(60, 25), font_size=12)
        self.password = mInput(self.panel11, st_label='密码', tc_label='oseasy@123', st_size=(60, 25), font_size=12,
                               password=True)
        self.name = mInput(self.panel11, st_label='名称', tc_label='', st_size=(60, 25), font_size=12)
        self.desc = mInput(self.panel11, st_label='描述', tc_label='', st_size=(60, 25), font_size=12)
        self.bt_connect = mButton(self.panel11, label='连接', color='deepgreen', size=(-1, 25))
        self.bt_connect.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        self.CB_save = wx.CheckBox(self.panel11, wx.ID_ANY, "保存登录信息", wx.DefaultPosition, wx.DefaultSize, 0)
        self.CB_save.Bind(wx.EVT_CHECKBOX, self.on_cb_save)

        sshconfig = configparser.ConfigParser()
        sshconfig.read('template.ini')
        self.num.SetValue(sshconfig.get('default', 'num'))
        self.host.SetValue(sshconfig.get('default', 'host'))
        self.username.SetValue(sshconfig.get('default', 'user'))
        self.password.SetValue(sshconfig.get('default', 'password'))


        bSizerInfo.Add(info_label, 0, wx.EXPAND, 0)
        bSizerInfo.Add(self.num, 0, wx.EXPAND | wx.TOP, 1)
        bSizerInfo.Add(self.host, 0, wx.EXPAND | wx.TOP, 1)
        bSizerInfo.Add(self.port, 0, wx.EXPAND | wx.TOP, 1)
        bSizerInfo.Add(self.username, 0, wx.EXPAND | wx.TOP, 1)
        bSizerInfo.Add(self.password, 0, wx.EXPAND | wx.TOP, 1)
        bSizerInfo.Add(self.CB_save, 0, wx.TOP, 5)
        bSizerInfo.Add(self.name, 0, wx.EXPAND | wx.TOP, 1)
        bSizerInfo.Add(self.desc, 0, wx.EXPAND | wx.TOP, 1)
        bSizerInfo.Add(self.bt_connect, 0, wx.EXPAND | wx.TOP, 1)

        self.name.tc.Disable()
        self.desc.tc.Disable()

        self.panel11.SetSizer(bSizerInfo)
        bSizer11.Add(self.panel11, 1, wx.EXPAND | wx.TOP, 5)

        self.tree_session = mHyperTreeList(self.panel12, cols=['主机', '任务'])
        self.tree_session.SetWindowStyle(wx.NO_BORDER)
        self.tree_session.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT)
        self.tree_session.SetBackgroundColour('white')
        self.tree_session.setColumnWidth([125, 85])
        il = wx.ImageList(16, 16)
        self.greenball = il.Add(wx.Bitmap('bitmaps/greenball.png', wx.BITMAP_TYPE_PNG))
        self.redball = il.Add(wx.Bitmap('bitmaps/redball.png', wx.BITMAP_TYPE_PNG))
        self.yellowball = il.Add(wx.Bitmap('bitmaps/yellowball.png', wx.BITMAP_TYPE_PNG))
        self.tree_session.AssignImageList(il)

        bSizerBT = wx.BoxSizer(wx.HORIZONTAL)
        txt1 = wx.StaticText(self.panel12, label='在线数：')
        txt1.SetFont(wx.Font(11, 70, 90, 90, False, "微软雅黑"))
        self.st_session_count = wx.StaticText(self.panel12, label='0')
        self.st_session_count.SetFont(wx.Font(11, 70, 90, 90, False, "微软雅黑"))
        # vdi_config = mBitmapButton(self.panel12, "bitmaps/terminalconfig.png", 'VDI终端设置')
        # vdi_config.Bind(wx.EVT_BUTTON, self.on_vdi_config)
        bt_refresh = mBitmapButton(self.panel12, 'bitmaps/ssh_refresh.png', '刷新')
        bt_refresh.Bind(wx.EVT_BUTTON, self.RefreshSSHList)
        bt_disconnect = mBitmapButton(self.panel12, 'bitmaps/disconnect.png', '全部断开')
        bt_disconnect.Bind(wx.EVT_BUTTON, self.close_all_ssh)

        bSizerBT.Add(txt1, 0, wx.LEFT | wx.ALIGN_CENTER, 5)
        bSizerBT.Add(self.st_session_count, 1, wx.ALIGN_CENTER)
        # bSizerBT.Add(vdi_config, 0, wx.ALIGN_CENTER)
        bSizerBT.Add(bt_refresh, 0, wx.ALIGN_CENTER | wx.LEFT, 5)
        bSizerBT.Add(bt_disconnect, 0, wx.ALIGN_CENTER | wx.LEFT, 5)

        bSizerTree = wx.BoxSizer(wx.VERTICAL)
        bSizerTree.Add(self.tree_session, 1, wx.EXPAND)
        bSizerTree.Add(bSizerBT, 0, wx.EXPAND)

        self.panel12.SetSizer(bSizerTree)
        bSizer12.Add(self.panel12, 1, wx.EXPAND | wx.TOP, 5)

        bSizer1.Add(bSizer11, 0, wx.EXPAND)
        bSizer1.Add(bSizer12, 1, wx.EXPAND)

        self.nb_console = SNB.FlatNotebook(self, wx.ID_ANY,
                                           agwStyle=SNB.FNB_FANCY_TABS
                                                    | SNB.FNB_NO_X_BUTTON
                                                    | SNB.FNB_NO_TAB_FOCUS
                                                    | SNB.FNB_X_ON_TAB
                                                    | SNB.FNB_OPEN_BUTTON
                                                    | SNB.FNB_MENU_BUTTON)
                                                    # | FNB.FNB_ALLOW_FOREIGN_DND)
        self.nb_console.SetTabAreaColour(globals.panel_bgcolor)
        self.nb_console.SetTabAreaColour(wx.Colour(237, 239, 242))

        self.ssh_menu = SSHPopupWindow(self, wx.SIMPLE_BORDER)
        self.ssh_menu.st_path.SetLabel(methods.get_config('ssh', 'download_path'))

        self.CreateRightClickMenu()
        self.add_default_page()

        bSizer2.Add(self.nb_console, 1, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)

        bSizer0.Add(bSizer1, 0, wx.EXPAND, 0)
        bSizer0.Add(bSizer2, 1, wx.EXPAND, 0)

        bSizerAll.Add(bSizer0, 1, wx.EXPAND | wx.LEFT, 5)
        self.SetSizer(bSizerAll)
        self.Layout()

    def __evt_bind(self):
        self.bt_connect.Bind(wx.EVT_BUTTON, self.create_connect)
        self.tree_session.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_sel)
        self.tree_session.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_tree_rightclick)
        self.tree_session.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_item_actived)
        self.Bind(SNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.onNotebookChange, self.nb_console)
        self.Bind(SNB.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.onNotebookPageClose, self.nb_console)
        self.ssh_menu.bt_open.Bind(wx.EVT_BUTTON, self.onOpenDownloadDir)
        self.ssh_menu.bt_cancel.Bind(wx.EVT_BUTTON, self.onSFTPCancel)

    def RefreshSSHList(self, evt):
        i = 0
        for conn in list(globals.multi_ssh_conn.values()):
            if not conn.linkok():
                self.tree_session.SetItemImage(self.treeNode_dict[conn.host],
                                               self.redball)
                continue
            else:
                i += 1
        self.st_session_count.SetLabel(str(i))
        if i == 0:
            self.close_all_ssh(None)
        else:
            self.link_ok = i
            wx.CallAfter(self.st_session_count.SetLabel, str(i))

    def ShowSSHMenu(self):
        rect = self.nb_console._pages.GetClientRect()
        pos = self.nb_console._pages.ClientToScreen((rect.width, 0))
        wid = self.ssh_menu.GetSize()[0]
        self.ssh_menu.Position(pos, (-5 - wid, 30))
        self.ssh_menu.Show(True)

    def onOpenDownloadDir(self, evt):
        path = self.ssh_menu.st_path.GetLabel()
        os.startfile(path)

    def onSFTPCancel(self, evt):
        self.sftp_status = False

    def on_cb_save(self, evt):
        if self.CB_save.GetValue():
            self.name.tc.Enable()
            self.desc.tc.Enable()
        else:
            self.name.tc.Disable()
            self.desc.tc.Disable()

    def onNotebookChange(self, evt):
        if self.nb_console.GetPage(self.nb_console.GetSelection()).conn:
            self.set_cur_conn(self.nb_console.GetPage(self.nb_console.GetSelection()).conn)

    def onNotebookPageClose(self, evt):
        "delele page触发，delete all page不触发"
        self._PageCount -= 1
        label = self.nb_console.GetPageText(evt.GetSelection())

        if label in globals.multi_ssh_conn.keys():  # 不是复制的页面
            globals.multi_ssh_conn[label].console = False
            self.shellpage_dic[label].nb_console_operate.MONITER_STAT = False  #停止监控线程
            self.shellpage_dic.pop(label)

        if self._PageCount == 0 and not self.is_conecting:
            self.add_default_page()


    def CreateRightClickMenu(self):
        self.nb_console_rmenu = wx.Menu()
        for text in '复制 关闭其他'.split():
            item = self.nb_console_rmenu.Append(wx.ID_ANY, text)
            self.Bind(wx.EVT_MENU, self.onNotebookTabMenu, item)
        self.nb_console.SetRightClickMenu(self.nb_console_rmenu)

    def onNotebookTabMenu(self, evt):
        item = self.nb_console_rmenu.FindItemById(evt.GetId())
        label = item.GetItemLabel()
        if label == '复制':
            conn = self.nb_console.GetCurrentPage().conn
            if conn:
                page_label = self.get_copy_increate_label(conn.host)
                self.add_shell_page(conn, page_label)

        elif label == '关闭其他':
            count = self.nb_console.GetPageCount()
            while count > 1:
                idx = self.nb_console.GetSelection()
                if idx > 0:
                    self.nb_console.DeletePage(0)
                else:
                    self.nb_console.DeletePage(1)
                count -= 1

    def add_shell_page(self, conn, label=None):
        if not label:  # 不是复制
            new_page = shell_panel(self.nb_console, conn)
            self.shellpage_dic[conn.host] = new_page
            label = conn.host
        else:
            new_page = CopyPage(self.nb_console, conn)
        self.nb_console.AddPage(new_page, label, True)
        self._PageCount += 1

    def get_copy_increate_label(self,ip):
        all_labels = [self.nb_console.GetPageText(i) for i in range(self.nb_console.GetPageCount())]
        filtered_labels = [label for label in all_labels if label.startswith(ip)]
        existing_numbers = [int(re.search(r'%s-(\d+)' % ip, s).group(1)) for s in filtered_labels if
                            re.search(r'%s-(\d+)' % ip, s)]
        if not existing_numbers:
            return f'{ip}-1'
        unused_number = next((i for i in range(1, max(existing_numbers) + 2) if i not in existing_numbers), None)
        new_string = f'%s-{unused_number}' % ip
        return new_string

    def add_default_page(self):
        page = DeafaultPage(self.nb_console)
        self.nb_console.AddPage(page, '新标签页', True)
        page.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_linklist_act)
        self._PageCount += 1

    # 连接动画效果
    def connect_ui(self, movetask=True):
        self.panel11.Hide()
        self.panel12.Show()
        self.Layout()
        # if movetask:
        #     moveTask(self.panel12, 500, 0, False, layout=self)
        #     moveTask(self.panel12, 500, 20, False, True, layout=self)

    def get_ssh_info(self):
        return self.num.GetValue(), self.host.GetValue(), self.port.GetValue(), self.username.GetValue(), self.password.GetValue(), self.name.GetValue(), self.desc.GetValue()

    def init_name(self, init_name, i):
        n = i
        if n > 1:
            self.tmp_name = init_name + '(%s)' % str(n)
        else:
            self.tmp_name = init_name
        for parent, dirnames, filenames in os.walk('data/sshclient'):
            for filename in filenames:
                if self.tmp_name == filename:
                    n += 1
                    self.init_name('新建会话', n)
                    break
            self.name.SetValue(self.tmp_name)

    def setTreeYellow(self):
        for conn in list(globals.multi_ssh_conn.values()):
            self.tree_session.SetItemImage(self.treeNode_dict[conn.host], self.yellowball)

    #  SSH连接

    def create_connect(self, evt):
        info = self.get_ssh_info()
        self.start_connect(info)
        self.nb_console.DeleteAllPages()

    def start_connect(self, info):
        num, host, port, user, password, name, desc = info
        self.total = int(num)
        self.done = 0

        # 创建本次连接字典link_list  ip:conn
        link_list = []
        for i in range(int(num)):
            IPAddr = methods.ipIncrease(host, i)
            if IPAddr in globals.multi_ssh_conn.keys():
                # 反复连接时排除掉已在当前连接列表的ip
                continue
            conn = ssh.sshClient()
            conn.host = IPAddr
            conn.port = int(port)
            conn.username = user
            conn.password = password
            conn.gauge = mGauge(self.panel12, (80, 18), 100, 'white', wx.Colour(230, 230, 230), border_colour='white')
            link_list.append(conn)
            globals.multi_ssh_conn[IPAddr] = conn
        if not link_list:
            self.is_conecting = False

        num, host, port, user, password, name, desc = info
        sshconfig = configparser.ConfigParser()
        if self.CB_save.GetValue():
            # 保存配置文件
            shutil.copyfile('template.ini', 'data/sshclient/%s' % name)
            sshconfig.read('data/sshclient/%s' % name)
            sshconfig.set('default', 'host', host)
            sshconfig.set('default', 'port', port)
            sshconfig.set('default', 'user', user)
            sshconfig.set('default', 'password', password)
            sshconfig.set('default', 'desc', desc)
            sshconfig.set('default', 'num', num)
            sshconfig.write(open('data/sshclient/%s' % name, "w"))
        else:
            sshconfig.read('template.ini')
            sshconfig.set('default', 'host', host)
            sshconfig.set('default', 'port', port)
            sshconfig.set('default', 'user', user)
            sshconfig.set('default', 'password', password)
            sshconfig.set('default', 'desc', desc)
            sshconfig.set('default', 'num', num)
            sshconfig.write(open('template.ini', "w"))
        self.CB_save.SetValue(False)

        if not self.tree_session.root:
            self.tree_session.root = self.tree_session.AddRoot('连接列表', ct_type=1)

        # 通过link_list初始化连接列表
        num2ip = lambda x: '.'.join([str(x // (256 ** i) % 256) for i in range(3, -1, -1)])

        # ip to num做排序
        tmp_list = [obj.host for obj in link_list]
        ip_list = []
        for ip in tmp_list:
            num = reduce(lambda x, y: (x << 8) + y, list(map(int, ip.split('.'))))
            ip_list.append(num)
        ip_list.sort()

        # num to ip，初始化Tree
        for num in ip_list:
            ip = num2ip(num)
            child = self.tree_session.AppendItem(self.tree_session.root, ip, ct_type=0)
            self.tree_session.SetItemWindow(child, globals.multi_ssh_conn[ip].gauge, 1)
            self.treeNode_dict[ip] = child

        # 线程池执行connect_tread
        pool = threadpool.ThreadPool(globals.max_thread)
        requests = threadpool.makeRequests(self.connect_thread, link_list)
        [pool.putRequest(req) for req in requests]
        self.st_session_count.SetLabel('%s' % self.link_ok)
        self.connect_ui()
        self.Layout()

    def connect_thread(self, conn):
        try:
            self.tree_session.SetItemImage(self.treeNode_dict[conn.host], self.yellowball)
            conn.gauge.SetValue(100, '连接中')
            conn.connect(int(globals.timeout))
            self.change_online_count(1)
            globals.cur_conn = conn
            self.tree_session.SetItemImage(self.treeNode_dict[conn.host], self.greenball)
            conn.gauge.SetValue(100, '无')
        except:
            self.tree_session.SetItemImage(self.treeNode_dict[conn.host], self.redball)
            conn.gauge.SetValue(100, '连接失败')
        self.done += 1
        if self.done == self.total:
            self.done = 0
            self.total = 0
            if self.link_ok > 0:
                wx.CallAfter(self.add_shell_page, (globals.cur_conn))
                self.is_conecting = False
                self.Layout()
            else:
                self.close_all_ssh(None)


    def open_connect(self):
        dlg = dialogs.open_connect()
        dlg.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_linklist_act)
        dlg.ShowModal()
        dlg.Destroy()

    def on_linklist_act(self, evt):
        parent = evt.GetEventObject().Parent  # panel or dialog
        sshclient = evt.GetText()
        info = self.read_ssh_config(sshclient)
        self.is_conecting = True
        self.start_connect(info)
        self.nb_console.DeletePage(self.nb_console.GetPageIndex(parent))
        if isinstance(parent, wx.Dialog):
            parent.Destroy()

    def close_all_ssh(self, evt):
        self._PageCount = 0
        self.nb_console.DeleteAllPages()  # 前两行顺序不能乱
        wx.CallAfter(self.add_default_page)
        self.shellpage_dic.clear()
        self.treeNode_dict.clear()
        globals.multi_ssh_conn.clear()
        self.tree_session.root = None
        self.tree_session.DeleteAllItems()
        self.change_online_count(None)
        self.panel11.Show()
        self.panel12.Hide()
        self.Layout()
        # globals.console_dict.clear()

    def change_online_count(self, n):
        if n == None:
            self.link_ok = 0
            self.st_session_count.SetLabel('0')
        else:
            self.link_ok += n
            if self.link_ok == 0:
                self.close_all_ssh(None)
            else:
                wx.CallAfter(self.st_session_count.SetLabel, str(self.link_ok))


    def set_cur_conn(self, conn):
        globals.cur_conn = conn

    def on_tree_sel(self, evt):
        self.link_selected = self.tree_session.GetItemText(evt.GetItem())

    def on_tree_rightclick(self, evt):
        self.link_selected = self.tree_session.GetItemText(evt.GetItem())
        self.treeMenu = wx.Menu()
        for text in '控制台 重连 断开 删除'.split():
            item = self.treeMenu.Append(wx.ID_ANY, text)
            self.Bind(wx.EVT_MENU, self.on_linktree_popup_sel, item)
        self.tree_session.PopupMenu(self.treeMenu)

    def on_tree_item_actived(self, evt):
        actived_host = self.tree_session.GetItemText(evt.GetItem())
        conn = globals.multi_ssh_conn[actived_host]
        if conn.linkok():
            if actived_host in list(self.shellpage_dic.keys()):
                page_label = self.get_copy_increate_label(conn.host)
                self.add_shell_page(conn, page_label)
            else:
                self.add_shell_page(conn)
        else:
            mMessageBox('连接状态异常！')

    def on_linktree_popup_sel(self, evt):
        item = self.treeMenu.FindItemById(evt.GetId())
        ip = self.link_selected
        if item.GetItemLabel() == '重连':
            if globals.multi_ssh_conn[self.link_selected].linkok():
                return
            conn = globals.multi_ssh_conn[self.link_selected]
            start_new_thread(self.reconnect, (conn,))
        elif item.GetItemLabel() == '断开':
            if globals.multi_ssh_conn[self.link_selected].linkok():
                globals.multi_ssh_conn[self.link_selected].close()
                self.change_online_count(-1)
                self.tree_session.SetItemImage(self.treeNode_dict[self.link_selected], self.redball)
                if ip in list(self.shellpage_dic.keys()):
                    self.nb_console.DeletePage(self.nb_console.GetPageIndex(self.shellpage_dic[ip]))
        elif item.GetItemLabel() == '控制台':
            conn = globals.multi_ssh_conn[self.link_selected]
            if conn.linkok():
                if self.link_selected in list(self.shellpage_dic.keys()):
                    page_label = self.get_copy_increate_label(conn.host)
                    self.add_shell_page(conn, page_label)
                else:
                    self.add_shell_page(conn)
            else:
                mMessageBox('连接状态异常！')
        elif item.GetItemLabel() == '删除':
            if globals.multi_ssh_conn[ip].linkok():
                mMessageBox('不能删除连接中的会话')
            else:
                self.tree_session.Delete(self.treeNode_dict[ip])
                globals.multi_ssh_conn.pop(ip)
                if ip in list(self.shellpage_dic.keys()):
                    self.nb_console.DeletePage(self.nb_console.GetPageIndex(self.shellpage_dic[ip]))
                    self.shellpage_dic.pop(ip)

    def reconnect(self, conn):
        try:
            conn.gauge.SetValue(100, '连接中')
            conn.connect(int(globals.timeout))
            self.change_online_count(1)
            self.tree_session.SetItemImage(self.treeNode_dict[self.link_selected], self.greenball)
            conn.gauge.SetValue(100, '无')
        except Exception as e:
            conn.gauge.SetValue(100, '连接失败')
            logging.error(f'{conn.host}: {str(e)}')

    def on_vdi_config(self, evt):
        if not globals.cur_conn:
            return
        if not globals.cur_conn.linkok():
            mMessageBox('当前会话连接异常')
            return
        dlg = dialogs.vdi_terminal(self)
        try:
            dlg.h264_val = \
                globals.cur_conn.recv("cat /etc/evdi/config/display_settings | grep -n '^h264='").split('=')[
                    1]
            dlg.init_config()
            dlg.ShowModal()
        except:
            mMessageBox('当前连接对象非VDI终端')
        dlg.Destroy()

    def read_ssh_config(self, filename):
        sshcf = configparser.ConfigParser()
        sshcf.read('data/sshclient/%s' % filename)
        info = [sshcf.get('default', 'num'),
                sshcf.get('default', 'host'),
                sshcf.get('default', 'port'),
                sshcf.get('default', 'user'),
                sshcf.get('default', 'password'),
                filename,
                sshcf.get('default', 'desc')]
        return info


# shell界面分割窗
class shell_panel(wx.SplitterWindow):
    def __init__(self, parent, conn):
        wx.SplitterWindow.__init__(self,parent=parent, size=(256, -1), style=wx.SP_NOBORDER | wx.TAB_TRAVERSAL)
        self.conn = conn
        self.SetBackgroundColour(globals.bgcolor)

        self.browser = WebView.New(self,backend=BACKEND)

        self.nb_console_operate = shell_notebook(self, self.conn)
        self.nb_console_operate.SetTabAreaColour(globals.panel_bgcolor)

        self.SetMinimumPaneSize(200)
        self.SplitHorizontally(self.browser, self.nb_console_operate, -200)
        self.SetSashGravity(1)

        self.refresh()

    def refresh(self):
        if self.conn:
            passwd_base64 = base64.b64encode(self.conn.password.encode('utf8'))
            passwd_base64 = passwd_base64.decode('utf8')
            url = "http://127.0.0.1:%s/?hostname=%s&username=%s&password=%s" % (
                globals.wssh_port, self.conn.host, self.conn.username, passwd_base64)
        else:
            url = "http://127.0.0.1:%s" % globals.wssh_port
        self.browser.LoadURL(url)

class DeafaultPage(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)

        self.conn = None
        self.SetBackgroundColour('white')

        self.bSizer1 = wx.BoxSizer(wx.VERTICAL)
        cols = ['名称', '起始IP', '端口', '数量', '用户名', '描述']
        self.listCtrl = sshclient_list(self, cols)
        self.listCtrl.SetColumnWidth(0, 150)
        self.listCtrl.SetColumnWidth(1, 120)
        self.listCtrl.SetColumnWidth(2, 60)
        self.listCtrl.SetColumnWidth(3, 60)
        self.bSizer1.Add(self.listCtrl, 1, wx.TOP | wx.BOTTOM | wx.LEFT, 20, 1)
        self.SetSizer(self.bSizer1)

        for parent, dirnames, filenames in os.walk('data/sshclient'):
            n = 0
            for filename in filenames:
                n += 1
                cf = configparser.ConfigParser()
                cf.read('data/sshclient/%s' % filename)
                info = [filename,
                        cf.get('default', 'host'),
                        cf.get('default', 'port'),
                        cf.get('default', 'num'),
                        cf.get('default', 'user'),
                        cf.get('default', 'desc')]
                # 增加行
                row = self.listCtrl.InsertItem(n, filename)
                for col in range(len(info)):
                    self.listCtrl.SetItem(row, col, info[col])


class CopyPage(wx.Panel):
    def __init__(self, parent, conn):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.conn = conn
        self.SetBackgroundColour(globals.bgcolor)

        self.browser = WebView.New(self,backend=BACKEND)
        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(self.browser, 1, wx.EXPAND)

        self.SetSizer(bsizer)
        self.refresh()

    def refresh(self):
        if self.conn:
            passwd_base64 = base64.b64encode(self.conn.password.encode('utf8'))
            passwd_base64 = passwd_base64.decode('utf8')
            url = "http://127.0.0.1:%s/?hostname=%s&username=%s&password=%s" % (
                globals.wssh_port, self.conn.host, self.conn.username,passwd_base64)
        else:
            url = "http://127.0.0.1:%s" % globals.wssh_port
        self.browser.LoadURL(url)

class shell_notebook(FNB.FlatNotebook):
    def __init__(self, parent, conn):
        FNB.FlatNotebook.__init__(self, parent=parent,  agwStyle=FNB.FNB_NODRAG | FNB.FNB_FF2
                                                                    | FNB.FNB_NO_X_BUTTON
                                                                    | FNB.FNB_NO_TAB_FOCUS)
        self.ssh_panel = parent.Parent.Parent
        self.conn = conn
        self.cmd_on_sel = None
        self.show_hiden = False
        self.cmd_bt_dict = {}
        self.item_sel = None
        self.MONITER_STAT = True

        self.panel_file = wx.Panel(self)
        self.panel_cmd = wx.Panel(self)
        self.panel_moniter = wx.Panel(self)
        self.panel_moniter.SetBackgroundColour('white')
        self.AddPage(self.panel_cmd, '命令')
        self.AddPage(self.panel_file, '文件')
        self.AddPage(self.panel_moniter, '系统信息')
        self.SetFont(wx.Font(10, 70, 90, 92, False, "宋体"))

        self.init_panel_cmd()
        self.init_panel_file()
        self.init_panel_moniter()
        self.Layout()

    ### 文件窗口
    def init_panel_file(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.panel_file.SetSizer(sizer_main)
        self.panel_file.SetBackgroundColour('white')

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_path = wx.TextCtrl(self.panel_file, value='/', size=(300, -1),
                                   style=wx.NO_BORDER
                                         | wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.onPathEnter, self.tc_path)
        self.tc_path.SetForegroundColour(wx.Colour(150, 150, 150))
        self.tc_path.SetFont(wx.Font(wx.Font(11, 70, 90, 90, False, '微软雅黑')))
        bt_refresh = mBitmapButton(self.panel_file, 'bitmaps/ssh_refresh.png', '刷新')
        bt_back = mBitmapButton(self.panel_file, 'bitmaps/ssh_back.png', '上级目录')
        bt_down = mBitmapButton(self.panel_file, 'bitmaps/ssh_down.png', '下载')
        bt_up = mBitmapButton(self.panel_file, 'bitmaps/ssh_up.png', '上传')
        bt_refresh.Bind(wx.EVT_BUTTON, self.onRefresh)
        bt_back.Bind(wx.EVT_BUTTON, self.onBackDir)
        bt_down.Bind(wx.EVT_BUTTON, self.onDownload)
        bt_up.Bind(wx.EVT_BUTTON, self.onUpload)

        sizer1.Add(self.tc_path, 1, wx.ALIGN_CENTER)
        sizer1.Add(bt_refresh, 0, wx.EXPAND, wx.LEFT, 5)
        sizer1.Add(bt_back, 0, wx.EXPAND, wx.LEFT, 5)
        sizer1.Add(bt_down, 0, wx.EXPAND, wx.LEFT, 5)
        sizer1.Add(bt_up, 0, wx.EXPAND, wx.LEFT, 5)
        sizer_main.Add(sizer1, 0, wx.EXPAND)

        self.file_tree = mHyperTreeList(self.panel_file,
                                        cols=['名称', '大小', '类型', '修改时间', '权限', '用户/用户组'])
        self.file_tree.setColumnWidth([200, 60, 60, 100, 100, 100])
        sizer_main.Add(self.file_tree, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 3)

        self.bmp_folder = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_TOOLBAR, (16, 16))
        self.bmp_file = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, (16, 16))
        self.file_tree.setImageList([self.bmp_folder, self.bmp_file])
        self.file_tree.root = self.file_tree.AddRoot('/', image=0)
        self.item_sel = self.file_tree.root

        self.file_tree.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.onDClick)
        self.file_tree.GetMainWindow().Bind(wx.EVT_LEFT_UP, self.onClick)
        self.file_tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.onRightUp)
        self.file_tree.GetMainWindow().Bind(wx.EVT_RIGHT_DOWN, self.onRightDown)
        self.file_tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.onLabelEdit)

        self.refresh_dir(self.file_tree.root)
        self.file_tree.Expand(self.file_tree.root)

    # 路径输入框回车事件
    def onPathEnter(self, evt):
        path = self.tc_path.GetValue()
        p_list = path.split('/')[1:]
        if not p_list:
            return
        cur_item = self.file_tree.root
        for p in p_list:
            for item in cur_item.GetChildren():
                if item.GetText() == p:
                    if item.GetImage() != 0:
                        break
                    self.refresh_dir(item)
                    self.file_tree.Expand(item)
                    self.file_tree.SelectItem(item)
                    cur_item = item
        self.item_sel = cur_item
        path = self.getItemPath(cur_item)
        if path != self.tc_path.GetValue():
            self.tc_path.SetValue(path)
        self.file_tree.SetFocus()

    def onRefresh(self, evt):
        self.onPathEnter(None)
        self.refresh_dir(self.item_sel)

    def onBackDir(self, evt):
        path = self.tc_path.GetValue()
        p_list = path.split('/')[1:-1]
        if not p_list:
            return
        cur_item = self.file_tree.root
        for p in p_list:
            for item in cur_item.GetChildren():
                if item.GetText() == p:
                    if item.GetImage() != 0:
                        break
                    self.refresh_dir(item)
                    self.file_tree.Expand(item)
                    self.file_tree.SelectItem(item)
                    cur_item = item
        self.item_sel = cur_item
        path = self.getItemPath(cur_item)
        if path != self.tc_path.GetValue():
            self.tc_path.SetValue(path)
        self.file_tree.SetFocus()

    def onDownload(self, evt):
        remote_path = self.getItemPath(self.item_sel)
        dlg = dialogs.mWarnDlg('下载的文件或目录路径：%s' % remote_path)
        if dlg.ShowModal() == wx.ID_OK:
            pass
        else:
            return
        dlg.Destroy()
        local_path = methods.get_config('ssh', 'download_path')
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        self.ssh_panel.ShowSSHMenu()
        start_new_thread(self.download, (local_path, remote_path))

    def onUpload(self, evt):
        remote_path = self.tc_path.GetValue()
        dlg = file_choice()
        dlg.st_path.SetLabel(remote_path)
        if dlg.ShowModal() == wx.ID_OK:
            local_paths = dlg.dirCtrl.GetPaths()
        else:
            dlg.Destroy()
            return
        multi = dlg.cb_multi.GetValue()
        rootlimit = dlg.cb_rootlimit.GetValue()
        dlg.Destroy()
        if multi:
            start_new_thread(self.multi_upload, (local_paths, remote_path, rootlimit))
        else:
            start_new_thread(self.upload, (local_paths, remote_path, rootlimit))
            self.ssh_panel.ShowSSHMenu()

    def multi_upload(self, local_paths, remote, rootlimit=False):
        self.ssh_panel.sftp_status = True  # 用来控制取消
        for conn in list(globals.multi_ssh_conn.values()):
            conn.gauge.SetValue(0, '等待上传')
        for conn in list(globals.multi_ssh_conn.values()):
            if not conn.linkok():
                conn.gauge.SetLeftString('连接异常')
                continue
            if rootlimit:
                conn.send('mount -o remount,rw /')
            self.sftp = conn.get_sftp()
            remote_path_map = {}
            for path in local_paths:  # 遍历所有文件
                if os.path.isdir(path):
                    self.refreshUploadList(path, remote, remote_path_map)
                else:
                    if os.path.getsize(path) == 0:
                        continue
                    filename = path.split('\\')[-1]
                    filename = filename.replace(" ", "_")
                    remote_path_map[path] = remote + '/' + filename
            try:
                for path in remote_path_map.keys():  # 逐个上传
                    conn.gauge.SetValue(0, path.split('\\')[-1])
                    conn.upload(path, remote_path_map[path], gauge=True)
                conn.gauge.SetValue(100, '无')
            except Exception as e:
                logging.error(e)
                continue

    def refreshUploadList(self, dirpath, remote, path_map):
        dirname = dirpath.split('\\')[-1]
        if remote == '/':
            remote = remote + dirname
        else:
            remote = remote + '/' + dirname  # 递归
        try:
            self.sftp.mkdir(remote)
        except Exception as e:
            logging.error(e)
        file_list = os.listdir(dirpath)
        for file in file_list:
            file = file.replace(" ", "_")
            cur_path = os.path.join(dirpath, file)
            if os.path.isdir(cur_path):
                self.refreshUploadList(cur_path, remote, path_map)
            else:
                if os.path.getsize(cur_path)==0:
                    continue
                else:
                    remote_path = remote + '/' + file
                    path_map[cur_path] = remote_path

    def upload(self, local_paths, remote, rootlimit=False):
        if not self.conn.linkok():
            self.conn.gauge.SetLeftString('连接异常')
            return
        if rootlimit:
            self.conn.send('mount -o remount,rw /')
        self.sftp = self.conn.get_sftp()
        self.ssh_panel.sftp_status = True  # 用来控制取消
        path_map = {}
        for path in local_paths:  # 遍历所有文件
            if os.path.isdir(path):
                self.refreshUploadList(path, remote, path_map)
            else:
                if os.path.getsize(path) == 0:
                    continue
                remote_path = remote + '/' + path.split('\\')[-1]
                idx = self.ssh_panel.ssh_menu.ulc_ssh.addItem(remote_path, 0)
                path_map[idx] = [path, remote_path]
        for index in path_map.keys():  # 逐个上传
            self.trans_index = index
            klass = self.ssh_panel.ssh_menu.ulc_ssh.map_klass[index]
            if not self.ssh_panel.sftp_status:
                klass.done = '已取消'
                wx.CallAfter(self.ssh_panel.ssh_menu.ulc_ssh.RefreshItem, index)
                continue
            try:
                self.sftp.put(path_map[index][0], path_map[index][1], callback=self.callback)
            except Exception as e:
                logging.error(f'{self.conn.host}: {e}')
                continue

        if self.ssh_panel.sftp_status:
            self.sftp.close()
            self.ssh_panel.sftp_status = False
        path_map.clear()
        if self.item_sel.GetImage() == 0:
            self.refresh_dir(self.item_sel)
        else:
            self.refresh_dir(self.item_sel.GetParent())

    def download(self, local, remote):
        basic_path = '/'.join(remote.split('/')[:-1])
        self.sftp = self.conn.get_sftp()
        self.ssh_panel.sftp_status = True  # 用来控制取消
        files = self.getRemoteFiles(remote, self.sftp)
        indexs = []

        for file in files:
            idx = self.ssh_panel.ssh_menu.ulc_ssh.addItem(file, 1)
            indexs.append(idx)
        for index in indexs:
            self.trans_index = index
            klass = self.ssh_panel.ssh_menu.ulc_ssh.map_klass[index]
            if not self.ssh_panel.sftp_status:
                klass.done = '已取消'
                wx.CallAfter(self.ssh_panel.ssh_menu.ulc_ssh.RefreshItem, index)
                continue
            remoteFileName = klass.filepath
            remote_son_dir = '/'.join(remoteFileName.split('/')[0:-1])
            son_dir = '/'+re.sub(basic_path,'',remote_son_dir)
            localFileName = os.path.join(local + son_dir, remoteFileName.split('/')[-1])
            if not os.path.exists(local + son_dir):
                os.makedirs(local + son_dir)
            try:
                self.last_callback_time = time.time()
                self.last_transferred = 0
                self.transfer_rate = '0K'
                self.sftp.get(remoteFileName, localFileName, callback=self.callback)
                if self.getRemoteFileSize(self.sftp, remoteFileName)== 0:
                    klass.progress = 100
                    klass.done = '已完成'
                    wx.CallAfter(self.ssh_panel.ssh_menu.ulc_ssh.RefreshItem, index)
            except Exception as e:
                logging.error(f'{self.conn.host}: {str(e)}')

        if self.ssh_panel.sftp_status:
            self.sftp.close()
            self.ssh_panel.sftp_status = False

    def callback(self, curent, total):
        now = time.time()
        elapsed_time = now - self.last_callback_time
        if elapsed_time >= 0.5:
            self.last_callback_time = now
            elapsed_data = curent - self.last_transferred
            self.last_transferred = curent
            self.transfer_rate = methods.bytes2human(elapsed_data / elapsed_time)
        klass = self.ssh_panel.ssh_menu.ulc_ssh.map_klass[self.trans_index]
        if not self.ssh_panel.sftp_status:
            klass.done = '已取消'
            self.sftp.close()
        else:
            klass.progress = round(100 * curent / total, 1)
            if klass.progress < 100:
                klass.done = f'{methods.bytes2human(curent)}-{klass.progress}%-{self.transfer_rate}/s'
            else:
                klass.done = '已完成'
        wx.CallAfter(self.ssh_panel.ssh_menu.ulc_ssh.RefreshItem, self.trans_index)

    def getRemoteFiles(self, remote, sftp):
        try:
            filesAttr = sftp.listdir_attr(remote)
            for fileAttr in filesAttr:
                # 判断是否为目录
                if stat.S_ISDIR(fileAttr.st_mode):
                    son_remoteDir = remote + '/' + fileAttr.filename
                    yield from self.getRemoteFiles(son_remoteDir, sftp)
                else:
                    if stat.S_ISREG(fileAttr.st_mode):  # 判断是否为普通文件，排除符号链接
                        yield remote + '/' + fileAttr.filename
        except:
            yield remote

    def getRemoteFileSize(self, sftp, path):
        return sftp.stat(path).st_size

    def refresh_dir(self, father):
        self.file_tree.DeleteChildren(father)
        path = self.getItemPath(father)
        if self.show_hiden:
            cmd = "ls -AhlL %s" % path
        else:
            cmd = 'ls -hlL %s' % path
        files = self.conn.recv(cmd).split('\n')
        files.sort(reverse=True)

        for file in files[1:]:
            filename = ''
            if not file:
                continue
            info = file.strip().split(' ')
            info = [item for item in info if item != '']

            # 处理文件名带空格的情况
            if len(info) < 10:
                filename = info[8]
            else:
                for item in info[8:]:
                    filename += item
            child = self.file_tree.AppendItem(father, filename)
            self.file_tree.SetItemText(child, info[4], 1)
            if not info[0][0] == 'd':
                self.file_tree.SetItemText(child, '文件', 2)
                self.file_tree.SetItemImage(child, 1)
            else:
                self.file_tree.SetItemText(child, '目录', 2)
                self.file_tree.SetItemImage(child, 0)
            self.file_tree.SetItemText(child, info[5] + info[6] + ' ' + info[7], 3)
            self.file_tree.SetItemText(child, info[0], 4)
            self.file_tree.SetItemText(child, info[2] + '/' + info[3], 5)
        self.file_tree.SelectItem(father)

    def getItemPath(self, item):
        path = item.GetText()
        if path == '/':
            return path
        parent = item.GetParent()
        while parent:
            txt = parent.GetText()
            if txt == '/':
                path = txt + path
            else:
                path = txt + '/' + path
            parent = parent.GetParent()
        return path

    def onClick(self, event):
        pt = event.GetPosition()
        item = self.file_tree.HitTest(pt)[0]
        if not item:
            return
        self.item_sel = item
        if item.GetImage() == 0:
            self.tc_path.SetValue(self.getItemPath(self.item_sel))
        else:
            self.tc_path.SetValue(self.getItemPath(self.item_sel.GetParent()))

    def onDClick(self, event):
        pt = event.GetPosition()
        item = self.file_tree.HitTest(pt)[0]
        if not item:
            return
        self.item_sel = item
        if item.GetImage() == 0:
            self.tc_path.SetValue(self.getItemPath(self.item_sel))
            if item._isCollapsed:
                self.refresh_dir(item)
        else:
            path = self.getItemPath(self.item_sel)
            txt_type = self.conn.recv('file %s' % path)
            txt_type = txt_type.split(':')[1]
            if 'ASCII text' in txt_type:
                if 'Non-ISO' in txt_type:
                    mMessageBox('不支持的编码')
                else:
                    txt = self.conn.recv('cat %s' % path)
                    frm = file_edit(self, path, self.conn, txt.replace('\r', ''))
                    frm.Show()
            elif 'Unicode text' in txt_type:
                txt = self.conn.recv('cat %s' % path)
                frm = file_edit(self, path, self.conn, txt.replace('\r', ''))
                frm.Show()
            elif 'empty' in txt_type:
                txt = self.conn.recv('cat %s' % path)
                frm = file_edit(self, path, self.conn, txt.replace('\r', ''))
                frm.Show()
            else:
                mMessageBox('不支持的文件类型')
        event.Skip()

    def onRightDown(self, event):
        pt = event.GetPosition()
        item, flags, column = self.file_tree.HitTest(pt)
        if item:
            self.item_sel = item
        self.file_tree.SelectItem(self.item_sel)
        if item.GetImage() == 0:
            self.tc_path.SetValue(self.getItemPath(self.item_sel))
        else:
            self.tc_path.SetValue(self.getItemPath(self.item_sel.GetParent()))

    def onRightUp(self, event):
        pt = event.GetPosition()
        item = self.file_tree.HitTest(pt)[0]
        if not item:
            return
        menu = wx.Menu()
        if item.GetImage() == 0:
            menu_list = ['刷新', 0, '上传', '下载', 0, '新建文件夹', '新建文件', '重命名', 0, '文件权限', '复制路径', 0,
                         '删除']
        else:
            menu_list = ['编辑', '下载', 0, '重命名', 0, '文件权限', '复制路径', 0, '删除']
        for txt in menu_list:
            if txt == 0:
                menu.AppendSeparator()
                continue
            item = menu.Append(-1, txt)
            self.Bind(wx.EVT_MENU, self.onFilePopupMenu, item)
        self.PopupMenu(menu)
        menu.Destroy()

    def onLabelEdit(self, evt):
        name = evt.GetLabel()
        old = self.getItemPath(self.item_sel)
        new = '/'.join(old.split('/')[:-1]) + '/' + name
        self.conn.recv('mv %s %s' % (old, new))
        self.refresh_dir(self.item_sel)

    def onFilePopupMenu(self, evt):
        txt = getLabelFromEVT(evt)
        if txt == '刷新':
            self.refresh_dir(self.item_sel)
        elif txt == '复制路径':
            pyperclip.copy(self.getItemPath(self.item_sel))
        elif txt == '新建文件夹':
            dirpath = self.getItemPath(self.item_sel)
            dlg = wx.TextEntryDialog(None, '创建路径：%s\n文件夹名称' % dirpath, '新建文件夹')
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                path = dirpath + '/' + name
                self.conn.recv('mkdir %s' % path)
                self.refresh_dir(self.item_sel)
            dlg.Destroy()
        elif txt == '新建文件':
            dirpath = self.getItemPath(self.item_sel)
            dlg = wx.TextEntryDialog(None, '创建路径：%s\n文件名称' % dirpath, '新建文件')
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                path = dirpath + '/' + name
                frm = file_edit(self, path, self.conn)
                frm.Show()
            dlg.Destroy()
        elif txt == '重命名':
            self.file_tree.EditLabel(self.item_sel)
        elif txt == '删除':
            dlg = mWarnDlg('删除后无法恢复，是否继续？')
            if dlg.ShowModal() == wx.ID_OK:
                path = self.getItemPath(self.item_sel)
                self.conn.recv('rm -rf %s' % path)
                self.refresh_dir(self.item_sel.GetParent())
            dlg.Destroy()
        elif txt == '文件权限':
            path = self.getItemPath(self.item_sel)
            filename = path.split('/')[-1]
            re = self.conn.recv('ls -dlL %s' % path)
            mod = re.split(' ')[0][1:10]
            dlg = file_chmod(filename, mod)
            if dlg.ShowModal() == wx.ID_OK:
                mod = dlg.GetMod()
                self.conn.recv('chmod -R %s %s' % (mod, path))
                self.refresh_dir(self.item_sel.GetParent())
            dlg.Destroy()
        elif txt == '上传':
            self.onUpload(None)
        elif txt == '下载':
            remote_path = self.getItemPath(self.item_sel)
            local_path = methods.get_config('ssh', 'download_path')
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            self.ssh_panel.ShowSSHMenu()
            start_new_thread(self.download, (local_path, remote_path))
        elif txt == '编辑':
            path = self.getItemPath(self.item_sel)
            txt = self.conn.recv('cat %s' % path)
            frm = file_edit(self, path, self.conn, txt.replace('\r', ''))
            frm.Show()

    ### 命令窗口
    def init_panel_cmd(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.panel_cmd.SetSizer(sizer_main)

        splitter = wx.SplitterWindow(self.panel_cmd, style=wx.SP_NOBORDER)
        splitter.SetSashGravity(1)
        sizer_main.Add(splitter, 1, wx.EXPAND)

        pnl_l = wx.Panel(splitter, style=wx.NO_BORDER)
        pnl_l.SetBackgroundColour('white')
        self.pnl_r = wx.Panel(splitter, style=wx.NO_BORDER)
        self.pnl_r.SetBackgroundColour('white')

        splitter.SetMinimumPaneSize(200)
        splitter.SplitVertically(pnl_l, self.pnl_r, -300)

        sizer_l = wx.BoxSizer(wx.VERTICAL)
        sizer_r = wx.BoxSizer(wx.VERTICAL)
        pnl_l.SetSizer(sizer_l)
        self.pnl_r.SetSizer(sizer_r)

        txt2 = wx.StaticText(pnl_l, label='命令编辑器')
        txt2.SetBackgroundColour('white')
        txt2.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer_l.Add(txt2, 0, wx.EXPAND, wx.LEFT, 5)

        self.stc = mSTC(pnl_l)
        sizer_l.Add(self.stc, 1, wx.EXPAND)

        txt1 = wx.StaticText(pnl_l, label='发送到')
        txt1.SetFont(wx.Font(10, 70, 90, 90, False, "微软雅黑"))

        self.combo = wx.ComboBox(pnl_l, style=wx.CB_DROPDOWN, size=(-1, 23))
        self.combo.Append('全部会话')
        self.combo.Append('当前会话')
        self.combo.SetStringSelection('全部会话')
        self.bt_send = wx.Button(pnl_l, label='发送命令')
        self.bt_send.Bind(wx.EVT_BUTTON, lambda evt, args=self.send_cmd: start_new_thread(args, ()))
        self.bt_save = wx.Button(pnl_l, label='保存命令')
        self.bt_save.Bind(wx.EVT_BUTTON, self.on_bt_save)
        self.bt_sendkeys = wx.Button(pnl_l, label='发送快捷键')
        self.bt_sendkeys.Bind(wx.EVT_BUTTON, self.on_bt_sendkeys)
        self.combo_keys = wx.ComboBox(pnl_l, style=wx.CB_DROPDOWN, size=(-1, 23))
        keys = ['ctrl+c', 'ctrl+z']
        for key in keys:
            self.combo_keys.Append(key)
        self.combo_keys.SetStringSelection('ctrl+c')

        sizer_l_bot = wx.BoxSizer(wx.HORIZONTAL)
        sizer_l_bot.Add(txt1, 0, wx.ALIGN_CENTER|wx.LEFT,10)
        sizer_l_bot.Add(self.combo, 0, wx.EXPAND | wx.LEFT, 2)
        sizer_l_bot.Add(self.bt_send, 0, wx.EXPAND)
        sizer_l_bot.Add(self.bt_save, 0, wx.EXPAND | wx.LEFT|wx.RIGHT,5)
        sizer_l_bot.Add((-1,0),1,wx.EXPAND)
        sizer_l_bot.Add(self.combo_keys, 0, wx.EXPAND)
        sizer_l_bot.Add(self.bt_sendkeys, 0, wx.EXPAND|wx.RIGHT,10 )

        # sizer_l.Add(sizer_l_bot, 0, wx.ALIGN_CENTER)
        sizer_l.Add(sizer_l_bot, 0,wx.EXPAND)

        txt3 = wx.StaticText(self.pnl_r, label='命令管理')
        txt3.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer_r.Add(txt3, 0, wx.EXPAND | wx.LEFT, 5)

        self.sizer_r_bt = wx.WrapSizer(wx.HORIZONTAL)
        sizer_r.Add(self.sizer_r_bt, 1, wx.EXPAND)

        self.pnl_r.Bind(wx.EVT_RIGHT_DOWN, self.SetPnlRightPopmenu)
        self.popupmenu_text = ['添加命令']

        self.init_cmds()

    def on_bt_save(self, evt):
        dlg = add_cmd_dlg()
        dlg.cmd.SetValue(self.stc.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.name.GetValue()
            if not name:
                mMessageBox('名称不能为空')
                return
            new_cmds = dlg.cmd.GetValue().split('\n')

            fo = open("data/cmd/%s" % name, "w")
            fo.write(new_cmds[0].strip())
            for i in new_cmds[1:]:
                fo.write('\n' + i.strip())
            fo.close()
            self.add_cmd_bt(name)
        dlg.Destroy()

    def on_bt_sendkeys(self, evt):
        keys = self.combo_keys.GetValue()
        self.send_cmd(keys)


    def SetPnlRightPopmenu(self, evt):
        menu = wx.Menu()
        for text in self.popupmenu_text:
            item = menu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.onPnlRightPopupMenu, item)
        self.PopupMenu(menu)

    def onPnlRightPopupMenu(self, evt):
        label = getLabelFromEVT(evt)
        if label == '添加命令':
            dlg = add_cmd_dlg()
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.name.GetValue()
                cmds = dlg.cmd.GetValue().split('\r')
                fo = open("data/cmd/%s" % name, "w")
                fo.writelines(cmds)
                fo.close()
                self.add_cmd_bt(name)
            dlg.Destroy()

    def send_cmd(self,keys=None):
        key_value = {'ctrl+c':'\x03', 'ctrl+z':'\x1a'}
        self.bt_send.Disable()
        value = self.stc.GetValue()
        cmds = value.split('\n')
        i = 0
        if self.combo.GetValue() == '全部会话':
            self.ssh_panel.setTreeYellow()
            for conn in list(globals.multi_ssh_conn.values()):
                if not conn.linkok():
                    self.ssh_panel.tree_session.SetItemImage(self.ssh_panel.treeNode_dict[conn.host],
                                                             self.ssh_panel.redball)
                    continue
                if not keys:
                    for cmd in cmds:
                        conn.send(cmd.strip())
                else:
                    conn.send(key_value[keys])
                i += 1
                self.ssh_panel.tree_session.SetItemImage(self.ssh_panel.treeNode_dict[conn.host],
                                                         self.ssh_panel.greenball)
            self.ssh_panel.st_session_count.SetLabel(str(i))
            if i == 0:
                self.ssh_panel.close_all_ssh(None)
            else:
                self.link_ok = i
                wx.CallAfter(self.ssh_panel.st_session_count.SetLabel, str(i))
        else:
            self.ssh_panel.tree_session.SetItemImage(self.ssh_panel.treeNode_dict[globals.cur_conn.host],
                                                     self.ssh_panel.yellowball)
            if not keys:
                for cmd in cmds:
                    globals.cur_conn.send(cmd.strip())
            else:
                globals.cur_conn.send(key_value[keys])
            self.ssh_panel.tree_session.SetItemImage(self.ssh_panel.treeNode_dict[globals.cur_conn.host],
                                                     self.ssh_panel.greenball)
        self.bt_send.Enable()

    def init_cmds(self):
        for root, dirs, files in os.walk('data/cmd'):
            for file in files:
                self.add_cmd_bt(file)

    def add_cmd_bt(self, label):
        bt = mFocusButton(self.pnl_r, label, bitmap='bitmaps/cmd.png', bg_colour='white')
        self.sizer_r_bt.Add(bt, 0, wx.TOP | wx.LEFT, 5)
        bt.SetFocus()
        bt.SetPopupMenu(['编辑', '删除'], self.onCMDPopupMenu)
        bt.Bind(wx.EVT_BUTTON, self.on_cmd_bt)
        self.cmd_bt_dict[label] = bt
        self.pnl_r.Layout()

    def on_cmd_bt(self, evt):
        name = evt.GetEventObject().GetLabel()
        fo = open("data/cmd/%s" % name, "r")
        cmds = fo.read()
        self.stc.SetValue(cmds)

    def onCMDPopupMenu(self, evt):
        label = getLabelFromEVT(evt)
        name = self.cmd_on_sel
        if label == '编辑':
            dlg = add_cmd_dlg()
            dlg.name.SetLabel(name)
            fo = open("data/cmd/%s" % name, "r")
            cmds = fo.read()
            dlg.cmd.SetValue(cmds)
            fo.close()
            if dlg.ShowModal() == wx.ID_OK:
                new_name = dlg.name.GetValue()
                if not new_name:
                    mMessageBox('名称不能为空')
                    return
                new_cmds = dlg.cmd.GetValue().split('\n')

                fo = open("data/cmd/%s" % name, "w")
                fo.write(new_cmds[0].strip())
                for i in new_cmds[1:]:
                    fo.write('\n' + i.strip())
                fo.close()
                bt = self.cmd_bt_dict[name]
                bt.SetLabel(new_name)
                bt.SetSize(bt.GetBestSize())
                self.pnl_r.Layout()
                self.cmd_bt_dict[new_name] = bt
                os.rename('data/cmd/%s' % name, 'data/cmd/%s' % new_name)
            dlg.Destroy()

        elif label == '删除':
            dlg = mWarnDlg('确认删除命令：%s' % name)
            if dlg.ShowModal() == wx.ID_OK:
                os.remove('data/cmd/%s' % name)
                self.cmd_bt_dict[name].Destroy()
                self.pnl_r.Layout()
            dlg.Destroy()

    # 监控窗口
    def init_panel_moniter(self):
        sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.panel_moniter.SetSizer(sizer_main)
        sizer1 = wx.BoxSizer(wx.VERTICAL)  # CPU 内存 运行
        s1l0 = wx.BoxSizer(wx.HORIZONTAL)
        s1l1 = wx.BoxSizer(wx.HORIZONTAL)
        s1l2 = wx.BoxSizer(wx.HORIZONTAL)
        s1l3 = wx.BoxSizer(wx.HORIZONTAL)
        s1l4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(s1l0, 0, wx.EXPAND)
        sizer1.Add(s1l1, 0, wx.EXPAND)
        sizer1.Add(s1l2, 0, wx.EXPAND)
        sizer1.Add(s1l3, 0, wx.EXPAND)
        sizer1.Add(s1l4, 0, wx.EXPAND)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer3 = wx.BoxSizer(wx.VERTICAL)  #
        sizer_main.Add(sizer1, 0, wx.EXPAND)
        sizer_main.Add(sizer2, 0, wx.EXPAND)
        sizer_main.Add(sizer3, 0, wx.EXPAND)

        self.gauge_cpu = mGauge(self.panel_moniter)
        self.gauge_mem = mGauge(self.panel_moniter)
        self.gauge_swap = mGauge(self.panel_moniter)
        st_cpu = wx.StaticText(self.panel_moniter, label='CPU')
        st_mem = wx.StaticText(self.panel_moniter, label='内存')
        st_swap = wx.StaticText(self.panel_moniter, label='交换')

        st_1 = wx.StaticText(self.panel_moniter, label='运行')
        st_2 = wx.StaticText(self.panel_moniter, label='负载')
        self.runtime = wx.StaticText(self.panel_moniter, label='')
        self.load = wx.StaticText(self.panel_moniter, label='')

        s1l0.Add(st_1, 0, wx.TOP | wx.LEFT, 5)
        s1l0.Add(self.runtime, 1, wx.TOP | wx.LEFT, 5)
        s1l1.Add(st_2, 0, wx.TOP | wx.LEFT, 5)
        s1l1.Add(self.load, 1, wx.TOP | wx.LEFT, 5)

        s1l2.Add(st_cpu, 0, wx.TOP | wx.LEFT, 5)
        s1l2.Add(self.gauge_cpu, 0, wx.TOP | wx.LEFT, 5)
        s1l3.Add(st_mem, 0, wx.TOP | wx.LEFT, 5)
        s1l3.Add(self.gauge_mem, 0, wx.TOP | wx.LEFT, 5)
        s1l4.Add(st_swap, 0, wx.TOP | wx.LEFT, 5)
        s1l4.Add(self.gauge_swap, 0, wx.TOP | wx.LEFT, 5)

        re = self.conn.recv("cat /proc/stat | head -n 1 | awk '{print $2,$3,$4,$5}'")
        re = re.strip().split('\n')
        cpuinfo = re[0].strip().split(' ')
        self.use_tmp = int(cpuinfo[0]) + int(cpuinfo[1]) + int(cpuinfo[2])
        self.idle_tmp = int(cpuinfo[3])
        start_new_thread(self.momniter, ())

    def momniter(self):
        time.sleep(1)
        while self.MONITER_STAT:
            try:
                use = self.use_tmp
                idle = self.idle_tmp
                cmd = "cat /proc/stat | head -n 1 | awk '{print $2,$3,$4,$5}';" \
                      "free | tail -n +2 | awk '{print $2,$3,$7}';" \
                      "uptime"
                re = self.conn.recv(cmd)
                re = re.strip().split('\n')
                cpuinfo = re[0].strip().split(' ')
                self.use_tmp = int(cpuinfo[0]) + int(cpuinfo[1]) + int(cpuinfo[2])
                self.idle_tmp = int(cpuinfo[3])

                cpu_use = int(100 * (self.use_tmp - use) / (self.use_tmp - use + self.idle_tmp - idle))
                self.gauge_cpu.SetValue(cpu_use, '%s%%' % cpu_use)

                mem = re[1].split(' ')
                mem_use = int(mem[0]) - int(mem[2])
                mem_tot = int(mem[0])
                mem_use_per = int(100 * mem_use / mem_tot)
                mem_use_fit = bytes2human(mem_use, start='K')
                mem_tot_fit = bytes2human(mem_tot, start='K')
                self.gauge_mem.SetValue(mem_use_per, '%s%%' % mem_use_per, '%s/%s' % (mem_use_fit, mem_tot_fit))

                swap = re[2].split(' ')
                swap_use = int(swap[1])
                swap_tot = int(swap[0])
                if not swap_tot:
                    self.gauge_swap.SetValue(0, 'no swap', '')
                else:
                    swap_use_per = int(100 * swap_use / swap_tot)
                    swap_use_fit = bytes2human(swap_use, start='K')
                    swap_tot_fit = bytes2human(swap_tot, start='K')
                    self.gauge_swap.SetValue(swap_use_per, '%s%%' % swap_use_per, '%s/%s' % (swap_use_fit, swap_tot_fit))

                uptime = re[3].split(',')
                self.runtime.SetLabel(uptime[0].split('up')[1])
                self.load.SetLabel(uptime[-3].split(':')[1] + uptime[-2] + uptime[-1])
                time.sleep(2)
            except Exception as e:
                logging.error(e)

