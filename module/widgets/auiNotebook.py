# -*- coding: utf-8 -*-

import wx, module.widgets.aui as aui

NOTEBOOK_STYLE = aui.AUI_NB_DEFAULT_STYLE \
                 | aui.AUI_NB_TAB_MOVE \
                 | aui.AUI_NB_TAB_EXTERNAL_MOVE \
                 | aui.AUI_NB_TAB_SPLIT \
                 | aui.AUI_NB_TAB_FLOAT \
                 | aui.AUI_NB_TAB_EXTERNAL_MOVE \
                 | wx.NO_BORDER \
                 | aui.AUI_NB_WINDOWLIST_BUTTON


class auiNotebook(aui.AuiNotebook):
    def __init__(self, parent):
        aui.AuiNotebook.__init__(self, parent, agwStyle=NOTEBOOK_STYLE)
        self._PageCount = 0
        self.parent = parent
        self.tab_buttons = {}
        self.tab_context_menu = {}
        self.active_button_tab = None

    def set_tab_context_menu(self):
        # 绑定右键菜单事件
        tab_ctrl = self.GetActiveTabCtrl()
        tab_ctrl.Bind(wx.EVT_RIGHT_UP, self.on_tab_context_menu)

    def on_tab_context_menu(self, event):
        active_tab_ctrl = self.GetActiveTabCtrl()
        pos = event.GetPosition()
        tab = active_tab_ctrl.TabHitTest(pos.x, pos.y)

        tab_index = self.GetPageIndex(tab)
        self.SetSelection(tab_index)

        # 创建右键菜单
        menu = wx.Menu()
        for txt in self.tab_context_menu['txt']:
            item = menu.Append(-1, txt)
            self.Bind(wx.EVT_MENU, self.tab_context_menu['method'], item)

        # 在鼠标位置显示右键菜单
        self.PopupMenu(menu, pos)
        menu.Destroy()

    def DeletePage(self, page_idx):
        self._PageCount -= 1
        # 调用父类的DeletePage方法
        super().DeletePage(page_idx)

    def OnTabButton(self, event):
        bt_id = event.GetInt()
        self.active_button_tab = event.GetEventObject()
        if bt_id in self.tab_buttons:
            self.tab_buttons[bt_id]['method']()
        super().OnTabButton(event)

    def addTabButtons(self, ids, local, bitmap, method):
        self.AddTabAreaButton(ids, local, bitmap)
        self.tab_buttons[ids] = {'bitmap': bitmap, 'method': method, 'local': local}

    def CreaateNewTabFrame(self):

        tab_ctrl = super().CreaateNewTabFrame()
        for tb_id in self.tab_buttons.keys():  #重建 tab frame时添加按钮
            self.addTabButtons(tb_id,
                               self.tab_buttons[tb_id]['local'],
                               self.tab_buttons[tb_id]['bitmap'],
                               self.tab_buttons[tb_id]['method'])
        return tab_ctrl

    def OnTabRightDown(self,event):
        self.OnTabClicked(event)
        active_tab_ctrl = self.GetActiveTabCtrl()
        tab_pos = active_tab_ctrl.GetPosition()
        pos = active_tab_ctrl._right_click_pt

        # 创建右键菜单
        menu = wx.Menu()
        for txt in self.tab_context_menu['txt']:
            item = menu.Append(-1, txt)
            self.Bind(wx.EVT_MENU, self.tab_context_menu['method'], item)

        # 在鼠标位置显示右键菜单
        self.PopupMenu(menu, pos+tab_pos)
        menu.Destroy()
        super().OnTabRightDown(event)