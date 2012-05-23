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
from gui.preferenceView import PreferenceView
import bitmapLoader
_ = wx.GetTranslation
class PreferenceDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE)
        self.SetTitle(_("pyfa - Preferences"))
        i = wx.IconFromBitmap(bitmapLoader.getBitmap("preferences_small", "icons"))
        self.SetIcon(i)
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.listbook = wx.Listbook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_DEFAULT)
        self.listbook.GetListView().SetMinSize((500, -1))
        self.listbook.GetListView().SetSize((500, -1))

        self.imageList = wx.ImageList(64,64)
        self.listbook.SetImageList(self.imageList)

        mainSizer.Add(self.listbook, 1, wx.EXPAND | wx.TOP|wx.BOTTOM|wx.LEFT, 5)

        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        mainSizer.Add( self.m_staticline2, 0, wx.EXPAND, 5 )

        btnSizer = wx.BoxSizer( wx.HORIZONTAL )
        btnSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        self.btnOK = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
        btnSizer.Add( self.btnOK, 0, wx.ALL, 5 )
        mainSizer.Add(btnSizer,0 , wx.EXPAND, 5)
        self.SetSizer(mainSizer)

        self.Centre(wx.BOTH)

        for title, prefView in PreferenceView.views.iteritems():
            page = wx.Panel(self.listbook)
            bmp = prefView.getImage()
            if bmp:
                imgID = self.imageList.Add(bmp)
            else:
                imgID = -1
            prefView.populatePanel(page)
            self.listbook.AddPage(page, title, imageId = imgID)

        self.Fit()
        self.Layout()

        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOK)

    def OnBtnOK(self, event):
        self.Destroy()