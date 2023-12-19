# -*- coding: utf-8 -*-
import logging, shutil, threadpool, wx.grid, wx.aui, pyperclip, base64, stat, configparser, os, re, time
from _thread import start_new_thread
from .myui import *
from functools import reduce
from module import methods, dialogs, globals, ssh
from module.widgets import platebtn
from wx.html2 import WebView
from module.dialogs import add_cmd_dlg, file_chmod, file_edit, file_choice, sshclient_list,system_moniter
from module.methods import getLabelFromEVT, bytes2human
from module.widgets import auiNotebook as ANB
import module.widgets.aui as aui
import wx.lib.agw.pycollapsiblepane as PCP

AUI_BUTTON_ADD = 201
AUI_BUTTON_FILETRANSFER = 202


class ssh_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.new_thread = methods.new_thread
        self.link_ok = 0  # 连接成功数
        self._IsMulti = True
        self.sftp_status = False
        self.is_split = False
        globals.multi_ssh_conn = {}  # host : {'conn','gauge'}
        self.treeNode_dict = {}  # host : child_id
        self.shellpage_dic = {}  # host : shell_panel
        self.__init__ui()
        self.__evt_bind()

    def __init__ui(self):
        self.splitter_all = wx.SplitterWindow(self)
        self.ssh_right_panel = wx.Panel(self.splitter_all)
        self.ssh_left_panel = wx.Panel(self.splitter_all)

        self.splitter_all.SplitVertically(self.ssh_left_panel, self.ssh_right_panel, 231)
        self.panel_multi_ssh = wx.Panel(self.ssh_left_panel, size=(231, -1))  # 批量连接设置
        self.splitter_left = wx.SplitterWindow(self.ssh_left_panel)

        self.panel_session_tree = wx.Panel(self.splitter_left, size=(231, -1), style=wx.BORDER_THEME)  # 连接列表
        self.panel_scp = scp_panel(self.splitter_left, None)  # 文件传输panel
        self.splitter_left.SplitHorizontally(self.panel_scp, self.panel_session_tree)
        self.splitter_left.SetSashGravity(0.5)

        # panel_multi_ssh
        bSizerInfo = wx.BoxSizer(wx.VERTICAL)
        self.panel_multi_ssh.SetSizer(bSizerInfo)
        info_label = wx.StaticText(self.panel_multi_ssh, label='批量连接', size=(-1, 25), style=wx.ALIGN_CENTER)
        info_label.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        info_label.SetBackgroundColour('#95a5a6')
        info_label.SetForegroundColour('#ffffff')
        self.num = mInput(self.panel_multi_ssh, st_label='数量', tc_label='2', st_size=(60, 25), font_size=12)
        self.host = mInput(self.panel_multi_ssh, st_label='起始IP', tc_label='172.31.13.240', st_size=(60, 25),
                           font_size=12)
        self.port = mInput(self.panel_multi_ssh, st_label='端口', tc_label='22', st_size=(60, 25), font_size=12)
        self.username = mInput(self.panel_multi_ssh, st_label='用户名', tc_label='root', st_size=(60, 25), font_size=12)
        self.password = mInput(self.panel_multi_ssh, st_label='密码', tc_label='oseasy@123', st_size=(60, 25),
                               font_size=12,
                               password=True)
        self.name = mInput(self.panel_multi_ssh, st_label='名称', tc_label='', st_size=(60, 25), font_size=12)
        self.desc = mInput(self.panel_multi_ssh, st_label='描述', tc_label='', st_size=(60, 25), font_size=12)
        self.bt_connect = mButton(self.panel_multi_ssh, label='连接', color='deepgreen', size=(-1, 25))
        self.bt_connect.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        self.CB_save = wx.CheckBox(self.panel_multi_ssh, wx.ID_ANY, "保存登录信息", wx.DefaultPosition, wx.DefaultSize,
                                   0)
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

        self.panel_multi_ssh.SetSizer(bSizerInfo)

        # panel_session_tree布局
        self.tree_session = mHyperTreeList(self.panel_session_tree, cols=['主机', '任务'])
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
        txt1 = wx.StaticText(self.panel_session_tree, label='在线数：')
        txt1.SetFont(wx.Font(11, 70, 90, 90, False, "微软雅黑"))
        self.st_session_count = wx.StaticText(self.panel_session_tree, label='0')
        self.st_session_count.SetFont(wx.Font(11, 70, 90, 90, False, "微软雅黑"))
        bt_refresh = mBitmapButton(self.panel_session_tree, 'bitmaps/refresh.png', '刷新')
        bt_refresh.Bind(wx.EVT_BUTTON, self.RefreshSSHList)
        bt_disconnect = mBitmapButton(self.panel_session_tree, 'bitmaps/disconnect.png', '全部断开')
        bt_disconnect.Bind(wx.EVT_BUTTON, self.close_all_ssh)

        bSizerBT.Add(txt1, 0, wx.LEFT | wx.ALIGN_CENTER, 5)
        bSizerBT.Add(self.st_session_count, 1, wx.ALIGN_CENTER)
        bSizerBT.Add(bt_refresh, 0, wx.ALIGN_CENTER | wx.LEFT, 5)
        bSizerBT.Add(bt_disconnect, 0, wx.ALIGN_CENTER | wx.LEFT, 5)
        bSizerTree = wx.BoxSizer(wx.VERTICAL)
        bSizerTree.Add(self.tree_session, 1, wx.EXPAND)
        bSizerTree.Add(bSizerBT, 0, wx.EXPAND)

        self.panel_session_tree.SetSizer(bSizerTree)

        # ssh_right_panel布局
        self.nb_console = ANB.auiNotebook(parent=self.ssh_right_panel)
        self.nb_console.tab_context_menu = {'txt': ['复制', '关闭其他'], 'method': self.onNotebookTabMenu}

        self.nb_console.addTabButtons(AUI_BUTTON_ADD, wx.LEFT,
                                      wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR, (20, 20)),
                                      self.onTabButtonAdd)

        self.ssh_menu = self.TopLevelParent.ssh_menu
        self.ssh_menu.st_path.SetLabel(methods.get_config('ssh', 'download_path'))

        self.cmd_panel = command_panel(self.ssh_right_panel)

        self.add_default_page()

        # 整体布局

        bSizer1 = wx.BoxSizer(wx.VERTICAL)  # 批量连接panel+spliter
        bSizer1.Add(self.panel_multi_ssh, 1, wx.EXPAND | wx.LEFT, 3)
        bSizer1.Add(self.splitter_left, 1, wx.EXPAND | wx.LEFT, 3)
        self.ssh_left_panel.SetSizer(bSizer1)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)  # SHELL界面
        bSizer2.Add(self.nb_console, 1, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)
        bSizer2.Add(self.cmd_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.ssh_right_panel.SetSizer(bSizer2)

        bSizerAll = wx.BoxSizer(wx.VERTICAL)
        bSizerAll.Add(self.splitter_all, 1, wx.EXPAND)
        self.SetSizer(bSizerAll)
        self.Layout()

    def __evt_bind(self):
        self.bt_connect.Bind(wx.EVT_BUTTON, self.create_connect)
        self.tree_session.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_sel)
        self.tree_session.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_tree_rightclick)
        self.tree_session.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_item_actived)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.onNotebookChange, self.nb_console)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.onNotebookPageClose, self.nb_console)
        self.TopLevelParent.menubarPnl.bt_transfer_menu.Bind(wx.EVT_BUTTON, self.ShowSSHMenu)
        self.TopLevelParent.menubarPnl.bt_split.Bind(wx.EVT_BUTTON, self.on_bt_split)
        self.TopLevelParent.menubarPnl.bt_moniter.Bind(wx.EVT_BUTTON, self.on_bt_moniter)
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

    def ShowSSHMenu(self, evt=None):
        rect = self.TopLevelParent.menubarPnl.bt_transfer_menu.GetRect()
        pos = self.TopLevelParent.menubarPnl.bt_transfer_menu.ClientToScreen((rect.width, 0))
        wid = self.ssh_menu.GetSize()[0]
        self.ssh_menu.Position(pos, (-5 - wid, 30))
        self.ssh_menu.Show(True)
        self.ssh_menu.st_path.SetLabel(methods.get_config('ssh', 'download_path'))

    def on_bt_split(self, evt):

        if self.TopLevelParent.mainPnl._sel != 0:
            return
        if not self.is_split:
            n = self.nb_console.GetPageCount()
            self.nb_console.Freeze()
            if n < 4:
                for i in range(n):
                    if i == 0:
                        continue
                    if i == 1:
                        self.nb_console.Split(i, wx.RIGHT)
                    if i > 1:
                        self.nb_console.Split(i, wx.DOWN)
            else:
                self.nb_console.Split(n - 3, wx.RIGHT)
                self.nb_console.Split(n - 2, wx.DOWN)
                self.nb_console.Split(n - 1, wx.DOWN)
            self.nb_console.Thaw()
            self.is_split = True
        else:
            self.nb_console.UnSplit()
            self.is_split = False

    def on_bt_moniter(self, evt):
        conn = self.get_cur_page().conn
        if not conn:
            return
        frm = system_moniter(self, conn.host, conn)
        frm.Show()
        frm.Raise()

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

    def onTabButtonAdd(self):
        self.add_default_page(self.nb_console.active_button_tab)

    def get_cur_page(self):
        return self.nb_console.GetPage(self.nb_console.GetSelection())

    def add_default_page(self, tabctrl=None):
        self.nb_console.Freeze()
        page = DeafaultPage(self.nb_console)
        if tabctrl:
            from wx.lib.agw.aui import framemanager
            info = wx.lib.agw.aui.auibook.AuiNotebookPage()
            info.window = page
            info.caption = '新标签页'
            info.active = True
            info.bitmap = wx.NullBitmap
            info.disabled_bitmap = wx.NullBitmap
            info.control = None
            info.tooltip = ''

            page_idx = self.nb_console.GetPageCount()

            originalPaneMgr = framemanager.GetManager(page)
            if originalPaneMgr:
                originalPane = originalPaneMgr.GetPane(page)

                if originalPane:
                    info.hasCloseButton = originalPane.HasCloseButton()
            self.nb_console._tabs.InsertPage(page, info, page_idx)

            tabctrl.AddPage(page, info)
            if self.nb_console._curpage >= page_idx:
                self.nb_console._curpage += 1
            self.nb_console.SetSelectionToWindow(page)
        else:
            self.nb_console.AddPage(page, '新标签页', True)
        page.listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_linklist_act)
        self.nb_console._PageCount += 1
        self.nb_console.Thaw()

    def onNotebookChange(self, evt):
        cur_page = self.nb_console.GetPage(self.nb_console.GetSelection())
        if cur_page.conn and self.panel_scp.conn != cur_page.conn:
            self.set_cur_conn(cur_page.conn)
            self.panel_scp.conn = cur_page.conn
            start_new_thread(self.panel_scp.refresh_dir, ())

    def onNotebookPageClose(self, evt):
        '点x时触发，事件完成后才调用DeletePage()，除此之外其他情况不添加default page'
        label = self.nb_console.GetPageText(evt.GetSelection())
        self.deletePageData(label)
        if self.nb_console._PageCount == 1:
            self.add_default_page()

    def DeleteAllPages(self, default_page=True):
        self.nb_console.Freeze()
        while self.nb_console._PageCount:
            self.nb_console.DeletePage(0)
            self.deletePageData(self.nb_console.GetPageText(0))
        if default_page:
            self.add_default_page()
        self.nb_console.Thaw()

    def deletePageData(self, page_label):
        '处理page相关线程和dict,只对dict内conn'
        if page_label in globals.multi_ssh_conn.keys():  # 不是复制的页面
            globals.multi_ssh_conn[page_label].console = False
            self.shellpage_dic.pop(page_label)
            # self.shellpage_dic[page_label].nb_console_operate.MONITER_STAT = False  # 停止监控线程

    def close_all_ssh(self, evt):
        self.DeleteAllPages(True)
        self.shellpage_dic.clear()
        self.treeNode_dict.clear()
        globals.multi_ssh_conn.clear()
        self.tree_session.root = None
        self.tree_session.DeleteAllItems()
        self.change_online_count(None)
        self.panel_multi_ssh.Show()
        self.splitter_left.Hide()
        self.panel_scp.tc_path.SetValue('')
        self.panel_scp.file_tree.DeleteChildren(self.panel_scp.file_tree.root)
        self.Layout()

    def onNotebookTabMenu(self, evt):
        menu = evt.GetEventObject()
        selected_item = menu.FindItemById(evt.GetId())
        label = selected_item.GetItemLabel()
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
        '已经connected'
        if not label:  # 不是复制
            new_page = shell_panel(self.nb_console, conn)
            self.shellpage_dic[conn.host] = new_page
            label = conn.host
        else:
            new_page = CopyPage(self.nb_console, conn)
        self.nb_console.AddPage(new_page, label, True)
        self.nb_console._PageCount += 1
        self.panel_scp.conn = conn
        self.panel_scp.init_file_tree()

    def get_copy_increate_label(self, ip):
        all_labels = [self.nb_console.GetPageText(i) for i in range(self.nb_console.GetPageCount())]
        filtered_labels = [label for label in all_labels if label.startswith(ip)]
        existing_numbers = [int(re.search(r'%s-(\d+)' % ip, s).group(1)) for s in filtered_labels if
                            re.search(r'%s-(\d+)' % ip, s)]
        if not existing_numbers:
            return f'{ip}-1'
        unused_number = next((i for i in range(1, max(existing_numbers) + 2) if i not in existing_numbers), None)
        new_string = f'%s-{unused_number}' % ip
        return new_string

    # 连接动画效果
    def connect_ui(self, movetask=True):
        self.panel_multi_ssh.Hide()
        self.splitter_left.Show()
        self.ssh_left_panel.Layout()
        # if movetask:
        #     moveTask(self.panel_session_tree, 500, 0, False, layout=self)
        #     moveTask(self.panel_session_tree, 500, 20, False, True, layout=self)

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

    def save_config_file(self, info):
        num, host, port, user, password, name, desc = info
        sshconfig = configparser.ConfigParser()
        shutil.copyfile('template.ini', 'data/sshclient/%s' % name)
        sshconfig.read('data/sshclient/%s' % name)
        sshconfig.set('default', 'host', host)
        sshconfig.set('default', 'port', port)
        sshconfig.set('default', 'user', user)
        sshconfig.set('default', 'password', password)
        sshconfig.set('default', 'desc', desc)
        sshconfig.set('default', 'num', num)
        sshconfig.write(open('data/sshclient/%s' % name, "w"))
        self.CB_save.SetValue(False)

    def init_session_tree(self, ip_list):
        if not self.tree_session.root:
            self.tree_session.root = self.tree_session.AddRoot('连接列表', ct_type=1)

        # 通过link_list初始化连接列表
        num2ip = lambda x: '.'.join([str(x // (256 ** i) % 256) for i in range(3, -1, -1)])

        # ip to num做排序
        num_list = []
        for ip in ip_list:
            num = reduce(lambda x, y: (x << 8) + y, list(map(int, ip.split('.'))))
            num_list.append(num)
        num_list.sort()

        # num to ip，初始化Tree
        for num in num_list:
            ip = num2ip(num)
            child = self.tree_session.AppendItem(self.tree_session.root, ip, ct_type=0)
            self.tree_session.SetItemWindow(child, globals.multi_ssh_conn[ip].gauge, 1)
            self.treeNode_dict[ip] = child

    def create_connect(self, evt):
        '批量连接'
        info = self.get_ssh_info()
        self.num.SetValue(info[0])
        self.host.SetValue(info[1])
        self.port.SetValue(info[2])
        self.username.SetValue(info[3])
        self.password.SetValue(info[4])
        self.start_connect(info)
        if self.CB_save.GetValue():
            self.save_config_file(info)

    def start_connect(self, info):
        "1、批量连接  2、session list dclick"
        num, host, port, user, password, name, desc = info

        self.total = int(num)
        self.done = 0

        # 初始化session tree
        conn_list = []
        ip_list = []
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
            conn.gauge = mGauge(self.panel_session_tree, (80, 18), 100, 'white', wx.Colour(230, 230, 230),
                                border_colour='white')
            conn_list.append(conn)
            ip_list.append(IPAddr)
            globals.multi_ssh_conn[IPAddr] = conn
        self.init_session_tree(ip_list)

        # 线程池执行connect_tread
        pool = threadpool.ThreadPool(globals.max_thread)
        requests = threadpool.makeRequests(self.connect_thread, conn_list)
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
                if not self.shellpage_dic:
                    self.DeleteAllPages(False)
                wx.CallAfter(self.add_shell_page, (globals.cur_conn))
                self.Layout()
            else:
                wx.CallAfter(self.close_all_ssh, None)

    def create_session(self, conn):
        self.num.SetValue('1')
        self.host.SetValue(conn.host)
        self.port.SetValue(str(conn.port))
        self.username.SetValue(conn.username)
        self.password.SetValue(conn.password)
        try:
            conn.connect()
        except:
            raise
        if not self.tree_session.root:
            self.connect_ui()
            self.tree_session.root = self.tree_session.AddRoot('连接列表', ct_type=1)
        globals.multi_ssh_conn[conn.host] = conn
        child = self.tree_session.AppendItem(self.tree_session.root, conn.host, ct_type=0)
        wx.CallAfter(self.tree_session.SetItemWindow, child, globals.multi_ssh_conn[conn.host].gauge, 1)
        self.tree_session.SetItemImage(child, self.greenball)
        conn.gauge.SetValue(100, '无')
        self.treeNode_dict[conn.host] = child
        self.change_online_count(1)
        globals.cur_conn = conn
        wx.CallAfter(self.add_shell_page, conn)
        return conn

    def on_linklist_act(self, evt):
        sshclient = evt.GetText()
        info = self.read_ssh_config(sshclient)
        self.num.SetValue(info[0])
        self.host.SetValue(info[1])
        self.port.SetValue(info[2])
        self.username.SetValue(info[3])
        self.password.SetValue(info[4])
        self.nb_console.DeletePage(self.nb_console.GetPageIndex(self.nb_console.GetCurrentPage()))
        self.start_connect(info)

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
        bitmaps = {
            '控制台': wx.Bitmap('bitmaps/ssh_console.png', wx.BITMAP_TYPE_PNG),
            '重连': wx.Bitmap('bitmaps/reconnect.png', wx.BITMAP_TYPE_PNG),
            '断开': wx.Bitmap('bitmaps/disconnect.png', wx.BITMAP_TYPE_PNG),
            '删除': wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU, size=(16, 16)),
        }
        self.link_selected = self.tree_session.GetItemText(evt.GetItem())
        self.treeMenu = wx.Menu()
        for text in '控制台 重连 断开 删除'.split():
            item = self.treeMenu.Append(wx.ID_ANY, text)
            item.SetBitmap(bitmaps[text])
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
            conn = globals.multi_ssh_conn[self.link_selected]
            if conn.linkok():
                conn.close()
                self.change_online_count(-1)
                if self.link_ok:
                    self.tree_session.SetItemImage(self.treeNode_dict[self.link_selected], self.redball)
                if conn.console:
                    self.delete_console_page(conn.host)
        elif item.GetItemLabel() == '控制台':
            conn = globals.multi_ssh_conn[self.link_selected]
            if conn.linkok():
                if self.link_selected in list(self.shellpage_dic.keys()):
                    page_label = self.get_copy_increate_label(conn.host)
                    self.add_shell_page(conn, page_label)
                else:
                    self.add_shell_page(conn)
            else:
                self.tree_session.SetItemImage(self.treeNode_dict[self.link_selected], self.redball)
                mMessageBox('连接状态异常！')
        elif item.GetItemLabel() == '删除':
            if globals.multi_ssh_conn[ip].linkok():
                mMessageBox('不能删除连接中的会话')
            else:
                self.tree_session.Delete(self.treeNode_dict[ip])
                if ip in list(self.shellpage_dic.keys()):
                    self.delete_console_page(ip)
                globals.multi_ssh_conn.pop(ip)

    def delete_console_page(self, ip):
        self.nb_console.DeletePage(self.nb_console.GetPageIndex(self.shellpage_dic[ip]))
        self.shellpage_dic.pop(ip)
        globals.multi_ssh_conn[ip].console = False

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


class shell_panel(wx.Panel):
    def __init__(self, parent, conn):
        wx.Panel.__init__(self, parent=parent)
        self.conn = conn
        self.SetBackgroundColour(globals.bgcolor)
        s0 = wx.BoxSizer()
        self.SetSizer(s0)
        self.browser = WebView.New(self, backend=self.GetTopLevelParent().web_backend)
        s0.Add(self.browser, 1, wx.EXPAND)

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

        self.ssh_panel = parent.Parent.Parent.Parent
        self.conn = None
        self.SetBackgroundColour('white')

        bSizer0 = wx.BoxSizer(wx.HORIZONTAL)
        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.ch_hostType = wx.Choice(self, choices=['oe server', 'oe 3v client'], style=wx.BORDER_SIMPLE)
        self.ch_hostType.SetSelection(0)
        self.tc_host = wx.TextCtrl(self, size=(150, -1), style=wx.TE_PROCESS_ENTER | wx.BORDER_SIMPLE)
        self.tc_host.SetHint('快速连接')
        self.tc_host.SetFocus()
        self.ai = wx.ActivityIndicator(self)
        self.ai.Hide()
        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter, self.tc_host)

        bSizer2.Add(self.tc_host, 0, wx.EXPAND)
        bSizer2.Add(self.ch_hostType, 0, wx.EXPAND)
        bSizer1.Add(bSizer2, 0, wx.ALIGN_CENTER)

        list_title = wx.StaticText(self, label='用户会话')
        list_title.SetFont(wx.Font(10, 70, 90, 92, False, "微软雅黑"))
        bSizer1.Add(list_title, 0, wx.ALIGN_CENTER | wx.TOP, 20)

        cols = ['名称', '起始IP', '端口', '数量', '用户名', '描述']
        self.listCtrl = sshclient_list(self, cols)
        self.listCtrl.SetColumnWidth(0, 100)
        self.listCtrl.SetColumnWidth(1, 120)
        self.listCtrl.SetColumnWidth(2, 50)
        self.listCtrl.SetColumnWidth(3, 50)
        self.listCtrl.SetSize(self.listCtrl.GetBestSize())

        bSizer1.Add(self.listCtrl, 0, wx.ALIGN_CENTER)

        bSizer0.Add(bSizer1, 1, wx.ALIGN_CENTER)
        self.SetSizer(bSizer0)

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

    def on_enter(self, evt):
        host = self.tc_host.GetValue()
        if host in globals.multi_ssh_conn.keys():
            return
        self.tc_host.Disable()
        self.ai.Start()
        self.ai.SetPosition(self.tc_host.GetPosition() - (30, 0))
        self.ai.Show()

        self.conn = ssh.sshClient()
        self.conn.host = host
        if self.ch_hostType.GetSelection() == 0:
            self.conn.username = globals.vdi_user
            self.conn.password = globals.vdi_user_pwd
        else:
            self.conn.username = 'root'
            self.conn.password = '3vclientroot'
        self.conn.gauge = mGauge(self.ssh_panel.panel_session_tree, (80, 18), 100, 'white', wx.Colour(230, 230, 230),
                                 border_colour='white')

        start_new_thread(self.create_session, ())

    def create_session(self):
        try:
            self.ssh_panel.create_session(self.conn)
            page_idx = self.Parent.GetPageIndex(self)
            self.Parent.DeletePage(page_idx)
        except Exception as e:
            self.ai.Stop()
            self.ai.Hide()
            self.tc_host.Enable()
            self.Layout()
            wx.CallAfter(mMessageBox, label=str(e), parent=None)


class CopyPage(wx.Panel):
    def __init__(self, parent, conn):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.conn = conn
        self.SetBackgroundColour(globals.bgcolor)

        self.browser = WebView.New(self, backend=self.GetTopLevelParent().web_backend)
        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(self.browser, 1, wx.EXPAND)

        self.SetSizer(bsizer)
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


class scp_panel(wx.Panel):
    def __init__(self, parent, conn):
        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_THEME)
        self.SetBackgroundColour(globals.bgcolor)
        self.ssh_panel = parent.Parent.Parent.Parent
        self.conn = conn
        self.item_sel = None
        self.show_hiden = False
        self.init_panel()
        self.tooltip_frame = mtooltip(self)

    def init_panel(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer_main)
        self.SetBackgroundColour('white')

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.cur_path = None
        self.tc_path = wx.TextCtrl(self, value='', style=wx.BORDER_SIMPLE
                                                         | wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.onPathEnter, self.tc_path)

        self.tc_path.SetForegroundColour(wx.Colour(150, 150, 150))
        self.tc_path.SetFont(wx.Font(wx.Font(9, 70, 90, 90, False, '微软雅黑')))
        bt_refresh = mBitmapButton(self, 'bitmaps/refresh.png', '刷新')
        bt_back = mBitmapButton(self, 'bitmaps/ssh_back.png', '上级目录')
        bt_down = mBitmapButton(self, 'bitmaps/download.png', '下载')
        bt_up = mBitmapButton(self, 'bitmaps/upload.png', '上传')
        bt_newdir = mBitmapButton(self, wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR, wx.ART_MENU, size=(18, 18)),
                                  '新建目录')
        bt_newfile = mBitmapButton(self, wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_MENU, size=(16, 16)), '新建文件')
        bt_show_all = platebtn.PlateButton(self, wx.ID_ANY, '',
                                           wx.Bitmap('bitmaps/file_showall.png', wx.BITMAP_TYPE_PNG),
                                           style=platebtn.PB_STYLE_DEFAULT | platebtn.PB_STYLE_TOGGLE)
        bt_show_all.SetToolTip('显示隐藏')
        bt_refresh.Bind(wx.EVT_BUTTON, self.onRefresh)
        bt_back.Bind(wx.EVT_BUTTON, self.onBackDir)
        bt_down.Bind(wx.EVT_BUTTON, self.onDownload)
        bt_up.Bind(wx.EVT_BUTTON, self.onUpload)
        bt_newfile.Bind(wx.EVT_BUTTON, self.onNewFile)
        bt_newdir.Bind(wx.EVT_BUTTON, self.onNewDir)
        bt_show_all.Bind(wx.EVT_TOGGLEBUTTON, self.onShowHiden)

        sizer1.Add(bt_refresh)
        sizer1.Add(bt_back)
        sizer1.Add(bt_down)
        sizer1.Add(bt_up)
        sizer1.Add(bt_newdir)
        sizer1.Add(bt_newfile)
        sizer1.Add((-1, -1), 1)
        sizer1.Add(bt_show_all, 0, wx.ALIGN_CENTER)
        sizer_main.Add(sizer1, 0, wx.EXPAND)
        sizer_main.Add(self.tc_path, 0, wx.EXPAND)

        self.file_tree = mHyperTreeList(self,
                                        cols=['名称', '大小', '类型', '修改时间', '权限', '用户/用户组'],
                                        show_header=False)
        self.file_tree.setColumnWidth([220, 60, 50, 100, 80, 135])
        self.file_tree.SetWindowStyle(wx.NO_BORDER)
        self.file_tree.SetAGWWindowStyleFlag(HTL.TR_FULL_ROW_HIGHLIGHT)
        sizer_main.Add(self.file_tree, 1, wx.EXPAND)

        bmp_folder = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_TOOLBAR, (16, 16))
        bmp_file = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, (16, 16))
        bmp_dir_up = wx.ArtProvider.GetBitmap(wx.ART_GO_DIR_UP, wx.ART_TOOLBAR, (16, 16))
        bmp_file_compress = wx.Bitmap('bitmaps/file_compress.png', wx.BITMAP_TYPE_PNG)
        bmp_file_config = wx.Bitmap('bitmaps/file_config.png', wx.BITMAP_TYPE_PNG)
        bmp_file_exec = wx.Bitmap('bitmaps/file_exec.png', wx.BITMAP_TYPE_PNG)
        bmp_file_py = wx.Bitmap('bitmaps/file_py.png', wx.BITMAP_TYPE_PNG)
        self.file_tree.setImageList(
            [bmp_folder, bmp_file, bmp_dir_up, bmp_file_config, bmp_file_compress, bmp_file_exec, bmp_file_py])
        self.file_tree.root = self.file_tree.AddRoot('..', image=2)
        self.item_sel = self.file_tree.root

        self.file_tree.GetMainWindow().Bind(wx.EVT_LEFT_DOWN, self.onClick)
        self.file_tree.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.onDClick)
        self.file_tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.onRightUp)
        self.file_tree.GetMainWindow().Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.file_tree.GetMainWindow().Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveFileTree)
        self.file_tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.onLabelEdit)

    def init_file_tree(self):
        if self.conn.username == 'root':
            self.conn.scp_path = '/root'
        else:
            self.conn.scp_path = '/home/%s' % self.conn.username
        self.refresh_dir()
        # self.file_tree.Expand(self.file_tree.root)

    def onPathEnter(self, evt):
        self.goto_dir(self.tc_path.GetValue())

    def goto_dir(self, path):
        self.conn.scp_path = path
        self.refresh_dir()

    def OnMouseMove(self, event):
        pt = event.GetPosition()
        item = self.file_tree.HitTest(pt)[0]
        if item:
            pos = wx.GetMousePosition()
            self.tooltip_frame.SetPosition((pos.x + 15, pos.y + 20))
            txt = item.GetData()
            if txt:
                self.tooltip_frame.SetLabel(txt)
                self.tooltip_frame.SetSize(self.tooltip_frame.GetBestSize())
                self.tooltip_frame.ShowWithoutActivating()
        else:
            self.tooltip_frame.Hide()

    def OnLeaveFileTree(self, evv):
        if self.tooltip_frame.IsShown():
            self.tooltip_frame.Hide()

    def onRefresh(self, evt):
        self.refresh_dir()

    def onBackDir(self, evt):
        path = self.get_remote_path()
        p_list = path.split('/')[1:-1]
        cur_path = ''
        if not p_list:
            cur_path = '/'
        else:
            for p in p_list:
                cur_path += '/%s' % p
        self.goto_dir(cur_path)

    def onNewFile(self, evt):
        dlg = wx.TextEntryDialog(None, '创建路径：%s\n文件名称' % self.conn.scp_path, '新建文件')
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            path = self.conn.scp_path + '/' + name
            frm = file_edit(self, path, self.conn, title=path)
            frm.Show()
        dlg.Destroy()

    def onNewDir(self, evt):
        dlg = wx.TextEntryDialog(None, '创建路径：%s\n文件夹名称' % self.conn.scp_path, '新建文件夹')
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            path = self.conn.scp_path + '/' + name
            try:
                self.conn.recv('mkdir %s' % path)
            except Exception as e:
                mMessageBox(e)
            self.refresh_dir()
        dlg.Destroy()

    def onShowHiden(self, evt):
        if evt.GetEventObject()._pressed:
            self.show_hiden = True
        else:
            self.show_hiden = False
        if self.conn:
            self.refresh_dir()

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
        start_new_thread(self.download, (local_path, remote_path))
        self.ssh_panel.ShowSSHMenu()

    def get_remote_path(self):
        if not self.conn:
            return
        else:
            return self.conn.scp_path

    def onUpload(self, evt):
        remote_path = self.get_remote_path()
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
                if os.path.getsize(cur_path) == 0:
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
                if remote == '/':
                    remote_path = remote + path.split('\\')[-1]
                else:
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
                self.last_callback_time = time.time()
                self.last_transferred = 0
                self.transfer_rate = '0K'
                self.sftp.put(path_map[index][0], path_map[index][1], callback=self.callback)
            except Exception as e:
                logging.error(f'{self.conn.host}: {e}')
                continue

        if self.ssh_panel.sftp_status:
            self.sftp.close()
            self.ssh_panel.sftp_status = False
        path_map.clear()
        self.refresh_dir()

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
            son_dir = '/' + re.sub(basic_path, '', remote_son_dir)
            localFileName = os.path.join(local + son_dir, remoteFileName.split('/')[-1])
            if not os.path.exists(local + son_dir):
                os.makedirs(local + son_dir)
            try:
                self.last_callback_time = time.time()
                self.last_transferred = 0
                self.transfer_rate = '0K'
                self.sftp.get(remoteFileName, localFileName, callback=self.callback)
                if self.getRemoteFileSize(self.sftp, remoteFileName) == 0:
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

    def refresh_dir(self):
        cur_host = self.conn.host
        if self.conn.scp_path:
            # 这个if去掉，第一次打开控制台有未知报错
            self.tc_path.SetValue(self.conn.scp_path)
        if self.show_hiden:
            cmd = "ls -AhlL %s" % self.conn.scp_path
        else:
            cmd = 'ls -hlL %s' % self.conn.scp_path

        files = self.conn.recv(cmd).split('\n')
        if cur_host != self.conn.host:
            # 防止快速切换后线程执行顺序错乱
            return
        files.sort(reverse=True)
        self.file_tree.DeleteChildren(self.file_tree.root)
        for file in files[1:]:
            if not file:
                continue
            info = file.strip().split(' ')
            info = [item for item in info if item != '']

            try:  # 没权限导致显示？的文件直接跳过
                filename = info[8]
            except:
                continue

            if len(info) >= 10:  # 处理文件名带空格的情况
                for item in info[9:]:
                    filename += ' %s' % item
            child = self.file_tree.AppendItem(self.file_tree.root, filename)
            self.file_tree.SetItemText(child, info[4], 1)
            type = info[0][0]
            if type == 'd':
                self.file_tree.SetItemText(child, '目录', 2)
                self.file_tree.SetItemImage(child, 0)
            else:
                self.file_tree.SetItemText(child, '文件', 2)
                if filename.endswith('.conf') or filename.endswith('cfg'):
                    self.file_tree.SetItemImage(child, 3)
                elif filename.endswith('.tar') or filename.endswith('zip'):
                    self.file_tree.SetItemImage(child, 4)
                elif filename.endswith('.bin') or filename.endswith('sh'):
                    self.file_tree.SetItemImage(child, 5)
                elif filename.endswith('.py'):
                    self.file_tree.SetItemImage(child, 6)
                else:
                    self.file_tree.SetItemImage(child, 1)

            self.file_tree.SetItemText(child, info[5] + info[6] + ' ' + info[7], 3)
            self.file_tree.SetItemText(child, info[0], 4)
            self.file_tree.SetItemText(child, info[2] + '/' + info[3], 5)
            child.SetData(
                info[-1] + '  ' + info[4] + ' ' + info[5] + " " + info[6] + ' ' + info[7] + ' ' + info[2] + ':' + info[
                    3] + ' ' + info[0])
        self.file_tree.Expand(self.file_tree.root)

    def getItemPath(self, item):
        if self.conn.scp_path == '/':
            cur_path = ''
        else:
            cur_path = self.conn.scp_path
        if not item == self.file_tree.root:
            path = item.GetText()
            return cur_path + '/%s' % path
        else:
            return cur_path

    def onClick(self, event):
        pt = event.GetPosition()
        item = self.file_tree.HitTest(pt)[0]
        if not item:
            return
        elif item == self.file_tree.root:
            self.item_sel = None
        else:
            self.item_sel = item

    def onDClick(self, event):
        pt = event.GetPosition()
        item = self.file_tree.HitTest(pt)[0]
        if not item:
            return
        if item.GetImage() == 2:
            self.onBackDir(None)
        elif item.GetImage() == 0:
            if self.conn.scp_path == '/':
                new_path = self.conn.scp_path + item.GetText()
            else:
                new_path = self.conn.scp_path + '/%s' % item.GetText()
            self.goto_dir(new_path)
        elif item.GetImage() == 1:
            path = self.getItemPath(item)
            txt_type = self.conn.recv('file %s' % path)
            txt_type = txt_type.split(':')[1]
            if 'ASCII text' in txt_type:
                if 'Non-ISO' in txt_type:
                    mMessageBox('不支持的编码')
                else:
                    txt = self.conn.recv('cat %s' % path)
                    frm = file_edit(self, path, self.conn, txt.replace('\r', ''), title=path)
                    frm.SetIcon(wx.Icon("bitmaps/file_edit.png"))
                    frm.Show()
            elif 'Unicode text' in txt_type:
                txt = self.conn.recv('cat %s' % path)
                frm = file_edit(self, path, self.conn, txt.replace('\r', ''), title=path)
                frm.Show()
            elif 'empty' in txt_type:
                txt = self.conn.recv('cat %s' % path)
                frm = file_edit(self, path, self.conn, txt.replace('\r', ''), title=path)
                frm.Show()
            else:
                mMessageBox('不支持的文件类型')

    def onRightUp(self, event):
        pt = event.GetPosition()
        item = self.file_tree.HitTest(pt)[0]
        menu = wx.Menu()
        bitmaps = {
            '新建目录': wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR, wx.ART_MENU, size=(20, 20)),
            '新建文件': wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_MENU, size=(20, 20)),
            '打开': wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, size=(20, 20)),
            '上传': wx.Bitmap('bitmaps/upload.png', wx.BITMAP_TYPE_PNG),
            '下载': wx.Bitmap('bitmaps/download.png', wx.BITMAP_TYPE_PNG),
            '重命名': wx.Bitmap('bitmaps/rename.png', wx.BITMAP_TYPE_PNG),
            '删除': wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU, size=(16, 16)),
            '权限': wx.Bitmap('bitmaps/chmod.png', wx.BITMAP_TYPE_PNG),
            '复制路径': wx.Bitmap('bitmaps/copy_path.png', wx.BITMAP_TYPE_PNG),
            '刷新': wx.Bitmap('bitmaps/refresh.png', wx.BITMAP_TYPE_PNG),
            '编辑': wx.Bitmap('bitmaps/file_edit.png', wx.BITMAP_TYPE_PNG),
        }
        if item:
            if item == self.file_tree.root:
                return
            self.item_sel = item
            if item.GetImage() == 0:
                menu_list = ['打开', '下载', 0, '重命名', '删除', 0, '权限', '复制路径']
            else:
                menu_list = ['编辑', '下载', 0, '重命名', '删除', 0, '权限', '复制路径']
        else:
            menu_list = ['刷新', 0, '新建目录', '新建文件', 0, '上传']
        for txt in menu_list:
            if txt == 0:
                menu.AppendSeparator()
                continue
            item = menu.Append(-1, txt)
            if txt in bitmaps:
                item.SetBitmap(bitmaps[txt])
            self.Bind(wx.EVT_MENU, self.onFilePopupMenu, item)

        self.PopupMenu(menu)
        menu.Destroy()

    def onLabelEdit(self, evt):
        old = self.getItemPath(self.item_sel)
        new = self.conn.scp_path + '/%s' % evt.GetLabel()
        try:
            self.conn.recv('mv %s %s' % (old, new))
        except Exception as e:
            mMessageBox(e)
            self.refresh_dir()

    def onFilePopupMenu(self, evt):
        txt = getLabelFromEVT(evt)
        if self.item_sel:
            path = self.getItemPath(self.item_sel)
        if txt == '刷新':
            self.refresh_dir()

        elif txt == '打开':
            self.goto_dir(self.getItemPath(self.item_sel))
            self.refresh_dir()

        elif txt == '复制路径':
            pyperclip.copy(path)
        elif txt == '新建目录':
            self.onNewDir(None)
        elif txt == '新建文件':
            self.onNewFile(None)
        elif txt == '重命名':
            self.file_tree.EditLabel(self.item_sel)
        elif txt == '删除':
            dlg = mWarnDlg('删除后无法恢复，是否继续？')
            if dlg.ShowModal() == wx.ID_OK:
                path = self.getItemPath(self.item_sel)
                path = path.replace(' ', r'\ ')
                self.conn.recv('rm -rf %s' % path)
                self.refresh_dir()
            dlg.Destroy()
        elif txt == '权限':
            path = self.getItemPath(self.item_sel)
            filename = path.split('/')[-1]
            re = self.conn.recv('ls -dlL %s' % path)
            mod = re.split(' ')[0][1:10]
            dlg = file_chmod(filename, mod)
            if dlg.ShowModal() == wx.ID_OK:
                mod = dlg.GetMod()
                self.conn.recv('chmod -R %s %s' % (mod, path))
                self.refresh_dir()
            dlg.Destroy()
        elif txt == '上传':
            self.onUpload(None)
        elif txt == '下载':
            self.ssh_panel.ShowSSHMenu()
            remote_path = path
            local_path = methods.get_config('ssh', 'download_path')
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            start_new_thread(self.download, (local_path, remote_path))
        elif txt == '编辑':
            path = self.getItemPath(self.item_sel)
            try:
                txt = self.conn.recv('cat %s' % path)
            except:
                return
            frm = file_edit(self, path, self.conn, txt.replace('\r', ''), title=path)
            frm.Show()


class command_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_THEME)
        self.ssh_panel = parent.Parent.Parent
        self.SetBackgroundColour(globals.bgcolor)

        self.cmd_on_sel = ''
        self.cmd_bt_dict = {}

        self.cp = PCP.PyCollapsiblePane(self, label='批量发送',
                                        agwStyle=wx.CP_NO_TLW_RESIZE | wx.CP_GTK_EXPANDER)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, self.cp)

        self.MakePaneContent(self.cp.GetPane())
        self.cp.Expand()

        s0 = wx.BoxSizer()
        self.SetSizer(s0)
        s0.Add(self.cp, 1, wx.EXPAND)

    def OnPaneChanged(self, event):
        self.Parent.Layout()

    def MakePaneContent(self, panel):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer_main)

        splitter = wx.SplitterWindow(panel, style=wx.NO_BORDER)
        splitter.SetSashGravity(1)
        sizer_main.Add(splitter, 1, wx.EXPAND)

        pnl_l = wx.Panel(splitter, style=wx.NO_BORDER)
        pnl_l.SetBackgroundColour('white')
        self.pnl_r = wx.Panel(splitter, style=wx.NO_BORDER)
        self.pnl_r.SetBackgroundColour('white')

        splitter.SetMinimumPaneSize(200)
        splitter.SplitVertically(pnl_l, self.pnl_r, -200)

        sizer_l = wx.BoxSizer(wx.VERTICAL)
        sizer_r = wx.BoxSizer(wx.VERTICAL)
        pnl_l.SetSizer(sizer_l)
        self.pnl_r.SetSizer(sizer_r)

        txt2 = wx.StaticText(pnl_l, label='命令编辑器')
        txt2.SetBackgroundColour('white')
        txt2.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer_l.Add(txt2, 0, wx.EXPAND, wx.LEFT, 5)

        self.stc = mSTC(pnl_l)
        self.stc.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)
        sizer_l.Add(self.stc, 1, wx.EXPAND)

        txt1 = wx.StaticText(pnl_l, label='发送到')
        txt1.SetFont(wx.Font(10, 70, 90, 90, False, "微软雅黑"))

        self.combo = wx.ComboBox(pnl_l, style=wx.CB_DROPDOWN, size=(-1, 23))
        self.combo.Append('全部会话')
        self.combo.Append('当前会话')
        self.combo.SetStringSelection('全部会话')
        self.bt_send = wx.Button(pnl_l, label='发送命令(ctrl+enter)')
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
        sizer_l_bot.Add(txt1, 0, wx.ALIGN_CENTER | wx.LEFT, 10)
        sizer_l_bot.Add(self.combo, 0, wx.EXPAND | wx.LEFT, 2)
        sizer_l_bot.Add(self.bt_send, 0, wx.EXPAND)
        sizer_l_bot.Add(self.bt_save, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        sizer_l_bot.Add((-1, 0), 1, wx.EXPAND)
        sizer_l_bot.Add(self.combo_keys, 0, wx.EXPAND)
        sizer_l_bot.Add(self.bt_sendkeys, 0, wx.EXPAND | wx.RIGHT, 10)

        sizer_l.Add(sizer_l_bot, 0, wx.EXPAND)

        txt3 = wx.StaticText(self.pnl_r, label='命令管理')
        txt3.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer_r.Add(txt3, 0, wx.EXPAND | wx.LEFT, 5)

        self.sizer_r_bt = wx.WrapSizer(wx.HORIZONTAL)
        sizer_r.Add(self.sizer_r_bt, 1, wx.EXPAND)

        self.pnl_r.Bind(wx.EVT_RIGHT_DOWN, self.SetPnlRightPopmenu)
        self.popupmenu_text = ['添加命令']

        self.init_cmds()
        self.Layout()

    def OnKeyPressed(self, event):
        if event.GetKeyCode() == 13 and event.ControlDown():
            self.send_cmd()
        event.Skip()

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

    def send_cmd(self, keys=None):
        if not globals.multi_ssh_conn:
            return
        elif not self.ssh_panel.shellpage_dic:
            mMessageBox('需要打开至少1个控制台')
            return

        key_value = {'ctrl+c': '\x03', 'ctrl+z': '\x1a'}
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

