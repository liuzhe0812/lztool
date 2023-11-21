# -*- coding: utf-8 -*-

__authur__ = u'liuzhe'
__version__ = '4.0'

import logging, wx.grid, sys,os,configparser
import wx.grid
import module.widgets.rectshapedbitmapbuttonTwo as SBBTwo
import wx.aui
from module import panels,ssh_panel,cloud_panel
from module.myui import *
from webssh import wssh
from module import methods
from module.dialogs import config_dlg


class MyTitleBar(wx.Control):
    def __init__(self, parent, label):
        style = (wx.BORDER_NONE)
        super(MyTitleBar, self).__init__(parent,
                                         style=style)

        self.bitmaps_dir = wx.GetApp().GetBitmapsDir()

        self.parent = parent
        self.label = label

        self.SetBackground()
        # self.SetProperties(label)
        self.CreateCtrls()
        self.DoLayout()
        self.BindEvents()

    # -----------------------------------------------------------------------

    def SetBackground(self):
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.WHITE)

    def SetProperties(self, label):
        """
        ...
        """

        self.label = label
        self.label_font = self.GetFont()
        self.label_font.SetFamily(wx.SWISS)
        self.label_font.SetWeight(wx.BOLD)
        self.SetFont(self.label_font)

    def CreateCtrls(self):
        # Load an icon bitmap for titlebar.
        icon = wx.Bitmap(os.path.join(self.bitmaps_dir,
                                      "logo.png"),
                         type=wx.BITMAP_TYPE_PNG)

        self.ico = wx.StaticBitmap(self, -1, icon)
        self.ico.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.appname = wx.StaticText(self,label=self.TopLevelParent.app_name)
        self.appname.SetFont(wx.Font(15, 70, 90, 90, False, "微软雅黑"))
        self.appname.SetForegroundColour('grey')

        self.bt_showlog = SBBTwo.ShapedBitmapButton(self, -1,
                                                   bitmap=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                 "showlog.png"),
                                                                    type=wx.BITMAP_TYPE_PNG),

                                                   pressedBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                     "showlog_pressed.png"),
                                                                        type=wx.BITMAP_TYPE_PNG),
                                                   label="",
                                                   labelForeColour=wx.WHITE,
                                                   labelFont=wx.Font(9,
                                                                     wx.FONTFAMILY_DEFAULT,
                                                                     wx.FONTSTYLE_NORMAL,
                                                                     wx.FONTWEIGHT_BOLD),
                                                   style=wx.BORDER_NONE)

        self.bt_config = SBBTwo.ShapedBitmapButton(self, -1,
                                              bitmap=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                            "config.png"),
                                                               type=wx.BITMAP_TYPE_PNG),

                                              pressedBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                "config_pressed.png"),
                                                                   type=wx.BITMAP_TYPE_PNG),
                                              label="",
                                              labelForeColour=wx.WHITE,
                                              labelFont=wx.Font(9,
                                                                wx.FONTFAMILY_DEFAULT,
                                                                wx.FONTSTYLE_NORMAL,
                                                                wx.FONTWEIGHT_BOLD),
                                              style=wx.BORDER_NONE)

        self.btn3 = SBBTwo.ShapedBitmapButton(self, -1,
                                              bitmap=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                            "btn_gloss_exit_normal_1.png"),
                                                               type=wx.BITMAP_TYPE_PNG),

                                              pressedBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                "btn_gloss_exit_selected_1.png"),
                                                                   type=wx.BITMAP_TYPE_PNG),

                                              hoverBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                              "btn_gloss_exit_normal_1.png"),
                                                                 type=wx.BITMAP_TYPE_PNG),

                                              disabledBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                 "btn_gloss_exit_normal_1.png"),
                                                                    type=wx.BITMAP_TYPE_PNG),

                                              label="",
                                              labelForeColour=wx.WHITE,
                                              labelFont=wx.Font(9,
                                                                wx.FONTFAMILY_DEFAULT,
                                                                wx.FONTSTYLE_NORMAL,
                                                                wx.FONTWEIGHT_BOLD),
                                              style=wx.BORDER_NONE)

        self.btn4 = SBBTwo.ShapedBitmapButton(self, -1,
                                              bitmap=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                            "btn_gloss_maximize_normal_1.png"),
                                                               type=wx.BITMAP_TYPE_PNG),

                                              pressedBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                "btn_gloss_maximize_selected_1.png"),
                                                                   type=wx.BITMAP_TYPE_PNG),

                                              hoverBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                              "btn_gloss_maximize_normal_1.png"),
                                                                 type=wx.BITMAP_TYPE_PNG),

                                              disabledBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                 "btn_gloss_maximize_normal_1.png"),
                                                                    type=wx.BITMAP_TYPE_PNG),

                                              label="",
                                              labelForeColour=wx.WHITE,
                                              labelFont=wx.Font(9,
                                                                wx.FONTFAMILY_DEFAULT,
                                                                wx.FONTSTYLE_NORMAL,
                                                                wx.FONTWEIGHT_BOLD),
                                              style=wx.BORDER_NONE)

        self.btn5 = SBBTwo.ShapedBitmapButton(self, -1,
                                              bitmap=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                            "btn_gloss_reduce_normal_1.png"),
                                                               type=wx.BITMAP_TYPE_PNG),

                                              pressedBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                "btn_gloss_reduce_selected_1.png"),
                                                                   type=wx.BITMAP_TYPE_PNG),

                                              hoverBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                              "btn_gloss_reduce_normal_1.png"),
                                                                 type=wx.BITMAP_TYPE_PNG),

                                              disabledBmp=wx.Bitmap(os.path.join(self.bitmaps_dir,
                                                                                 "btn_gloss_reduce_normal_1.png"),
                                                                    type=wx.BITMAP_TYPE_PNG),

                                              label="",
                                              labelForeColour=wx.WHITE,
                                              labelFont=wx.Font(9,
                                                                wx.FONTFAMILY_DEFAULT,
                                                                wx.FONTSTYLE_NORMAL,
                                                                wx.FONTWEIGHT_BOLD),
                                              style=wx.BORDER_NONE)

    def DoLayout(self):
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        # ------------

        mainSizer.Add(self.ico, 0, wx.LEFT|wx.TOP , 4)
        mainSizer.Add(self.appname, 0, wx.LEFT|wx.TOP , 4)

        self._tab = TabContainer(self,size=(270,40))
        self._tab.AddImage('bitmaps/multissh2.png','bitmaps/multissh1.png')
        self._tab.AddImage('bitmaps/oevdi2.png','bitmaps/oevdi1.png')
        self._tab.AddImage('bitmaps/tools2.png','bitmaps/tools1.png')
        self._tab.AddPage('SSH',0,0)
        self._tab.AddPage('桌面云',0,1)
        self._tab.AddPage('工具箱',0,2)
        self._tab._nIndex = 0
        mainSizer.Add(self._tab,0,wx.EXPAND|wx.LEFT,10)


        mainSizer.Add((0, 0), 1)
        mainSizer.Add(self.bt_showlog, 0, wx.RIGHT, 4)
        mainSizer.Add(self.bt_config, 0, wx.RIGHT, 4)
        mainSizer.Add(self.btn5, 0, wx.RIGHT, 4)
        mainSizer.Add(self.btn4, 0, wx.RIGHT, 4)
        mainSizer.Add(self.btn3, 0, wx.RIGHT, 4)

        # ------------

        self.SetSizer(mainSizer)
        self.Layout()

    def BindEvents(self):
        # self.ico.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        # self.ico.Bind(wx.EVT_LEFT_DOWN, self.OnRightDown)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDLeft)

        self.btn3.Bind(wx.EVT_BUTTON, self.OnBtnClose)
        self.btn4.Bind(wx.EVT_BUTTON, self.OnFullScreen)
        self.btn5.Bind(wx.EVT_BUTTON, self.OnIconfiy)

    def OnDLeft(self,evt):
        self.OnFullScreen(None)

    def OnLeftDown(self, event):
        self.GetTopLevelParent().OnLeftDown(event)

    def OnLeftUp(self, event):
        self.GetTopLevelParent().OnLeftUp(event)

    def DoGetBestSize(self):
        """
        ...
        """

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())

        textWidth, textHeight = dc.GetTextExtent(self.label)
        spacing = 10
        totalWidth = textWidth + (spacing)
        totalHeight = textHeight + (spacing)

        best = wx.Size(totalWidth, totalHeight)
        self.CacheBestSize(best)

        return best

    def GetLabel(self):
        """
        ...
        """

        return self.label

    def GetLabelColor(self):
        """
        ...
        """

        return self.foreground

    def GetLabelSize(self):
        """
        ...
        """

        return self.size

    def SetLabelColour(self, colour):
        """
        ...
        """

        self.labelColour = colour

    def OnPaint(self, event):
        """
        ...
        """
        dc = wx.BufferedPaintDC(self)
        gcdc = wx.GCDC(dc)
        gcdc.Clear()

        # Get the working size we can draw in.
        # width, height = self.GetSize()

        # Use the GCDC to draw the text.
        # brush = wx.WHITE
        # gcdc.SetPen(wx.Pen(brush, 1))
        # gcdc.SetBrush(wx.Brush(brush))
        # gcdc.DrawRectangle(0, 0, width, height)

        # # Get the system font.
        # gcdc.SetFont(self.GetFont())
        #
        # textWidth, textHeight = gcdc.GetTextExtent(self.label)
        # tposx, tposy = ((width / 2) - (textWidth / 2), (height / 3) - (textHeight / 3))#居中
        #
        # # Set position and text color.
        # if tposx <= 100:
        #     gcdc.SetTextForeground("white")
        #     gcdc.DrawText("", int(tposx), int(tposy + 1))
        #
        #     gcdc.SetTextForeground(self.labelColour)
        #     gcdc.DrawText("", int(tposx), int(tposy))
        #
        # else:
        #     gcdc.SetTextForeground("white")
        #     gcdc.DrawText(self.label, int(tposx), int(tposy + 1))
        #
        #     gcdc.SetTextForeground(self.labelColour)
        #     gcdc.DrawText(self.label, int(tposx), int(tposy))

    def OnIconfiy(self, event):
        """
        ...
        """

        self.GetTopLevelParent().OnIconfiy(self)

    def OnFullScreen(self, event):
        """
        ...
        """

        self.GetTopLevelParent().OnFullScreen(self)

    def OnBtnClose(self, event):
        self.GetTopLevelParent().OnCloseWindow(self)

class MyTitleBarPnl(wx.Panel):
    """
    Thanks to Cody Precord.
    """

    def __init__(self, parent, id=-1, size=(-1,40)):
        style = (wx.NO_BORDER)
        super(MyTitleBarPnl, self).__init__(parent,
                                            id=-1,
                                            size=size,
                                            style=style)

        self.parent = parent

        self.config = wx.GetApp().GetConfig()
        self.app_name = wx.GetApp().GetAppName()
        self.bitmaps_dir = wx.GetApp().GetBitmapsDir()

        self.SetProperties()
        self.CreateCtrls()
        self.BindEvents()

    # -----------------------------------------------------------------------

    def SetProperties(self):
        self.SetBackgroundColour('white')

    def CreateCtrls(self):
        w, h = self.GetClientSize()

        self.titleBar = MyTitleBar(self,
                                   label=self.app_name)
        self.titleBar.SetPosition((0, 0))
        self.titleBar.SetSize((w, 24))
        self.titleBar.SetLabelColour("grey")

        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(self.titleBar, 1, wx.EXPAND)
        self.SetSizer(bsizer)

    def BindEvents(self):
        self.Bind(wx.EVT_SIZE, self.OnResize)

    def OnResize(self, event):
        w, h = self.GetClientSize()
        self.titleBar.SetSize((w, 24))
        self.Refresh()
        self.Layout()

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
        self.panel_ssh.panel11.Show()
        self.panel_ssh.panel12.Hide()

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
        self.Centre(wx.BOTH)

    def SetProperties(self):
        if wx.Platform == "__WXMSW__":
            self.SetDoubleBuffered(True)

class Myframe(wx.Frame):
    def __init__(self):
        methods.new_thread(wssh.start, ())
        style = (wx.CLIP_CHILDREN | wx.CLOSE_BOX |
                 wx.MINIMIZE_BOX | wx.SYSTEM_MENU |
                 wx.RESIZE_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE)
        super(wx.Frame, self).__init__(None,
                                    -1, size=(1024, 720),
                                    title="",
                                    style=style)
        # ------------

        self.SetBackgroundColour('white')
        self.opacity_out = 255
        self.deltaN = -70
        self.delta = wx.Point(0, 0)

        self.config = wx.GetApp().GetConfig()
        # Return application name.
        self.app_name = wx.GetApp().GetAppName()
        self.SetProperties()

        self.Freeze()
        self.CreateCtrls()
        self.CreateStatus()
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
        self.SetMinSize((258, 58))

    def BindEvents(self):
        self.titleBarPnl.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.titleBarPnl.titleBar.bt_showlog.Bind(wx.EVT_BUTTON, self.OnShowLog)
        self.titleBarPnl.titleBar.bt_config.Bind(wx.EVT_BUTTON, self.OnConfig)
        self.titleBarPnl.titleBar._tab.Bind(wx.EVT_LEFT_DOWN, self.OnTabMouseLeftDown)

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def AlphaCycle(self, *args):
        """
        关闭窗口淡出效果
        """

        self.opacity_out += self.deltaN
        if self.opacity_out >= 255:
            self.deltaN = -self.deltaN
            self.opacity_out = 255

        if self.opacity_out <= 0:
            self.deltaN = -self.deltaN
            self.opacity_out = 0

            self.timer_out.Stop()
            wx.CallAfter(self.Destroy)
            wx.Exit()

        self.SetTransparent(self.opacity_out)

    def CreateCtrls(self):
        self.titleBarPnl = MyTitleBarPnl(self)
        self.titleBarPnl.SetPosition((0, 0))
        self.mainPnl = MyMainPnl(self)

    def CreateStatus(self):
        # 消息弹窗
        self.info = wx.InfoBar(self)

    def DoLayout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        mainSizer.Add(self.titleBarPnl, 0, wx.EXPAND, 0)
        mainSizer.Add(self.mainPnl, 1, wx.EXPAND, 0)
        mainSizer.Add(self.info, 0, wx.EXPAND, 0)

        self.SetSizer(mainSizer)
        self.Layout()

    def Message(self, msg, tyep=0):
        flags = [wx.ICON_NONE, wx.ICON_WARNING, wx.ICON_ERROR]
        self.info.ShowMessage(msg, flags[0])

    def OnTabMouseLeftDown(self,event):
        self.titleBarPnl.titleBar._tab.OnMouseLeftDown(event)
        self.mainPnl.SelectPanel(self.titleBarPnl.titleBar._tab._tabSel)
        event.Skip()

    def OnLeftDown(self, event):
        self.CaptureMouse()
        x, y = self.ClientToScreen(event.GetPosition())
        originx, originy = self.GetPosition()
        dx = x - originx
        dy = y - originy
        self.delta = ((dx, dy))

    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMouseMove(self, event):
        """
        ...
        """

        if event.Dragging() and event.LeftIsDown():
            x, y = self.ClientToScreen(event.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            # self.Freeze()
            self.Move(fp)
            # self.Thaw()

    def OnCloseWindow(self, event):
        pos = self.GetPosition()
        size = self.GetSize()
        val =  str(pos[0])+','+str(pos[1])+','+str(size[0])+','+str(size[1])
        self.config.set('default', 'last_rect',val)
        self.config.write(open('config.ini', "r+"))
        self.Destroy()

    def OnFullScreen(self, event):
        self.ShowFullScreen(not self.IsFullScreen(),
                            wx.FULLSCREEN_NOCAPTION)

    def OnIconfiy(self, event):
        self.Iconize()

    def OnShowLog(self,evt):
        # os.startfile('error.log')
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

from module.dialogs import file_edit as LOGEDIT

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
