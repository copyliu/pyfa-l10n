import wx
import gui.utils.colorUtils as colorUtils
import gui.utils.drawUtils as drawUtils
from gui import bitmapLoader
_ = wx.GetTranslation

SearchButton, EVT_SEARCH_BTN = wx.lib.newevent.NewEvent()
CancelButton, EVT_CANCEL_BTN = wx.lib.newevent.NewEvent()
TextEnter, EVT_TEXT_ENTER = wx.lib.newevent.NewEvent()
TextTyped, EVT_TEXT = wx.lib.newevent.NewEvent()

class PFSearchBox(wx.Window):
    def __init__(self, parent, id = wx.ID_ANY, value = "", pos = wx.DefaultPosition, size = wx.Size(-1,24), style = 0):
        wx.Window.__init__(self, parent, id, pos, size, style = 0)

        self.isSearchButtonVisible = False
        self.isCancelButtonVisible = False

        self.descriptiveText = _("Search")

        self.searchBitmap = None
        self.cancelBitmap = None
        self.bkBitmap = None

        self.resized = True

        self.searchButtonX = 0
        self.searchButtonY = 0
        self.searchButtonPressed = False

        self.cancelButtonX = 0
        self.cancelButtonY = 0
        self.cancelButtonPressed = False

        self.editX = 0
        self.editY = 0


        self.padding = 4

        self._hl = False

        w,h = size
        self.EditBox = wx.TextCtrl(self, wx.ID_ANY, "", wx.DefaultPosition, (-1, h - 2 if 'wxGTK' in wx.PlatformInfo else -1 ), wx.TE_PROCESS_ENTER | (wx.BORDER_NONE if 'wxGTK' in wx.PlatformInfo else 0))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBk)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)

        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterLeaveWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnEnterLeaveWindow)

#        self.EditBox.ChangeValue(self.descriptiveText)

        self.EditBox.Bind(wx.EVT_SET_FOCUS, self.OnEditSetFocus)
        self.EditBox.Bind(wx.EVT_KILL_FOCUS, self.OnEditKillFocus)

        self.EditBox.Bind(wx.EVT_TEXT, self.OnText)
        self.EditBox.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)

        self.SetMinSize(size)

    def OnEnterLeaveWindow(self, event):
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        self._hl = False

    def OnText(self, event):
        wx.PostEvent(self, TextTyped())

    def OnTextEnter(self, event):
        wx.PostEvent(self, TextEnter())

    def OnEditSetFocus(self, event):
#        value = self.EditBox.GetValue()
#        if value == self.descriptiveText:
#            self.EditBox.ChangeValue("")
        pass

    def OnEditKillFocus(self, event):
        if self.EditBox.GetValue() == "":
            self.Clear()

    def Clear(self):
        self.EditBox.Clear()
#        self.EditBox.ChangeValue(self.descriptiveText)

    def SetValue(self, value):
        self.EditBox.SetValue(value)

    def ChangeValue(self, value):
        self.EditBox.ChangeValue(value)

    def GetValue(self):
        return self.EditBox.GetValue()

    def GetLineText(self, lineno):
        return self.EditBox.GetLineText(lineno)

    def HitTest(self, target, position, area):
        x, y = target
        px, py = position
        aX, aY = area
        if (px > x and px < x + aX) and (py > y and py < y + aY):
            return True
        return False

    def GetButtonsPos(self):
        btnpos = []
        btnpos.append( (self.searchButtonX, self.searchButtonY) )
        btnpos.append( (self.cancelButtonX, self.cancelButtonY) )
        return btnpos

    def GetButtonsSize(self):
        btnsize = []

        if self.searchBitmap:
            sw = self.searchBitmap.GetWidth()
            sh = self.searchBitmap.GetHeight()
        else:
            sw = 0
            sh = 0

        if self.cancelBitmap:
            cw = self.cancelBitmap.GetWidth()
            ch = self.cancelBitmap.GetHeight()
        else:
            cw = 0
            ch = 0

        btnsize.append( (sw,sh))
        btnsize.append( (cw,ch))
        return btnsize

    def OnMouseMove(self, event):
        btnpos = self.GetButtonsPos()
        btnsize = self.GetButtonsSize()
        for btn in xrange(2):
            if self.HitTest(btnpos[btn], event.GetPosition(), btnsize[btn]):
                if not self._hl:
                    self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
                    self._hl = True
                break
            else:
                if self._hl:
                    self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
                    self._hl = False

    def OnLeftDown(self, event):
        btnpos = self.GetButtonsPos()
        btnsize = self.GetButtonsSize()

        self.CaptureMouse()
        for btn in xrange(2):
            if self.HitTest(btnpos[btn], event.GetPosition(), btnsize[btn]):
                if btn == 0:
                    if not self.searchButtonPressed:
                        self.searchButtonPressed = True
                        self.Refresh()
                if btn == 1:
                    if not self.cancelButtonPressed:
                        self.cancelButtonPressed = True
                        self.Refresh()

    def OnLeftUp(self, event):
        btnpos = self.GetButtonsPos()
        btnsize = self.GetButtonsSize()

        if self.HasCapture():
            self.ReleaseMouse()

        for btn in xrange(2):
            if self.HitTest(btnpos[btn], event.GetPosition(), btnsize[btn]):
                if btn == 0:
                    if self.searchButtonPressed:
                        self.searchButtonPressed = False
                        self.Refresh()
                        self.SetFocus()
                        wx.PostEvent(self, SearchButton())
                if btn == 1:
                    if self.cancelButtonPressed:
                        self.cancelButtonPressed = False
                        self.Refresh()
                        self.SetFocus()
                        wx.PostEvent(self, CancelButton())
            else:
                if btn == 0:
                    if self.searchButtonPressed:
                        self.searchButtonPressed = False
                        self.Refresh()
                if btn == 1:
                    if self.cancelButtonPressed:
                        self.cancelButtonPressed = False
                        self.Refresh()

    def OnSize(self, event):
        self.resized = True
        self.Refresh()

    def OnEraseBk(self, event):
        pass

    def UpdateElementsPos(self, dc):
        rect = self.GetRect()

        if self.searchBitmap and self.isSearchButtonVisible:
            sw = self.searchBitmap.GetWidth()
            sh = self.searchBitmap.GetHeight()
        else:
            sw = 0
            sh = 0

        if self.cancelBitmap and self.isCancelButtonVisible:
            cw = self.cancelBitmap.GetWidth()
            ch = self.cancelBitmap.GetHeight()
        else:
            cw = 0
            ch = 0

        cwidth = rect.width
        cheight = rect.height

        self.searchButtonX = self.padding
        self.searchButtonY = (cheight - sh) / 2
        self.cancelButtonX = cwidth - self.padding - cw
        self.cancelButtonY = (cheight - ch) / 2

        self.editX = self.searchButtonX + self.padding + sw

        editWidth, editHeight = self.EditBox.GetSize()

        self.editY = (cheight - editHeight)/2
        self.EditBox.SetPosition((self.editX, self.editY))
        self.EditBox.SetSize( (self.cancelButtonX - self.padding - self.editX, -1))

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)

        bkColor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
        sepColor = colorUtils.GetSuitableColor(bkColor, 0.2)
        rect = self.GetRect()

        if self.resized:
            self.bkBitmap = drawUtils.RenderGradientBar(bkColor, rect.width, rect.height, 0.1, 0.1, 0.2, 2)
            self.UpdateElementsPos(dc)
            self.resized = False

        dc.DrawBitmap(self.bkBitmap, 0, 0)

        if self.isSearchButtonVisible:
            if self.searchBitmap:
                if self.searchButtonPressed:
                    spad = 1
                else:
                    spad = 0

                dc.DrawBitmap(self.searchBitmapShadow, self.searchButtonX + 1, self.searchButtonY + 1)
                dc.DrawBitmap(self.searchBitmap, self.searchButtonX + spad, self.searchButtonY + spad)


        if self.isCancelButtonVisible:
            if self.cancelBitmap:
                if self.cancelButtonPressed:
                    cpad = 1
                else:
                    cpad = 0
                dc.DrawBitmap(self.cancelBitmapShadow, self.cancelButtonX + 1, self.cancelButtonY + 1)
                dc.DrawBitmap(self.cancelBitmap, self.cancelButtonX + cpad, self.cancelButtonY + cpad)

        dc.SetPen(wx.Pen(sepColor,1))
        dc.DrawLine(0,rect.height - 1, rect.width, rect.height - 1)

    def SetSearchBitmap(self, bitmap):
        self.searchBitmap = bitmap
        self.searchBitmapShadow = drawUtils.CreateDropShadowBitmap(bitmap, 0.2)

    def SetCancelBitmap(self, bitmap):
        self.cancelBitmap = bitmap
        self.cancelBitmapShadow = drawUtils.CreateDropShadowBitmap(bitmap, 0.2)

    def IsSearchButtonVisible(self):
        return self.isSearchButtonVisible

    def IsCancelButtonVisible(self):
        return self.isCancelButtonVisible

    def ShowSearchButton(self, show = True):
        self.isSearchButtonVisible = show

    def ShowCancelButton(self, show = True):
        self.isCancelButtonVisible = show

    def SetDescriptiveText(self, text):
        self.descriptiveText = text

    def GetDescriptiveText(self):
        return self.descriptiveText

