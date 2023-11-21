# -*- coding: utf-8 -*-
import wx.grid, wx.aui, wx.stc as stc,time
import wx.lib.mixins.listctrl as listmix
import wx.lib.agw.ultimatelistctrl as ULC
import wx.lib.platebtn as platebtn
import wx.lib.agw.hypertreelist as HTL
import wx.lib.agw.labelbook as LB
import wx.lib.gizmos as gizmos
import wx.lib.buttons as buttons
from sys import maxsize
from os import startfile
from module import globals
from module.methods import getLabelFromEVT, get_download_path
from wx.lib.agw.artmanager import ArtManager
from wx.lib.agw.fmresources import *


class mButton(wx.Button):
    def __init__(self, parent, label=u'Button', color=None, size=(-1, -1), id=wx.ID_ANY, font_size=None,
                 font_color='white'):
        wx.Button.__init__(self, parent=parent, id=id, label=label, style=wx.NO_BORDER, size=size)
        self.selected = 0
        self.colorname = color
        self.SetColor(color)
        if font_size:
            self.SetFont(wx.Font(font_size, 70, 90, 92, False, u"微软雅黑"))
        else:
            self.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, u"微软雅黑"))

        self.SetForegroundColour(font_color)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.Bind(wx.EVT_SET_FOCUS, self.on_enter)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_leave)

        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def SetColor(self, color=None):
        if color:
            self.colorname = color
        if self.colorname == 'green':
            self.color = '#1abc9c'
            self.focusColor = '#2ecc71'
        elif self.colorname == 'red':
            self.color = wx.Colour(237, 115, 104)
            self.focusColor = wx.Colour(247, 125, 114)
        elif self.colorname == 'blue':
            self.color = '#2980b9'
            self.focusColor = '#3498db'
        elif self.colorname == 'yellow':
            self.color = '#f39c12'
            self.focusColor = '#f1c40f'
        elif self.colorname == 'purple':
            self.color = '#8e44ad'
            self.focusColor = '#9b59b6'
        elif self.colorname == 'deepgreen':
            self.color = '#16a085'
            self.focusColor = '#1abc9c'
        elif self.colorname == 'grey':
            self.color = '#bdc3c7'
            self.focusColor = '#ecf0f1'
        elif self.colorname == 'pink':
            self.color = '#d770ad'
            self.focusColor = '#ec87c0'
        elif self.colorname == 'deepgrey':
            self.color = '#7f8c8d'
            self.focusColor = '#95a5a6'
        elif self.colorname == 'deepyellow':
            self.color = '#d35400'
            self.focusColor = '#e67e22'
        elif self.colorname == 'deepblue':
            self.color = wx.Colour(63, 82, 103)
            self.focusColor = wx.Colour(83, 102, 123)
        elif self.colorname == 'white':
            self.color = wx.Colour(255, 255, 255)
            self.focusColor = wx.Colour(globals.bgcolor)
        else:
            self.color = self.colorname
            a = self.colorname[0] - 20
            if a < 0:
                a = 0
            b = self.colorname[1] - 20
            if b < 0:
                b = 0
            c = self.colorname[2] - 20
            if c < 0:
                c = 0
            self.focusColor = wx.Colour(a, b, c)
        self.SetBackgroundColour(self.color)

    def on_enter(self, evt):
        if not self.selected:
            self.SetBackgroundColour(self.focusColor)

    def on_leave(self, evt):
        if not self.selected:
            self.SetBackgroundColour(self.color)

    def setBmp(self, bmpPath, margins=(2, 2)):
        bmp = wx.Image(bmpPath, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.SetBitmap(bmp)
        self.SetBitmapMargins(margins)


class mFocusButton(wx.Button):
    def __init__(self, parent, label=None, size=(-1, -1), bitmap=None, bg_colour=None):
        wx.Button.__init__(self, parent=parent, id=wx.ID_ANY, label=label, style=wx.NO_BORDER | wx.TEXT_ALIGNMENT_LEFT,
                           size=size)

        self.parent = parent
        if bg_colour:
            self.bg_colour = bg_colour
        else:
            self.bg_colour = 'white'
        self.SetBackgroundColour(bg_colour)
        self.focus = False
        self.SetSize(self.GetBestSize())
        self.Bind(wx.EVT_SET_FOCUS, self.get_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.lose_focus)
        self.Bind(wx.EVT_ENTER_WINDOW, self.enter_window)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.leave_window)
        if bitmap:
            bmp = wx.Image(bitmap, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
            self.SetBitmap(bmp, wx.LEFT)
            self.SetBitmapMargins((2, 2))  # default is 4 but that seems too big to me.

    def SetPopupMenu(self, menu_txt=[], method=None):
        self.menu_txt = menu_txt
        self.method = method
        self.Bind(wx.EVT_RIGHT_DOWN, self.creaPopupMenu)

    def creaPopupMenu(self, evt):
        self.parent.Parent.Parent.Parent.cmd_on_sel = self.GetLabel()
        menu = wx.Menu()
        for text in self.menu_txt:
            item = menu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.method, item)
        self.PopupMenu(menu)

    def get_focus(self, evt):
        self.focus = True
        self.SetBackgroundColour(wx.Colour(225, 225, 225))

    def lose_focus(self, evt):
        self.focus = False
        self.SetBackgroundColour(self.bg_colour)

    def enter_window(self, evt):
        if not self.focus:
            self.SetBackgroundColour(wx.Colour(225, 225, 225))

    def leave_window(self, evt):
        if not self.focus:
            self.SetBackgroundColour(self.bg_colour)


class mPlateBtn(platebtn.PlateButton):
    def __init__(self, parent, label="", imagePath=None, color=None, font=None, gradient=True, toggle=False, menu=None):
        style = platebtn.PB_STYLE_DEFAULT
        if gradient:
            style = style | platebtn.PB_STYLE_GRADIENT
        if toggle:
            style = style | platebtn.PB_STYLE_TOGGLE

        if gradient:
            platebtn.PlateButton.__init__(self, parent=parent, id=wx.ID_ANY, label=label, style=style)
        else:
            platebtn.PlateButton.__init__(self, parent=parent, id=wx.ID_ANY, label=label, style=style)
        if imagePath:
            bmp = wx.Image(imagePath, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
            self.SetBitmap(bmp)
        if color:
            self.SetPressColor(color)
        if font:
            self.SetFont(font)
        if menu:
            mMenu = wx.Menu()
            for s in menu:
                mMenu.Append(wx.ID_ANY, s)
            self.SetMenu(mMenu)

    def setMenuEvent(self, method):
        self.Bind(wx.EVT_MENU, method)


class mButtonSimple(wx.Button):
    def __init__(self, parent, label="", b_color=None, size=(-1, -1), id=wx.ID_ANY, font=(10, True),
                 f_color=(44, 151, 250)):
        wx.Button.__init__(self, parent=parent, id=id, label=label, style=wx.NO_BORDER, size=size)
        self.f_color = f_color
        self.SetForegroundColour(self.f_color)
        self.SetBackgroundColour(b_color)
        if font[1]:
            self.SetFont(wx.Font(font[0], 70, 90, 92, False, u"微软雅黑"))
        else:
            self.SetFont(wx.Font(font[0], 70, 90, 90, False, u"微软雅黑"))

        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def on_enter(self, evt):
        fc = self.GetForegroundColour()
        self.SetForegroundColour((fc[0] - 20, fc[1] - 20, fc[2] - 20))

    def on_leave(self, evt):
        self.SetForegroundColour(self.f_color)


class mBitmapButton(buttons.GenBitmapButton):
    def __init__(self, parent, bmp_path, tooltip=''):
        bmp = wx.Bitmap(bmp_path, wx.BITMAP_TYPE_PNG)
        buttons.GenBitmapButton.__init__(self, parent, -1, bmp, style=wx.NO_BORDER)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetToolTip(tooltip)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))


class mRadio(wx.BoxSizer):
    def __init__(self, parent=None, label_list=None, bgcolor=None, size=(-1, -1), font_size=12, method=None):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.focus = None
        self.radios = []
        self.method = method
        self.firstSet = True
        num = len(label_list)
        for i in range(num):
            radio = wx.RadioButton(parent, i, label_list[i], size=size)
            radio.Bind(wx.EVT_RADIOBUTTON, self.on_select)
            radio.SetFont(wx.Font(font_size, 70, 90, 92, False, u"微软雅黑"))
            if bgcolor:
                radio.SetBackgroundColour(bgcolor)
            self.Add(radio, 1, wx.ALIGN_CENTER)
            self.radios.append(radio)

    def setFoces(self, index):
        self.radios[index].SetFocus()
        self.firstSet = False

    def on_select(self, evt):
        obj = evt.GetEventObject()
        self.focus = obj.GetLabel()
        if self.method:
            if not self.firstSet:
                self.method(None)


class mListCtrl(wx.ListCtrl, listmix.TextEditMixin, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, colnames=None, size=(-1, -1), border=False, editable=False,
                 method=None, popupmemu=[]):
        if border:
            wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT, size=size)
        else:
            wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.NO_BORDER, size=size)
        if editable:
            listmix.TextEditMixin.__init__(self)
        self.item = None  # 当前选中

        listmix.ListCtrlAutoWidthMixin.__init__(self)

        for i in range(len(colnames)):
            self.InsertColumn(i, colnames[i])
        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.on_focus)

        if method:
            self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.SetPopupMenu)
            self.method = method
            self.popupmenu_text = popupmemu

    def on_focus(self, evt):
        # self.focus = evt.GetText()
        self.item = self.GetFocusedItem()

    def getItemData(self, col):
        return self.GetItemText(self.item, col)

    def addRow(self, item, color=None):
        i = self.GetItemCount()
        try:
            id = self.InsertItem(i, str(item[0]))
        except:
            id = self.InsertItem(i, item[0])
        num = len(item)
        for i in range(num):
            if i > 0:
                try:
                    self.SetItem(id, i, item[i])
                except:
                    self.SetItem(id, i, str(item[i]))
        if color:
            self.SetItemTextColour(id, color)

    def SetPopupMenu(self, evt):
        self.popupmenu = wx.Menu()
        for text in self.popupmenu_text:
            item = self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.method, item)
        self.PopupMenu(self.popupmenu)

    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(self.popupmenu, pos)



class mHyperTreeList(HTL.HyperTreeList):
    def __init__(self, parent, cols=None,
                 agwStyle=HTL.TR_AUTO_CHECK_CHILD | HTL.TR_AUTO_CHECK_PARENT | wx.TR_HAS_VARIABLE_ROW_HEIGHT):
        HTL.HyperTreeList.__init__(self, parent, id=wx.ID_ANY, agwStyle=agwStyle)

        self.root = None
        self.EnableSelectionVista(True)
        for col in cols:
            self.AddColumn(col)

    def addItem(self, item, father=None):
        if not father:
            father = self.root

        child = self.AppendItem(father, item[0])
        i = 1
        for it in item[1:]:
            if isinstance(it, str):
                self.SetItemText(child, it, i)
            else:
                self.SetItemWindow(child, it, i)
            i += 1
        return child

    def setColumnWidth(self, width=[]):
        i = 0
        for w in width:
            self.SetColumnWidth(i, w)
            i += 1

    def setImageList(self, bmp_list):
        il = wx.ImageList(16, 16)
        for bmp in bmp_list:
            il.Add(bmp)
        self.AssignImageList(il)

    def OnItemExpanded(self, event):

        item = event.GetItem()
        if item:
            print("OnItemExpanded: %s\n" % self.GetItemText(item))

    def OnItemExpanding(self, event):

        item = event.GetItem()
        if item:
            print("OnItemExpanding: %s\n" % self.GetItemText(item))

        event.Skip()

    def OnItemCollapsed(self, event):

        item = event.GetItem()
        if item:
            print("OnItemCollapsed: %s" % self.GetItemText(item))


class mStatusBar(wx.BoxSizer):
    def __init__(self, parent=None):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

        self.panel = wx.Panel(parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.gauge = wx.Gauge(self.panel, wx.ID_ANY, 100, wx.DefaultPosition, (-1, -1), wx.NO_BORDER)
        self.init_gauge()

        self.stat1 = wx.StaticText(self.panel, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,
                                   0 | wx.NO_BORDER)
        self.stat1.SetFont(wx.Font(12, 70, 90, 90, False, u"微软雅黑"))

        self.stat2 = wx.StaticText(self.panel, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,
                                   0 | wx.NO_BORDER)
        self.stat2.SetFont(wx.Font(12, 70, 90, 90, False, u"微软雅黑"))

        bSizer1.Add(self.stat1, 1, wx.EXPAND, 5)
        bSizer1.Add(self.stat2, 0, wx.EXPAND, 5)
        bSizer1.Add(self.gauge, 0, wx.ALIGN_CENTER, 5)

        self.panel.SetSizer(bSizer1)
        self.panel.Layout()
        bSizer1.Fit(self.panel)
        self.Add(self.panel, 1, wx.EXPAND, 5)

    def SetStatusText(self, label, n=1):
        if n == 1:
            self.stat1.SetLabel(label)
        if n == 2:
            self.stat2.SetLabel(label)
        self.Layout()

    def init_gauge(self):
        self.gauge.SetValue(0)
        self.gauge.Hide()
        self.panel.Layout()

    def show_gauge(self):
        self.gauge.Show()
        self.panel.Layout()


class mInput(wx.BoxSizer):
    def __init__(self, parent=None, id=wx.ID_ANY, st_label=u'', tc_label=u'', st_size=(-1, -1), tc_size=(-1, -1),
                 font_size=12, color='#95a5a6', password=False):
        if not font_size:
            font_size = wx.NORMAL_FONT.GetPointSize()
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.st = wx.StaticText(parent, id, st_label, size=st_size, style=wx.NO_BORDER | wx.ALIGN_CENTER)
        self.st.SetBackgroundColour(color)
        self.st.SetForegroundColour('#ffffff')
        self.st.SetFont(wx.Font(font_size, 70, 90, 92, False, u"微软雅黑"))
        if not password:
            self.tc = wx.TextCtrl(parent, id, size=tc_size, style=wx.NO_BORDER)
        else:
            self.tc = wx.TextCtrl(parent, id, size=tc_size, style=wx.NO_BORDER | wx.TE_PASSWORD)
        self.tc.SetFont(wx.Font(10, 70, 90, 90, False, u"微软雅黑"))
        self.tc.SetLabel(tc_label)
        self.tc.SetBackgroundColour('white')
        self.Add(self.st, 0)
        self.Add(self.tc, 1, wx.EXPAND, 0)

    def GetValue(self):
        return self.tc.GetValue()

    def SetValue(self, val):
        self.tc.SetValue(val)

    def Hide(self):
        self.st.Hide()
        self.tc.Hide()

    def Show(self):
        self.st.Show()
        self.tc.Show()


class mChoice(wx.BoxSizer):
    def __init__(self, parent=None, id=wx.ID_ANY, st_label=u'', choice=None, st_size=(-1, -1),
                 font_size=12, color='#95a5a6'):
        if not font_size:
            font_size = wx.NORMAL_FONT.GetPointSize()
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.st = wx.StaticText(parent, id, st_label, size=st_size, style=wx.NO_BORDER | wx.ALIGN_CENTER)
        self.st.SetBackgroundColour(color)
        self.st.SetForegroundColour('#ffffff')
        self.st.SetFont(wx.Font(font_size, 70, 90, 92, False, u"微软雅黑"))

        self.choice = wx.Choice(parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice, wx.NO_BORDER)
        self.choice.SetSelection(0)

        self.Add(self.st, 0, wx.EXPAND)
        self.Add(self.choice, 1, wx.EXPAND, 0)

    def GetStringSelection(self):
        return self.choice.GetStringSelection()

    def SetStringSelection(self, label):
        self.choice.SetStringSelection(label)

    def Disable(self):
        self.choice.Disable()

    def Enable(self):
        self.choice.Enable()

    def Hide(self):
        self.st.Hide()
        self.choice.Hide()


class mStaticBox(wx.BoxSizer):
    def __init__(self, parent, label=u''):
        wx.BoxSizer.__init__(self, wx.VERTICAL)

        self.title = wx.StaticText(parent, -1, label, style=wx.ALIGN_CENTER)
        self.title.SetFont(wx.Font(12, 70, 90, 92, False, u"微软雅黑"))
        self.title.SetForegroundColour((44, 94, 250))
        # self.title.SetBackgroundColour(parent.GetBackgroundColour())
        self.Add(self.title, 0)

        line = wx.StaticLine(parent)
        self.Add(line, 0, wx.EXPAND)


class mPanel(wx.Panel):
    def __init__(self, parent=None, label=u''):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.title = wx.StaticText(self, -1, label, style=wx.ALIGN_CENTER)
        self.title.SetFont(wx.Font(12, 70, 90, 92, False, u"微软雅黑"))
        self.title.SetForegroundColour(wx.Colour(255, 255, 255))
        self.title.SetBackgroundColour('#2980b9')
        self.sizer.Add(self.title, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Add = self.sizer.Add


class mWarnDlg(wx.Dialog):
    def __init__(self, label):
        wx.Dialog.__init__(self, None, id=wx.ID_ANY)

        self.SetBackgroundColour('white')

        bSizer8 = wx.BoxSizer(wx.VERTICAL)

        bSizer9 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, label, style=wx.NO_BORDER)
        self.m_staticText2.SetFont(wx.Font(12, 70, 90, 92, False, u"微软雅黑"))

        bSizer9.Add(self.m_staticText2, 1, wx.ALIGN_CENTER | wx.TOP, 10)

        bSizer8.Add(bSizer9, 1, wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP, 5)

        bSizer8.Add((0, 0), 0, wx.EXPAND, 5)

        bSizer10 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer10.Add((0, 0), 1, wx.EXPAND, 5)

        self.bt_yes = mButton(self, id=wx.ID_OK, label=u'是', color='deepgreen')

        bSizer10.Add(self.bt_yes, 0, wx.ALL, 5)

        self.bt_no = mButton(self, id=wx.ID_CANCEL, label=u'否', color='red')

        bSizer10.Add(self.bt_no, 0, wx.ALL, 5)

        bSizer10.Add((0, 0), 1, wx.EXPAND, 5)

        bSizer8.Add(bSizer10, 0, wx.EXPAND | wx.TOP, 20)

        self.SetSizer(bSizer8)
        self.SetSize(self.GetBestSize() + (50, 0))
        self.Layout()

        self.Centre(wx.BOTH)


class mMessageBox(wx.Dialog):
    def __init__(self, label, parent=None):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY)

        self.SetBackgroundColour(wx.Colour(255, 255, 255, 0))

        bSizer8 = wx.BoxSizer(wx.VERTICAL)

        bSizer9 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, label, style=wx.NO_BORDER)
        self.m_staticText2.SetFont(wx.Font(14, 70, 90, 92, False, u"微软雅黑"))

        bSizer9.Add(self.m_staticText2, 1, wx.ALIGN_CENTER | wx.TOP, 10)

        bSizer8.Add(bSizer9, 1, wx.ALIGN_CENTER | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP, 5)

        bSizer8.Add((0, 0), 0, wx.EXPAND, 5)

        bSizer10 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer10.Add((0, 0), 1, wx.EXPAND, 5)

        bSizer10.Add((0, 0), 1, wx.EXPAND, 5)

        bSizer8.Add(bSizer10, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer8)
        self.SetSize(self.GetBestSize() + (50, 20))
        self.Layout()

        self.Centre(wx.BOTH)
        try:
            self.ShowModal()
        except:
            pass
        self.Destroy()


class moveable():
    def __init__(self, parent, widget, son=0):
        self.d = {}
        self.parent = parent
        self.son = son
        widget.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        widget.Bind(wx.EVT_MOTION, self.MouseMove)
        widget.Bind(wx.EVT_LEFT_UP, self.MouseUp)

    def MouseDown(self, e):
        o = e.GetEventObject()
        if self.son:
            for i in range(self.son):
                o = o.GetParent()
        sx, sy = self.parent.ScreenToClient(o.GetPositionTuple())
        dx, dy = self.parent.ScreenToClient(wx.GetMousePosition())
        o._x, o._y = (sx - dx, sy - dy)
        self.d['d'] = o

    def MouseMove(self, e):
        try:
            if 'd' in self.d:
                o = self.d['d']
                x, y = wx.GetMousePosition()
                o.SetPosition(wx.Point(x + o._x, y + o._y))
        except:
            pass

    def MouseUp(self, e):
        try:
            if 'd' in self.d: del self.d['d']
        except:
            pass


class moveTask():
    def __init__(self, widget, distance, speed=5, horizontal=True, back=False, layout=None):
        self.layout = layout
        self.back = back
        self.distance = distance
        self.horizontal = horizontal
        self.speed = speed
        self.widget = widget
        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(10)
        self.n = 0

    def OnTimer(self, evt):
        if self.speed == 0:
            if self.back:
                self.distance = 0 - self.distance
            pos = self.widget.GetPosition()
            if self.horizontal:
                pos = (pos.x + self.distance, pos.y)
            else:
                pos = (pos.x, pos.y + self.distance)
            self.widget.Move(pos)
            self.timer.Stop()
        else:
            if self.n < self.distance:
                if self.n + self.speed > self.distance:
                    self.speed = self.distance - self.n
                self.n += self.speed
                pos = self.widget.GetPosition()
                if self.back:
                    speed = 0 - self.speed
                else:
                    speed = self.speed
                if self.horizontal:
                    pos = (pos.x + speed, pos.y)
                else:
                    pos = (pos.x, pos.y + speed)
                self.widget.Move(pos)
            else:
                self.timer.Stop()
                if self.layout:
                    self.layout.Layout()


class mFlatLabelBook(LB.FlatImageBook):
    def __init__(self, parent, labels=dict, panels=dict, images=list, style=16384):
        LB.FlatImageBook.__init__(self, parent, wx.ID_ANY, agwStyle=style)

        imagelist = wx.ImageList(32, 32)
        for img in images:
            newImg = 'bitmaps/%s' % img
            bmp = wx.Bitmap(newImg, wx.BITMAP_TYPE_PNG)
            imagelist.Add(bmp)

        self.AssignImageList(imagelist)

        i = 0
        for label in labels:
            self.AddPage(panels[i], label, True, i)
            i += 1
        self.SetSelection(0)


class mLabelBook(LB.LabelBook):
    def __init__(self, parent, labels=None, panels=None, images=None):
        imagelist = wx.ImageList(24, 24)
        if images:
            LB.LabelBook.__init__(self, parent, wx.ID_ANY, agwStyle=128 | 2)
            for img in images:
                newImg = 'bitmaps/%s' % img
                bmp = wx.Bitmap(newImg, wx.BITMAP_TYPE_PNG)
                imagelist.Add(bmp)
        else:
            LB.LabelBook.__init__(self, parent, wx.ID_ANY, agwStyle=128 | 2 | 32)
        self.AssignImageList(imagelist)

        i = 0
        for label in labels:
            self.AddPage(panels[i], label, True, i)
            i += 1
        self.SetSelection(0)

        self.SetUserColours()
        self.SetFontSizeMultiple(1.2)
        self.SetFontBold(False)

    def SetUserColours(self, bg='white', bg_selected=globals.bgcolor, border='white', txt='black',
                       txt_selectet='black'):
        self.SetColour(100, bg)  # 背景
        self.SetColour(101, bg_selected)  # 选中背景
        self.SetColour(102, border)  # 边框
        self.SetColour(103, txt)  # 文字
        self.SetColour(104, txt_selectet)  # 选中文字


class switch(wx.Button):
    def __init__(self, parent, key=False):
        super(switch, self).__init__(parent,
                                     size=(50, 21),
                                     style=wx.NO_BORDER)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.key = key
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def OnPaint(self, event):
        self.dc = wx.PaintDC(self)
        self.dc.Clear()
        rect = self.GetClientRect()

        if not self.key:
            self.dc.SetPen(wx.Pen((149, 149, 149)))
            self.dc.SetBrush(wx.Brush(wx.Colour(149, 149, 149)))
            width = rect.width
            height = 21
            radius = 10
            x = rect.x
            y = int((rect.height - height) / 2)
            self.dc.DrawRoundedRectangle(x, y, width, height, radius)

            self.dc.SetPen(wx.Pen((255, 255, 255)))
            self.dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255)))
            radius = 8
            x = rect.x + radius + 3
            y = 10 + rect.y
            self.dc.DrawCircle(x, y, radius)

            font = wx.Font(10, 70, 90, 92, False, u"微软雅黑")
            self.dc.SetFont(font)
            self.dc.SetTextForeground('white')
            x = rect.x + 21
            y = rect.y + 1
            self.dc.DrawText('OFF', x, y)

        else:
            self.dc.SetPen(wx.Pen((43, 128, 192)))
            self.dc.SetBrush(wx.Brush(wx.Colour(43, 128, 192)))
            width = rect.width
            height = 21
            radius = 10
            x = rect.x
            y = (rect.height - height) / 2
            self.dc.DrawRoundedRectangle(x, int(y), width, height, radius)

            self.dc.SetPen(wx.Pen((255, 255, 255)))
            self.dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255)))
            radius = 8
            x = rect.x + rect.width - radius - 4
            y = 10 + rect.y
            self.dc.DrawCircle(x, y, radius)

            font = wx.Font(10, 70, 90, 92, False, u"微软雅黑")
            self.dc.SetFont(font)
            self.dc.SetTextForeground('white')
            x = rect.x + 5
            y = rect.y + 1
            self.dc.DrawText('ON', x, y)


class BTPanel(wx.Panel):
    def __init__(self, parent=None,size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER,size=size)
        self.size = size
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.conn = None

    def add_button(self, label, color):
        bt = mButton(self, label, color)
        self.sizer.Add(bt, 0, wx.RIGHT, 3)

    def add_bitmap_button(self, bmp_path, tooltip, onclick_method, size=wx.DefaultSize):
        bt = mBitmapButton(self, bmp_path, tooltip)
        bt.Bind(wx.EVT_BUTTON, onclick_method)
        self.sizer.Add(bt, 0, wx.RIGHT, 3)



class ToggleButtonBox(wx.Panel):
    def __init__(self, parent=None):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self._mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._sel = None
        self._buttons = {}  # label:btn
        self.SetSizer(self._mainSizer)

    def AddImageButton(self, label, bmp_path, font=None, fgcolour=None, bgcolour=None):
        btn = wx.ToggleButton()
        if font:
            btn.SetFont(font)
        if fgcolour:
            btn.SetForegroundColour(fgcolour)
        if bgcolour:
            btn.SetBackgroundColour(bgcolour)
        self._mainSizer.Add(btn, 0, wx.RIGHT, 2)
        self._buttons[label] = btn


class mULC_Report(ULC.UltimateListCtrl):
    def __init__(self, parent, kind=1, style=0,
                 agwStyle=wx.LC_REPORT
                          | wx.BORDER_NONE
                          | wx.LC_VRULES
                          | wx.LC_HRULES
                          | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                          | ULC.ULC_AUTO_CHECK_CHILD
                          | ULC.ULC_AUTO_CHECK_PARENT):
        ULC.UltimateListCtrl.__init__(self, parent, wx.ID_ANY, style=style, agwStyle=agwStyle)
        self.kind = kind
        self.EnableSelectionVista(True)
        self.selected = None
        self.Bind(ULC.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

    def create(self, cols_title):
        i = 0
        for text in cols_title:
            info = ULC.UltimateListItem()
            info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
            info._format = 0
            info._text = text
            if self.kind and i == 0:
                info._kind = 1
                info._mask = info._mask | ULC.ULC_MASK_CHECK
            self.InsertColumnInfo(i, info)
            i += 1

    def insert(self, data):
        index = self.InsertImageStringItem(maxsize, data[0], [], it_kind=self.kind)
        i = 1
        for item in data[1:]:
            if isinstance(item, str):
                self.SetStringItem(index, i, item)
            else:
                ulcitem = self.GetItem(index, i)
                ulcitem.SetWindow(item)
                self.SetItem(ulcitem)
            i += 1
        return index

    def setColumnWidth(self, width, autofill=None):
        i = 0
        for w in width:
            self.SetColumnWidth(i, w)
            i += 1
        if autofill:
            self.SetColumnWidth(autofill, ULC.ULC_AUTOSIZE_FILL)

    def disable(self, item_index):
        item = self.GetItem(item_index)
        item.Enable(False)
        self.SetItem(item)

    def OnItemSelected(self, evt):
        self.selected = evt.Index

    def SetColString(self, col, text):
        for i in range(self.GetItemCount()):
            self.SetStringItem(i, col, text)

    def get_selected_item(self):
        items = []
        for i in range(self.GetItemCount()):
            if self.IsItemChecked(i):
                items.append(i)
        return items


class mFileTree(gizmos.TreeListCtrl):
    def __init__(self, parent, conn):
        gizmos.TreeListCtrl.__init__(self, parent, -1, style=0, agwStyle=gizmos.TR_DEFAULT_STYLE
                                                                         # | gizmos.TR_HAS_BUTTONS
                                                                         | gizmos.TR_TWIST_BUTTONS
                                                                         # | gizmos.TR_ROW_LINES
                                                                         # | gizmos.TR_COLUMN_LINES
                                                                         # | gizmos.TR_NO_LINES
                                                                         # | gizmos.TR_LINES_AT_ROOT
                                                                         | gizmos.TR_FULL_ROW_HIGHLIGHT
                                     )

        self.conn = conn

        isz = (16, 16)
        il = wx.ImageList(isz[0], isz[1])
        bmp_folder = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz))
        bmp_file = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        self.SetImageList(il)
        self.il = il

        self.AddColumn("大小")
        self.AddColumn("类型")
        self.AddColumn("修改时间")
        self.AddColumn("权限")
        self.AddColumn("用户/用户组")

        self.root = self.AddRoot("/")


class mSTC(stc.StyledTextCtrl):
    def __init__(self, parent, lex=0):
        stc.StyledTextCtrl.__init__(self, parent, style=wx.TE_MULTILINE | wx.TE_WORDWRAP)
        faces = {'times': 'Times New Roman',
                 'mono': 'Courier New',
                 'helv': 'Arial',
                 'other': 'Courier New',
                 'size': 10,
                 'size2': 8,
                 }

        type_dic = {1: stc.STC_LEX_BASH,
                    2: stc.STC_LEX_XML}

        self.SetMarginType(0, 1)
        self.SetMarginWidth(0, 20)
        if lex:
            self.SetLexer(type_dic[lex])

        # styles
        # Default
        self.StyleSetSpec(stc.STC_P_DEFAULT, "fore:#000000,size:%(size)d" % faces)
        # Comments（xml-head）
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        # Number(注释-绿)
        self.StyleSetSpec(stc.STC_P_NUMBER, "fore:#007F00,size:%(size)d" % faces)
        # String
        self.StyleSetSpec(stc.STC_P_STRING, "fore:#7F007F,size:%(size)d" % faces)
        # # Single quoted string
        # self.StyleSetSpec(stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # # Keyword
        # self.StyleSetSpec(stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        # # Triple quotes
        # self.StyleSetSpec(stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        # Triple double quotes(INI括号)
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        # # Function or method name definition
        # self.StyleSetSpec(stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        # # # Operators
        # # self.StyleSetSpec(stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        # # Identifiers
        # self.StyleSetSpec(stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # # Comment-blocks
        # self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        # End of line where string is not closed
        self.StyleSetSpec(stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)
        self.SetCaretForeground("BLUE")


class mGauge(wx.Panel):
    def __init__(self, parent, size=(118, 18), percent=0,
                 done_colour=wx.Colour(173, 220, 173),
                 bg_colour=wx.Colour(251, 251, 251),
                 fg_colour=wx.Colour(96, 96, 96),
                 border_colour=wx.Colour(211, 211, 211)):
        wx.Panel.__init__(self, parent, size=size)
        self.parent = parent
        self.left_txt = ''
        self.right_txt = ''
        self.percent = percent
        self.width = size[0]
        self.height = size[1]
        self.done_colour = done_colour
        self.bg_colour = bg_colour
        self.fg_colour = fg_colour
        self.border_colour = border_colour
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)

        width_done = int((self.width - 2) * self.percent / 100)

        dc.SetPen(wx.Pen(self.border_colour))
        dc.SetBrush(wx.Brush(self.bg_colour))
        dc.DrawRectangle(0, 0, self.width, self.height)

        dc.SetPen(wx.Pen(self.done_colour))
        dc.SetBrush(wx.Brush(self.done_colour))
        dc.DrawRectangle(1, 1, width_done, self.height - 2)

        dc.SetTextForeground(self.fg_colour)
        if self.left_txt:
            dc.DrawText(self.left_txt, 5, 1)
        if self.right_txt:
            textWidth, dummy = dc.GetTextExtent(self.right_txt)
            dc.DrawText(self.right_txt, self.width - 5 - textWidth, 1)

    def SetValue(self, per, left_str='', right_str=''):
        if left_str:
            self.left_txt = left_str
        if right_str:
            self.right_txt = right_str
        self.percent = per
        self.Refresh()

    def SetLeftString(self, label):
        self.left_txt = label
        self.Refresh()


class FileRenderer(object):
    "文件传输进度条"
    DONE_BITMAP = None
    REMAINING_BITMAP = None

    def __init__(self, parent, filepath, is_down):

        self.filepath = filepath
        self.progress = 0
        self.done = 0
        self.is_down = is_down

    def DrawSubItem(self, dc, rect, line, highlighted, enabled):
        mdc = wx.MemoryDC()
        canvas = wx.Bitmap(rect.width, rect.height)
        mdc.SelectObject(canvas)

        if highlighted:
            mdc.SetBackground(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)))
        else:
            mdc.SetBackground(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)))
        mdc.Clear()

        mdc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        ypos = 5
        xtext, ytext = mdc.GetTextExtent(self.filepath)
        mdc.DrawText(self.filepath, 0, ypos)

        ypos += ytext + 5
        self.DrawProgressBar(mdc, 0, ypos, rect.width, 20, self.progress)
        mdc.SetFont(wx.Font(8, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        text = "%s" % self.done
        textWidth, dummy = mdc.GetTextExtent(text)
        mdc.DrawText(text, int(rect.width / 2 - textWidth / 2), ypos + 5)

        dc.SetClippingRegion(rect.x, rect.y, rect.width, rect.height)
        dc.Blit(rect.x + 3, rect.y, rect.width - 6, rect.height, mdc, 0, 0)
        dc.DestroyClippingRegion()

    def GetLineHeight(self):

        return 40

    def GetSubItemWidth(self):

        return 250

    def DrawHorizontalPipe(self, dc, x, y, w, colour):
        PIPE_HEIGHT = 18
        for r in range(PIPE_HEIGHT):
            dc.SetPen(wx.Pen(colour))
            dc.DrawLine(x, y + r, x + w, y + r)

    def DrawProgressBar(self, dc, x, y, w, h, percent):
        PIPE_WIDTH = 2000
        PIPE_HEIGHT = 18
        # Create two pipes
        if self.DONE_BITMAP is None:
            self.DONE_BITMAP = wx.Bitmap(PIPE_WIDTH, PIPE_HEIGHT)
            mdc = wx.MemoryDC()
            mdc.SelectObject(self.DONE_BITMAP)
            self.DrawHorizontalPipe(mdc, 0, 0, PIPE_WIDTH, wx.Colour(142, 229, 238))
            mdc.SelectObject(wx.NullBitmap)

            self.REMAINING_BITMAP = wx.Bitmap(PIPE_WIDTH, PIPE_HEIGHT)
            mdc = wx.MemoryDC()
            mdc.SelectObject(self.REMAINING_BITMAP)
            self.DrawHorizontalPipe(mdc, 0, 0, PIPE_WIDTH, wx.WHITE)  # 中线
            self.DrawHorizontalPipe(mdc, 1, 0, PIPE_WIDTH - 1, wx.Colour(102, 139, 139))
            mdc.SelectObject(wx.NullBitmap)

        # Center the progress bar vertically in the box supplied
        y = int(y + (h - PIPE_HEIGHT) / 2)

        if percent == 0:
            middle = 0
        else:
            middle = int((w * percent) / 100)

        if w < 1:
            return

        if middle == 0:  # not started
            bitmap = self.REMAINING_BITMAP.GetSubBitmap((1, 0, w, PIPE_HEIGHT))
            dc.DrawBitmap(bitmap, x, y, False)
        elif middle == w:  # completed
            bitmap = self.DONE_BITMAP.GetSubBitmap((0, 0, w, PIPE_HEIGHT))
            dc.DrawBitmap(bitmap, x, y, False)
        else:  # in progress
            try:
                doneBitmap = self.DONE_BITMAP.GetSubBitmap((0, 0, middle, PIPE_HEIGHT))
                dc.DrawBitmap(doneBitmap, x, y, False)
                remainingBitmap = self.REMAINING_BITMAP.GetSubBitmap((0, 0, w - middle, PIPE_HEIGHT))
                dc.DrawBitmap(remainingBitmap, x + middle, y, False)
            except Exception as e:
                print(e)



class SSH_ULC(ULC.UltimateListCtrl, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):

        ULC.UltimateListCtrl.__init__(self, parent, id, pos, size, style,
                                      agwStyle=wx.LC_REPORT
                                               | wx.BORDER_SUNKEN
                                               | wx.LC_HRULES
                                               | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                                               | wx.LC_NO_HEADER
                                      )
        self.selected = None
        self.Bind(ULC.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

        il = wx.ImageList(32, 32)
        il.Add(wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_OTHER, (32, 32)))
        il.Add(wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_OTHER, (32, 32)))
        self.SetImageList(il, wx.IMAGE_LIST_SMALL)

        info = ULC.UltimateListItem()
        info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT
        info.Align = 0
        info.Text = ""

        self.InsertColumnInfo(0, info)

        info = ULC.UltimateListItem()
        info.Align = wx.LIST_FORMAT_LEFT
        info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT
        info.Image = []
        info.Text = ""

        self.InsertColumnInfo(1, info)

        self.map_klass = {}  # index:klass

        ##解决不能自适应宽度问题
        self.addItem('')
        self.DeleteAllItems()
        self.SetColumnWidth(1, 300)
        self.Bind(wx.EVT_RIGHT_UP, self.SetPopupMenu)

    def addItem(self, filepath, is_down=1):
        self.Freeze()
        index = self.InsertImageStringItem(maxsize, "", [is_down])
        self.SetStringItem(index, 0, "")
        klass = FileRenderer(self, filepath, is_down)
        self.SetItemCustomRenderer(index, 1, klass)
        self.SetColumnWidth(0, 34)
        self.Thaw()
        self.Update()

        self.map_klass[index] = klass
        return index

    def OnItemSelected(self, evt):
        self.selected = evt.Index

    def SetPopupMenu(self, evt):
        self.popupmenu = wx.Menu()
        for text in ['打开文件路径', 0, '清除', '清除全部']:
            if text == 0:
                self.popupmenu.AppendSeparator()
                continue
            item = self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupMenu, item)
        self.PopupMenu(self.popupmenu)

    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(self.popupmenu, pos)

    def OnPopupMenu(self, evt):
        txt = getLabelFromEVT(evt)
        if txt == '清除':
            self.DeleteItem(self.selected)
        elif txt == '清除全部':
            self.DeleteAllItems()
        elif txt == '打开文件路径':
            if self.map_klass[self.selected].is_down:
                d_path = self.map_klass[self.selected].filepath
                r_path = get_download_path()
                d_path = '\\'.join(d_path.split('/')[:-1])
                startfile(r_path + '\\' + d_path)


class SSHPopupWindow(wx.PopupTransientWindow):
    def __init__(self, parent, style):
        wx.PopupTransientWindow.__init__(self, parent, style)
        panel = wx.Panel(self)

        txt1 = wx.StaticText(panel, -1, '下载：', style=wx.NO_BORDER)
        self.st_path = wx.StaticText(panel, -1, '', size=(250, -1), style=wx.NO_BORDER)
        self.bt_open = mBitmapButton(panel, 'bitmaps/openfile.png', '打开')
        self.bt_cancel = mBitmapButton(panel, 'bitmaps/ssh_cancel.png', '取消')

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(txt1, 0, wx.LEFT | wx.ALIGN_CENTER, 5)
        sizer1.Add(self.st_path, 1, wx.ALIGN_CENTER)
        sizer1.Add(self.bt_open, 0)
        sizer1.Add(self.bt_cancel, 0)

        self.ulc_ssh = SSH_ULC(panel, size=(350, 280))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sizer1, 0)
        sizer.Add(self.ulc_ssh, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        panel.SetSizer(sizer)

        sizer.Fit(panel)
        sizer.Fit(self)
        self.SetSize(self.GetBestSize())
        self.Layout()

    def ProcessLeftDown(self, evt):
        return wx.PopupTransientWindow.ProcessLeftDown(self, evt)

    def OnDismiss(self):
        self.Hide()


class TabContainerBase(wx.Panel):
    """
    Base class for :class:`FlatImageBook` image container.
    """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):

        self._nIndex = -1
        self._nImgSize = 23
        self._ImageList = None
        self._ImageListFocus = None
        self._nHoveredImgIdx = -1
        self._tabAreaSize = (-1, -1)
        self._pagesInfoVec = []
        self._tabSel = -1

        wx.Panel.__init__(self, parent, id, pos, size, wx.NO_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE)

    def ClearFlag(self, flag):
        """
        Removes flag from the style.

        :param `flag`: a window style flag.

        :see: :meth:`~ImageContainerBase.HasAGWFlag` for a list of possible window style flags.
        """

        parent = self.GetParent()
        agwStyle = parent.GetAGWWindowStyleFlag()
        agwStyle &= ~flag
        parent.SetAGWWindowStyleFlag(agwStyle)

    def AssignImageList(self, imglist,imglist_focus):
        """
        Assigns an image list to the :class:`wx.ImageContainerBase`.

        :param `imglist`: an instance of :class:`wx.ImageList`.
        """

        if imglist and imglist.GetImageCount() != 0:
            self._nImgSize = imglist.GetBitmap(0).GetHeight()

        self._ImageList = imglist
        self._ImageListFocus = imglist_focus

        parent = self.GetParent()

    def GetImageList(self):
        """ Return the image list for :class:`wx.ImageContainerBase`. """

        return self._ImageList

    def GetFocusImageList(self):
        """ Return the image list for :class:`wx.ImageContainerBase`. """

        return self._ImageListFocus

    def GetImageSize(self):
        """ Returns the image size inside the :class:`wx.ImageContainerBase` image list. """

        return self._nImgSize

    def FixTextSize(self, dc, text, maxWidth):
        """
        Fixes the text, to fit `maxWidth` value. If the text length exceeds
        `maxWidth` value this function truncates it and appends two dots at
        the end. ("Long Long Long Text" might become "Long Long...").

        :param `dc`: an instance of :class:`wx.DC`;
        :param `text`: the text to fix/truncate;
        :param `maxWidth`: the maximum allowed width for the text, in pixels.
        """

        return ArtManager.Get().TruncateText(dc, text, maxWidth)

    def CanDoBottomStyle(self):
        """
        Allows the parent to examine the children type. Some implementation
        (such as :class:`LabelBook`), does not support top/bottom images, only left/right.
        """

        return False

    def AddPage(self, caption, selected=False, imgIdx=-1):
        """
        Adds a page to the container.

        :param `caption`: specifies the text for the new tab;
        :param `selected`: specifies whether the page should be selected;
        :param `imgIdx`: specifies the optional image index for the new tab.
        """

        self._pagesInfoVec.append(TabInfo(caption, imgIdx))
        self.Refresh()

    def SetPageImage(self, page, imgIdx):
        """
        Sets the image for the given page.

        :param `page`: the index of the tab;
        :param `imgIdx`: specifies the optional image index for the tab.
        """

        imgInfo = self._pagesInfoVec[page]
        imgInfo.SetImageIndex(imgIdx)

    def SetPageText(self, page, text):
        """
        Sets the tab caption for the given page.

        :param `page`: the index of the tab;
        :param `text`: the new tab caption.
        """

        imgInfo = self._pagesInfoVec[page]
        imgInfo.SetCaption(text)

    def GetPageImage(self, page):
        """
        Returns the image index for the given page.

        :param `page`: the index of the tab.
        """

        imgInfo = self._pagesInfoVec[page]
        return imgInfo.GetImageIndex()

    def GetPageText(self, page):
        """
        Returns the tab caption for the given page.

        :param `page`: the index of the tab.
        """

        imgInfo = self._pagesInfoVec[page]
        return imgInfo.GetCaption()

    def GetEnabled(self, page):
        """
        Returns whether a tab is enabled or not.

        :param `page`: an integer specifying the page index.
        """

        if page >= len(self._pagesInfoVec):
            return True  # Adding a page - enabled by default

        imgInfo = self._pagesInfoVec[page]
        return imgInfo.GetEnabled()

    def EnableTab(self, page, enabled=True):
        """
        Enables or disables a tab.

        :param `page`: an integer specifying the page index;
        :param `enabled`: ``True`` to enable a tab, ``False`` to disable it.
        """

        if page >= len(self._pagesInfoVec):
            return

        imgInfo = self._pagesInfoVec[page]
        imgInfo.EnableTab(enabled)

    def ClearAll(self):
        """ Deletes all the pages in the container. """

        self._pagesInfoVec = []
        self._nIndex = wx.NOT_FOUND

    def DoDeletePage(self, page):
        """
        Does the actual page deletion.

        :param `page`: the index of the tab.
        """

        # Remove the page from the vector
        book = self.GetParent()
        self._pagesInfoVec.pop(page)

        if self._nIndex >= page:
            self._nIndex = self._nIndex - 1

        # The delete page was the last first on the array,
        # but the book still has more pages, so we set the
        # active page to be the first one (0)
        if self._nIndex < 0 and len(self._pagesInfoVec) > 0:
            self._nIndex = 0

        # Refresh the tabs
        if self._nIndex >= 0:
            book._bForceSelection = True
            book.SetSelection(self._nIndex)
            book._bForceSelection = False

        if not self._pagesInfoVec:
            # Erase the page container drawings
            dc = wx.ClientDC(self)
            dc.Clear()

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`wx.ImageContainerBase`.

        :param `event`: a :class:`wx.SizeEvent` event to be processed.
        """

        self.Refresh()  # Call on paint
        event.Skip()

    def OnEraseBackground(self, event):
        """
        Handles the ``wx.EVT_ERASE_BACKGROUND`` event for :class:`wx.ImageContainerBase`.

        :param `event`: a :class:`EraseEvent` event to be processed.

        :note: This method is intentionally empty to reduce flicker.
        """

        pass

    def HitTest(self, pt):
        """
        Returns the index of the tab at the specified position or ``wx.NOT_FOUND``
        if ``None``, plus the flag style of :meth:`~ImageContainerBase.HitTest`.

        :param `pt`: an instance of :class:`wx.Point`, to test for hits.

        :return: The index of the tab at the specified position plus the hit test
         flag, which can be one of the following bits:

         ====================== ======= ================================
         HitTest Flags           Value  Description
         ====================== ======= ================================
         ``IMG_OVER_IMG``             0 The mouse is over the tab icon
         ``IMG_OVER_PIN``             1 The mouse is over the pin button
         ``IMG_OVER_EW_BORDER``       2 The mouse is over the east-west book border
         ``IMG_NONE``                 3 Nowhere
         ====================== ======= ================================

        """

        for i in range(len(self._pagesInfoVec)):

            if self._pagesInfoVec[i].GetPosition() == wx.Point(-1, -1):
                break

            buttonRect = wx.Rect(self._pagesInfoVec[i].GetPosition(), self._pagesInfoVec[i].GetSize())

            if buttonRect.Contains(pt):
                self._tabSel = i
                return i, IMG_OVER_IMG

        if self.PointOnSash(pt):
            return -1, IMG_OVER_EW_BORDER
        else:
            return -1, IMG_NONE

    def PointOnSash(self, pt):
        """
        Tests whether pt is located on the sash.

        :param `pt`: an instance of :class:`wx.Point`, to test for hits.
        """

        # Check if we are on a the sash border
        cltRect = self.GetClientRect()

        if pt.x > cltRect.x + cltRect.width - 4:
            return True

        return False

    def OnMouseLeftDown(self, event):
        """
        Handles the ``wx.EVT_LEFT_DOWN`` event for :class:`wx.ImageContainerBase`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        event.Skip()

        tabIdx, where = self.HitTest(event.GetPosition())

        if where == IMG_OVER_IMG:
            self._nHoveredImgIdx = -1

        self._tabSel = tabIdx

        if tabIdx == -1:
            return
        else:
            self._nIndex = tabIdx

    def OnMouseLeaveWindow(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`wx.ImageContainerBase`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        bRepaint = self._nHoveredImgIdx != -1
        self._nHoveredImgIdx = -1

        # Restore cursor
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

        if bRepaint:
            self.Refresh()

    def OnMouseLeftUp(self, event):
        """
        Handles the ``wx.EVT_LEFT_UP`` event for :class:`wx.ImageContainerBase`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        pass

    def OnMouseMove(self, event):
        """
        Handles the ``wx.EVT_MOTION`` event for :class:`wx.ImageContainerBase`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        imgIdx, where = self.HitTest(event.GetPosition())

        # Allow hovering unless over current tab or tab is disabled
        self._nHoveredImgIdx = -1

        if imgIdx < len(self._pagesInfoVec) and self.GetEnabled(imgIdx) and imgIdx != self._nIndex:
            self._nHoveredImgIdx = imgIdx

        self.Refresh()


class TabContainer(TabContainerBase):
    """
    Base class for :class:`FlatImageBook` image container.
    """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 tabSize=(90, 32)):
        """
        Default class constructor.

        :param `parent`: parent window. Must not be ``None``;
        :param `id`: window identifier. A value of -1 indicates a default value;
        :param `pos`: the control position. A value of (-1, -1) indicates a default position,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `size`: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `style`: the underlying :class:`Panel` window style;
        :param `agwStyle`: the AGW-specific window style. This can be a combination of the
         following bits:

         =========================== =========== ==================================================
         Window Styles               Hex Value   Description
         =========================== =========== ==================================================
         ``INB_BOTTOM``                      0x1 Place labels below the page area. Available only for :class:`FlatImageBook`.
         ``INB_LEFT``                        0x2 Place labels on the left side. Available only for :class:`FlatImageBook`.
         ``INB_RIGHT``                       0x4 Place labels on the right side.
         ``INB_TOP``                         0x8 Place labels above the page area.
         ``INB_BORDER``                     0x10 Draws a border around :class:`LabelBook` or :class:`FlatImageBook`.
         ``INB_SHOW_ONLY_TEXT``             0x20 Shows only text labels and no images. Available only for :class:`LabelBook`.
         ``INB_SHOW_ONLY_IMAGES``           0x40 Shows only tab images and no label texts. Available only for :class:`LabelBook`.
         ``INB_FIT_BUTTON``                 0x80 Displays a pin button to show/hide the book control.
         ``INB_DRAW_SHADOW``               0x100 Draw shadows below the book tabs. Available only for :class:`LabelBook`.
         ``INB_USE_PIN_BUTTON``            0x200 Displays a pin button to show/hide the book control.
         ``INB_GRADIENT_BACKGROUND``       0x400 Draws a gradient shading on the tabs background. Available only for :class:`LabelBook`.
         ``INB_WEB_HILITE``                0x800 On mouse hovering, tabs behave like html hyperlinks. Available only for :class:`LabelBook`.
         ``INB_NO_RESIZE``                0x1000 Don't allow resizing of the tab area.
         ``INB_FIT_LABELTEXT``            0x2000 Will fit the tab area to the longest text (or text+image if you have images) in all the tabs.
         ``INB_BOLD_TAB_SELECTION``       0x4000 Show the selected tab text using a bold font.
         =========================== =========== ==================================================

        :param `name`: the window name.
        """

        TabContainerBase.__init__(self, parent, id, pos, size)

        imageList1 = wx.ImageList(23, 23)
        imageList2 = wx.ImageList(23, 23)
        self.AssignImageList(imageList1,imageList2)
        self._tabSize = tabSize
        self._Size = size

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        # self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        # self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeaveWindow)

    def AddImage(self, path, focus_path=None):
        self.GetImageList().Add(wx.Bitmap(path, wx.BITMAP_TYPE_PNG))
        if focus_path:
            self.GetFocusImageList().Add(wx.Bitmap(focus_path, wx.BITMAP_TYPE_PNG))


    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`wx.ImageContainer`.

        :param `event`: a :class:`wx.SizeEvent` event to be processed.
        """

        TabContainerBase.OnSize(self, event)
        event.Skip()

    def OnMouseLeftDown(self, event):
        """
        Handles the ``wx.EVT_LEFT_DOWN`` event for :class:`wx.ImageContainer`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        TabContainerBase.OnMouseLeftDown(self, event)
        event.Skip()

    def OnMouseLeftUp(self, event):
        """
        Handles the ``wx.EVT_LEFT_UP`` event for :class:`wx.ImageContainer`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        TabContainerBase.OnMouseLeftUp(self, event)
        self.SetPageImage()
        event.Skip()

    def OnEraseBackground(self, event):
        """
        Handles the ``wx.EVT_ERASE_BACKGROUND`` event for :class:`wx.ImageContainer`.

        :param `event`: a :class:`EraseEvent` event to be processed.
        """

        TabContainerBase.OnEraseBackground(self, event)

    def OnMouseMove(self, event):
        """
        Handles the ``wx.EVT_MOTION`` event for :class:`wx.ImageContainer`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        TabContainerBase.OnMouseMove(self, event)
        event.Skip()

    def OnMouseLeaveWindow(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`wx.ImageContainer`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        TabContainerBase.OnMouseLeaveWindow(self, event)
        event.Skip()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`wx.ImageContainer`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """
        dc = wx.BufferedPaintDC(self)
        backBrush = wx.WHITE_BRUSH
        borderPen = wx.TRANSPARENT_PEN

        size = self.GetSize()

        # Background
        dc.SetBrush(backBrush)

        borderPen.SetWidth(1)
        dc.SetPen(borderPen)
        dc.DrawRectangle(0, 0, size.x, size.y)

        borderPen = wx.BLACK_PEN
        borderPen.SetWidth(1)
        dc.SetPen(borderPen)
        dc.DrawLine(0, size.y, size.x, size.y)
        dc.DrawPoint(0, size.y)

        clientSize = size.GetWidth()

        pos = 0

        nTextPaddingLeft = 2
        imgTopPadding = 6

        count = 0
        normalFont = wx.Font(12, 70, 90, 90, False, u"微软雅黑")

        for i in range(len(self._pagesInfoVec)):

            count = count + 1

            dc.SetFont(normalFont)

            textWidth, textHeight = dc.GetTextExtent(self._pagesInfoVec[i].GetCaption())

            rectWidth, rectHeight = self._tabSize
            if pos + rectWidth > clientSize:
                break

            # Calculate the button rectangle
            buttonRect = wx.Rect(pos, 0, rectWidth, rectHeight)

            # Check if we need to draw a rectangle around the button
            if self._nIndex == i:   #选中
                # Set the colours
                penColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION)
                brushColour = ArtManager.Get().LightColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION), 75)

                dc.SetPen(wx.Pen(penColour))
                dc.SetBrush(wx.Brush(brushColour))

                # Fix the surrounding of the rect if border is set
                dc.DrawRectangle(buttonRect)

            if self._nHoveredImgIdx == i:   #悬停
                # Set the colours
                penColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION)
                brushColour = ArtManager.Get().LightColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION), 90)

                dc.SetPen(wx.Pen(penColour))
                dc.SetBrush(wx.Brush(brushColour))

                dc.DrawRectangle(buttonRect)

            # Draw the caption and text
            imgXcoord = int(rectWidth / 2 - (self._nImgSize + nTextPaddingLeft + textWidth) / 2 + pos)
            imgYcoord = imgTopPadding
            if self._nIndex == i:
                self._ImageListFocus.Draw(self._pagesInfoVec[i].GetImageIndex(), dc,
                                     imgXcoord, imgYcoord,
                                     wx.IMAGELIST_DRAW_TRANSPARENT, True)
            else:
                self._ImageList.Draw(self._pagesInfoVec[i].GetImageIndex(), dc,
                                              imgXcoord, imgYcoord,
                                              wx.IMAGELIST_DRAW_TRANSPARENT, True)

            # Draw the text
            fixedText = self.FixTextSize(dc, self._pagesInfoVec[i].GetCaption(),
                                         rectWidth - self._nImgSize - nTextPaddingLeft)
            textOffsetX = imgXcoord + self._nImgSize + nTextPaddingLeft
            textOffsetY = imgYcoord

            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            dc.DrawText(fixedText, textOffsetX, textOffsetY)

            # Update the page info
            self._pagesInfoVec[i].SetPosition(buttonRect.GetPosition())
            self._pagesInfoVec[i].SetSize(buttonRect.GetSize())

            pos += rectWidth


class TabInfo(object):
    """
    This class holds all the information (caption, image, etc...) belonging to a
    single tab in :class:`LabelBook`.
    """

    def __init__(self, strCaption="", imageIndex=-1, enabled=True):
        """
        Default class constructor.

        :param `strCaption`: the tab caption;
        :param `imageIndex`: the tab image index based on the assigned (set)
         :class:`wx.ImageList` (if any);
        :param `enabled`: sets the tab as enabled or disabled.
        """

        self._pos = wx.Point()
        self._size = wx.Size()
        self._strCaption = strCaption
        self._ImageIndex = imageIndex
        self._captionRect = wx.Rect()
        self._bEnabled = enabled

    def SetCaption(self, value):
        """
        Sets the tab caption.

        :param `value`: the new tab caption.
        """

        self._strCaption = value

    def GetCaption(self):
        """ Returns the tab caption. """

        return self._strCaption

    def SetPosition(self, value):
        """
        Sets the tab position.

        :param `value`: the new tab position, an instance of :class:`wx.Point`.
        """

        self._pos = value

    def GetPosition(self):
        """ Returns the tab position. """

        return self._pos

    def SetSize(self, value):
        """
        Sets the tab size.

        :param `value`:  the new tab size, an instance of :class:`wx.Size`.
        """

        self._size = value

    def GetSize(self):
        """ Returns the tab size. """

        return self._size

    def SetImageIndex(self, value):
        """
        Sets the tab image index.

        :param `value`: an index into the image list..
        """

        self._ImageIndex = value

    def GetImageIndex(self):
        """ Returns the tab image index. """

        return self._ImageIndex

    def SetTextRect(self, rect):
        """
        Sets the client rectangle available for the tab text.

        :param `rect`: the tab text client rectangle, an instance of :class:`wx.Rect`.
        """

        self._captionRect = rect

    def GetTextRect(self):
        """ Returns the client rectangle available for the tab text. """

        return self._captionRect

    def GetEnabled(self):
        """ Returns whether the tab is enabled or not. """

        return self._bEnabled

    def EnableTab(self, enabled):
        """
        Sets the tab enabled or disabled.

        :param `enabled`: ``True`` to enable a tab, ``False`` to disable it.
        """

        self._bEnabled = enabled
