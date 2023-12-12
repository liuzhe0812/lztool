import wx
from wx.lib.agw.artmanager import ArtManager
from wx.lib.agw.fmresources import *

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
        self.Refresh()

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