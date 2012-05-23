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
from gui.statsView import StatsView
from gui import builtinStatsViews
from gui.utils.numberFormatter import formatAmount
_ = wx.GetTranslation
class TargetingMiscViewFull(StatsView):
    name = "targetingmiscViewFull"
    def __init__(self, parent):
        StatsView.__init__(self)
        self.parent = parent
        self._cachedValues = []
    def getHeaderText(self, fit):
        return _("Targeting && Misc")

    def getTextExtentW(self, text):
        width, height = self.parent.GetTextExtent( text )
        return width

    def populatePanel(self, contentPanel, headerPanel):
        contentSizer = contentPanel.GetSizer()

        self.panel = contentPanel
        self.headerPanel = headerPanel
        gridTargetingMisc = wx.FlexGridSizer(1, 3)
        contentSizer.Add( gridTargetingMisc, 0, wx.EXPAND | wx.ALL, 0)
        gridTargetingMisc.AddGrowableCol(0)
        gridTargetingMisc.AddGrowableCol(2)
        # Targeting

        gridTargeting = wx.FlexGridSizer(4, 2)
        gridTargeting.AddGrowableCol(1)

        gridTargetingMisc.Add(gridTargeting, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        labels = ((_("Targets"), "Targets", ""),
                  (_("Range"), "Range", "km"),
                  (_("Scan res."), "ScanRes", "mm"),
                  (_("Sensor str."), "SensorStr", ""),
                  (_("Drone range"), "CtrlRange", "km"))

        for header, labelShort, unit in labels:
            gridTargeting.Add(wx.StaticText(contentPanel, wx.ID_ANY, "%s: " % header), 0, wx.ALIGN_LEFT)

            box = wx.BoxSizer(wx.HORIZONTAL)
            gridTargeting.Add(box, 0, wx.ALIGN_LEFT)

            lbl = wx.StaticText(contentPanel, wx.ID_ANY, "0 %s" %unit)
            setattr(self, "label%s" % labelShort, lbl)
            box.Add(lbl, 0, wx.ALIGN_LEFT)

            self._cachedValues.append(0)

        # Misc
        gridTargetingMisc.Add( wx.StaticLine( contentPanel, wx.ID_ANY, style = wx.VERTICAL),0, wx.EXPAND, 3 )
        gridMisc = wx.FlexGridSizer(4, 2)
        gridMisc.AddGrowableCol(1)
        gridTargetingMisc.Add(gridMisc,0 , wx.ALIGN_LEFT | wx.ALL, 5)

        labels = ((_("Speed"), "Speed", "m/s"),
                  (_("Align time"), "AlignTime", "s"),
                  (_("Signature"), "SigRadius", "m"),
                  (_("Warp Speed"), "WarpSpeed", "AU/s"),
                  (_("Cargo"), "Cargo", u"m\u00B3"))

        for header, labelShort, unit in labels:
            gridMisc.Add(wx.StaticText(contentPanel, wx.ID_ANY, "%s: " % header), 0, wx.ALIGN_LEFT)

            box = wx.BoxSizer(wx.HORIZONTAL)
            gridMisc.Add(box, 0, wx.ALIGN_LEFT)

            lbl = wx.StaticText(contentPanel, wx.ID_ANY, "0 %s" % unit)
            setattr(self, "labelFull%s" % labelShort, lbl)
            box.Add(lbl, 0, wx.ALIGN_LEFT)

            self._cachedValues.append(0)


    def refreshPanel(self, fit):
        #If we did anything intresting, we'd update our labels to reflect the new fit's stats here

        stats = (("labelTargets", lambda: fit.maxTargets, 3, 0, 0, ""),
                 ("labelRange", lambda: fit.maxTargetRange / 1000, 3, 0, 0, "km"),
                 ("labelScanRes", lambda: fit.ship.getModifiedItemAttr("scanResolution"), 3, 0, 0, "mm"),
                 ("labelSensorStr", lambda: fit.scanStrength, 3, 0, 0, ""),
                 ("labelCtrlRange", lambda: fit.extraAttributes["droneControlRange"] / 1000, 3, 0, 0, "km"),
                 ("labelFullSpeed", lambda: fit.ship.getModifiedItemAttr("maxVelocity"), 3, 0, 0, "m/s"),
                 ("labelFullAlignTime", lambda: fit.alignTime, 3, 0, 0, "s"),
                 ("labelFullSigRadius", lambda: fit.ship.getModifiedItemAttr("signatureRadius"), 3, 0, 9, ""),
                 ("labelFullWarpSpeed", lambda: fit.warpSpeed, 3, 0, 0, "AU/s"),
                 ("labelFullCargo", lambda: fit.ship.getModifiedItemAttr("capacity"), 3, 0, 9, u"m\u00B3"))

        counter = 0
        RADII = [("Pod",25), ("Interceptor",33), ("Frigate",38),
                 ("Destroyer", 83), ("Cruiser", 130),
                 ("Battlecruiser", 265),  ("Battleship",420),
                 ("Carrier", 3000)]
        for labelName, value, prec, lowest, highest, unit in stats:
            label = getattr(self, labelName)
            value = value() if fit is not None else 0
            value = value if value is not None else 0
            if self._cachedValues[counter] != value:
                label.SetLabel("%s %s" %(formatAmount(value, prec, lowest, highest), unit))
                # Tooltip stuff
                if fit:
                    if labelName == "labelScanRes":
                        lockTime = "%s\n" % _("Lock Times").center(30)
                        for size, radius in RADII:
                            left = "%.1fs" % fit.calculateLockTime(radius)
                            right = "%s [%d]" % (size, radius)
                            lockTime += "%5s\t%s\n" % (left,right)
                        # print lockTime # THIS IS ALIGNED!
                        label.SetToolTip(wx.ToolTip(lockTime))
                    elif labelName == "labelSensorStr":
                        label.SetToolTip(wx.ToolTip(_("Type: %s - %.1f") % (fit.scanType, value)))
                    elif labelName == "labelFullSigRadius":
                        label.SetToolTip(wx.ToolTip(_("Probe Size: %.3f") % (fit.probeSize or 0) ))
                    elif labelName == "labelFullWarpSpeed":
                        label.SetToolTip(wx.ToolTip(_("Max Warp Distance: %.1f AU") % fit.maxWarpDistance))
                    else:
                        label.SetToolTip(wx.ToolTip("%.1f" % value))
                else:
                    label.SetToolTip(wx.ToolTip(""))
                self._cachedValues[counter] = value
            elif labelName == "labelFullWarpSpeed":
                if fit:
                    label.SetToolTip(wx.ToolTip(_("Max Warp Distance: %.1f AU") % fit.maxWarpDistance))
                else:
                    label.SetToolTip(wx.ToolTip(""))

            counter += 1

        self.panel.Layout()
        self.headerPanel.Layout()

TargetingMiscViewFull.register()
