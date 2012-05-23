#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import wx
import service
import gui.display as d
import gui.marketBrowser as mb
from gui.builtinViewColumns.state import State
from gui.contextMenu import ContextMenu
import globalEvents as GE
_ = wx.GetTranslation
class ImplantView(d.Display):
    DEFAULT_COLS = ["State",
                    "attr:implantness",
                    "Base Name"]

    def __init__(self, parent):
        d.Display.__init__(self, parent, style=wx.LC_SINGLE_SEL | wx.BORDER_NONE)

        self.lastFitId = None

        self.mainFrame.Bind(GE.FIT_CHANGED, self.fitChanged)
        self.mainFrame.Bind(mb.ITEM_SELECTED, self.addItem)
        self.Bind(wx.EVT_LEFT_DCLICK, self.removeItem)
        self.Bind(wx.EVT_LEFT_DOWN, self.click)
        self.Bind(wx.EVT_KEY_UP, self.kbEvent)

        if "__WXGTK__" in  wx.PlatformInfo:
            self.Bind(wx.EVT_RIGHT_UP, self.scheduleMenu)
        else:
            self.Bind(wx.EVT_RIGHT_DOWN, self.scheduleMenu)

    def kbEvent(self,event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_DELETE or keycode == wx.WXK_NUMPAD_DELETE:
            fitID = self.mainFrame.getActiveFit()
            cFit = service.Fit.getInstance()
            row = self.GetFirstSelected()
            if row != -1:
                cFit.removeImplant(fitID, self.GetItemData(row))
                wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))
        event.Skip()

    def fitChanged(self, event):
        #Clear list and get out if current fitId is None
        if event.fitID is None and self.lastFitId is not None:
            self.DeleteAllItems()
            self.lastFitId = None
            event.Skip()
            return

        cFit = service.Fit.getInstance()
        fit = cFit.getFit(event.fitID)

        self.original = fit.implants if fit is not None else None
        self.implants = stuff = fit.implants if fit is not None else None
        if stuff is not None: stuff.sort(key=lambda implant: implant.slot)

        if event.fitID != self.lastFitId:
            self.lastFitId = event.fitID

            item = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)

            if item != -1:
                self.EnsureVisible(item)

            self.deselectItems()

        self.populate(stuff)
        self.refresh(stuff)
        event.Skip()

    def addItem(self, event):
        cFit = service.Fit.getInstance()
        fitID = self.mainFrame.getActiveFit()
        trigger = cFit.addImplant(fitID, event.itemID)
        if trigger:
            wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))
            self.mainFrame.additionsPane.select(_("Implants"))

        event.Skip()

    def removeItem(self, event):
        row, _ = self.HitTest(event.Position)
        if row != -1:
            col = self.getColumn(event.Position)
            if col != self.getColIndex(State):
                fitID = self.mainFrame.getActiveFit()
                cFit = service.Fit.getInstance()
                implant = self.implants[self.GetItemData(row)]
                cFit.removeImplant(fitID, self.original.index(implant))
                wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))

    def click(self, event):
        event.Skip()
        row, _ = self.HitTest(event.Position)
        if row != -1:
            col = self.getColumn(event.Position)
            if col == self.getColIndex(State):
                fitID = self.mainFrame.getActiveFit()
                cFit = service.Fit.getInstance()
                cFit.toggleImplant(fitID, row)
                wx.PostEvent(self.mainFrame, GE.FitChanged(fitID=fitID))

    def scheduleMenu(self, event):
        event.Skip()
        if self.getColumn(event.Position) != self.getColIndex(State):
            wx.CallAfter(self.spawnMenu)

    def spawnMenu(self):
        sel = self.GetFirstSelected()
        if sel != -1:
            cFit = service.Fit.getInstance()
            fit = cFit.getFit(self.mainFrame.getActiveFit())
            implant = fit.implants[sel]

            sMkt = service.Market.getInstance()
            sourceContext = "implantItem"
            itemContext = sMkt.getCategoryByItem(implant.item).name

            menu = ContextMenu.getMenu((implant,), (sourceContext, itemContext))
            self.PopupMenu(menu)
