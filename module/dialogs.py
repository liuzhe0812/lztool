# encoding=utf-8
import os, configparser, shutil, re, time, wx.adv, logging
from _thread import start_new_thread
from module import methods
from module.myui import *
import module.widgets.filebrowsebutton as filebrowse


class create_connect(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, title="会话信息")
        self.SetBackgroundColour('white')

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)

        bSizer7 = wx.BoxSizer(wx.VERTICAL)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.staticText1 = wx.StaticText(sbSizer1.GetStaticBox(), wx.ID_ANY, "会话名称", wx.DefaultPosition,
                                         wx.Size(75, -1), 0)
        self.staticText1.Wrap(-1)
        bSizer2.Add(self.staticText1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.name = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                0)
        bSizer2.Add(self.name, 0, wx.ALL, 5)

        bSizer7.Add(bSizer2, 1, wx.EXPAND, 5)

        bSizer_num = wx.BoxSizer(wx.HORIZONTAL)

        self.st_num = wx.StaticText(sbSizer1.GetStaticBox(), wx.ID_ANY, "数量", wx.DefaultPosition,
                                    wx.Size(75, -1), 0)
        bSizer_num.Add(self.st_num, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.num = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                               0)
        bSizer_num.Add(self.num, 0, wx.ALL, 5)

        bSizer7.Add(bSizer_num, 1, wx.EXPAND, 5)

        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText2 = wx.StaticText(sbSizer1.GetStaticBox(), wx.ID_ANY, "主机IP", wx.DefaultPosition,
                                           wx.Size(75, -1), 0)
        self.m_staticText2.Wrap(-1)
        bSizer3.Add(self.m_staticText2, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.host = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, '', wx.DefaultPosition, wx.DefaultSize,
                                0)
        bSizer3.Add(self.host, 0, wx.ALL, 5)

        bSizer7.Add(bSizer3, 1, wx.EXPAND, 5)

        bSizer9 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText6 = wx.StaticText(sbSizer1.GetStaticBox(), wx.ID_ANY, "端口", wx.DefaultPosition,
                                           wx.Size(75, -1), 0)
        self.m_staticText6.Wrap(-1)
        bSizer9.Add(self.m_staticText6, 0, wx.ALL, 5)

        self.port = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, '22', wx.DefaultPosition, wx.DefaultSize,
                                0)
        bSizer9.Add(self.port, 0, wx.ALL, 5)

        bSizer7.Add(bSizer9, 1, wx.EXPAND, 5)

        bSizer4 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText3 = wx.StaticText(sbSizer1.GetStaticBox(), wx.ID_ANY, "登录用户", wx.DefaultPosition,
                                           wx.Size(75, -1), 0)
        self.m_staticText3.Wrap(-1)
        bSizer4.Add(self.m_staticText3, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.user = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, 'root', wx.DefaultPosition, wx.DefaultSize,
                                0)
        bSizer4.Add(self.user, 0, wx.ALL, 5)

        bSizer7.Add(bSizer4, 1, wx.EXPAND, 5)

        bSizer5 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText4 = wx.StaticText(sbSizer1.GetStaticBox(), wx.ID_ANY, "登录密码", wx.DefaultPosition,
                                           wx.Size(75, -1), 0)
        self.m_staticText4.Wrap(-1)
        bSizer5.Add(self.m_staticText4, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.password = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, 'oseasy', wx.DefaultPosition,
                                    wx.DefaultSize, wx.TE_PASSWORD)
        bSizer5.Add(self.password, 0, wx.ALL, 5)

        bSizer7.Add(bSizer5, 1, wx.EXPAND, 5)

        sbSizer1.Add(bSizer7, 0)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText5 = wx.StaticText(sbSizer1.GetStaticBox(), wx.ID_ANY, "描述", wx.DefaultPosition,
                                           wx.Size(75, -1), 0)
        self.m_staticText5.Wrap(-1)
        bSizer6.Add(self.m_staticText5, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.desc = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                wx.TE_MULTILINE)
        bSizer6.Add(self.desc, 0, wx.ALL, 5)

        sbSizer1.Add(bSizer6, 0, wx.EXPAND, 5)

        bSizer1.Add(sbSizer1, 1, wx.EXPAND, 5)

        bSizer8 = wx.BoxSizer(wx.HORIZONTAL)

        self.bt_ok = mButton(self, id=wx.ID_OK, label="确定", color="deepgreen")

        self.bt_ok.SetDefault()
        self.bt_cancel = mButton(self, id=wx.ID_CANCEL, label="取消", color="red")
        bSizer8.Add((0, 0), 1)
        bSizer8.Add(self.bt_ok, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        bSizer8.Add(self.bt_cancel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        bSizer8.Add((0, 0), 1)

        bSizer1.Add(bSizer8, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        bSizer1.Fit(self)

        self.Centre(wx.BOTH)

        self.i = 1
        self.init_name('新建会话')

    def init_name(self, init_name):
        if self.i > 1:
            self.tmp_name = init_name + '(%s)' % str(self.i)
        else:
            self.tmp_name = init_name
        for parent, dirnames, filenames in os.walk('data/sshclient'):
            for filename in filenames:
                if self.tmp_name == filename:
                    self.i += 1
                    self.init_name('新建会话')
                    break
            self.name.SetValue(self.tmp_name)

    def OnRadio(self, evt):
        if evt.GetSelection() == 0:
            self.desc.Show()
            self.m_staticText5.Show()
            self.staticText1.SetLabel('会话名称')
            self.m_staticText2.SetLabel('主机IP')
            self.init_name('新建会话')
            self.name.SetValue(self.tmp_name)
            self.Layout()
        else:
            self.desc.Hide()
            self.m_staticText5.Hide()
            self.staticText1.SetLabel('会话数量')
            self.m_staticText2.SetLabel('起始IP')
            self.name.SetValue('1')
            self.Layout()

    def get_value(self):
        return self.name.GetValue(), self.num.GetValue(), self.host.GetValue(), self.port.GetValue(), self.user.GetValue(), self.password.GetValue(), self.desc.GetValue()


class sshclient_list(mListCtrl):
    def __init__(self, parent, cols):
        mListCtrl.__init__(self, parent, cols, method=self.on_linklist_popupmenu,
                           popupmemu=['新建', '另存', '编辑', '删除'])
        self.popupmemu = []
        self.list = []
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLinkSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnLinkDeSelect)

    def on_linklist_popupmenu(self, evt):
        menu = evt.GetEventObject()
        text = menu.GetLabel(evt.GetId())
        if text == '新建':
            self.new_sshclient(None)
        elif text == '另存':
            self.save_sshclient(None)
        elif text == '编辑':
            self.edit_sshclient(None)
        else:
            self.delete_sshclient(None)

    def new_sshclient(self, evt):
        dlg = create_connect()
        if dlg.ShowModal() == wx.ID_OK:
            name, num, host, port, user, password, desc = dlg.get_value()
            shutil.copyfile('template.ini', 'data/sshclient/%s' % name)
            cf = configparser.ConfigParser()
            cf.read('data/sshclient/%s' % name)
            cf.set('default', 'host', host)
            cf.set('default', 'port', port)
            cf.set('default', 'user', user)
            cf.set('default', 'password', password)
            cf.set('default', 'num', num)
            cf.set('default', 'desc', desc)
            cf.write(open('data/sshclient/%s' % name, "w"))
        dlg.Destroy()
        self.RefreshListCtrl()

    def delete_sshclient(self, evt):
        for filename in self.list:
            os.remove('data/sshclient/%s' % filename)
        self.RefreshListCtrl()

    def save_sshclient(self, evt):
        for filename in self.list:
            newname = '%s-副本' % filename
            shutil.copy('data/sshclient/%s' % filename, 'data/sshclient/%s' % newname)
        self.RefreshListCtrl()

    def edit_sshclient(self, evt):
        for filename in self.list:
            dlg = create_connect()
            cf = configparser.ConfigParser()
            cf.read('data/sshclient/%s' % filename)
            dlg.name.SetValue(filename)
            dlg.host.SetValue(cf.get('default', 'host'))
            dlg.port.SetValue(cf.get('default', 'port'))
            dlg.user.SetValue(cf.get('default', 'user'))
            dlg.num.SetValue(cf.get('default', 'num'))
            dlg.password.SetValue(cf.get('default', 'password'))
            dlg.desc.SetValue(cf.get('default', 'desc'))
            if dlg.ShowModal() == wx.ID_OK:
                newname, num, host, port, user, password, desc = dlg.get_value()
                cf.set('default', 'host', host)
                cf.set('default', 'port', port)
                cf.set('default', 'user', user)
                cf.set('default', 'password', password)
                cf.set('default', 'num', num)
                cf.set('default', 'desc', desc)
                cf.write(open('data/sshclient/%s' % filename, "w"))
            dlg.Destroy()
            self.RefreshListCtrl()

    def create_listctrl(self):
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
                row = self.InsertItem(n, filename)
                for col in range(6):
                    self.SetItem(row, col, info[col])

    def OnLinkSelect(self, evt):
        self.list.append(evt.GetText())

    def OnLinkDeSelect(self, evt):
        self.list.remove(evt.GetText())

    def RefreshListCtrl(self):
        self.DeleteAllItems()
        self.create_listctrl()
        self.list = []


class sql_connect(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, title="连接数据库")
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.host = mInput(self, st_label='主机', tc_label='192.168.239.200', st_size=(80, -1))

        bSizer1.Add(self.host, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 10)

        self.port = mInput(self, st_label='端口', tc_label='3306', st_size=(80, -1))
        bSizer1.Add(self.port, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 10)

        self.username = mInput(self, st_label='用户名', tc_label='oseasy', st_size=(80, -1))
        bSizer1.Add(self.username, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 10)

        self.password = mInput(self, st_label='密码', tc_label='cloudhan', st_size=(80, -1), password=True)
        bSizer1.Add(self.password, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 10)

        bSizer5 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer5.Add((0, 0), 1, wx.EXPAND, 5)

        self.m_button1 = mButton(self, id=wx.ID_OK, label="确定", color='deepgreen')
        bSizer5.Add(self.m_button1, 0, wx.ALL, 5)

        self.m_button2 = mButton(self, id=wx.ID_CANCEL, label="取消", color='red')
        bSizer5.Add(self.m_button2, 0, wx.ALL, 5)
        bSizer5.Add((0, 0), 1, wx.EXPAND, 5)
        bSizer1.Add(bSizer5, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 10)

        self.SetSizer(bSizer1)
        self.SetSize(self.GetBestSize())
        self.Layout()

        self.Centre(wx.BOTH)

        self.m_button1.SetDefault()

    def set_default_host(self, host):
        self.host.SetValue(host)

    def set_default_passwd(self, passwd):
        self.password.SetValue(passwd)


class file_check_dlg(wx.Dialog):
    def __init__(self, check_file=True):
        wx.Dialog.__init__(self, None, -1, size=(500, 400), title="选择文件")

        self.check_file = check_file

        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.list = mListCtrl(self, ['名称', '大小', '类型', '修改时间', '属性', '所有者'])
        self.list.SetColumnWidth(0, 100)
        self.list.SetColumnWidth(1, 50)
        self.list.SetColumnWidth(2, 50)
        self.list.SetColumnWidth(3, 90)
        self.list.SetColumnWidth(4, 90)
        bSizer1.Add(self.list, 1, wx.ALL | wx.EXPAND, 5)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.path = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.path, 1, wx.ALIGN_CENTER | wx.ALL, 5)

        self.goto = mButton(self, "", color='white', size=(34, 29))
        self.goto.setBmp('bitmaps/goto.png')
        self.goto.SetDefault()
        self.back = mButton(self, "", color='white', size=(29, 29))
        self.back.setBmp('bitmaps/back.png')
        bSizer2.Add(self.goto, 0, wx.ALL, 5)
        bSizer2.Add(self.back, 0, wx.RIGHT | wx.TOP | wx.BOTTOM, 5)

        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        bSizer3.Add((0, 0), 1, wx.EXPAND, 5)
        self.bt_ok = mButton(self, id=wx.ID_OK, label="确定", color='deepgreen')
        bSizer3.Add(self.bt_ok, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.bt_cancel = mButton(self, id=wx.ID_CANCEL, label="取消", color='red')
        bSizer3.Add(self.bt_cancel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        bSizer3.Add((0, 0), 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer2, 0, wx.EXPAND, 5)
        bSizer1.Add(bSizer3, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        # self.Centre(wx.BOTH)

    def create_file_list(self, files):
        if not files:
            return
        if not files[0]:
            return
        i = 0
        for file in files:
            info = file.strip().split(' ')
            info = [item for item in info if item != '']
            row = self.list.InsertItem(i, info[-1])
            i += 1
            self.list.SetItem(row, 1, info[4])
            if info[1] == '1':
                self.list.SetItem(row, 2, '文件')
            else:
                self.list.SetItem(row, 2, '目录')
            self.list.SetItem(row, 3,
                              info[5].decode('utf8') + info[6] + ' ' + info[7])
            self.list.SetItem(row, 4, info[0])
            self.list.SetItem(row, 5, info[2])

    def on_close(self, evt):
        self.Destroy()


class file_chmod(wx.Dialog):
    def __init__(self, filename, mod):
        wx.Dialog.__init__(self, None, -1, title="修改权限")
        self.SetBackgroundColour('white')
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer_main)
        self.mod = mod

        txt = wx.StaticText(self, label=filename)
        txt.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))

        sizer_main.Add(txt, 0, wx.LEFT, 10)

        sb_user = wx.StaticBox(self, -1, '所有者')
        sb_group = wx.StaticBox(self, -1, '组')
        sb_other = wx.StaticBox(self, -1, '其他')
        sizer1 = wx.StaticBoxSizer(sb_user, wx.HORIZONTAL)
        sizer2 = wx.StaticBoxSizer(sb_group, wx.HORIZONTAL)
        sizer3 = wx.StaticBoxSizer(sb_other, wx.HORIZONTAL)

        sizer_main.Add(sizer1, 0, wx.LEFT | wx.RIGHT, 10)
        sizer_main.Add(sizer2, 0, wx.LEFT | wx.RIGHT, 10)
        sizer_main.Add(sizer3, 0, wx.LEFT | wx.RIGHT, 10)

        self.cb1 = wx.CheckBox(self, -1, "读取")
        self.cb2 = wx.CheckBox(self, -1, "写入")
        self.cb3 = wx.CheckBox(self, -1, "执行")
        sizer1.Add(self.cb1, 0, wx.LEFT, 5)
        sizer1.Add(self.cb2, 0, wx.LEFT, 5)
        sizer1.Add(self.cb3, 0, wx.LEFT, 5)

        self.cb4 = wx.CheckBox(self, -1, "读取")
        self.cb5 = wx.CheckBox(self, -1, "写入")
        self.cb6 = wx.CheckBox(self, -1, "执行")
        sizer2.Add(self.cb4, 0, wx.LEFT, 5)
        sizer2.Add(self.cb5, 0, wx.LEFT, 5)
        sizer2.Add(self.cb6, 0, wx.LEFT, 5)

        self.cb7 = wx.CheckBox(self, -1, "读取")
        self.cb8 = wx.CheckBox(self, -1, "写入")
        self.cb9 = wx.CheckBox(self, -1, "执行")
        sizer3.Add(self.cb7, 0, wx.LEFT, 5)
        sizer3.Add(self.cb8, 0, wx.LEFT, 5)
        sizer3.Add(self.cb9, 0, wx.LEFT, 5)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        bSizer2.Add((0, 0), 1, wx.EXPAND, 5)

        self.m_button1 = mButton(self, id=wx.ID_OK, label='确定', color='deepgreen')
        bSizer2.Add(self.m_button1, 0, wx.ALL, 5)

        self.m_button2 = mButton(self, id=wx.ID_CANCEL, label='取消', color='red')
        bSizer2.Add(self.m_button2, 0, wx.ALL, 5)
        sizer_main.Add(bSizer2, 0, wx.ALIGN_CENTER)

        self.SetSize(self.GetBestSize())
        self.Center()
        self.map = {self.cb1: 4, self.cb2: 2, self.cb3: 1,
                    self.cb4: 4, self.cb5: 2, self.cb6: 1,
                    self.cb7: 4, self.cb8: 2, self.cb9: 1}
        self.SetMod()

    def SetMod(self):
        i = 0
        for cb in self.map.keys():
            if self.mod[i] == '-':
                cb.SetValue(False)
            else:
                cb.SetValue(True)
            i += 1

    def GetMod(self):
        i = 0
        u_mod = 0
        g_mod = 0
        o_mod = 0
        for cb in [self.cb1, self.cb2, self.cb3]:
            if cb.GetValue():
                u_mod += self.map[cb]

        for cb in [self.cb4, self.cb5, self.cb6]:
            if cb.GetValue():
                g_mod += self.map[cb]

        for cb in [self.cb7, self.cb8, self.cb9]:
            if cb.GetValue():
                o_mod += self.map[cb]
        return str(u_mod) + str(g_mod) + str(o_mod)


class file_edit(wx.Frame):
    def __init__(self, parent=None, path=None, conn=None, txt=None, local_file=None, title=''):
        wx.Frame.__init__(self, parent=parent, size=(800, 600), title=title)
        self.SetIcon(wx.Icon('bitmaps/file_edit.png'))
        self.conn = conn
        self.path = path
        self.parent = parent
        self.local_file = local_file
        self.pos = 0
        self.size = 0
        self.recycle = 1
        if path:
            self.SetTitle(path)

        self.CreateStatusBar()
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1.Append(101, "&保存\tCtrl+S")
        menu1.Append(102, "&退出\tCtrl+Q")

        menu2 = wx.Menu()
        menu2.Append(103, "&查找\tCtrl+F")
        menu2.Append(104, "&替换\tCtrl+R")
        menuBar.Append(menu1, "&文件")
        menuBar.Append(menu2, "&编辑")
        self.SetMenuBar(menuBar)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        self.stc = mSTC(self, 1)
        self.stc.SetMarginType(1, 2)
        self.stc.SetMarginWidth(0, 35)

        if txt:
            self.SetText(txt)

        bSizer1.Add(self.stc, 1, wx.EXPAND)

        self.SetSizer(bSizer1)
        self.Layout()

        self.CenterOnScreen()

        self.Bind(wx.EVT_MENU, self.onMenuSave, id=101)
        self.Bind(wx.EVT_MENU, self.onMenuQuit, id=102)
        self.Bind(wx.EVT_MENU, self.onMenuFind, id=103)
        self.Bind(wx.EVT_MENU, self.onMenuReplace, id=104)
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFindNext)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnReplace)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAll)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)

    def SetText(self, txt):
        self.stc.SetText(txt)

    def onMenuSave(self, evt):
        txt = self.stc.GetText()
        if self.Parent:
            tmp_path = "data/tmp/%s" % self.path.split('/')[-1]
            fo = open(tmp_path, "w")
            fo.write(txt.replace('\r', ''))
            fo.close()
            try:
                self.SetStatusText("正在保存...")
                self.conn.upload(tmp_path, self.path)
                self.SetStatusText("")
            except Exception as e:
                mMessageBox('upload %s faild' % self.path)
                logging.error(e)
            os.remove(tmp_path)
            self.parent.refresh_dir()
        else:
            with open(self.local_file, "w") as f:
                f.write(txt.replace('\r', ''))

    def onMenuQuit(self, evt):
        self.Destroy()

    def onMenuFind(self, evt):
        self.stc_txt = self.stc.GetValue()
        self.find_data = wx.FindReplaceData()
        self.find_dlg = wx.FindReplaceDialog(self.stc, self.find_data, '查找')
        self.find_dlg.Show()

    def onMenuReplace(self, evt):
        self.stc_txt = self.stc.GetValue()
        self.find_data = wx.FindReplaceData()
        self.find_dlg = wx.FindReplaceDialog(self.stc, self.find_data, '替换', wx.FR_REPLACEDIALOG)
        self.find_dlg.Show()

    def OnFind(self, event):
        tosearch = event.GetFindString()
        anchor = self.stc.GetAnchor()
        length = self.stc.GetTextLength()
        flags = event.GetFlags()
        forward = int(bin(flags)[2:].zfill(3)[2])
        if forward:
            n = self.stc.FindText(anchor, length, tosearch, flags)
            if n[0] == -1:
                n = self.stc.FindText(0, anchor, tosearch, flags)
        else:
            n = self.stc.FindText(anchor, 0, tosearch, flags)
            if n[0] == -1:
                n = self.stc.FindText(length, anchor, tosearch, flags)
        if n[0] != -1:
            self.CenterPosInView(n)
        else:
            mMessageBox('找不到"%s"' % tosearch, self)
        return n

    def OnFindNext(self, event):
        tosearch = event.GetFindString()
        anchor = self.stc.GetAnchor()
        length = self.stc.GetTextLength()
        flags = event.GetFlags()
        forward = int(bin(flags)[2:].zfill(3)[2])
        if forward:
            n = self.stc.FindText(anchor + 1, length, tosearch, flags)
        else:
            n = self.stc.FindText(anchor, 0, tosearch, flags)
        if n[0] != -1:
            self.CenterPosInView(n)
        else:
            if self.recycle:
                if forward:
                    self.stc.SetAnchor(0)
                    n = self.stc.FindText(0, length, tosearch, flags)
                else:
                    self.stc.SetAnchor(length)
                    n = self.stc.FindText(length, 0, tosearch, flags)
                self.CenterPosInView(n)

    def OnReplace(self, event):
        replaceStr = event.GetReplaceString()
        n = self.OnFind(event)
        if n != -1:
            startSel, endSel = self.stc.GetSelection()
            self.stc.Replace(startSel, endSel, replaceStr)
            self.stc.SetSelection(startSel, endSel)

    def OnReplaceAll(self, event):
        tosearch = event.GetFindString()
        replaceStr = event.GetReplaceString()
        length = self.stc.GetTextLength()
        flags = event.GetFlags()
        n = self.stc.FindText(0, length, tosearch, flags)
        if n[0] == -1:
            mMessageBox('找不到"%s"' % tosearch, self)
            return
        while n[0] != -1:
            self.stc.Replace(n[0], n[1], replaceStr)
            n = self.stc.FindText(0, length, tosearch, flags)

    def OnFindClose(self, evt):
        self.stc.SelectNone()
        self.pos = 0
        self.size = 0

    def CenterLineInView(self, line):
        nlines = self.stc.LinesOnScreen()
        first = self.stc.GetFirstVisibleLine()
        target = int(first + nlines / 2)
        self.stc.LineScroll(0, line - target)

    def CenterPosInView(self, pos):
        line = self.stc.LineFromPosition(pos[0])
        self.CenterLineInView(line)
        self.stc.GotoLine(line)
        self.stc.GotoPos(pos[0])
        self.stc.SetSelection(pos[0], pos[1])


class xml_viewer(wx.Dialog):
    def __init__(self, title=None):
        wx.Dialog.__init__(self, None, -1, size=(800, 600), title=u"文本编辑", style=wx.DEFAULT_FRAME_STYLE)

        if title:
            self.SetTitle(title)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        self.data = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE)

        self.data.SetBackgroundColour(globals.ssh_b_colour)
        self.data.SetForegroundColour(globals.ssh_f_colour)
        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        bSizer2.Add((0, 0), 1, wx.EXPAND, 5)

        self.m_button1 = mButton(self, id=wx.ID_OK, label=u'保存', color='deepgreen')
        bSizer2.Add(self.m_button1, 0, wx.ALL, 5)

        self.m_button2 = mButton(self, id=wx.ID_CANCEL, label=u'取消', color='red')
        bSizer2.Add(self.m_button2, 0, wx.ALL, 5)

        bSizer1.Add(self.data, 1, wx.EXPAND)
        bSizer1.Add(bSizer2, 0, wx.EXPAND)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)


class get_info_dlg(wx.Dialog):
    def __init__(self, conn):
        wx.Dialog.__init__(self, None, id=wx.ID_ANY, title='系统检测 - %s' % conn.host, pos=wx.DefaultPosition,
                           size=wx.Size(570, 520))
        self.conn = conn
        conn.connect()

        self.init_dlg()
        self.bt_start.Bind(wx.EVT_BUTTON, self.start)
        self.bt_stop.Bind(wx.EVT_BUTTON, self.stop)
        self.Bind(wx.EVT_CLOSE, self.__on_close)
        self.BackgroundColour = '#ffffff'
        start_new_thread(self.check, ())

    def init_dlg(self):
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "系统信息"), wx.VERTICAL)

        line0 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc0 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "系统内核", wx.DefaultPosition, wx.Size(105, -1),
                               wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line0.Add(self.tc0, 0, wx.LEFT | wx.TOP, 5)

        self.kernel = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                  wx.DefaultSize, wx.TE_READONLY | wx.STATIC_BORDER)
        line0.Add(self.kernel, 1, wx.RIGHT | wx.TOP, 5)

        sbSizer1.Add(line0, 0, wx.EXPAND, 5)

        line1 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc1 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "CPU型号", wx.DefaultPosition, wx.Size(105, -1),
                               wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line1.Add(self.tc1, 0, wx.LEFT | wx.TOP, 5)

        self.cpu_model = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                     wx.DefaultSize, wx.TE_READONLY | wx.STATIC_BORDER)
        line1.Add(self.cpu_model, 1, wx.RIGHT | wx.TOP, 5)

        sbSizer1.Add(line1, 0, wx.EXPAND, 5)

        line2 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc21 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "CPU数量", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line2.Add(self.tc21, 0, wx.LEFT | wx.TOP, 5)

        self.cpu_num = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                   wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line2.Add(self.cpu_num, 0, wx.TOP, 5)

        self.tc22 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "CPU核心", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line2.Add(self.tc22, 0, wx.TOP, 5)

        self.cpu_core = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                    wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line2.Add(self.cpu_core, 0, wx.TOP, 5)

        self.tc23 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "CPU线程", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line2.Add(self.tc23, 0, wx.TOP, 5)

        self.cpu_pro = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                   wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line2.Add(self.cpu_pro, 0, wx.RIGHT | wx.TOP, 5)

        sbSizer1.Add(line2, 0, wx.EXPAND, 5)

        line3 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc31 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "内存总量", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line3.Add(self.tc31, 0, wx.LEFT | wx.TOP, 5)

        self.mem_total = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                     wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line3.Add(self.mem_total, 0, wx.TOP, 5)

        self.tc32 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "可用内存", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line3.Add(self.tc32, 0, wx.TOP, 5)

        self.mem_dev = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                   wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line3.Add(self.mem_dev, 0, wx.TOP, 5)

        self.tc33 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "内存条数", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line3.Add(self.tc33, 0, wx.TOP, 5)

        self.mem_dev1 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                    wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line3.Add(self.mem_dev1, 0, wx.RIGHT | wx.TOP, 5)

        sbSizer1.Add(line3, 0, wx.EXPAND, 5)

        line4 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc4 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "SCSI设备", wx.DefaultPosition, (105, 0o1),
                               wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line4.Add(self.tc4, 0, wx.LEFT | wx.TOP | wx.EXPAND, 5)

        self.scsi = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(80, -1),
                                wx.TE_MULTILINE | wx.TE_READONLY | wx.STATIC_BORDER)
        line4.Add(self.scsi, 1, wx.TOP | wx.RIGHT | wx.EXPAND, 5)

        sbSizer1.Add(line4, 1, wx.EXPAND, 5)

        line5 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc5 = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, "HBA卡信息", wx.DefaultPosition, (105, -1),
                               wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line5.Add(self.tc5, 0, wx.LEFT | wx.TOP | wx.EXPAND, 5)

        self.wwn = wx.TextCtrl(sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(80, -1),
                               wx.TE_MULTILINE | wx.TE_READONLY | wx.STATIC_BORDER)
        line5.Add(self.wwn, 1, wx.TOP | wx.RIGHT | wx.EXPAND, 5)

        sbSizer1.Add(line5, 1, wx.EXPAND, 5)

        bSizer1.Add(sbSizer1, 1, wx.EXPAND, 5)

        sbSizer2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "监控信息"), wx.VERTICAL)

        line7 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc71 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "CPU使用率", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line7.Add(self.tc71, 0, wx.TOP | wx.LEFT, 5)

        self.cpu_stat = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                    wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line7.Add(self.cpu_stat, 0, wx.TOP, 5)

        self.tc72 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "内存使用率", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line7.Add(self.tc72, 0, wx.TOP, 5)

        self.mem_stat = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                    wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line7.Add(self.mem_stat, 0, wx.TOP, 5)

        self.tc73 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "磁盘使用率", wx.DefaultPosition, wx.Size(105, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line7.Add(self.tc73, 0, wx.TOP, 5)

        self.disk_stat = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                     wx.Size(80, -1), wx.TE_READONLY | wx.STATIC_BORDER)
        line7.Add(self.disk_stat, 0, wx.TOP | wx.RIGHT, 5)

        sbSizer2.Add(line7, 1, 0, 5)

        line8 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc81 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "网卡设备", wx.DefaultPosition, wx.DefaultSize,
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line8.Add(self.tc81, 0, wx.TOP | wx.LEFT, 5)

        self.tc82 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "上行速率(KB)", wx.DefaultPosition, wx.Size(-1, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line8.Add(self.tc82, 0, wx.TOP, 5)

        self.tc83 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "下行速率(KB)", wx.DefaultPosition, wx.DefaultSize,
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line8.Add(self.tc83, 0, wx.TOP, 5)

        self.tc84 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "上行总量(KB)", wx.DefaultPosition, wx.Size(-1, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line8.Add(self.tc84, 0, wx.TOP, 5)

        self.tc85 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "下行总量(KB)", wx.DefaultPosition, wx.Size(-1, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line8.Add(self.tc85, 0, wx.TOP | wx.RIGHT, 5)

        sbSizer2.Add(line8, 1, wx.EXPAND, 5)

        line9 = wx.BoxSizer(wx.HORIZONTAL)

        self.interface = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                     wx.DefaultSize, wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line9.Add(self.interface, 0, wx.LEFT, 5)

        self.up_speed = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                    wx.Size(-1, -1), wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line9.Add(self.up_speed, 0, 0, 5)

        self.down_speed = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                      wx.DefaultSize, wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line9.Add(self.down_speed, 0, 0, 5)

        self.up_total = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                    wx.Size(-1, -1), wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line9.Add(self.up_total, 0, 0, 5)

        self.down_dotal = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                      wx.Size(-1, -1), wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line9.Add(self.down_dotal, 0, wx.RIGHT, 5)

        sbSizer2.Add(line9, 1, wx.EXPAND, 5)

        line10 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc111 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "磁盘设备", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line10.Add(self.tc111, 0, wx.TOP | wx.LEFT, 5)

        self.tc112 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "读速率(KB)", wx.DefaultPosition, wx.Size(-1, -1),
                                 wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line10.Add(self.tc112, 0, wx.TOP, 5)

        self.tc113 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "写速率(KB)", wx.DefaultPosition, wx.DefaultSize,
                                 wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line10.Add(self.tc113, 0, wx.TOP, 5)

        self.tc114 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "iowait", wx.DefaultPosition, wx.Size(-1, -1),
                                 wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line10.Add(self.tc114, 0, wx.TOP, 5)

        self.tc116 = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, "iops", wx.DefaultPosition, wx.Size(-1, -1),
                                 wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line10.Add(self.tc116, 0, wx.TOP | wx.RIGHT, 5)

        sbSizer2.Add(line10, 1, wx.EXPAND, 5)

        line11 = wx.BoxSizer(wx.HORIZONTAL)

        self.disk = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line11.Add(self.disk, 0, wx.LEFT, 5)

        self.read_speed = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                      wx.Size(-1, -1), wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line11.Add(self.read_speed, 0, 0, 5)

        self.write_speed = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                       wx.DefaultSize, wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line11.Add(self.write_speed, 0, 0, 5)

        self.iowait = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                  wx.Size(-1, -1), wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line11.Add(self.iowait, 0, 0, 5)

        self.iops = wx.TextCtrl(sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(-1, -1),
                                wx.TE_CENTRE | wx.TE_READONLY | wx.STATIC_BORDER)
        line11.Add(self.iops, 0, wx.RIGHT, 5)

        sbSizer2.Add(line11, 1, wx.EXPAND, 5)

        bSizer1.Add(sbSizer2, 0, wx.EXPAND, 5)

        self.m_staticline1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer1.Add(self.m_staticline1, 0, wx.EXPAND | wx.TOP, 5)

        line6 = wx.BoxSizer(wx.HORIZONTAL)

        self.tc6 = wx.StaticText(self, wx.ID_ANY, "监控网卡", wx.DefaultPosition, wx.DefaultSize, 0)
        self.tc6.Wrap(-1)
        line6.Add(self.tc6, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.select_int = wx.TextCtrl(self, wx.ID_ANY, "eth0", wx.DefaultPosition, wx.DefaultSize, 0)
        line6.Add(self.select_int, 1, wx.ALIGN_CENTER | wx.ALL, 5)

        self.tc61 = wx.StaticText(self, wx.ID_ANY, "监控磁盘", wx.DefaultPosition, wx.DefaultSize, 0)
        self.tc61.Wrap(-1)
        line6.Add(self.tc61, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.select_disk = wx.TextCtrl(self, wx.ID_ANY, "sda", wx.DefaultPosition, wx.DefaultSize, 0)
        line6.Add(self.select_disk, 1, wx.ALIGN_CENTER | wx.ALL, 5)

        self.bt_start = wx.Button(self, wx.ID_ANY, "开始", wx.DefaultPosition, wx.Size(80, 31), 0)
        line6.Add(self.bt_start, 0, wx.BOTTOM | wx.TOP, 5)

        self.bt_stop = wx.Button(self, wx.ID_ANY, "停止", wx.DefaultPosition, wx.Size(80, 31), 0)
        line6.Add(self.bt_stop, 0, wx.ALL, 5)

        bSizer1.Add(line6, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

    def __on_close(self, evt):
        try:
            self.stop(None)  # 线程停止后对象被销毁
        except:
            pass
        self.Destroy()

    def check(self):
        # OS
        kernal = self.conn.recv('uname -r').strip()

        # CPU
        cur_conn = self.conn
        c = cur_conn.recv("cat /proc/cpuinfo")
        cpumodelr = r'model name.*?\:(.+)'
        cpumodelr = re.compile(cpumodelr)
        cpumodel = re.findall(cpumodelr, c)
        cpuidr = r'cpu cores.*?\:(.+)'
        cpuidr = re.compile(cpuidr)
        cpuid = re.findall(cpuidr, c)[0].strip()
        cpupr = r'physical id.*?\:(.+)'
        cpupr = re.compile(cpupr)
        cpups = re.findall(cpupr, c)
        cpup = str(len(list(set(cpups))))
        cpupror = str(len(cpumodel))
        # 内存
        memtext = cur_conn.recv('dmidecode -t 17')
        meminfo = cur_conn.recv('sed -n \'1p;3p\' /proc/meminfo | awk \'{print $2}\'')
        meminfo = meminfo
        memt, mema = meminfo.strip().split('\n')
        memtalr = r'Handle.*?,'
        memtalr = re.compile(memtalr)
        memtal = re.findall(memtalr, memtext)  # 内存插槽的个数
        memuser = r'Size: No Module Installed'
        memuser = re.compile(memuser)
        memuse = re.findall(memuser, memtext)  # 内存插槽未使用的个数
        # SCSI设备
        c = cur_conn.recv("cat /proc/scsi/scsi")
        diskr = r'.*?Model: (.+) R'
        diskr = re.compile(diskr)
        disk = re.findall(diskr, c)
        scsi = ''
        for d in range(len(disk)):
            scsi = scsi + '%s. %s\n' % (d + 1, disk[d])
        # HBA卡
        wwn = ''
        recv = cur_conn.recv("ls /sys/class/fc_host")
        if recv:
            hba_list = recv.split(' ')
            for host in hba_list:
                recv = cur_conn.recv("cat /sys/class/fc_host/%s/port_name" % host.strip())
                wwn += '%s：%s\n' % (host.strip(), recv.split('x')[1])
        self.kernel.SetValue(kernal)
        self.cpu_model.SetValue(cpumodel[0])
        self.cpu_num.SetValue(cpup)
        self.cpu_core.SetValue(cpuid)
        self.cpu_pro.SetValue(cpupror)
        self.mem_dev1.SetValue(str((len(memtal) - len(memuse))))
        memt = int(memt) // 1024
        if memt > 1024:
            memt = memt // 1024
            self.mem_total.SetValue(str(memt) + 'G')
        else:
            self.mem_total.SetValue(str(memt) + 'M')
        mema = int(mema) // 1024
        if mema > 1024:
            mema = mema // 1024
            self.mem_dev.SetValue(str(mema) + 'G')
        else:
            self.mem_dev.SetValue(str(mema) + 'M')
        self.scsi.SetValue(scsi)
        self.wwn.SetValue(wwn)

    def disk_monitor(self):
        old_rio = self.rio
        old_rs = self.rs
        old_wio = self.wio
        old_ws = self.ws
        old_rt = self.rt
        old_wt = self.wt
        old_time = self.time1
        re = self.conn.recv(
            "grep %s /proc/diskstats | awk '{print $4,$6,$8,$10,$7,$11}';echo $[10#$(date +%%d%%M%%S%%N)/1000000]" %
            self.check_disk)
        re = re.strip().split('\n')

        disk_info = re[0].split(' ')
        self.rio = int(disk_info[0])
        self.rs = int(disk_info[1])
        self.wio = int(disk_info[2])
        self.ws = int(disk_info[3])
        self.rt = int(disk_info[4])
        self.wt = int(disk_info[5])
        self.time1 = int(re[-1].strip())
        mtime = self.time1 - old_time
        io_total = self.rio - old_rio + self.wio - old_wio
        if io_total != 0:
            iowait = float(self.rt - old_rt + self.wt - old_wt) / io_total
        else:
            iowait = 0
        read_speed = (self.rs - old_rs) * 1000 / mtime / 2
        write_speed = (self.ws - old_ws) * 1000 / mtime / 2
        iops = (self.rio - old_rio + self.wio - old_wio) * 1000 / mtime
        self.read_speed.SetValue(str(round(read_speed, 2)))
        self.write_speed.SetValue(str(round(write_speed, 2)))
        self.iops.SetValue(str(round(iops, 2)))
        self.iowait.SetValue(str(round(iowait, 2)))

        time.sleep(2)

    def net_monitor(self):
        old_downt = self.downt
        old_upt = self.upt
        old_time = self.time2
        re = self.conn.recv(
            "grep %s /proc/net/dev | awk '{print $2,$10}';echo $[10#$(date +%%d%%M%%S%%N)/1000000]" % self.check_intf)
        re = re.strip().split('\n')

        net_info = re[0].split(' ')
        self.downt = int(net_info[0]) // 1024
        self.upt = int(net_info[1]) // 1024
        self.time2 = int(re[-1].strip())
        mtime = self.time2 - old_time
        self.up_total.SetValue(str(self.upt))
        self.down_dotal.SetValue(str(self.downt))
        up_speed = (self.upt - old_upt) * 1000 / mtime
        down_speed = (self.downt - old_downt) * 1000 / mtime
        self.up_speed.SetValue(str(round(up_speed, 2)))
        self.down_speed.SetValue(str(round(down_speed, 2)))
        time.sleep(2)

    def basic_monitor(self):
        use = self.use
        idle = self.idle
        re = self.conn.recv(
            "cat /proc/stat | head -n 1 | awk '{print $2,$3,$4,$5}';free | grep Mem | awk '{print $2,$7}';df  | grep %s | awk '{print $2,$3}'" % self.check_disk)
        re = re.strip().split('\n')
        cpuinfo = re[0].strip().split(' ')
        self.use = int(cpuinfo[0]) + int(cpuinfo[1]) + int(cpuinfo[2])
        self.idle = int(cpuinfo[3])

        cpu_use = 100 * (self.use - use) / (self.use - use + self.idle - idle)

        mem = re[1].split(' ')
        mem_use = 100 * (float(mem[0]) - float(mem[1])) / float(mem[0])
        if len(re) > 2:
            disk_tot = 0
            disk_use = 0
            for i in re[2:]:
                try:
                    disk_tot += int(i.strip().split(' ')[0])
                    disk_use += int(i.strip().split(' ')[1])
                except:
                    continue
            disk_use = str(float(disk_use) / float(disk_tot) * 100)[:4]
            self.disk_stat.SetValue(disk_use)
        self.cpu_stat.SetValue(str(round(cpu_use, 2)))
        self.mem_stat.SetValue(str(round(mem_use, 2)))
        time.sleep(2)

    def start(self, evt):
        int_ok = True
        disk_ok = True
        basic_ok = True

        self.disk_job = methods.job()
        self.net_job = methods.job()
        self.basic_job = methods.job()
        self.bt_start.Disable()

        self.check_disk = self.select_disk.GetValue()
        re = self.conn.recv(
            "grep %s /proc/diskstats | awk '{print $4,$6,$8,$10,$7,$11}';echo $[10#$(date +%%d%%M%%S%%N)/1000000]" % self.check_disk)
        re = re.strip().split('\n')
        if len(re) != 1:
            disk_info = re[0].split(' ')
            self.rio = int(disk_info[0])
            self.rs = int(disk_info[1])
            self.wio = int(disk_info[2])
            self.ws = int(disk_info[3])
            self.rt = int(disk_info[4])
            self.wt = int(disk_info[5])
            self.time1 = int(re[-1].strip())
            self.disk.SetValue(self.check_disk)
        else:
            disk_ok = False

        self.check_intf = self.select_int.GetValue()
        cmd = "grep %s /proc/net/dev | awk '{print $2,$10}';echo $[10#$(date +%%d%%M%%S%%N)/1000000]" % self.check_intf
        re = self.conn.recv(cmd)
        re = re.strip().split('\n')
        if len(re) != 1:
            net_info = re[0].split(' ')
            self.downt = int(net_info[0]) // 1024
            self.upt = int(net_info[1]) // 1024
            self.time2 = int(re[-1].strip())
            self.interface.SetValue(self.check_intf)
        else:
            int_ok = False

        re = self.conn.recv(
            "cat /proc/stat | head -n 1 | awk '{print $2,$3,$4,$5}';free | grep Mem | awk '{print $2,$3}';df  | grep %s | awk '{print $2,$3}'" % self.check_disk)
        re = re.strip().split('\n')
        cpuinfo = re[0].strip().split(' ')
        self.use = int(cpuinfo[0]) + int(cpuinfo[1]) + int(cpuinfo[2])
        self.idle = int(cpuinfo[3])

        time.sleep(1)
        if disk_ok:
            start_new_thread(self.disk_job.start, (self.disk_monitor,))
        if int_ok:
            start_new_thread(self.net_job.start, (self.net_monitor,))
        if basic_ok:
            start_new_thread(self.basic_job.start, (self.basic_monitor,))

    def stop(self, evt):
        self.bt_start.Enable()
        self.disk_job.stop()
        self.net_job.stop()
        self.basic_job.stop()


class sys_config(wx.Dialog):
    def __init__(self, conn):
        wx.Dialog.__init__(self, None, id=wx.ID_ANY, title='系统设置 - %s' % conn.host)
        self.conn = conn
        self.SetBackgroundColour(wx.Colour(227, 224, 219))
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.Centre(wx.BOTH)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # 时间同步
        funcbox1 = mStaticBox(self, '时间同步')
        bsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        panel1 = wx.Panel(self)
        panel1.SetBackgroundColour(self.GetBackgroundColour())
        panel1.SetSizer(bsizer1)
        bt11 = mButton(panel1, label='同步本地时间', color='deepgreen')
        bt11.Bind(wx.EVT_BUTTON, self.sync_time)
        bt12 = mButton(panel1, label='查看服务器时间', color='deepgreen')
        bt12.Bind(wx.EVT_BUTTON, self.check_time)
        bsizer1.Add(bt11, 0, wx.ALL, 5)
        bsizer1.Add(bt12, 0, wx.ALL, 5)
        funcbox1.Add(panel1, 0)

        # NAT
        funcbox2 = mStaticBox(self, 'SNAT')
        bsizer2 = wx.BoxSizer(wx.VERTICAL)
        panel2 = wx.Panel(self)
        panel2.SetBackgroundColour('#ffffff')
        panel2.SetSizer(bsizer2)
        self.wan_int = mInput(panel2, st_label='WAN网卡：', tc_label='eth0', st_size=(100, -1))
        self.lan_int = mInput(panel2, st_label='LAN网卡：', tc_label='eth1', st_size=(100, -1))
        self.gw = mInput(panel2, st_label='LAN网关IP：', tc_label='192.168.10.1', st_size=(100, -1))
        self.mask = mInput(panel2, st_label='子网掩码：', tc_label='255.255.255.0', st_size=(100, -1))
        bt21 = mButton(panel2, label='添加配置', color='deepgreen')
        bt21.Bind(wx.EVT_BUTTON, self.nat)
        bt22 = mButton(panel2, label='删除配置', color='red')
        bt22.Bind(wx.EVT_BUTTON, self.del_nat)
        bsizer21 = wx.BoxSizer(wx.HORIZONTAL)
        bsizer21.Add(bt21, 1)
        bsizer21.Add(bt22, 1)
        bsizer2.Add(self.wan_int, 0, wx.EXPAND)
        bsizer2.Add(self.lan_int, 0, wx.EXPAND | wx.TOP, 1)
        bsizer2.Add(self.gw, 0, wx.EXPAND | wx.TOP, 1)
        bsizer2.Add(self.mask, 0, wx.EXPAND | wx.TOP, 1)
        bsizer2.Add(bsizer21, 0, wx.EXPAND)
        funcbox2.Add(panel2, 0, wx.EXPAND)

        box1 = wx.BoxSizer(wx.VERTICAL)
        box1.Add(funcbox1, 0, wx.EXPAND)
        box1.Add((0, 10))
        box1.Add(funcbox2, 0, wx.EXPAND)

        bSizerAll = wx.BoxSizer(wx.VERTICAL)
        bSizerAll.Add(box1, 0, wx.ALL, 10)
        self.SetSizer(bSizerAll)
        self.SetSize(self.GetBestSize())

    def on_close(self, evt):
        self.Destroy()

    def nat(self, evt):
        wan_int = self.wan_int.GetValue()
        lan_int = self.lan_int.GetValue()
        gw = self.gw.GetValue()
        mask = self.mask.GetValue()
        cmd1 = "iptables -t nat -A POSTROUTING -o %s -j MASQUERADE" % wan_int
        cmd2 = "iptables -A FORWARD -i %s -o %s  -m state --state RELATED,ESTABLISHED -j ACCEPT" % (
            wan_int, lan_int)
        cmd3 = "iptables -A FORWARD -i %s -o %s -j ACCEPT" % (lan_int, wan_int)
        cmd4 = "ifconfig %s add %s netmask %s" % (lan_int, gw, mask)
        if wan_int == lan_int:
            mMessageBox('NAT配置需要两个网卡设备！')
            return
        try:
            self.conn.send_withlog(cmd1)
            self.conn.send_withlog(cmd2)
            self.conn.send_withlog(cmd3)
            self.conn.send_withlog(cmd4)
            self.conn.send_withlog("chmod a+x /etc/rc.d/rc.local")
            self.conn.send_withlog("echo '%s'>>/etc/rc.d/rc.local" % cmd1)
            self.conn.send_withlog("echo '%s'>>/etc/rc.d/rc.local" % cmd2)
            self.conn.send_withlog("echo '%s'>>/etc/rc.d/rc.local" % cmd3)
            self.conn.send_withlog("echo '%s'>>/etc/rc.d/rc.local" % cmd4)
            mMessageBox('NAT配置成功！')
        except Exception as e:
            mMessageBox(str(e))

    def del_nat(self, evt):
        try:
            self.conn.send_withlog("cp /etc/rc.d/rc.local /etc/rc.d/rc.local.bak")
            self.conn.send_withlog("sed -i '/^iptables\ -A\ FORWARD\ -i/d' /etc/rc.d/rc.local")
            self.conn.send_withlog("sed -i '/^iptables\ -t\ nat/d' /etc/rc.d/rc.local")
            self.conn.send_withlog("sed -i '/^ifconfig/d' /etc/rc.d/rc.local")
            mMessageBox('删除成功，服务器重启后生效！')
        except Exception as e:
            mMessageBox('删除失败：%s' % str(e))

    def sync_time(self, evt):
        cur_time = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
        fix_command_time = "date -s \"%s\"" % cur_time
        fix_command_zone = "cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime"
        try:
            self.conn.send_withlog(fix_command_time)
            self.conn.send_withlog(fix_command_zone)
            self.conn.send_withlog('hwclock --systohc')
            mMessageBox('同步时间成功！')
        except Exception as e:
            mMessageBox(str(e))

    def check_time(self, evt):
        time = self.conn.recv('date')
        mMessageBox(time.strip())


class vdi_terminal(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title='VDI终端设置')
        self.link_dic = globals.multi_ssh_conn
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.Centre(wx.BOTH)
        bs = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(bs)

        self.h264_val = None
        bs_h264 = wx.BoxSizer(wx.HORIZONTAL)
        label_h264 = wx.StaticText(self, label="H264: ")
        label_h264.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        self.radio_h264 = mRadio(self, ['关', '开'], method=self.config_h264)

        bs_h264.Add(label_h264, 0)
        bs_h264.Add(self.radio_h264, 0, wx.LEFT, 10)
        bs.Add(bs_h264, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSize(self.GetBestSize() + (20, 0))
        bs.Layout()

    def init_config(self):
        if int(self.h264_val) == -1:
            self.radio_h264.setFoces(0)
        else:
            self.radio_h264.setFoces(1)

    def config_h264(self):
        if self.radio_h264.focus == '开':
            val = 1
        else:
            val = -1
        for conn in list(self.link_dic.values()):
            conn.send("sed -i '/^h264=/ch264=%s' /etc/evdi/config/display_settings" % val)
        mMessageBox('修改成功')


class vdi_chClass(wx.Dialog):
    def __init__(self, label, pools):
        wx.Dialog.__init__(self, None, id=wx.ID_ANY, title='修改教室')
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.Centre(wx.BOTH)

        sbSizerAll = wx.BoxSizer(wx.VERTICAL)

        self.st = wx.StaticText(self, wx.ID_ANY, "设置场景：%s" % label)
        self.st.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        sbSizerAll.Add(self.st, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 10)

        self.choice = mChoice(self, st_label='选择教室', choice=pools)
        sbSizerAll.Add(self.choice, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 10)

        linebt = wx.BoxSizer(wx.HORIZONTAL)
        self.bt_ok = mButton(self, id=wx.ID_OK, label="确定", color='deepgreen')
        linebt.Add(self.bt_ok, 0)

        self.bt_cancel = mButton(self, id=wx.ID_CANCEL, label="取消", color='red')
        linebt.Add(self.bt_cancel, 0, wx.LEFT, 10)

        sbSizerAll.Add(linebt, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 10)

        self.SetSizer(sbSizerAll)

        self.SetSize(self.GetBestSize())
        self.Layout()


class vdi_chSubnet(wx.Dialog):
    def __init__(self, name):
        wx.Dialog.__init__(self, None, id=wx.ID_ANY, title='修改子网掩码')
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.Centre(wx.BOTH)

        sbSizerAll = wx.BoxSizer(wx.VERTICAL)

        self.st = wx.StaticText(self, wx.ID_ANY, "子网名称：%s" % name)
        self.st.SetFont(wx.Font(12, 70, 90, 92, False, "微软雅黑"))
        sbSizerAll.Add(self.st, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 10)

        self.mask = mInput(self, st_label='子网掩码')
        sbSizerAll.Add(self.mask, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 10)

        linebt = wx.BoxSizer(wx.HORIZONTAL)
        self.bt_ok = mButton(self, id=wx.ID_OK, label="确定", color='deepgreen')
        linebt.Add(self.bt_ok, 0)

        self.bt_cancel = mButton(self, id=wx.ID_CANCEL, label="取消", color='red')
        linebt.Add(self.bt_cancel, 0, wx.LEFT, 10)

        sbSizerAll.Add(linebt, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(sbSizerAll)

        self.SetSize(self.GetBestSize())
        self.Layout()


class add_cmd_dlg(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, id=wx.ID_ANY, title='添加命令', size=(480, 380))

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer_main)

        txt1 = wx.StaticText(self, label='名称')
        txt1.SetFont(wx.Font(12, 70, 90, 90, False, "微软雅黑"))
        sizer_main.Add(txt1, 0, wx.LEFT, 10)

        self.name = wx.TextCtrl(self, size=(300, -1))
        sizer_main.Add(self.name, 0, wx.LEFT, 10)

        txt2 = wx.StaticText(self, label='命令')
        txt2.SetFont(wx.Font(12, 70, 90, 90, False, "微软雅黑"))
        sizer_main.Add(txt2, 0, wx.LEFT | wx.TOP, 10)

        self.cmd = wx.stc.StyledTextCtrl(self)
        self.cmd.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        self.cmd.SetMarginWidth(0, 20)
        sizer_main.Add(self.cmd, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        linebt = wx.BoxSizer(wx.HORIZONTAL)
        self.bt_ok = mButton(self, id=wx.ID_OK, label="确定", color='deepgreen')
        linebt.Add(self.bt_ok, 0)

        self.bt_cancel = mButton(self, id=wx.ID_CANCEL, label="取消", color='red')
        linebt.Add(self.bt_cancel, 0, wx.LEFT, 10)

        sizer_main.Add(linebt, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        self.Layout()


class file_choice(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, id=wx.ID_ANY, title='选择文件', size=(480, 380))
        self.dirCtrl = wx.GenericDirCtrl(self, -1, size=(200, 225),
                                         style=wx.DIRCTRL_MULTIPLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        sizer.Add(self.dirCtrl, 1, wx.EXPAND)

        linebt = wx.BoxSizer(wx.HORIZONTAL)

        txt1 = wx.StaticText(self, -1, '上传路径:')
        self.st_path = wx.StaticText(self, -1, '%s')
        self.cb_multi = wx.CheckBox(self, -1, '上传全部会话')
        self.cb_multi.SetValue(True)
        self.cb_rootlimit = wx.CheckBox(self, -1, '开启根目录权限')
        self.bt_ok = wx.Button(self, id=wx.ID_OK, size=(40, -1), label="确定")
        self.bt_cancel = wx.Button(self, id=wx.ID_CANCEL, size=(40, -1), label="取消")

        linebt.Add((-1, -1), 1)
        linebt.Add(self.cb_rootlimit, 0, wx.ALIGN_CENTER)
        linebt.Add(self.cb_multi, 0, wx.ALIGN_CENTER)
        linebt.Add(self.bt_ok, 0, wx.RIGHT, 5)
        linebt.Add(self.bt_cancel, 0, wx.RIGHT, 10)

        sizer_path = wx.BoxSizer(wx.HORIZONTAL)
        sizer_path.Add(txt1, 0, wx.ALIGN_CENTER)
        sizer_path.Add(self.st_path, 0, wx.ALIGN_CENTER)

        sizer.Add(sizer_path, 0, wx.EXPAND | wx.TOP | wx.LEFT, 5)
        sizer.Add(linebt, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT, 5)

        self.Layout()


class config_dlg(wx.adv.PropertySheetDialog):
    def __init__(self, parent, bookType):
        wx.adv.PropertySheetDialog.__init__(self)
        self.SetBackgroundColour(globals.panel_bgcolor)
        sheetStyle = bookType | wx.adv.PROPSHEET_SHRINKTOFIT
        self.SetSheetStyle(sheetStyle)
        self.SetSheetInnerBorder(0)
        self.SetSheetOuterBorder(0)

        self.Create(parent, title="选项")
        self.CreateButtons(wx.OK | wx.CANCEL)

        notebook = self.GetBookCtrl()
        notebook.AddPage(self.create_ssh_config_panel(notebook), "会话")
        notebook.AddPage(self.create_oseasy_config_panel(notebook), "桌面云")

        self.LayoutDialog()

    def create_ssh_config_panel(self, parent):
        panel = wx.Panel(parent, size=(400, 300))

        topSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        txt1 = wx.StaticText(panel, -1, "最大并发连接数", size=(80, -1), style=wx.ALIGN_RIGHT)
        self.max_thread = wx.SpinCtrl(panel, -1, "", (-1, -1), (40, -1), wx.SP_ARROW_KEYS, 1, 60, 1)
        self.max_thread.SetValue(globals.max_thread)
        sizer1.Add(txt1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer1.Add(self.max_thread, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        txt2 = wx.StaticText(panel, -1, "连接超时(s)", size=(80, -1), style=wx.ALIGN_RIGHT)
        self.timeout = wx.SpinCtrl(panel, -1, "", (-1, -1), (40, -1), wx.SP_ARROW_KEYS, 1, 60, 1)
        self.timeout.SetValue(globals.timeout)
        sizer2.Add(txt2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer2.Add(self.timeout, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        txt3 = wx.StaticText(panel, -1, 'webssh端口', size=(80, -1), style=wx.ALIGN_RIGHT)
        self.wssh_port = wx.TextCtrl(panel, value=globals.wssh_port)
        sizer3.Add(txt3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer3.Add(self.wssh_port, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        self.download_path = filebrowse.DirBrowseButton(panel, -1, size=(450, -1))
        self.download_path.SetValue(globals.download_path)
        sizer4.Add(self.download_path, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        topSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(sizer4, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(topSizer)
        return panel

    def create_oseasy_config_panel(self, parent):
        panel = wx.Panel(parent, size=(400, 300))
        topSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        txt1 = wx.StaticText(panel, -1, 'root密码', size=(80, -1), style=wx.ALIGN_RIGHT)
        self.vdi_root_pwd = wx.TextCtrl(panel, value=globals.vdi_root_pwd)
        sizer1.Add(txt1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer1.Add(self.vdi_root_pwd, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        txt2 = wx.StaticText(panel, -1, '默认用户名', size=(80, -1), style=wx.ALIGN_RIGHT)
        self.vdi_user = wx.TextCtrl(panel, value=globals.vdi_user)
        sizer2.Add(txt2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer2.Add(self.vdi_user, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        txt3 = wx.StaticText(panel, -1, '默认用户密码', size=(80, -1), style=wx.ALIGN_RIGHT)
        self.vdi_user_pwd = wx.TextCtrl(panel, value=globals.vdi_user_pwd)
        sizer3.Add(txt3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer3.Add(self.vdi_user_pwd, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        txt4 = wx.StaticText(panel, -1, '数据库密码', size=(80, -1), style=wx.ALIGN_RIGHT)
        self.mysql_pwd = wx.TextCtrl(panel, value=globals.vdi_mysql_pwd)
        sizer4.Add(txt4, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer4.Add(self.mysql_pwd, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        topSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)
        topSizer.Add(sizer4, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(topSizer)
        return panel


class system_moniter(wx.Frame):
    def __init__(self, parent, title, conn):
        wx.Frame.__init__(self, parent=parent, title=title,
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX))
        self.conn = conn
        if not self.conn:
            self.conn.connect()
        self.MONITER_STAT = True
        self.time_cost = 0  # 单位：秒
        self.old_time = 0
        self.st_width = 70
        self.SetBackgroundColour('white')
        self.SetIcon(wx.Icon('bitmaps/bt_moniter.png'))

        self.init_panel()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.int_choice.Bind(wx.EVT_CHOICE, self.on_choice_change)

    # 监控窗口
    def init_panel(self):
        try:
            stat = self.get_stat()
            res = self.conn.recv("lsblk | sed 's/├─//g' |sed 's/└─//g' |sed '1d' | awk '{print $1,$7}';"
                                 "echo '-separate-';"
                                 "uname -r;"
                                 "echo '-separate-';"
                                 "LANG=c lscpu | grep -E 'Model name|Socket\(s\)|Core\(s\)|Thread\(s\)';"
                                 "echo '-separate-';"
                                 "lspci | grep -i Ethernet;"
                                 "echo '-separate-';"
                                 "lsscsi")
            self.basic_info = res.split('-separate-')
            if self.basic_info[3].strip() == '':
                res = self.conn.server_recv('lspci | grep -i Ethernet')
                int_str = ''
                for int_info in res.split('lspci | grep -i Ethernet')[1].strip().split('\n')[:-1]:
                    int_info = int_info.split(': ')[1].strip() + '\n'
                    int_info = re.sub(r'\x1b[@-_][0-?]*[^@-_]*\[K', '', int_info)
                    int_str += int_info
                self.basic_info[3] = int_str[:-1]
        except Exception as e:
            self.Destroy()
            mMessageBox(str(e))
            raise

        self.init_pwin_system()
        self.init_pwin_net()
        self.init_pwin_disk()

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer1)
        s1l0 = wx.BoxSizer(wx.HORIZONTAL)
        s1l1 = wx.BoxSizer(wx.HORIZONTAL)

        titel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_system = mPlateButton(self, None, '系统', (-1, 20), platebtn.PB_STYLE_DROPARROW)
        title_system.Bind(platebtn.EVT_PLATEBTN_DROPARROW_PRESSED, self.on_system)
        title_system.SetFont(wx.Font(10, 70, 90, 92, False, '微软雅黑'))
        titel_sizer.Add(title_system)
        titel_sizer.Add((-1, -1), 1, wx.EXPAND)
        titel_sizer.Add(wx.StaticText(self, label='刷新频率'), 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        self.freq_ctrl = wx.SpinCtrl(self, -1, "2", size=(-1, 20))
        titel_sizer.Add(self.freq_ctrl, 0, wx.EXPAND | wx.RIGHT, 20)

        title_disk = mPlateButton(self, None, '磁盘', (-1, 20), platebtn.PB_STYLE_DROPARROW)
        title_disk.Bind(platebtn.EVT_PLATEBTN_DROPARROW_PRESSED, self.on_disk)
        title_disk.SetFont(wx.Font(10, 70, 90, 92, False, '微软雅黑'))
        title_net = mPlateButton(self, None, '网络', (-1, 20), platebtn.PB_STYLE_DROPARROW)
        title_net.Bind(platebtn.EVT_PLATEBTN_DROPARROW_PRESSED, self.on_net)
        title_net.SetFont(wx.Font(10, 70, 90, 92, False, '微软雅黑'))

        sizer1.Add(titel_sizer, 0, wx.EXPAND | wx.TOP | wx.LEFT, 10)
        sizer1.Add(s1l0, 0, wx.EXPAND)
        sizer1.Add(s1l1, 0, wx.EXPAND)

        self.gauge_cpu = mGauge(self)
        self.gauge_mem = mGauge(self)
        self.gauge_swap = mGauge(self)
        st_cpu = wx.StaticText(self, label='CPU', size=(self.st_width, -1), style=wx.ALIGN_RIGHT)
        st_mem = wx.StaticText(self, label='内存', style=wx.ALIGN_RIGHT)
        st_swap = wx.StaticText(self, label='交换', style=wx.ALIGN_RIGHT)

        st_1 = wx.StaticText(self, label='运行', size=(self.st_width, -1), style=wx.ALIGN_RIGHT)
        st_2 = wx.StaticText(self, label='负载', size=(self.st_width, -1), style=wx.ALIGN_RIGHT)
        self.runtime = wx.StaticText(self, label='')
        self.load = wx.StaticText(self, label='')

        s1l0.Add(st_1, 0, wx.TOP | wx.LEFT, 5)
        s1l0.Add(self.runtime, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        s1l0.Add(st_2, 0, wx.TOP | wx.LEFT, 5)
        s1l0.Add(self.load, 0, wx.TOP | wx.LEFT, 5)

        s1l1.Add(st_cpu, 0, wx.TOP | wx.LEFT, 5)
        s1l1.Add(self.gauge_cpu, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        s1l1.Add(st_mem, 0, wx.TOP | wx.LEFT, 5)
        s1l1.Add(self.gauge_mem, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        s1l1.Add(st_swap, 0, wx.TOP | wx.LEFT, 5)
        s1l1.Add(self.gauge_swap, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)

        # time
        self.old_time = int(stat['time'])

        # cpu
        self.use_tmp = int(stat['system']['cpu_use'])
        self.idle_tmp = int(stat['system']['cpu_idle'])

        # net
        self.int_list = {}
        for int_info in stat['net']:
            int_info = int_info.split(' ')
            if int_info[0] == 'lo:':
                continue
            int_name = int_info[0][:-1]
            self.int_list[int_name] = {
                'upload': int_info[1],
                'download': int_info[2],
            }

        sizer_net = wx.BoxSizer(wx.HORIZONTAL)

        self.int_choice = wx.Choice(self, choices=list(self.int_list.keys()), style=wx.NO_BORDER, size=(118, 20))
        self.int_choice.SetSelection(0)

        sizer_net.Add(wx.StaticText(self, label='网卡', size=(self.st_width, -1),
                                    style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 0,
                      wx.TOP | wx.LEFT | wx.ALIGN_CENTER, 5)
        sizer_net.Add(self.int_choice, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)

        sizer_net.Add(wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap('bitmaps/upload.png', wx.BITMAP_TYPE_PNG)), 0,
                      wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 5)
        self.st_upload = wx.StaticText(self, label='/', size=(50, -1))
        sizer_net.Add(self.st_upload, 0, wx.TOP | wx.ALIGN_CENTER, 5)

        sizer_net.Add(wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap('bitmaps/download.png', wx.BITMAP_TYPE_PNG)), 0,
                      wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 5)

        self.st_download = wx.StaticText(self, label='/', size=(50, -1))
        sizer_net.Add(self.st_download, 0, wx.TOP | wx.ALIGN_CENTER, 5)

        sizer_net.Add(wx.StaticText(self, label='速率：'), 0, wx.TOP | wx.LEFT | wx.ALIGN_CENTER, 5)
        self.st_int_speed = wx.StaticText(self, label='/', size=(70, -1))
        sizer_net.Add(self.st_int_speed, 0, wx.TOP | wx.RIGHT | wx.ALIGN_CENTER, 5)

        sizer_net.Add(wx.StaticText(self, label='接口：'), 0, wx.TOP | wx.LEFT | wx.ALIGN_CENTER, 5)
        self.st_int_port = wx.StaticText(self, label='/', size=(40, -1))
        sizer_net.Add(self.st_int_port, 0, wx.TOP | wx.RIGHT | wx.ALIGN_CENTER, 5)

        sizer_net.Add(wx.StaticText(self, label='连接状态：'), 0, wx.TOP | wx.LEFT | wx.ALIGN_CENTER, 5)
        self.st_int_detected = wx.StaticText(self, label='/', size=(20, -1))
        sizer_net.Add(self.st_int_detected, 0, wx.TOP | wx.RIGHT | wx.ALIGN_CENTER, 5)

        sizer1.Add(title_net, 0, wx.TOP | wx.LEFT, 10)
        sizer1.Add(sizer_net, 0, wx.EXPAND)

        self.on_choice_change(None)

        # disk
        blk_info = self.basic_info[0].split('\n')
        mount_point = {}
        for disk in blk_info:
            if not disk:
                continue
            disk_info = disk.split(' ')
            mount_point[disk_info[0]] = disk_info[1]

        sizer1.Add(title_disk, 0, wx.TOP | wx.LEFT, 10)
        self.disks = {}
        disk_info = stat['disk']
        for disk in disk_info:
            disk = disk.split(' ')
            if disk[0].startswith('loop') or disk[0].startswith('sr'):
                continue
            gauge = mGauge(self)
            st_read = wx.StaticText(self, label='/', size=(50, -1))
            st_write = wx.StaticText(self, label='/', size=(50, -1))
            st_iops = wx.StaticText(self, label='/', size=(50, -1))

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(wx.StaticText(self, label=disk[0], size=(self.st_width, -1), style=wx.ALIGN_RIGHT), 0,
                      wx.TOP | wx.LEFT, 5)
            sizer.Add(gauge, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
            sizer.Add(wx.StaticText(self, label='读：'), 0, wx.TOP | wx.LEFT, 5)
            sizer.Add(st_read, 0, wx.TOP | wx.LEFT, 5)
            sizer.Add(wx.StaticText(self, label='写：'), 0, wx.TOP | wx.LEFT, 5)
            sizer.Add(st_write, 0, wx.TOP | wx.LEFT, 5)
            sizer.Add(wx.StaticText(self, label='iops：'), 0, wx.TOP | wx.LEFT, 5)
            sizer.Add(st_iops, 0, wx.TOP | wx.LEFT, 5)
            sizer.Add(
                wx.StaticText(self, label='挂载点：%s' % mount_point[disk[0]] if disk[0] in mount_point else '挂载点：'),
                0, wx.TOP | wx.LEFT | wx.RIGHT, 5)

            self.disks[disk[0]] = {
                'read_io': int(disk[1]),
                'write_io': int(disk[2]),
                'read_sectors': int(disk[3]),
                'write_sectors': int(disk[4]),
                'io_time': int(disk[5]),
                'gauge': gauge,
                'st_read': st_read,
                'st_write': st_write,
                'st_iops': st_iops,
            }
            sizer1.Add(sizer, 0, wx.EXPAND)

        self.Layout()
        self.SetSize(self.GetBestSize() + (20, 20))
        self.Centre()

        start_new_thread(self.momniter, ())

    def get_stat(self):
        cmd = "cat /proc/net/dev | awk '{print $1,$2,$10}';" \
              "echo '-separate-';" \
              "cat /proc/diskstats | awk '{print $3,$4,$8,$6,$10,$13}';" \
              "echo '-separate-';" \
              "cat /proc/stat | head -n 1 | awk '{sum = $2 + $3 + $4; print sum,$5}';" \
              "free | tail -n +2 | awk '{print $2,$3,$7}';" \
              "uptime;" \
              "echo '-separate-';" \
              "echo $[10#$(date +%d%M%S%N)/1000000]"
        re = self.conn.recv(cmd)
        re = re.strip().split('-separate-')

        sys_info = re[2].strip().split('\n')
        sys_stat = {
            'cpu_use': sys_info[0].split(' ')[0],
            'cpu_idle': sys_info[0].split(' ')[1],
            'mem': sys_info[1].split(' '),
            'swap': sys_info[2].split(' '),
            'uptime': sys_info[3].split(',')
        }

        status = {
            "net": re[0].strip().split('\n')[2:],
            'disk': re[1].strip().split('\n'),
            'system': sys_stat,
            'time': re[3]
        }
        return status

    def momniter(self):
        while self.MONITER_STAT:
            try:
                stat = self.get_stat()
                time_now = int(stat['time'])
                self.time_cost = (time_now - self.old_time) / 1000
                self.old_time = time_now
                self.set_system_stat(stat['system'])
                self.set_disk_stat(stat['disk'])
                self.set_net_stat(stat['net'])
            except Exception as e:
                logging.error(e)
                raise
            time.sleep(self.freq_ctrl.GetValue())

    def init_pwin_system(self):
        self.pwin_system = mPopupWindow(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.pwin_system.SetSizer(sizer)

        kernal = self.basic_info[1].strip()

        # cpu_info格式化
        cpu_info = self.basic_info[2].strip().split('\n')
        cpu_model = cpu_info[3].split(':')[1].strip()
        cpu_count = int(cpu_info[2].split(':')[1].strip())
        core_per_cpu = int(cpu_info[1].split(':')[1].strip())
        thread_per_core = int(cpu_info[0].split(':')[1].strip())

        s1 = wx.BoxSizer(wx.HORIZONTAL)
        s1str = wx.StaticText(self.pwin_system, label='内核: ', size=(60, -1), style=wx.ALIGN_RIGHT)
        s1str.SetFont(wx.Font(9, 70, 90, 92, False, '微软雅黑'))
        s1.Add(s1str, 0)
        s1.Add(wx.StaticText(self.pwin_system, label=kernal), 1)
        sizer.Add(s1, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        s2 = wx.BoxSizer(wx.HORIZONTAL)
        s2str = wx.StaticText(self.pwin_system, label='CPU型号: ', size=(60, -1), style=wx.ALIGN_RIGHT)
        s2str.SetFont(wx.Font(9, 70, 90, 92, False, '微软雅黑'))
        s2.Add(s2str, 0)
        s2.Add(wx.StaticText(self.pwin_system, label=cpu_model), 1)
        sizer.Add(s2, 0, wx.LEFT | wx.RIGHT, 10)

        s3 = wx.BoxSizer(wx.HORIZONTAL)
        s3str = wx.StaticText(self.pwin_system, label='CPU参数: ', size=(60, -1), style=wx.ALIGN_RIGHT)
        s3str.SetFont(wx.Font(9, 70, 90, 92, False, '微软雅黑'))
        s3.Add(s3str, 0)
        s3.Add(wx.StaticText(self.pwin_system,
                             label=f'{cpu_count}路/{core_per_cpu * cpu_count}核/{cpu_count * core_per_cpu * thread_per_core}线程'),
               1)
        sizer.Add(s3, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.pwin_system.SetSize(self.pwin_system.GetBestSize())
        self.pwin_system.Layout()

    def init_pwin_net(self):
        self.pwin_net = mPopupWindow(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.pwin_net.SetSizer(sizer)
        sizer.Add(wx.StaticText(self.pwin_net, label=self.basic_info[3].strip()), 1, wx.ALL, 10)

        self.pwin_net.SetSize(self.pwin_net.GetBestSize())
        self.pwin_net.Layout()

    def init_pwin_disk(self):
        self.pwin_disk = mPopupWindow(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.pwin_disk.SetSizer(sizer)
        sizer.Add(wx.StaticText(self.pwin_disk, label=self.basic_info[4].strip()), 1, wx.ALL, 10)

        self.pwin_disk.SetSize(self.pwin_disk.GetBestSize())
        self.pwin_disk.Layout()

    def on_system(self, evt):
        bt = evt.GetEventObject()
        pos = bt.ClientToScreen((0, 0))
        self.pwin_system.Position(pos, (30, 30))
        wx.CallAfter(self.pwin_system.Show, True)

    def on_net(self, evt):
        bt = evt.GetEventObject()
        pos = bt.ClientToScreen((0, 0))
        self.pwin_net.Position(pos, (30, 30))
        wx.CallAfter(self.pwin_net.Show, True)

    def on_disk(self, evt):
        bt = evt.GetEventObject()
        pos = bt.ClientToScreen((0, 0))
        self.pwin_disk.Position(pos, (30, 30))
        wx.CallAfter(self.pwin_disk.Show, True)

    def set_system_stat(self, stat):
        use = self.use_tmp
        idle = self.idle_tmp
        self.use_tmp = int(stat['cpu_use'])
        self.idle_tmp = int(stat['cpu_idle'])

        cpu_use = 100 * (self.use_tmp - use) / (self.use_tmp - use + self.idle_tmp - idle)
        self.gauge_cpu.SetValue(int(cpu_use), f'{cpu_use:.1f}%')

        mem = stat['mem']
        mem_use = int(mem[0]) - int(mem[2])
        mem_tot = int(mem[0])
        mem_use_per = 100 * mem_use / mem_tot
        mem_use_fit = methods.bytes2human(mem_use, start='K')
        mem_tot_fit = methods.bytes2human(mem_tot, start='K')
        self.gauge_mem.SetValue(int(mem_use_per), f'{mem_use_per:.1f}%')
        self.gauge_mem.SetToolTip(f'{mem_use_fit}/{mem_tot_fit}')

        swap = stat['swap']
        swap_use = int(swap[1])
        swap_tot = int(swap[0])
        if not swap_tot:
            self.gauge_swap.SetValue(0, 'no swap', '')
        else:
            swap_use_per = int(100 * swap_use / swap_tot)
            swap_use_fit = methods.bytes2human(swap_use, start='K')
            swap_tot_fit = methods.bytes2human(swap_tot, start='K')
            self.gauge_swap.SetValue(swap_use_per, '%s%%' % swap_use_per)
            self.gauge_swap.SetToolTip(f'{swap_use_fit}/{swap_tot_fit}')

        uptime = stat['uptime']
        self.runtime.SetLabel(uptime[0].split('up')[1])
        self.load.SetLabel(uptime[-3].split(':')[1] + uptime[-2] + uptime[-1])

    def set_disk_stat(self, disk_info):
        for disk in disk_info:
            disk = disk.split(' ')
            if disk[0].startswith('loop') or disk[0].startswith('sr'):
                continue
            r_io_old = self.disks[disk[0]]['read_io']
            w_io_old = self.disks[disk[0]]['write_io']
            r_sec_old = self.disks[disk[0]]['read_sectors']
            w_sec_old = self.disks[disk[0]]['write_sectors']
            io_time_old = self.disks[disk[0]]['io_time']
            self.disks[disk[0]]['read_io'] = int(disk[1])
            self.disks[disk[0]]['write_io'] = int(disk[2])
            self.disks[disk[0]]['read_sectors'] = int(disk[3])
            self.disks[disk[0]]['write_sectors'] = int(disk[4])
            self.disks[disk[0]]['io_time'] = int(disk[5])

            read_speed = (int(disk[3]) - r_sec_old) / self.time_cost / 2
            read_speed_format = methods.bytes2human(int(read_speed), 'K')
            write_speed = (int(disk[4]) - w_sec_old) / self.time_cost / 2
            write_speed_format = methods.bytes2human(int(write_speed), 'K')
            iops = (int(disk[1]) - r_io_old + int(disk[2]) - w_io_old) / self.time_cost
            busy = (int(disk[5]) - io_time_old) * 100 / (self.time_cost * 1000)  # 时间换算成毫秒
            self.disks[disk[0]]['gauge'].SetValue(int(busy), left_str=f'{busy:.1f}%')
            self.disks[disk[0]]['st_read'].SetLabel(f'{read_speed_format}/s')
            self.disks[disk[0]]['st_write'].SetLabel(f'{write_speed_format}/s')
            self.disks[disk[0]]['st_iops'].SetLabel(f'{iops:.0f}')

    def set_net_stat(self, net_info):
        int_name = self.int_choice.GetStringSelection()
        if not int_name:
            return
        for int_info in net_info:
            int_info = int_info.split(' ')
            if int_info[0][:-1] == int_name:
                up_last = int(self.int_list[int_name]['upload'])
                down_last = int(self.int_list[int_name]['download'])
                up_new = int(int_info[1])
                down_new = int(int_info[2])
                self.int_list[int_name]['upload'] = int_info[1]
                self.int_list[int_name]['download'] = int_info[2]
                up_speed = (up_new - up_last) / 1024 / self.time_cost
                down_speed = (down_new - down_last) / 1024 / self.time_cost
                up_speed_format = methods.bytes2human(int(up_speed), 'K')
                down_speed_format = methods.bytes2human(int(down_speed), 'K')
                self.st_upload.SetLabel(f'{up_speed_format}/s')
                self.st_download.SetLabel(f'{down_speed_format}/s')

    def on_choice_change(self, evt):
        int_name = self.int_choice.GetStringSelection()
        start_new_thread(self.set_int_info, (int_name,))

    def set_int_info(self, int_name):
        if self.conn.username == globals.vdi_user:
            res = self.conn.server_recv("ethtool %s | grep -E 'Speed|Port|Link detected'" % int_name)
            res = res.split('\n')[-4:-1]
        else:
            res = self.conn.recv("ethtool %s | grep -E 'Speed|Port|Link detected'" % int_name)
            res = res.split('\n')
        self.st_int_speed.SetLabel(res[0].split(': ')[1])
        port_type = res[1].split(': ')[1].strip()
        if port_type == 'FIBRE':
            port_type = '光'
        elif port_type == 'Twisted Pair':
            port_type = '电'
        else:
            port_type = 'other'
        self.st_int_port.SetLabel(port_type)
        self.st_int_detected.SetLabel(res[2].split(': ')[1])

    def on_close(self, evt):
        self.MONITER_STAT = False
        self.Destroy()
