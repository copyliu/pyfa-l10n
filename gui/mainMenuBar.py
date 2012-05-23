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
import config
import bitmapLoader
import gui.mainFrame
import gui.graphFrame
import gui.globalEvents as GE
_ = wx.GetTranslation
class MainMenuBar(wx.MenuBar):
    def __init__(self):
        self.characterEditorId = wx.NewId()
        self.damagePatternEditorId = wx.NewId()
        self.graphFrameId = wx.NewId()
        self.backupFitsId = wx.NewId()
        self.preferencesId = wx.NewId()

        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

        wx.MenuBar.__init__(self)

        # File menu
        fileMenu = wx.Menu()
        self.Append(fileMenu, _("&File"))

        fileMenu.Append(self.mainFrame.addPageId, _("&New Tab\tCTRL+T"), _("Open a new fitting tab"))
        fileMenu.Append(self.mainFrame.closePageId, _("&Close Tab\tCTRL+W"), _("Close the current fit"))
        fileMenu.AppendSeparator()

        fileMenu.Append(self.backupFitsId, _("&Backup fits"), _("Backup all fittings to a XML file"))
        fileMenu.Append(wx.ID_OPEN, _("&Import\tCTRL+O"), _("Import a fit into pyfa."))
        fileMenu.Append(wx.ID_SAVEAS, _("&Export\tCTRL+S"), _("Export the fit to another format."))
        fileMenu.AppendSeparator()

        fileMenu.Append(wx.ID_EXIT)


        # Edit menu
        editMenu = wx.Menu()
        self.Append(editMenu, _("&Edit"))

        #editMenu.Append(wx.ID_UNDO)
        #editMenu.Append(wx.ID_REDO)


        copyText = _("&To Clipboard") + (_("\tCTRL+C") if 'wxMSW' in wx.PlatformInfo else "")
        pasteText = _("&From Clipboard") + (_("\tCTRL+V") if 'wxMSW' in wx.PlatformInfo else "")
        editMenu.Append(wx.ID_COPY, copyText, _("Export a fit to the clipboard"))
        editMenu.Append(wx.ID_PASTE, pasteText, _("Import a fit from the clipboard"))

        # Character menu
        windowMenu = wx.Menu()
        self.Append(windowMenu, _("&Window"))

        charEditItem = wx.MenuItem(windowMenu, self.characterEditorId, _("&Character Editor\tCTRL+E"))
        charEditItem.SetBitmap(bitmapLoader.getBitmap("character_small", "icons"))
        windowMenu.AppendItem(charEditItem)

        damagePatternEditItem = wx.MenuItem(windowMenu, self.damagePatternEditorId, _("Damage Pattern Editor\tCTRL+D"))
        damagePatternEditItem.SetBitmap(bitmapLoader.getBitmap("damagePattern_small", "icons"))
        windowMenu.AppendItem(damagePatternEditItem)

        graphFrameItem = wx.MenuItem(windowMenu, self.graphFrameId, "Graphs\tCTRL+G")
        graphFrameItem.SetBitmap(bitmapLoader.getBitmap("graphs_small", "icons"))
        windowMenu.AppendItem(graphFrameItem)

        #=======================================================================
        # DISABLED FOR RC2 Release
        #
        preferencesItem = wx.MenuItem(windowMenu, self.preferencesId, _("Preferences\tCTRL+P"))
        preferencesItem.SetBitmap(bitmapLoader.getBitmap("preferences_small", "icons"))
        windowMenu.AppendItem(preferencesItem)
        #=======================================================================

        # Help menu
        helpMenu = wx.Menu()
        self.Append(helpMenu, _("&Help"))
        helpMenu.Append(wx.ID_ABOUT)

        if config.debug:
            helpMenu.Append( self.mainFrame.widgetInspectMenuID, _("Open Widgets Inspect tool"), _("Open Widgets Inspect tool"))



        self.mainFrame.Bind(GE.FIT_CHANGED, self.fitChanged)

    def fitChanged(self, event):
        enable = event.fitID is not None
        self.Enable(wx.ID_SAVEAS, enable)
        self.Enable(wx.ID_COPY, enable)
        event.Skip()

