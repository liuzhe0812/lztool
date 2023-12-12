# -*- coding: utf-8 -*-

__authur__ = 'liuzhe'
__version__ = '4.0'

import logging, wx.grid, sys,os,configparser,wx.grid
from module.widgets.TabContainer import TabContainer
from module import panels,ssh_panel,cloud_panel
from module.myui import *
from webssh import wssh
from module import methods
from module.dialogs import config_dlg
from module.dialogs import file_edit as LOGEDIT


class MyMenuBar(wx.Panel):
    def __init__(self, parent):
        style = (wx.BORDER_NONE)
        super(wx.Panel, self).__init__(parent,style=style)

        self.bitmaps_dir = wx.GetApp().GetBitmapsDir()

        self.parent = parent

        self.SetBackground()
        self.CreateCtrls()
        self.DoLayout()
        self.BindEvents()

    def SetBackground(self):
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.WHITE)

    def CreateCtrls(self):
        self.bt_split = mBitmapButton(self,'bitmaps/split.png','分屏显示')
        self.bt_showlog = mBitmapButton(self,'bitmaps/showlog.png','错误日志')
        self.bt_config = mBitmapButton(self,'bitmaps/config.png','设置')
        self.bt_transfer_menu = mBitmapButton(self,'bitmaps/transfer_menu.png','传输列表')

    def DoLayout(self):
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._tab = TabContainer(self,size=(270,40))
        self._tab.AddImage('bitmaps/multissh2.png','bitmaps/multissh1.png')
        self._tab.AddImage('bitmaps/oevdi2.png','bitmaps/oevdi1.png')
        self._tab.AddImage('bitmaps/tools2.png','bitmaps/tools1.png')
        self._tab.AddPage('SSH',0,0)
        self._tab.AddPage('桌面云',0,1)
        self._tab.AddPage('工具箱',0,2)
        self._tab._nIndex = 0
        mainSizer.Add(self._tab,0,wx.ALIGN_BOTTOM|wx.LEFT,2)
        mainSizer.Add((1,-1),1,wx.EXPAND)

        mainSizer.Add(self.bt_split, 0, wx.LEFT|wx.ALIGN_CENTER, 5)
        mainSizer.Add(self.bt_showlog, 0, wx.ALIGN_CENTER)
        mainSizer.Add(self.bt_config, 0,wx.ALIGN_CENTER)
        mainSizer.Add(self.bt_transfer_menu, 0,wx.ALIGN_CENTER)

        # ------------

        self.SetSizer(mainSizer)
        self.Layout()

    def BindEvents(self):
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        "消除残影"
        dc = wx.BufferedPaintDC(self)
        gcdc = wx.GCDC(dc)
        gcdc.Clear()


class MyMainPnl(wx.Panel):

    def __init__(self, parent, size=wx.DefaultSize):
        style = (wx.NO_BORDER | wx.TAB_TRAVERSAL)
        super(MyMainPnl, self).__init__(parent,
                                        id=-1,
                                        size=size,
                                        style=style)
        self.SetBackgroundColour(globals.bgcolor)
        #主面板
        self.panel_ssh = ssh_panel.ssh_panel(self)
        self.panel_ssh.SetBackgroundColour(globals.bgcolor)
        self.panel_ssh.splitter_left.Hide()

        self.panel_tools = panels.tool_panel(self)
        self.panel_tools.SetBackgroundColour(globals.bgcolor)
        self.panel_tools.Hide()

        self.panel_vdi = cloud_panel.vdi_panel(self)
        self.panel_vdi.SetBackgroundColour(globals.bgcolor)
        self.panel_vdi.Hide()

        self._panels = [self.panel_ssh,self.panel_vdi,self.panel_tools]
        self._sel = 0

        self.SetProperties()
        self.DoLayout()

    def SelectPanel(self,idx):
        if idx == self._sel:
            return
        if idx == -1:
            return
        self.Freeze()
        self._panels[self._sel].Hide()
        self._panels[idx].Show()
        self._sel = idx
        self.Layout()
        self.Thaw()

    def DoLayout(self):
        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        for p in self._panels:
            bSizer1.Add(p, 1, wx.EXPAND)
        self.SetSizer(bSizer1)

    def SetProperties(self):
        self.SetDoubleBuffered(True)

class Myframe(wx.Frame):
    def __init__(self):
        methods.new_thread(wssh.start, ())
        style = (wx.DEFAULT_FRAME_STYLE|wx.CLIP_CHILDREN)
        super(wx.Frame, self).__init__(None,
                                    -1, size=(1024, 720),
                                    title="",
                                    style=style)
        # ------------
        self.SetBackgroundColour('white')
        self.SetIcon(wx.Icon('bitmaps/logo.png'))
        self.opacity_out = 255
        self.deltaN = -70
        self.delta = wx.Point(0, 0)
        self.ssh_menu = SSHPopupWindow(self, wx.SIMPLE_BORDER)

        self.config = wx.GetApp().GetConfig()
        # Return application name.
        self.app_name = wx.GetApp().GetAppName()
        self.SetProperties()

        self.Freeze()
        self.CreateCtrls()
        self.CreateInfoBar()
        self.DoLayout()
        self.BindEvents()
        rect = self.config.get('default','last_rect').split(',')

        if rect[3] !='0':
            self.SetPosition((int(rect[0]),int(rect[1])))
            self.SetSize(int(rect[2]),int(rect[3]))
        else:
            self.CenterOnScreen(wx.BOTH)
        self.Thaw()

        self.init_config()

    def init_config(self):
        globals.timeout = self.config.get('ssh', 'timeout')
        globals.max_thread = int(self.config.get('ssh', 'max_thread'))
        globals.ssh_f_colour = tuple([int(i) for i in self.config.get('ssh', 'f_colour')[1:-1].split(',')])
        globals.ssh_b_colour = tuple([int(i) for i in self.config.get('ssh', 'b_colour')[1:-1].split(',')])
        globals.vdi_root_pwd = self.config.get('oseasy', 'vdi_root_pwd')
        globals.vdi_user = self.config.get('oseasy', 'vdi_user')
        globals.vdi_user_pwd = self.config.get('oseasy', 'vdi_user_pwd')
        globals.vdi_mysql_pwd = self.config.get('oseasy', 'mysql_pwd')
        globals.wssh_port = self.config.get('oseasy', 'wssh_port')

        if not self.config.get('ssh', 'download_path'):
            desktop = methods.get_desktop_path()
            default_download_path = desktop + '\\lztdownload'
            self.config.set('ssh', 'download_path', default_download_path)
            self.config.write(open('config.ini', "r+"))

    def SetProperties(self):
        self.SetTitle(self.app_name)
        self.SetMinSize((600, 400))

    def BindEvents(self):
        self.menubarPnl.bt_showlog.Bind(wx.EVT_BUTTON, self.OnShowLog)
        self.menubarPnl.bt_config.Bind(wx.EVT_BUTTON, self.OnConfig)
        self.menubarPnl._tab.Bind(wx.EVT_LEFT_DOWN, self.OnTabMouseLeftDown)


    def CreateCtrls(self):
        self.menubarPnl = MyMenuBar(self)
        self.mainPnl = MyMainPnl(self)

    def CreateInfoBar(self):
        # 消息弹窗
        self.info = wx.InfoBar(self)

    def DoLayout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        mainSizer.Add(self.menubarPnl, 0, wx.EXPAND, 0)
        mainSizer.Add(self.mainPnl, 1, wx.EXPAND, 0)
        mainSizer.Add(self.info, 0, wx.EXPAND, 0)

        self.SetSizer(mainSizer)
        self.Layout()

    def Message(self, msg, type=0):
        flags = [wx.ICON_NONE, wx.ICON_WARNING, wx.ICON_ERROR]
        self.info.ShowMessage(msg, flags[type])

    def OnTabMouseLeftDown(self,event):
        self.menubarPnl._tab.OnMouseLeftDown(event)
        self.mainPnl.SelectPanel(self.menubarPnl._tab._tabSel)
        event.Skip()

    def OnShowLog(self,evt):
        logframe = LogFrame()
        logframe.Show()

    def OnConfig(self,evt):
        dlg = config_dlg(None, wx.adv.PROPSHEET_LISTBOOK)
        if dlg.ShowModal() == wx.ID_OK:
            globals.max_thread = dlg.max_thread.GetValue()
            globals.timeout = dlg.timeout.GetValue()
            globals.vdi_root_pwd = dlg.vdi_root_pwd.GetValue()
            globals.vdi_user = dlg.vdi_user.GetValue()
            globals.vdi_user_pwd = dlg.vdi_user_pwd.GetValue()
            globals.vdi_mysql_pwd = dlg.mysql_pwd.GetValue()

            self.config.set('ssh', 'max_thread', str(globals.max_thread))
            self.config.set('ssh', 'timeout', str(globals.timeout))
            self.config.set('oseasy', 'vdi_root_pwd', globals.vdi_root_pwd)
            self.config.set('oseasy', 'vdi_user', globals.vdi_user)
            self.config.set('oseasy', 'vdi_user_pwd', globals.vdi_user_pwd)
            self.config.set('oseasy', 'mysql_pwd', globals.vdi_mysql_pwd)
            self.config.set('oseasy', 'wssh_port', globals.wssh_port)
            self.config.write(open('config.ini', "w"))
        dlg.Destroy()


class LogFrame(LOGEDIT):
    def __init__(self):
        LOGEDIT.__init__(self,local_file='error.log',title='错误日志')
        self.Bind(wx.EVT_CLOSE,self.on_close)
        self.SetIcon(wx.Icon("bitmaps/showlog.png"))

        logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.handler = logging.StreamHandler(stream=self.stc)
        self.handler.setLevel(logging.ERROR)
        self.handler.setFormatter(formatter)
        logger.addHandler(self.handler)

        self.display_log()


    def display_log(self):
        with open('error.log', 'r') as file:
            log_contents = file.read()
        self.stc.SetText(log_contents)

    def on_close(self,evt):
        logger.removeHandler(self.handler)
        self.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        self.SetAppName("LZTool v%s"%__version__)
        self.installDir = os.path.split(os.path.abspath(sys.argv[0]))[0]

        frame = Myframe()
        frame.Show(True)
        return True

    # -----------------------------------------------------------------------

    def GetBitmapsDir(self):
        bitmaps_dir = os.path.join(self.installDir, "bitmaps")
        return bitmaps_dir

    def GetConfig(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config


if __name__ == '__main__':
    file_handler1 = logging.FileHandler('info.log')
    file_handler2 = logging.FileHandler('error.log')

    # 创建两个格式化器
    formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter2 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler1.setLevel(logging.INFO)
    file_handler1.setFormatter(formatter1)

    file_handler2.setLevel(logging.ERROR)
    file_handler2.setFormatter(formatter2)

    # 获取root logger并为其添加处理器
    logger = logging.getLogger()
    logger.addHandler(file_handler1)
    logger.addHandler(file_handler2)

    # 设置全局日志级别为INFO，这样只有INFO级别及以上的日志才会被记录
    logger.setLevel(logging.INFO)
    app = MyApp(False)
    app.MainLoop()
