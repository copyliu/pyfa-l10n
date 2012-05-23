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
import gui.mainFrame
from gui.boosterView import BoosterView
from gui.droneView import DroneView
from gui.implantView import ImplantView
from gui.projectedView import ProjectedView
from gui.pyfatogglepanel import TogglePanel
from gui.gangView import GangView
from gui import bitmapLoader

import gui.chromeTabs
_ = wx.GetTranslation
class AdditionsPane(TogglePanel):

    def __init__(self, parent):

        TogglePanel.__init__(self, parent, forceLayout = 1)

        self.SetLabel(_("Additions"))
        pane = self.GetContentPane()

        baseSizer = wx.BoxSizer(wx.HORIZONTAL)
        pane.SetSizer(baseSizer)

        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

        self.notebook = gui.chromeTabs.PFNotebook(pane, False)
        size = wx.Size()
        # This size lets you see 4 drones at a time
        size.SetHeight(180)
        self.notebook.SetMinSize(size)
        baseSizer.Add(self.notebook, 1, wx.EXPAND)

        droneImg = bitmapLoader.getImage("drone_small", "icons")
        implantImg = bitmapLoader.getImage("implant_small", "icons")
        boosterImg = bitmapLoader.getImage("booster_small", "icons")
        projectedImg = bitmapLoader.getImage("projected_small", "icons")
        gangImg = bitmapLoader.getImage("fleet_fc_small", "icons")

        self.notebook.AddPage(DroneView(self.notebook), _("Drones"), tabImage = droneImg, showClose = False)
        self.notebook.AddPage(ImplantView(self.notebook), _("Implants"), tabImage = implantImg, showClose = False)
        self.notebook.AddPage(BoosterView(self.notebook), _("Boosters"), tabImage = boosterImg, showClose = False)

        self.projectedPage = ProjectedView(self.notebook)
        self.notebook.AddPage(self.projectedPage, _("Projected"), tabImage = projectedImg, showClose = False)

        self.gangPage = GangView(self.notebook)
        self.notebook.AddPage(self.gangPage, _("Fleet"), tabImage = gangImg, showClose = False)
        self.notebook.SetSelection(0)


    PANES = [_("Drones"), _("Implants"), _("Boosters"), _("Projected"), _("Fleet")]
    def select(self, name):
        self.notebook.SetSelection(self.PANES.index(name))
