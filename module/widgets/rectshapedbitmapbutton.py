#!/usr/bin/env python


# --------------------------------------------------------------------------- #
# SHAPEDBITMAPBUTTON Control wxPython IMPLEMENTATION
# Python Code By:
#
# Edward Greig, @ 17 Jan 2014
# Latest Revision: Edward Greig 24 Nov 2015, 21.00 GMT
#
#
# TODO List/Caveats
#
# 1. Creating *A Lot* Of ShapedBitmapButtons May Require Some Time.
#
#
# For All Kind Of Problems, Requests Of Enhancements And Bug Reports, Please
# Write To Me At:
#
# metaliobovinus@gmail.com
#
# Or, Obviously, To The wxPython Mailing List!!!
#
#
# End Of Comments
# --------------------------------------------------------------------------- #


"""
ShapedBitmapButton
==================

`ShapedBitmapButton` tries to fill the lack of "custom shaped" controls in wxPython
and it can be used to build round or custom-shaped buttons from images with
alpha(PNG).


Description
-----------

`ShapedBitmapButton` tries to fill the lack of "custom shaped" controls in wxPython
(that depends on the same lack in wxWidgets). It can be used to build round
buttons or elliptic buttons.

`ShapedBitmapButton` is based on a :class:`Window`, in which multiple images are
drawn depending on the button state (pressed, not pressed, hovering, disabled).

`ShapedBitmapButton` has the ability to draw it's parent widgets background
colour or tiled bitmap, so that everything looks nice.

`ShapedBitmapButton` reacts on mouse events *only* if the mouse event occurred inside
the image region, even if `ShapedBitmapButton` is built on a rectangular window.


Usage
-----

Usage example::

    import wx
    import wx.lib.mcow.shapedbitmapbutton as SBB

    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, "ShapedBitmapButton Demo")

            # Optionally define a bitmap to use for the Paint Event Handler and
            # the ShapedBitmapButtons parentBgBmp keywordArg.
            bmp = wx.Bitmap('seamless.png', wx.BITMAP_TYPE_PNG)
            self.backgroundBitmap = SBB.ShapedBitmapButton.MakeDisplaySizeBackgroundBitmap(bmp)

            # Create 1-5 bitmaps for the button. bitmap is required.
            sButton = SBB.ShapedBitmapButton(self, -1,
                bitmap=wx.Bitmap('shapedbitmapbutton-normal.png', wx.BITMAP_TYPE_PNG),
                pressedBmp=wx.Bitmap('shapedbitmapbutton-pressed.png', wx.BITMAP_TYPE_PNG),
                hoverBmp=wx.Bitmap('shapedbitmapbutton-hover.png', wx.BITMAP_TYPE_PNG),
                disabledBmp=wx.Bitmap('shapedbitmapbutton-disabled.png', wx.BITMAP_TYPE_PNG),
                parentBgBmp=self.backgroundBitmap,
                pos=(20, 20))
            sButton.Bind(wx.EVT_BUTTON, self.OnButton)

            # Optionally Add these for the custom background painting.
            self.Bind(wx.EVT_PAINT, self.OnPaint)
            self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        def OnButton(self, event):
            print('wxPython Rocks!')

        def OnEraseBackground(self, event):
            pass

        def OnPaint(self, event):
            dc = wx.BufferedPaintDC(self)
            dc.Clear()
            dc.DrawBitmap(self.backgroundBitmap, 0, 0, True)

    # our normal wxApp-derived class, as usual

    app = wx.App(0)

    frame = MyFrame(None)
    app.SetTopWindow(frame)
    frame.Show()

    app.MainLoop()


Methods and Settings
--------------------

With `ShapedBitmapButton` you can:

- Create rounded/elliptical buttons/togglebuttons;
- Set images for the enabled/disabled/focused/selected state of the button;
- Set an background image (will be tiled-seamless textures work best) for the button;
- Create other great looking custom widgets(Ex: Notebook Tabs, Personas, Graphical Grids/Tables)
  fast and easily with images containing alpha;
- Create point and click games/apps;
- Never worry about the calculating the custom shape of your buttons again;
- Improve the look and functionality of current basic buttons in applications;

TODO Methods:

- Draw the focus indicator (or disable it);
- Draw the focus indicator and label with(Option for Adjustable Blur/DropShadows);
- Set label colour and font(LabelEnable);
- Apply a rotation/pos to the `ShapedBitmapButton` label;
- Change `ShapedBitmapButton` size and text orientation in runtime.(Ex: SVG);
- Integrate CheckBox Functionalities so a 3-way/multiple way CustomCheckbox is possible.


Window Styles
-------------

`No particular window styles are available for this class.`


Events Processing
-----------------

This class processes the following events:

================= ==================================================
Event Name        Description
================= ==================================================
``wx.EVT_BUTTON`` Process a `wxEVT_COMMAND_BUTTON_CLICKED` event, when the button is clicked.
================= ==================================================


Supported Platforms
-------------------
:class:`ShapedBitmapButton` has been tested on the following platforms:
  * Windows (Windows XP, 7).


License And Version
-------------------

`ShapedBitmapButton` is distributed under the wxPython license.

Edward Greig, @ 17 Jan 2014
Latest revision: Edward Greig @ 24 Nov 2015, 21.00 GMT

Version 0.3.2

-------------------

Modified file for my needs (Ecco).

"""

##  import time # DEBUGGING
import wx
from wx import GetMousePosition as wxGetMousePosition

## print(wx.version())
PHOENIX = 'phoenix' in wx.version()
if PHOENIX:
    # Classic Vs.Phoenix Compatibility/Deprecations.
    wx.RegionFromBitmapColour = wx.Region
    wx.PyCommandEvent = wx.CommandEvent
    wx.PyControl = wx.Control
    wx.EmptyBitmap = wx.Bitmap
    wx.BrushFromBitmap = wx.Brush

# def MakeDisplayWidthBackgroundBitmap
# def MakeDisplayHeightBackgroundBitmap
# def MakeDisplaySizeBackgroundBitmap
# class ShapedBitmapButtonEvent 
# class ShapedBitmapButton
# class ShapedBitmapButtonAdv

HOVER = 1
""" Flag used to indicate that the mouse is hovering on a :class:`ShapedBitmapButton`. """
CLICK = 2
""" Flag used to indicate that the :class:`ShapedBitmapButton` is on a pressed state. """


def MakeDisplayWidthBackgroundBitmap(bitmap=wx.NullBitmap):
    """
    Makes and returns a display width size(fullscreen width x bitmap height) bitmap
    to tile seamlessly for the :class:`ShapedBitmapButton`'s parent.
    This should be the same visually as for, example the parent widget's
    Paint handler would produce.

    :param `bitmap`: the bitmap to be tiled, an instance of :class:`Bitmap`.
    :returns: a display width size bitmap to be tiled, an instance of :class:`Bitmap`.
    :rtype: :class:`Bitmap`
    """

    if not bitmap:
        raise Exception('Need a Bitmap!')  # TODO Make Custom Exception Class??? MissingBitmapError...
    bmpW = bitmap.GetWidth()
    bmpH = bitmap.GetHeight()
    if not bmpW or not bmpH:
        raise Exception('Bitmap width and height should be greater than 0!')
    width, height = wx.GetDisplaySize()
    bmp = wx.EmptyBitmap(width, bmpH)
    mdc = wx.MemoryDC(bmp)

    bmpBrush = wx.BrushFromBitmap(bitmap)
    mdc.SetBrush(bmpBrush)
    mdc.DrawRectangle(-1, -1, width + 2, bmpH + 2)
    # ...or this would work too. timeit: BrushFromBitmap way is faster.
    ## localDrawBitmap = mdc.DrawBitmap
    ## [localDrawBitmap(bitmap, x, 0, True)
    ##     for x in range(0, width, bmpW)]

    return mdc.GetAsBitmap(wx.Rect(0, 0, width, bmpH))


def MakeDisplayHeightBackgroundBitmap(bitmap=wx.NullBitmap):
    """
    Makes and returns a display height size(bitmap width x fullscreen height) bitmap
    to tile seamlessly for the :class:`ShapedBitmapButton`'s parent.
    This should be the same visually as for, example the parent widget's
    Paint handler would produce.

    :param `bitmap`: the bitmap to be tiled, an instance of :class:`Bitmap`.
    :returns: a display height size bitmap to be tiled, an instance of :class:`Bitmap`.
    :rtype: :class:`Bitmap`
    """
    if not bitmap:
        raise Exception('Need a Bitmap!')  # TODO Make Custom Exception Class??? MissingBitmapError...
    bmpW = bitmap.GetWidth()
    bmpH = bitmap.GetHeight()
    if not bmpW or not bmpH:
        raise Exception('Bitmap width and height should be greater than 0!')
    width, height = wx.GetDisplaySize()
    bmp = wx.EmptyBitmap(bmpW, height)
    mdc = wx.MemoryDC(bmp)

    bmpBrush = wx.BrushFromBitmap(bitmap)
    mdc.SetBrush(bmpBrush)
    mdc.DrawRectangle(-1, -1, bmpW + 2, height + 2)
    # ...or this would work too. timeit: BrushFromBitmap way is faster.
    ## localDrawBitmap = mdc.DrawBitmap
    ## [localDrawBitmap(bitmap, 0, y, True)
    ##     for y in range(0, height, bmpH)]

    return mdc.GetAsBitmap(wx.Rect(0, 0, bmpW, height))


def MakeDisplaySizeBackgroundBitmap(bitmap=wx.NullBitmap):
    """
    Makes and returns a display size(fullscreen width x height) bitmap
    to tile seamlessly for the :class:`ShapedBitmapButton`'s parent.
    This should be the same visually as for, example the parent widget's
    Paint handler would produce.

    :param `bitmap`: the bitmap to be tiled, an instance of :class:`Bitmap`.
    :returns: a display size bitmap to be tiled, an instance of :class:`Bitmap`.
    :rtype: :class:`Bitmap`
    """
    if not bitmap:
        raise Exception('Need a Bitmap!')  # TODO Make Custom Exception Class??? MissingBitmapError...
    bmpW = bitmap.GetWidth()
    bmpH = bitmap.GetHeight()
    if not bmpW or not bmpH:
        raise Exception('Bitmap width and height should be greater than 0!')
    width, height = wx.GetDisplaySize()
    bmp = wx.EmptyBitmap(width, height)
    mdc = wx.MemoryDC(bmp)

    bmpBrush = wx.BrushFromBitmap(bitmap)
    mdc.SetBrush(bmpBrush)
    mdc.DrawRectangle(-1, -1, width + 2, height + 2)
    # ...or this would work too. timeit: BrushFromBitmap way is faster.
    ## localDrawBitmap = mdc.DrawBitmap
    ## [[localDrawBitmap(bitmap, x, y, True)
    ##     for y in range(0, height, bmpH)]
    ##         for x in range(0, width, bmpW)]

    return mdc.GetAsBitmap(wx.Rect(0, 0, width, height))


class ShapedBitmapButtonEvent(wx.PyCommandEvent):
    """ Event sent from :class:`ShapedBitmapButton` when the button is activated. """

    def __init__(self, eventType, eventId):
        """
        Default class constructor.

        :param `eventType`: the event type;
        :param `eventId`: the event identifier.
        """

        wx.PyCommandEvent.__init__(self, eventType, eventId)
        self.isDown = False
        self.theButton = None

    def SetIsDown(self, isDown):
        """
        Sets the button event as pressed.

        :param `isDown`: ``True`` to set the event as "pressed", ``False`` otherwise.
        """

        self.isDown = isDown

    def GetIsDown(self):
        """ Returns ``True`` if the button event is "pressed". """

        return self.isDown

    def SetButtonObj(self, btn):
        """
        Sets the event object for the event.

        :param `btn`: the button object, an instance of :class:`ShapedBitmapButton`.
        """

        self.theButton = btn

    def GetButtonObj(self):
        """
        Returns the object associated with this event.

        :return: An instance of :class:`ShapedBitmapButton`.
        """

        return self.theButton


class ShapedBitmapButton(wx.PyControl):
    """ This is the main class implementation of :class:`ShapedBitmapButton`. """
    def __init__(self, parent, id=wx.ID_ANY, bitmap=wx.NullBitmap,
                 pressedBmp=None, hoverBmp=None, disabledBmp=None, parentBgBmp=None,
                 label="", labelEnable=True, labelForeColour=wx.BLACK, labelBackColour=wx.TransparentColour,
                 labelStrokeColour=wx.WHITE,
                 labelStrokeWidth=0, labelDropShadowBlur=3, labelDropShadowDist=3,
                 labelFont=None, labelPosition=None, labelRotation=0.0,                #<-- Modif here  / labelPosition=(0, 0)
                 raiseOnSetFocus=True,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.NO_BORDER, validator=wx.DefaultValidator,
                 name="shapedbutton"):
        """
        Default class constructor.

        :param `parent`: the :class:`ShapedBitmapButton` parent;
        :param `id`: window identifier. A value of -1 indicates a default value;
        :param `bitmap`: the button bitmap (if any);
        :param `pressedBmp`: the pressed button bitmap (if any);
        :param `hoverBmp`: the hover button bitmap (if any);
        :param `disabledBmp`: the disabled button bitmap (if any);
        :param `label`: the button text label;
        :param `labelEnable`: draw the label?;
        :param `labelForeColour`: the label foreground colour;
        :param `labelBackColour`: the label background colour;
        :param `labelBackgroundMode`: ``wx.TRANSPARENT``(default) or ``wx.SOLID``;
        :param `pos`: the control position. A value of (-1, -1) indicates a default position,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `size`: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `style`: the button style (unused);
        :param `validator`: the validator associated to the button;
        :param `name`: the button name.
        """

        wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)

######################## MODIFIED HERE
        self.SetDoubleBuffered(True)    ## IMPORTANT
########################
        
        self.parent = parent

        self._bitmap = bitmap
        ## if not bitmap.GetWidth() and not bitmap.GetHeight(): # wx.NullBitmap
        ##     self._bitmap = wx.Bitmap(1, 1)

        self._pressedBmp = pressedBmp
        self._hoverBmp = hoverBmp
        try:
            self._disabledBmp = disabledBmp or bitmap.ConvertToDisabled()
        except AttributeError:
            self._disabledBmp = disabledBmp or \
                bitmap.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()

        self._regionColour = wx.TransparentColour  # wx.Colour(0, 0, 0, 0)  # Alpha
        self._region = wx.RegionFromBitmapColour(bitmap, self._regionColour)

        self._parentBgBmp = parentBgBmp

        self._raiseOnSetFocus = raiseOnSetFocus
        self._makeChildBmp = False  # Used by ShapedBitmapButton children
        self._sbbChildBmp = None    # Used by ShapedBitmapButton children

        self._mouseAction = None
        #self._hasFocus = False
        self._mouseIsInRegion = False
        # Label attributes.
        self._label = label
        self._labelsList = []
        self._labelEnable = labelEnable
        self._labelBackColour = labelBackColour
        self._labelForeColour = labelForeColour
        self._labelStrokeColour = labelStrokeColour
        self._labelStrokeWidth = labelStrokeWidth
        self._labelDropShadowBlur = labelDropShadowBlur
        self._labelDropShadowDist = labelDropShadowDist
        self._labelPosition = labelPosition
        self._labelRotation = float(labelRotation)
        self._labelFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT) if not labelFont else labelFont

        self_Bind = self.Bind
        self_Bind(wx.EVT_SIZE, self.OnSize)
        self_Bind(wx.EVT_PAINT, self.OnPaint)
        self_Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self_Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self_Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self_Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self_Bind(wx.EVT_RIGHT_DCLICK, self.OnRightDClick)
        self_Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self_Bind(wx.EVT_MIDDLE_DOWN, self.OnMiddleDown)
        self_Bind(wx.EVT_MIDDLE_DCLICK, self.OnMiddleDClick)
        self_Bind(wx.EVT_MIDDLE_UP, self.OnMiddleUp)
        self_Bind(wx.EVT_MOUSE_AUX1_DOWN, self.OnAux1Down)
        self_Bind(wx.EVT_MOUSE_AUX1_UP, self.OnAux1Up)
        self_Bind(wx.EVT_MOUSE_AUX1_DCLICK, self.OnAux1DClick)
        self_Bind(wx.EVT_MOUSE_AUX2_DOWN, self.OnAux2Down)
        self_Bind(wx.EVT_MOUSE_AUX2_UP, self.OnAux2Up)
        self_Bind(wx.EVT_MOUSE_AUX2_DCLICK, self.OnAux2DClick)
        self_Bind(wx.EVT_MOTION, self.OnMotion)
        self_Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self_Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        self_Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        # self_Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        self_Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self_Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self_Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self_Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        # self_Bind(wx.EVT_SET_FOCUS, self.OnGainFocus)
        # self_Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)

        self.SetLabel(label)
######################## MODIFIED HERE
        # Thanks to Andrea Gavanna.
        # Initialize the focus pen colour/dashes,
        # for faster drawing later.
        self.InitializeColours()   
########################
        self.InheritAttributes()
        self.SetInitialSize(size)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        imAChild = hasattr(self.GetParent(), '_sbbChildBmp')
        if imAChild:  # I am a child here.
            wx.CallAfter(self.parent.MakeChildBmp)
            wx.CallAfter(self.Refresh)
 
######################## MODIFIED HERE        
    def InitializeColours(self):
        """
        Thanks to Andrea Gavana. 
        Initializes the focus indicator pen.
        """
        textClr = wx.WHITE   #000000
        if wx.Platform == "__WXMAC__":
            self._focusIndPen = wx.Pen(textClr, 1, wx.SOLID)
        else:
            self._focusIndPen = wx.Pen(colour=textClr,
                                       width=1,
                                       style=wx.PENSTYLE_USER_DASH)
                                       # wx.PENSTYLE_TRANSPARENT)
            self._focusIndPen.SetDashes([1,1])
            self._focusIndPen.SetCap(wx.CAP_BUTT)    
########################

    def UpdateBackgroundColourFromParent(self):
        self.SetBackgroundColour(self.parent.GetBackgroundColour())
        self.Refresh()

    def Rotate180(self):
        """
        Rotates the button bitmaps by 180 degrees.
        """
        self._bitmap = self._bitmap.ConvertToImage().Rotate180().ConvertToBitmap()
        self._pressedBmp = self._pressedBmp.ConvertToImage().Rotate180().ConvertToBitmap()
        self._hoverBmp = self._hoverBmp.ConvertToImage().Rotate180().ConvertToBitmap()
        self._disabledBmp = self._disabledBmp.ConvertToImage().Rotate180().ConvertToBitmap()
        self._region = wx.RegionFromBitmapColour(self._bitmap, self._regionColour)

    def Rotate90(self, clockwise=True):
        """
        Rotates the button bitmaps 90 degrees in the direction indicated by ``clockwise``.

        :param `clockwise`: ``True`` for horizontally and ``False`` for vertically.
        :type `clockwise`: bool
        """

        self._bitmap = self._bitmap.ConvertToImage().Rotate90(clockwise).ConvertToBitmap()
        self._pressedBmp = self._pressedBmp.ConvertToImage().Rotate90(clockwise).ConvertToBitmap()
        self._hoverBmp = self._hoverBmp.ConvertToImage().Rotate90(clockwise).ConvertToBitmap()
        self._disabledBmp = self._disabledBmp.ConvertToImage().Rotate90(clockwise).ConvertToBitmap()
        self._region = wx.RegionFromBitmapColour(self._bitmap, self._regionColour)

    def Mirror(self, horizontally=True):
        """
        Mirrors the button. The parameter ``horizontally`` indicates the orientation.

        :param `horizontally`: ``True`` for horizontally and ``False`` for vertically.
        :type `horizontally`: bool
        """
        self._bitmap = self._bitmap.ConvertToImage().Mirror(horizontally).ConvertToBitmap()
        self._pressedBmp = self._pressedBmp.ConvertToImage().Mirror(horizontally).ConvertToBitmap()
        self._hoverBmp = self._hoverBmp.ConvertToImage().Mirror(horizontally).ConvertToBitmap()
        self._disabledBmp = self._disabledBmp.ConvertToImage().Mirror(horizontally).ConvertToBitmap()
        self._region = wx.RegionFromBitmapColour(self._bitmap, self._regionColour)

    def GetBackgroundBitmap(self):
        return self._parentBgBmp

    def SetBackgroundBitmap(self, bitmap):
        self._parentBgBmp = bitmap

    @staticmethod
    def WillLabelTextFitInsideButton(bitmap, text, font=None):
        """
        Will the text(unrotated) fit inside the buttons rectangle.

        :param `bitmap`: the bitmap for the button
        :type `bitmap`: `wx.Bitmap`
        :param `text`: text to measure
        :type `text`: str
        :param `font`: font for the text
        :type `font`: `wx.Font`
        """
        sdc = wx.ScreenDC()
        if PHOENIX:
            width, height, lineHeight = sdc.GetFullMultiLineTextExtent(text, font)
        else:
            width, height, lineHeight = sdc.GetMultiLineTextExtent(text, font)
        bmpW = bitmap.GetWidth()
        bmpH = bitmap.GetHeight()
        return width < bmpW and height < bmpH

    def GetLabel(self):
        """
        Get the buttons text label.

        :returns: The buttons text label to be drawn.
        :rtype: str
        """
        return self._label

    def SetLabel(self, label=None):
        """
        Set the buttons text label.

        :param `label`: The buttons text label to be drawn.
        :type `label`: str
        """
        if label is None:
            label = ''
        self._label = label

    def GetLabelsList(self):
        """
        Get the buttons text labels list.

        :returns: The list of [labels, coords, foregrounds, backgrounds] to be drawn.
        :rtype: list
        """
        return self._labelsList

    def SetLabelsList(self, labelsList=[], coords=[], foregrounds=[], backgrounds=[], fonts=[], rotations=[]):
        """
        Set the buttons text labels list.

        :param `labelsList`: A list of text labels to be drawn.
        :type `labelsList`: list
        :param `coords`: A list of (x,y) positions. List length must be equal to the length of labelsList.
        :type `coords`: list
        :param `foregrounds`: A list of wx.Colour objects to use for the foregrounds of the strings. If nothing is passed, use the default colour in the constructor.
        :type `foregrounds`: list of wx.Colours or a single wx.Colour
        :param `backgrounds`: A list of wx.Colour objects to use for the backgrounds of the strings. If nothing is passed, use the default colour in the constructor.
         Note: ``wx.TransparentColour`` is a valid colour for the text backgrounds.
        :type `backgrounds`: list of wx.Colours or a single wx.Colour
        :param `fonts`: A list of wx.Font objects to use for the fonts of the strings. If nothing is passed, use the default font in the constructor.
        :type `fonts`: list of fonts or a single wx.Font
        :param `rotations`: A list of floats to use for the rotations of the strings. If nothing is passed, use the default rotation in the constructor.
        :type `rotations`: list of floats or a single float
        """
        if not labelsList:
            self._labelsList = labelsList
            return
        assert len(labelsList) == len(coords) # == len(foregrounds) == len(backgrounds) == len(fonts) == len(rotations)
        if not foregrounds:
            fg = self._labelForeColour
            foregrounds = [fg] * len(labelsList)
        elif isinstance(foregrounds, wx.Colour):
            foregrounds = [foregrounds] * len(labelsList)
        if not backgrounds:
            bg = self._labelBackColour
            backgrounds = [bg] * len(labelsList)
        elif isinstance(backgrounds, wx.Colour):
            backgrounds = [backgrounds] * len(labelsList)
        if not fonts:
            fnt = self._labelFont
            fonts = [fnt] * len(labelsList)
        elif isinstance(fonts, wx.Font):
            fonts = [fonts] * len(labelsList)
        if not rotations:
            rot = self._labelRotation
            rotations = [rot] * len(labelsList)
        elif isinstance(rotations, (int, float)):
            rotations = [rotations] * len(labelsList)
        rotations = [float(rot) for rot in rotations]

        self._labelsList = zip(labelsList, coords, foregrounds, backgrounds, fonts, rotations)

    def GetLabelEnabled(self):
        """
        :returns: ``True`` if the button's label is enabled, ``False`` otherwise.
        :rtype: bool
        """
        return self._labelEnable

    def SetLabelEnabled(self, enable=True):
        """
        Set whether the label should be drawn for :class:`ShapedBitmapButton`.

        :param `enable`: ``True`` to enable drawing the button's label, ``False`` to disable it.
        :type `enable`: bool
        """
        self._labelEnable = enable

    def GetLabelColour(self):
        """
        Get the button label colour.

        :returns: the button label colour.
        :rtype: `wx.Colour`
        """

        return self._labelForeColour

    def SetLabelColour(self, colour=None):
        """
        Sets the button label colour.

        :param `colour`: an instance of :class:`Colour`.
        """

        if colour is None:
            colour = wx.BLACK

        self._labelForeColour = colour

    def SetLabelRotation(self, angle=None):
        """
        Sets angle of button label rotation.

        :param `angle`: the label rotation, in degrees.
        :type `angle`: float
        """

        if angle is None:
            angle = 0

        self._labelRotation = float(angle)

    def SetLabelPosition(self, pos=None):
        """
        Sets the position of button label.

        :param `pos`: the label position.
        :type `pos`: point
        """

#        if pos is None:                 <----------- Modif here
#            pos = (0, 0)

        self._labelPosition = pos
        self.Refresh()

    def OnEraseBackground(self, event):
        """
        Handles the ``wx.EVT_ERASE_BACKGROUND`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`EraseEvent` event to be processed.
        """

        # This is intentionally empty, because we are using the combination
        # of wx.BufferedPaintDC + an empty OnEraseBackground event to
        # reduce flicker
        pass

    def DoGetBestSize(self):

        return self._bitmap.GetSize()

    def AcceptsFocus(self):
        """
        Can this window be given focus by mouse click?

        :note: Overridden from `wx.PyControl`.
        """

        return self.IsShown() and self.IsEnabled()

    def Enable(self, enable=True):
        """
        Enables/disables the button.

        :param `enable`: ``True`` to enable the button, ``False`` to disable it.

        :note: Overridden from :class:`PyControl`.
        """

        wx.PyControl.Enable(self, enable)
        self.Refresh()

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`SizeEvent` event to be processed.
        """
        self.Refresh()
        event.Skip()
        # print('OnSize')

    def SetParentBackgroundBitmap(self, bitmap):
        """
        Sets the bitmap to tile seamlessly for the :class:`ShapedBitmapButton`'s parent.
        This should be the same visually as for, example the parent widget's
        Paint handler would produce.

        :param `bitmap`: the bitmap to set, an instance of :class:`Bitmap`.
        """
        self._parentBgBmp = bitmap

    def GetBitmap(self):
        """
        Gets the bitmap for the :class:`ShapedBitmapButton`.

        :returns: the bitmap
        :rtype: `wx.Bitmap`
        """

        return self._bitmap

    def SetBitmap(self, bitmap):
        """
        Sets the bitmap for the :class:`ShapedBitmapButton`.

        :param `bitmap`: the bitmap to set, an instance of :class:`Bitmap`.
        """

        self._bitmap = bitmap
        self.Refresh()

    def GetBitmapPressed(self):
        """
        Gets the pressed bitmap for the :class:`ShapedBitmapButton`.

        :returns: the pressed bitmap
        :rtype: `wx.Bitmap`
        """
               
        return self._pressedBmp

    def SetBitmapPressed(self, bitmap):
        """
        Sets the pressed bitmap for the :class:`ShapedBitmapButton`.

        :param `bitmap`: the pressed bitmap to set, an instance of :class:`Bitmap`.
        """

        self._pressedBmp = bitmap
        self.Refresh()

    def GetBitmapHover(self):
        """
        Gets the hover bitmap for the :class:`ShapedBitmapButton`.

        :returns: the hover bitmap
        :rtype: `wx.Bitmap`
        """

        return self._hoverBmp

    def SetBitmapHover(self, bitmap):
        """
        Sets the hover bitmap for the :class:`ShapedBitmapButton`.

        :param `bitmap`: the hover bitmap to set, an instance of :class:`Bitmap`.
        """

        self._hoverBmp = bitmap
        self.Refresh()

    def GetBitmapDisabled(self):
        """
        Gets the disabled bitmap for the :class:`ShapedBitmapButton`.

        :returns: the disabled bitmap
        :rtype: `wx.Bitmap`
        """

        return self._disabledBmp

    def SetBitmapDisabled(self, bitmap):
        """
        Sets the disabled bitmap for the :class:`ShapedBitmapButton`.

        :param `bitmap`: the disabled bitmap to set, an instance of :class:`Bitmap`.
        """

        self._disabledBmp = bitmap
        self.Refresh()

    def GetSBBChildren(self):
        childrenShapedBitmapButtons = [
                sbb for sbb in self.GetChildren()
                     if isinstance(sbb, ShapedBitmapButton)]
        return childrenShapedBitmapButtons

    def GetSBBSiblings(self):
        """
        Get a list of all the parents shaped bitmap buttons
        instances minus myself.
        """
        parent = self.GetParent()
        if not parent:  # Probably been/being deleted.
            return
        siblingShapedBitmapButtons = [
                sbb for sbb in parent.GetChildren()
                     if isinstance(sbb, ShapedBitmapButton)]
        siblingShapedBitmapButtons.remove(self)
        return siblingShapedBitmapButtons

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """
        # print('OnPaint - ShapedBitmapButton %s' % time.time()) # Debug/Optimize how many times Refresh is firing off.
        # print('children', self.GetChildren())

######################## MODIFIED HERE
        #dc = wx.BufferedPaintDC(self)
        dc = wx.AutoBufferedPaintDCFactory(self)
########################
        
        bitmap = self._bitmap

        parent = self.GetParent()
        if not parent:  # Probably been/being deleted.
            return
        dc.SetBackground(wx.Brush(parent.GetBackgroundColour()))
        dc.Clear()
        dc_DrawBitmap = dc.DrawBitmap

        imAChild = hasattr(parent, '_sbbChildBmp')
        if imAChild:  # I am a child here.
            parent.MakeChildBmp()
            dc.SetBackground(wx.Brush(parent.GetParent().GetBackgroundColour()))
            pos = self.GetPosition()
            sz = self.GetSize()
            parent_sbbChildBmp = parent._sbbChildBmp
            if parent_sbbChildBmp:
                dc_DrawBitmap(parent_sbbChildBmp.
                              GetSubBitmap(wx.Rect(pos[0], pos[1], sz[0], sz[1])), 0, 0, True)
        # @ NOTE: This section of code could cause errors with various sizers
        #         when sizing the frame to zilch/nothing.
        # @ except wx._core.wxAssertionError, wx._core.PyAssertionError:
        elif self._parentBgBmp:
            sz = self.Size  # sz = self.GetSize()
            # print('sz = %s, parentSz = %s' % (sz, self.parent.GetSize()))
            if sz[0] and sz[1]:  # if x or y is 0 it WILL cause major fubar havok; BoxSizer, WrapSizer
                pos = self.Position  # pos = self.GetPosition()
                # print('pos = %s, parentPos = %s' % (pos, self.parent.GetPosition()))
                if (pos[0] >= 0) and (pos[1] >= 0) and (pos[0]+sz[0] >= sz[0]) and (pos[1]+sz[1] >= sz[1]): # GridSizer fubar havok
                    dc_DrawBitmap(self._parentBgBmp.
                        GetSubBitmap(wx.Rect(pos[0], pos[1], sz[0], sz[1])), 0, 0, True)
                else:  # Something is better than nothing even if it is off a bit. TODO: Try to recalculate correct overlaying of GetSubBitmap
                    dc_DrawBitmap(self._parentBgBmp, 0, 0, True)

        if self._mouseAction == CLICK:
            bitmap = self._pressedBmp or bitmap
        elif self._mouseAction == HOVER:
            bitmap = self._hoverBmp or bitmap
        elif not self.IsEnabled():
            bitmap = self._disabledBmp or bitmap

        dc_DrawBitmap(bitmap, 0, 0)


            
            
        if self._labelEnable and self._labelsList or self._label:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            transparentColour = wx.TransparentColour
            transparent = wx.TRANSPARENT
            solid = wx.SOLID
            if self._labelsList:
                dc_SetBackgroundMode = dc.SetBackgroundMode
                dc_SetTextForeground = dc.SetTextForeground
                dc_SetTextBackground = dc.SetTextBackground
                dc_SetFont = dc.SetFont
                dc_DrawRotatedText = dc.DrawRotatedText
                for label, coords, foreground, background, font, rotation in self._labelsList:
                    if background == transparentColour:
                        dc_SetBackgroundMode(transparent)
                    else:
                        dc_SetBackgroundMode(solid)
                    dc_SetTextForeground(foreground)
                    dc_SetTextBackground(background)
                    dc_SetFont(font)
                    dc_DrawRotatedText(label,
                                       coords[0],
                                       coords[1],
                                       rotation)
            else:  # self._label
                if self._labelBackColour == transparentColour:
                    dc.SetBackgroundMode(transparent)
                else:
                    dc.SetBackgroundMode(solid)
                dc.SetTextBackground(self._labelBackColour)
                dc.SetTextForeground(self._labelForeColour)
                dc.SetFont(self._labelFont)



######################## MODIFIED HERE (CENTERED TEXT / BTN BACKGROUND COLOR)

                # Get the working rectangle we can draw in.
                rect = self.GetClientRect()
                x, y = self.GetSize()

                rect = wx.Rect(rect.x, rect.y,
                               rect.width, rect.height)

#                gcdc.SetFont(boldFont)
                # Get the text color.
#                dc.SetTextForeground(self.foreground)
#                dc.DrawLabel(self._label, rect, wx.ALIGN_CENTER)


                # Get button size.
                w, h = self.GetSize()
                dc.SetBrush(wx.Brush("#6c921e"))        
                dc.DrawRoundedRectangle(1, 1, w-2, h-2, 4)
            
                dc.DrawLabel(self._label,
                                   rect,
                                   #self._labelPosition[0],
                                   #self._labelPosition[1],
                                   wx.ALIGN_CENTER,
                                   self._labelRotation)


        if self._mouseAction == CLICK:   #<------------------------  ADD HERE
            # Get the working rectangle we can draw in.
            rect = self.GetClientRect()
            x, y = self.GetSize()

            rect = wx.Rect(rect.x, rect.y,
                           rect.width, rect.height)

            # Get button size.
            w, h = self.GetSize()
            dc.SetBrush(wx.Brush("#1473e6"))   # or   #1473e6    ???? Scintillement maintenir barre espace et bouger la souris sur la frame 
            dc.DrawRoundedRectangle(1, 1, w-2, h-2, 4)

            dc.DrawLabel(self._label,
                        rect,
                        #self._labelPosition[0],
                        #self._labelPosition[1],
                        wx.ALIGN_CENTER,
                        self._labelRotation)


            
        if self._mouseAction == HOVER:   #<------------------------  ADD HERE
            # Get the working rectangle we can draw in.
            rect = self.GetClientRect()
            x, y = self.GetSize()

            rect = wx.Rect(rect.x, rect.y,
                           rect.width, rect.height)

            # Get button size.
            w, h = self.GetSize()
            dc.SetBrush(wx.Brush("#46a0f5"))        
            dc.DrawRoundedRectangle(1, 1, w-2, h-2, 4)

            dc.DrawLabel(self._label,
                        rect,
                        #self._labelPosition[0],
                        #self._labelPosition[1],
                        wx.ALIGN_CENTER,
                        self._labelRotation)

                
        if self._makeChildBmp:  # I am a parent here.
            self._sbbChildBmp = dc.GetAsBitmap()
            self._makeChildBmp = False


#222
            
######################## MODIFIED HERE (FOCUS STATE / WHITE BORDER)
######################## MODIFIED HERE (KEYBOARD FOCUS STATE / BLUE BORDER)
            
        # Thanks to Andrea Gavana. 
        # Get button size.
        w, h = self.GetSize()
            
        # Thanks to Andrea Gavana.       
        # Let's see if we have keyboard focus and, if this is the case,
        # we draw a dotted rectangle around the text (Windows behavior,
        # I don't know on other platforms...).
        if self.HasFocus():
            # Yes, we are focused! So, now, use a transparent brush with
            # a dotted black pen to draw a rectangle around the text.
            dc = wx.GCDC(dc)

            self.color = wx.WHITE  #<------- Focus int. bouton
            # White focus Stroke.
            pen = wx.Pen(colour=self.color,
                         width=0,
                         style=wx.PENSTYLE_USER_DASH)
            pen.SetDashes([1,1])
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetPen(pen)
            #dc.DrawRectangle(5, 5, w-10, h-10)
            dc.DrawRoundedRectangle(5, 5, w-11, h-11, 2)

            self.color = "#fdf240"  #<------- Focus ext. bouton  #94c3f0
            # Blue focus Stroke.
            pen = wx.Pen(colour=self.color,
                         width=3,
                         style=wx.PENSTYLE_SOLID)
            dc.SetPen(pen)
            dc.DrawRoundedRectangle(1, 1, w-2, h-2, 4)

######################## ADD HERE (NORMAL STATE / WHITE BORDER) ######################################
            
        else :
            # Yes, we are focused! So, now, use a transparent brush with
            # a dotted black pen to draw a rectangle around the text.
            dc = wx.GCDC(dc)

            self.color = wx.WHITE
            # Blue focus Stroke.
            pen = wx.Pen(colour=self.color,
                         width=3,
                         style=wx.PENSTYLE_SOLID)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetPen(pen)
            dc.DrawRoundedRectangle(1, 1, w-2, h-2, 4)
            
        self.Refresh()
        event.Skip()

# dc.SetBrush(wx.Brush(wx.BLACK))

########################################################################################################### 
        
    def MakeChildBmp(self):
        self._makeChildBmp = True
        # self.Refresh()

    def OnKeyDown(self, event):
        """
        Handles the ``wx.EVT_KEY_DOWN`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`KeyEvent` event to be processed.
        """

        hasFocus = self.HasFocus()
        if hasFocus and event.GetKeyCode() == ord(" "):
            if self.HasCapture():
                self.ReleaseMouse()
            self._mouseAction = CLICK
            self.CaptureMouse()
            self.Refresh()

        elif hasFocus and self.HasFlag(wx.WANTS_CHARS) and wx.GetKeyState(wx.WXK_RETURN):
            if self.HasCapture():
                self.ReleaseMouse()
            self._mouseAction = CLICK
            self.CaptureMouse()
            self.Refresh()

        # print('PROCESS_ENTER', self.HasFlag(wx.PROCESS_ENTER))
        # print('WANTS_CHARS', self.HasFlag(wx.WANTS_CHARS))

        event.Skip()
        # print('OnKeyDown')

    def OnKeyUp(self, event):
        """
        Handles the ``wx.EVT_KEY_UP`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`KeyEvent` event to be processed.
        """

        hasFocus = self.HasFocus()
        if hasFocus and event.GetKeyCode() == ord(" "):
            if self.HasCapture():
                self.ReleaseMouse()
            self._mouseAction = HOVER
            self.Notify()

        elif hasFocus and self.HasCapture() and not wx.GetKeyState(wx.WXK_RETURN):
            if self.HasCapture():
                self.ReleaseMouse()
            self._mouseAction = None
            self.Notify()

        x, y = event.GetPosition()
        if not self._region.Contains(x, y):
            self._mouseAction = None
        else:
            self._mouseAction = HOVER

        self.Refresh()
        event.Skip()
        # print('OnKeyUp')

    def GetRegion(self):
        """
        Get the region.

        :returns: The region for the shaped bitmap button.
        :rtype: `wx.Region`
        """
        return self._region

    def SetRegion(self, region):
        """
        Set the region.

        :param `region`: The region to set for the shaped bitmap button.
        :type `region`: `wx.Region`
        """
        self._region = region

    def RegionContainsPoint(self, point):
        """
        Does the region contain a point.

        :param `point`: The point to check for in the region.
        :type `point`: `wx.Point`
        """
        return self._region.ContainsPoint(point)

    def RegionContains(self, x, y):
        """
        Does the region contain x, y.

        :param `x`: A  `wx.Point` x value.
        :type `x`: int
        :param `y`: A `wx.Point` y value.
        :type `y`: int
        """
        return self._region.Contains(x, y)

    def OnLeftDown(self, event):
        """
        Handles the ``wx.EVT_LEFT_DOWN`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        ## self._mouseIsInRegion = self_mouseIsInRegion = self.IsMousePositionInRegion()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        parent = self.GetParent()
        ## imAChild = hasattr(parent, '_sbbChildBmp')
        ## if not self_mouseIsInRegion and imAChild:
        ##     selfPosX, selfPosY = self.GetPosition()
        ##     underX, underY = selfPosX + x, selfPosY + y
        ##     if parent._region.Contains(underX, underY):
        ##         # Send the event back to the parent because we are hovering over it and have clicked.
        ##         parent._mouseAction = CLICK
        ##         # parent._mouseIsInRegion = True
        ##         parent.Refresh()
        ##         event.Skip()
        ##         return

        if not self_mouseIsInRegion:  # Pass the wx.EVT_LEFT_DOWN to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(parent, wx.wxEVT_LEFT_DOWN, underX, underY)

        if not self.IsEnabled():
            return

        if self_mouseIsInRegion:
            self._mouseAction = CLICK
            if self.HasCapture():
                self.ReleaseMouse()
            self.CaptureMouse()

            if hasattr(self, '_sbbChildBmp'):
                self.MakeChildBmp()
            self.Refresh()

        event.Skip()

    def OnLeftDClick(self, event):
        """
        Handles the ``wx.EVT_LEFT_DCLICK`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        self.OnLeftDown(event)
        event.Skip()

    def OnLeftUp(self, event):
        """
        Handles the ``wx.EVT_LEFT_UP`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        ## self._mouseIsInRegion = self_mouseIsInRegion = self.IsMousePositionInRegion()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)
        # print('OnLeftUp', self.GetName())

        parent = self.GetParent()
        imAChild = hasattr(parent, '_sbbChildBmp')
        if not self_mouseIsInRegion and imAChild:  # I am a child here.
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            if parent._region.Contains(underX, underY):
                # Send the event back to the parent because we are hovering over it and have clicked.
                # self.parent._mouseIsInRegion = True
                parent._mouseAction = HOVER
                parent.Notify()
                return

        if not self_mouseIsInRegion:  # Pass the wx.EVT_LEFT_UP to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(parent, wx.wxEVT_LEFT_UP, underX, underY)

        if not self.IsEnabled() or not self.HasCapture():
            return

        if self.HasCapture():
            self.ReleaseMouse()

        if self_mouseIsInRegion:
            self._mouseAction = HOVER
            if self.IsMousePositionInAnyChildsRegion():
                pass
            else:
                self.Notify()
        else:
            self._mouseAction = None

        self.Refresh()
        event.Skip()

    def OnRightDown(self, event):
        """
        Handles the ``wx.EVT_RIGHT_DOWN`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_RIGHT_DOWN to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_RIGHT_DOWN, underX, underY)

    def OnRightDClick(self, event):
        """
        Handles the ``wx.EVT_RIGHT_DCLICK`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_RIGHT_DCLICK to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_RIGHT_DCLICK, underX, underY)

    def OnRightUp(self, event):
        """
        Handles the ``wx.EVT_RIGHT_UP`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_RIGHT_UP to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_RIGHT_UP, underX, underY)

    def OnMiddleDown(self, event):
        """
        Handles the ``wx.EVT_MIDDLE_DOWN`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MIDDLE_DOWN to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MIDDLE_DOWN, underX, underY)

    def OnMiddleDClick(self, event):
        """
        Handles the ``wx.EVT_MIDDLE_DCLICK`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MIDDLE_DCLICK to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MIDDLE_DCLICK, underX, underY)

    def OnMiddleUp(self, event):
        """
        Handles the ``wx.EVT_MIDDLE_UP`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MIDDLE_UP to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MIDDLE_UP, underX, underY)

    def OnAux1Down(self, event):
        """
        Handles the ``wx.EVT_MOUSE_AUX1_DOWN`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MOUSE_AUX1_DOWN to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MOUSE_AUX1_DOWN, underX, underY)

    def OnAux1Up(self, event):
        """
        Handles the ``wx.EVT_MOUSE_AUX1_UP`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MOUSE_AUX1_UP to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MOUSE_AUX1_UP, underX, underY)

    def OnAux1DClick(self, event):
        """
        Handles the ``wx.EVT_MOUSE_AUX1_DCLICK`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MOUSE_AUX1_DCLICK to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MOUSE_AUX1_DCLICK, underX, underY)

    def OnAux2Down(self, event):
        """
        Handles the ``wx.EVT_MOUSE_AUX2_DOWN`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MOUSE_AUX2_DOWN to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MOUSE_AUX2_DOWN, underX, underY)

    def OnAux2Up(self, event):
        """
        Handles the ``wx.EVT_MOUSE_AUX2_UP`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MOUSE_AUX2_UP to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MOUSE_AUX2_UP, underX, underY)

    def OnAux2DClick(self, event):
        """
        Handles the ``wx.EVT_MOUSE_AUX2_DCLICK`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MOUSE_AUX2_DCLICK to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MOUSE_AUX2_DCLICK, underX, underY)

    def OnMotion(self, event):
        """
        Handles the ``wx.EVT_MOTION`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        x, y = event.GetPosition()
        ## x, y = event.GetPosition()
        ## x, y = self.ScreenToClient(wxGetMousePosition())
        ## self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        regionContainsPoint = self._region.Contains(x, y)
        parent = self.GetParent()
        imAChild = hasattr(parent, '_sbbChildBmp')

        if not regionContainsPoint and imAChild:  # I am a child here.
            selfPosX, selfPosY = self.GetPosition()
            # print('selfPos = %s, %s' % (selfPosX, selfPosY))
            # print('OnMotion x, y = %s,%s' % (x, y))
            if parent._region.Contains(selfPosX + x, selfPosY + y):
                # Simulate the event back to the parent because we are hovering over it.

                # print('OnMotion x, y = %s,%s' % (x, y))
                # print('self.parent._mouseAction', parent._mouseAction)
                # print('self.parent._mouseIsInRegion', parent._mouseIsInRegion)
                if ((not parent._mouseAction == HOVER) or (not parent._mouseIsInRegion)):  # Don't constantly paint
                    parent._mouseAction = HOVER
                    parent._mouseIsInRegion = True
                    parent.MakeChildBmp()
                    parent.Refresh()

                # print('self.parent._makeChildBmp', parent._makeChildBmp)
                # if self.parent._makeChildBmp:
                #     parent.MakeChildBmp()
                #     parent.Refresh()
                #     parent._makeChildBmp = False

                if self.HasCapture():
                    self._mouseAction = CLICK
                else:
                    self._mouseAction = None
                    if self.GetToolTip():  # HOVER event happens before CLICK.
                        self.GetToolTip().Enable(False)

                self._mouseIsInRegion = False
                # self.Refresh()
                event.Skip()
                return

        if not regionContainsPoint:
            if self._mouseIsInRegion:  # Update Visual.
                self._mouseIsInRegion = False
                if hasattr(self, '_sbbChildBmp'):
                    self.MakeChildBmp()
                self.Refresh()
            self._mouseAction = None
            if self.GetToolTip():  # Only show the tooltip when in region, not when in rect.
                self.GetToolTip().Enable(False)

            # Pass the wx.EVT_MOTION to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(parent, wx.wxEVT_MOTION, underX, underY)

        else:
            if self.HasCapture():
                self._mouseAction = CLICK
            else:
                self._mouseAction = HOVER
                if self.GetToolTip():  # HOVER event happens before CLICK.
                    self.GetToolTip().Enable(True)
            if imAChild:
                parent._mouseAction = None
                parent.MakeChildBmp()
                parent.Refresh()
            if not self._mouseIsInRegion:
                self._mouseIsInRegion = True

                if hasattr(self, '_sbbChildBmp'):
                    self.MakeChildBmp()

                self.Refresh()

        event.Skip()
        ## print('OnMotion (%s, %s)' % (x, y))

    def OnEnterWindow(self, event):
        """
        Handles the ``wx.EVT_ENTER_WINDOW`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled():
            return

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if self_mouseIsInRegion:
            self._mouseAction = HOVER

            self.Refresh()

        event.Skip()

    def OnLeaveWindow(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if self._mouseAction: # not == None
            self._mouseAction = None
            self._mouseIsInRegion = False
            if hasattr(self, '_sbbChildBmp'):
                self.MakeChildBmp()
            self.Refresh()
            # self.Update()

        event.Skip()

    def OnMouseWheel(self, event):
        """
        Handles the ``wx.EVT_MOUSEWHEEL`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        ## x, y = event.GetPosition()
        x, y = self.ScreenToClient(wxGetMousePosition())
        self._mouseIsInRegion = self_mouseIsInRegion = self._region.Contains(x, y)

        if not self_mouseIsInRegion:  # Pass the wx.EVT_MOUSEWHEEL to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(self.parent, wx.wxEVT_MOUSEWHEEL, underX, underY)

    def OnMouseEvents(self, event):
        """
        Handles the ``wx.EVT_MOUSE_EVENTS`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """
        event.Skip()
        NotImplemented
        x, y = event.GetPosition()

        ## if not self._region.Contains(x, y):  # Pass the wx.EVT_MOUSE_EVENTS to the parent
        ##     selfPosX, selfPosY = self.GetPosition()
        ##     underX, underY = selfPosX + x, selfPosY + y
        ##     self.SendMouseEvent(self.parent, wx.wxEVT_???, underX, underY)

    def OnGainFocus(self, event):
        """
        Handles the ``wx.EVT_SET_FOCUS`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`FocusEvent` event to be processed.
        """
        # self._hasFocus = True
        # self.Refresh()
        # self.Update()
        # event.Skip()
        # print('OnGainFocus')
        pass

    def OnLoseFocus(self, event):
        """
        Handles the ``wx.EVT_KILL_FOCUS`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`FocusEvent` event to be processed.
        """
        # self._hasFocus = False
        # self.Refresh()
        # self.Update()
        # event.Skip()
        # print('OnLoseFocus')
        pass

    def OnContextMenu(self, event):
        """
        Handles the ``wx.EVT_CONTEXT_MENU`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`ContextMenuEvent` event to be processed.
        """

        x, y = event.GetPosition()

        if not self._region.Contains(x, y):  # Pass the wx.EVT_CONTEXT_MENU to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendContextMenuEvent(self.parent, underX, underY)

    def SendContextMenuEvent(self, window, x, y):
        cmd = wx.ContextMenuEvent(wx.wxEVT_CONTEXT_MENU)
        cmd.SetEventObject(window)
        cmd.SetId(window.GetId())
        cmd.SetX(x)
        cmd.SetY(y)
        window.GetEventHandler().ProcessEvent(cmd)

    def SendMouseEvent(self, window, mouseType, x, y):
        cmd = wx.MouseEvent(mouseType)
        cmd.SetEventObject(window)
        cmd.SetId(window.GetId())
        cmd.SetX(x)
        cmd.SetY(y)
        window.GetEventHandler().ProcessEvent(cmd)

    def SendEvent(self, window, PyEventBinder):
        # Example of PyEventBinder: wx.EVT_BUTTON
        # window is the window (control) that triggers the event
        cmd = wx.CommandEvent(PyEventBinder.evtType[0])
        cmd.SetEventObject(window)
        cmd.SetId(window.GetId())
        window.GetEventHandler().ProcessEvent(cmd)

    def Notify(self):
        """ Actually sends a ``wx.EVT_BUTTON`` event to the listener (if any). """
        if self._raiseOnSetFocus:
            self.Refresh()
            if self._mouseIsInRegion:
                self.Raise()
        evt = ShapedBitmapButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def IsMousePositionInRegion(self):
        x, y = self.ScreenToClient(wxGetMousePosition())
        return self._region.Contains(x, y)

    def IsMousePositionInAnyChildsRegion(self):
        childrenShapedBitmapButtons = [
                sbb for sbb in self.GetChildren()
                     if isinstance(sbb, ShapedBitmapButton)]
        for child in childrenShapedBitmapButtons:
            x, y = child.ScreenToClient(wxGetMousePosition())
            if child._region.Contains(x, y):
                return True
        return False


class ShapedBitmapButtonAdv(ShapedBitmapButton):
    """
    This is the advanced class implementation of :class:`ShapedBitmapButton`.

    Handles sibling ShapedBitmapButton's alpha drawing when within anothers rect

    """

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """
 
        ## print('OnPaint - ShapedBitmapButton %s' % time.time())  # DEBUG/Optimize how many times Refresh is firing off.
######################## MODIFIED HERE
        #dc = wx.BufferedPaintDC(self)
        dc = wx.AutoBufferedPaintDCFactory(self)
########################
        
        bitmap = self._bitmap

        parent = self.GetParent()
        if not parent:  # Probably been/being deleted.
            return
        dc.SetBackground(wx.Brush(parent.GetBackgroundColour()))
        dc.Clear()
        dc_DrawBitmap = dc.DrawBitmap

        imAChild = hasattr(parent, '_sbbChildBmp')
        if imAChild:  # I am a child here.
            parent.MakeChildBmp()
            dc.SetBackground(wx.Brush(parent.GetParent().GetBackgroundColour()))
            posX, posY = self.GetPosition()
            szW, szH = self.GetSize()
            parent_sbbChildBmp = parent._sbbChildBmp
            if parent_sbbChildBmp:
                dc_DrawBitmap(parent_sbbChildBmp.
                              GetSubBitmap(wx.Rect(posX, posY, szW, szH)), 0, 0, True)
        # @ NOTE: This section of code could cause errors with various sizers
        #         when sizing the frame to zilch/nothing.
        # @ except wx._core.wxAssertionError, wx._core.PyAssertionError:
        elif self._parentBgBmp:
            szW, szH = self.Size  # sz = self.GetSize()
            # print('sz = %s, parentSz = %s' % (sz, self.parent.GetSize()))
            if szW and szH:  # if x or y is 0 it WILL cause major fubar havok; BoxSizer, WrapSizer
                posX, posY = self.Position  # pos = self.GetPosition()
                if (posX >= 0) and (posY >= 0) and (posX + szW >= szW) and (posY + szH >= szH): # GridSizer fubar havok
                    dc_DrawBitmap(self._parentBgBmp.
                        GetSubBitmap(wx.Rect(posX, posY, szW, szH)), 0, 0, True)
                else:  # Something is better than nothing even if it is off a bit. TODO: Try to recalculate correct overlaying of GetSubBitmap
                    # print('posX, posY', posX, posY)
                    dc_DrawBitmap(self._parentBgBmp, 0, 0, True)
            ## else:  # Something is better than nothing even if it is off a bit. TODO: Try to recalculate correct overlaying of GetSubBitmap
            ##     dc_DrawBitmap(self._parentBgBmp, 0, 0, True)

        if self._mouseAction == CLICK:
            bitmap = self._pressedBmp or bitmap
        elif self._mouseAction == HOVER:
            bitmap = self._hoverBmp or bitmap
        elif not self.IsEnabled():
            bitmap = self._disabledBmp or bitmap

        # EXPERIMENTAL TODO: make an option for this sibling drawing as it may not be necessary if sbb's are in a sizer ect...
        if not parent.GetSizer():  # It's obvious this wouldnt be needed if they are in a sizer.
            siblings = self.GetSBBSiblings()
            if siblings:
                ### mx, my = self.GetPosition()
                ### mw, mh = bitmap.GetWidth(), bitmap.GetHeight()
                ### myrect = wx.Rect(mx, my, mw, mh)
                mx, my, mw, mh = myrect = self.GetRect()
                myrect_Contains = myrect.Contains
                # print('--')
                wxRect = wx.Rect
                selfIsMousePositionInRegion = self.IsMousePositionInRegion()
                for sibling in siblings:
                    sibbmp = sibling._bitmap
                    sx, sy = sibpos = sibling.GetPosition()
                    sibw = sibbmp.GetWidth()
                    sibh = sibbmp.GetHeight()
                    ### sx, sy, sw, sh = sibling.GetRect()
                    ### sibw = sx + sw
                    ### sibh = sy + sh
                    ## sibpos = (sx, sy)
                    ## print('sibpos %s' % sibling.Name, sibpos)
                    topLeftPt = (sx, sy)
                    topRightPt = (sx + sibw, sy)
                    bottomLeftPt = (sx, sy + sibh)
                    bottomRightPt = (sx + sibw, sy + sibh)
                    topLeft = myrect_Contains(topLeftPt)
                    topRight = myrect_Contains(topRightPt)
                    bottomLeft = myrect_Contains(bottomLeftPt)
                    bottomRight = myrect_Contains(bottomRightPt)
                    ### topLeft = mx <= sx <= mx + mw and my <= sy <= my + mh
                    ### topRight = mx <= sx + sibw <= mx + mw and my <= sy <= my + mh
                    ### bottomLeft = mx <= sx <= mx + mw and my <= sy + sibh <= my + mh
                    ### bottomRight = mx <= sx + sibw <= mx + mw and my <= sy + sibh <= my + mh
                    # print('topLeft', topLeft)
                    # print('topRight', topRight)
                    # print('bottomLeft', bottomLeft)
                    # print('bottomRight', bottomRight)
                    sibIsMousePositionInRegion = sibling.IsMousePositionInRegion()
                    if topLeft and not bottomRight and not topRight and not bottomLeft:  # TopLeftCorner point
                        x = 0
                        y = 0
                        w = mw - (sx - mx)
                        h = mh - (sy - my)
                        # print('x,y,w,h topLeft: ',x,y,w,h)
                        if not w or not h:
                             continue

                        if sibIsMousePositionInRegion and not selfIsMousePositionInRegion:
                            sibsubbmp = sibling._hoverBmp.GetSubBitmap(wxRect(x,y,w,h))
                        else:
                            sibsubbmp = sibling._bitmap.GetSubBitmap(wxRect(x,y,w,h))

                        # sibsubbmp = sibling._bitmap.GetSubBitmap(wxRect(x,y,w,h))
                        dc_DrawBitmap(sibsubbmp, sx - mx, sy - my)
                    elif topRight and not bottomRight and not topLeft and not bottomLeft:  # TopRightCorner point
                        w = sx + sibw - mx
                        h = mh - (sy - my)
                        x = sibw - w
                        y = 0
                        # print('x,y,w,h topLeft: ',x,y,w,h)
                        if not w or not h:
                            continue

                        if sibIsMousePositionInRegion and not selfIsMousePositionInRegion:
                            sibsubbmp = sibling._hoverBmp.GetSubBitmap(wxRect(x,y,w,h))
                        else:
                            sibsubbmp = sibling._bitmap.GetSubBitmap(wxRect(x,y,w,h))

                        # sibsubbmp = sibling._bitmap.GetSubBitmap(wxRect(x,y,w,h))
                        dc_DrawBitmap(sibsubbmp, 0, sy - my)
                    elif bottomLeft and not topLeft and not bottomRight and not topRight:  # BottomLeftCorner point
                        w = mw - (sx - mx)
                        h = sy + sibh - my
                        x = 0
                        y = sibh - h
                        # print('x,y,w,h bottomLeft: ',x,y,w,h)
                        if not w or not h:
                            continue

                        if sibIsMousePositionInRegion and not selfIsMousePositionInRegion:
                            sibsubbmp = sibling._hoverBmp.GetSubBitmap(wxRect(x,y,w,h))
                        else:
                            sibsubbmp = sibling._bitmap.GetSubBitmap(wxRect(x,y,w,h))

                        # sibsubbmp = sibling._bitmap.GetSubBitmap(wxRect(x,y,w,h))
                        dc_DrawBitmap(sibsubbmp, sx - mx, 0)
                    elif bottomRight and not topLeft and not bottomLeft and not topRight:  # BottomRightCorner point
                        w = sx + sibw - mx
                        h = sy + sibh - my
                        x = sibw - w
                        y = sibh - h
                        # print('x,y,w,h bottomRight: ',x,y,w,h)
                        if not w or not h:
                            continue

                        if sibIsMousePositionInRegion and not selfIsMousePositionInRegion:
                            sibsubbmp = sibling._hoverBmp.GetSubBitmap(wxRect(x,y,w,h))
                        else:
                            sibsubbmp = sibling._bitmap.GetSubBitmap(wxRect(x,y,w,h))

                        # sibsubbmp = sibling._bitmap.GetSubBitmap(wxRect(x,y,w,h))
                        dc_DrawBitmap(sibsubbmp, 0, 0)


        dc_DrawBitmap(bitmap, 0, 0)

        if self._labelEnable and self._labelsList or self._label:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            transparentColour = wx.TransparentColour
            transparent = wx.TRANSPARENT
            solid = wx.SOLID
            if self._labelsList:
                dc_SetBackgroundMode = dc.SetBackgroundMode
                dc_SetTextForeground = dc.SetTextForeground
                dc_SetTextBackground = dc.SetTextBackground
                dc_SetFont = dc.SetFont
                dc_DrawRotatedText = dc.DrawRotatedText
                for label, coords, foreground, background, font, rotation in self._labelsList:
                    if background == transparentColour:
                        dc_SetBackgroundMode(transparent)
                    else:
                        dc_SetBackgroundMode(solid)
                    dc_SetTextForeground(foreground)
                    dc_SetTextBackground(background)
                    dc_SetFont(font)
                    dc_DrawRotatedText(label,
                                       coords[0],
                                       coords[1],
                                       rotation)
            else:  # self._label
                if self._labelBackColour == transparentColour:
                    dc.SetBackgroundMode(transparent)
                else:
                    dc.SetBackgroundMode(solid)
                dc.SetTextBackground(self._labelBackColour)
                dc.SetTextForeground(self._labelForeColour)
                dc.SetFont(self._labelFont)

                # Get the working rectangle we can draw in.          #<----------------- Ne sert pas
                rect = self.GetClientRect()
                x, y = self.GetSize()

                rect = wx.Rect(rect.x, rect.y,
                               rect.width, rect.height)

#                gcdc.SetFont(boldFont)
                # Get the text color.
#                dc.SetTextForeground(self.foreground)
#                dc.DrawLabel(self._label, rect, wx.ALIGN_CENTER)


        
                dc.DrawLabel(self._label,
                                   rect,
                                   #self._labelPosition[0],
                                   #self._labelPosition[1],
                                   wx.ALIGN_CENTER,
                                   self._labelRotation)

        if self._makeChildBmp:  # I am a parent here.
            self._sbbChildBmp = dc.GetAsBitmap()
            self._makeChildBmp = False

    def OnMouseEvents(self, event):
        """
        Handles the ``wx.EVT_MOUSE_EVENTS`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """
        evtType = event.GetEventType()
        # print('OnMouseEvents: ', event.GetEventType())
        x, y = event.GetPosition()
        if evtType == wx.EVT_MOTION:  # Handle this here in this class.
            self.OnMotion(event)
        else:
            # if self._region.Contains(x, y):
            event.Skip()
        # event.Skip()
        # NotImplemented

        ## if not self._region.Contains(x, y):  # Pass the wx.EVT_MOUSE_EVENTS to the parent
        ##     selfPosX, selfPosY = self.GetPosition()
        ##     underX, underY = selfPosX + x, selfPosY + y
        ##     self.SendMouseEvent(self.parent, wx.wxEVT_???, underX, underY)

    def OnMotion(self, event):
        """
        Handles the ``wx.EVT_MOTION`` event for :class:`ShapedBitmapButton`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """
        # print('draworder: ', [sib.GetName() for sib in self.GetSBBSiblings()])
        x, y = event.GetPosition()
        mouseX, mouseY = self.ScreenToClient(wxGetMousePosition())
        # print('Motion x, y, mouseX, mouseY', x, y, mouseX, mouseY)

        regionContainsPoint = self._region.Contains(x, y)
        parent = self.GetParent()
        imAChild = hasattr(parent, '_sbbChildBmp')

        if not regionContainsPoint and imAChild:  # I am a child here.
            selfPosX, selfPosY = self.GetPosition()
            # print('selfPos = %s, %s' % (selfPosX, selfPosY))
            # print('OnMotion x, y = %s,%s' % (x, y))
            if parent._region.Contains(selfPosX + x, selfPosY + y):
                # Simulate the event back to the parent because we are hovering over it.

                # print('OnMotion x, y = %s,%s' % (x, y))
                # print('parent._mouseAction', parent._mouseAction)
                # print('parent._mouseIsInRegion', parent._mouseIsInRegion)
                if ((not parent._mouseAction == HOVER) or (not parent._mouseIsInRegion)):  # Don't constantly paint
                    parent._mouseAction = HOVER
                    parent._mouseIsInRegion = True
                    parent.Refresh()

                # print('parent._makeChildBmp', parent._makeChildBmp)
                # if parent._makeChildBmp:
                #     parent.MakeChildBmp()
                #     parent.Refresh()
                #     parent._makeChildBmp = False

                if self.HasCapture():
                    self._mouseAction = CLICK
                else:
                    self._mouseAction = None
                    if self.GetToolTip():  # HOVER event happens before CLICK.
                        self.GetToolTip().Enable(False)

                self._mouseIsInRegion = False
                # self.Refresh()
                event.Skip()
                return

        if not regionContainsPoint:
            if self._mouseIsInRegion:  # Update Visual.
                self._mouseIsInRegion = False
                self.Refresh()
            self._mouseAction = None
            if self.GetToolTip():  # Only show the tooltip when in region, not when in rect.
                self.GetToolTip().Enable(False)

            # Pass the wx.EVT_MOTION to the parent
            selfPosX, selfPosY = self.GetPosition()
            underX, underY = selfPosX + x, selfPosY + y
            self.SendMouseEvent(parent, wx.wxEVT_MOTION, underX, underY)

            for child in self.GetChildren():
                if child.IsMousePositionInRegion():
                    child._mouseAction = HOVER
                    child._mouseIsInRegion = True
                else:
                    child._mouseAction = None
                    child._mouseIsInRegion = False
                child.Refresh()

        else:
            if self.HasCapture():
                self._mouseAction = CLICK
            else:
                self._mouseAction = HOVER
                if self.GetToolTip(): # HOVER event happens before CLICK.
                    self.GetToolTip().Enable(True)
            if hasattr(self.GetParent(), '_sbbChildBmp'):
                parent._mouseAction = None
                parent.Refresh()
            if not self._mouseIsInRegion:
                self._mouseIsInRegion = True
                self.Refresh()

        for sibling in self.GetSBBSiblings():
            if not sibling.IsMousePositionInRegion():
                pass # print(sibling.GetName(), 'isinregion')

        selfIsMousePositionInRegion = self.IsMousePositionInRegion()
        for sibling in self.GetSBBSiblings():
            sibIsMousePositionInRegion = sibling.IsMousePositionInRegion()
            if sibIsMousePositionInRegion and not selfIsMousePositionInRegion:
                sibling._mouseAction = HOVER
                sibling.Refresh()
            else:
                sibling._mouseAction = None
                sibling.Refresh()

        # self.Refresh()


        event.Skip()
        # print('OnMotion (%s, %s)' % (x, y))

    # def OnLeftUp(self, event):
    #     """
    #     Handles the ``wx.EVT_LEFT_UP`` event for :class:`ShapedBitmapButton`.
    #
    #     :param `event`: a :class:`MouseEvent` event to be processed.
    #     """
    #
    #     x, y = event.GetPosition()
    #
    #     parent = self.GetParent()
    #     imAChild = hasattr(parent, '_sbbChildBmp')
    #     if not self._region.Contains(x, y) and imAChild:  # I am a child here.
    #         selfPosX, selfPosY = self.GetPosition()
    #         underX, underY = selfPosX + x, selfPosY + y
    #         # print('selfPos = %s, %s' %(selfPosX, selfPosY))
    #         # print('OnLeftUp x, y = %s,%s' %(x, y))
    #         if parent._region.Contains(underX, underY):
    #             # Send the event back to the parent because we are hovering over it and have clicked.
    #             # self.parent._mouseIsInRegion = True
    #             # parent._mouseAction = HOVER
    #             # parent.Notify()
    #             parent.SendMouseEvent(parent, wx.wxEVT_LEFT_UP, underX, underY)
    #             return
    #
    #     if not self._region.Contains(x, y):  # Pass the wx.EVT_LEFT_UP to the parent
    #         selfPosX, selfPosY = self.GetPosition()
    #         underX, underY = selfPosX + x, selfPosY + y
    #         self.SendMouseEvent(self.parent, wx.wxEVT_LEFT_UP, underX, underY)
    #         return
    #
    #     if not self.IsEnabled() or not self.HasCapture():
    #         return
    #
    #     if self.HasCapture():
    #         self.ReleaseMouse()
    #
    #     if self._region.Contains(x, y):
    #         self._mouseAction = HOVER
    #         self.Notify()
    #     else:
    #         self._mouseAction = None
    #
    #     self.Refresh()
    #     event.Skip()

# __main__ Demo -------------------------------------------------------------

