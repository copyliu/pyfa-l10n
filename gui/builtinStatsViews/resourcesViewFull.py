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
from gui import bitmapLoader
from gui import pygauge as PG

from eos.types import Hardpoint

from gui.utils.numberFormatter import formatAmount
_ = wx.GetTranslation
class ResourcesViewFull(StatsView):
    name = "resourcesViewFull"
    def __init__(self, parent):
        StatsView.__init__(self)
        self.parent = parent
    def getHeaderText(self, fit):
        return _("Resources")

    def getTextExtentW(self, text):
        width, height = self.parent.GetTextExtent( text )
        return width

    def populatePanel(self, contentPanel, headerPanel):

        contentSizer = contentPanel.GetSizer()
        root = wx.BoxSizer(wx.VERTICAL)
        contentSizer.Add(root, 0, wx.EXPAND, 0)

        sizer = wx.GridSizer(1, 4)
        root.Add(sizer, 0, wx.EXPAND)
        root.Add(wx.StaticLine(contentPanel, wx.ID_ANY, style=wx.HORIZONTAL), 0, wx.EXPAND)

        sizerResources = wx.BoxSizer(wx.HORIZONTAL)
        root.Add(sizerResources, 1, wx.EXPAND, 0)

        parent = self.panel = contentPanel
        self.headerPanel = headerPanel
        panel = "full"


        base = sizerResources

        #Turrets & launcher hardslots display
        tooltipText = {"turret":_("Turret hardpoints"), "launcher":_("Launcher hardpoints"), "drones":_("Drones active"), "calibration":_("Calibration")}
        for type in ("turret", "launcher", "drones", "calibration"):
            box = wx.BoxSizer(wx.HORIZONTAL)

            bitmap = bitmapLoader.getStaticBitmap("%s_big" % type, parent, "icons")
            tooltip = wx.ToolTip(tooltipText[type])
            bitmap.SetToolTip(tooltip)

            box.Add(bitmap, 0, wx.ALIGN_CENTER)

            sizer.Add(box, 0, wx.ALIGN_CENTER)

            suffix = {'turret':_('Hardpoints'), 'launcher':_('Hardpoints'), 'drones':_('Active'), 'calibration':_('Points')}
            lbl = wx.StaticText(parent, wx.ID_ANY, "0")
            setattr(self, "label%sUsed%s%s" % (panel.capitalize(), type.capitalize(), suffix[type].capitalize()), lbl)
            box.Add(lbl, 0, wx.ALIGN_CENTER | wx.LEFT, 5)

            box.Add(wx.StaticText(parent, wx.ID_ANY, "/"), 0, wx.ALIGN_CENTER)

            lbl = wx.StaticText(parent, wx.ID_ANY, "0")
            setattr(self, "label%sTotal%s%s" % (panel.capitalize(), type.capitalize(), suffix[type].capitalize()), lbl)
            box.Add(lbl, 0, wx.ALIGN_CENTER)


        #PG, Cpu & drone stuff
        tooltipText = {"cpu":"CPU", "pg":_("PowerGrid"), "droneBay":_("Drone bay"), "droneBandwidth":_("Drone bandwidth")}
        for i, group in enumerate((("cpu", "pg"), ("droneBay", "droneBandwidth"))):
            main = wx.BoxSizer(wx.VERTICAL)
            base.Add(main, 1 , wx.ALIGN_CENTER)

            for type in group:
                capitalizedType = type[0].capitalize() + type[1:]
                bitmap = bitmapLoader.getStaticBitmap(type + "_big", parent, "icons")
                tooltip = wx.ToolTip(tooltipText[type])
                bitmap.SetToolTip(tooltip)

                stats = wx.BoxSizer(wx.VERTICAL)
                absolute =  wx.BoxSizer(wx.HORIZONTAL)
                stats.Add(absolute, 0, wx.EXPAND)

                b = wx.BoxSizer(wx.HORIZONTAL)
                main.Add(b, 1, wx.ALIGN_CENTER)

                b.Add(bitmap, 0, wx.ALIGN_BOTTOM)

                b.Add(stats, 1, wx.EXPAND)

                lbl = wx.StaticText(parent, wx.ID_ANY, "0")
                setattr(self, "label%sUsed%s" % (panel.capitalize(), capitalizedType), lbl)
                absolute.Add(lbl, 0, wx.ALIGN_LEFT | wx.LEFT, 3)

                absolute.Add(wx.StaticText(parent, wx.ID_ANY, "/"), 0, wx.ALIGN_LEFT)

                lbl = wx.StaticText(parent, wx.ID_ANY, "0")
                setattr(self, "label%sTotal%s" % (panel.capitalize(), capitalizedType), lbl)
                absolute.Add(lbl, 0, wx.ALIGN_LEFT)

                units = {"cpu":_(" tf"), "pg":_(" MW"), "droneBandwidth":_(" mbit/s"), "droneBay":u" m\u00B3"}
                lbl = wx.StaticText(parent, wx.ID_ANY, "%s" % units[type])
                absolute.Add(lbl, 0, wx.ALIGN_LEFT)

                # Gauges modif. - Darriele

                gauge = PG.PyGauge(parent, wx.ID_ANY, 1)
                gauge.SetValueRange(0, 0)
                gauge.SetMinSize((self.getTextExtentW("1.999M/1.99M MW"), 23))
                gauge.SetFractionDigits(2)

                setattr(self, "gauge%s%s" % (panel.capitalize(),capitalizedType), gauge)
                stats.Add(gauge, 0, wx.ALIGN_CENTER)

    def refreshPanel(self, fit):
        #If we did anything intresting, we'd update our labels to reflect the new fit's stats here

        stats = (("label%sUsedTurretHardpoints", lambda: fit.getHardpointsUsed(Hardpoint.TURRET), 0, 0, 0),
                         ("label%sTotalTurretHardpoints", lambda: fit.ship.getModifiedItemAttr('turretSlotsLeft'), 0, 0, 0),
                         ("label%sUsedLauncherHardpoints", lambda: fit.getHardpointsUsed(Hardpoint.MISSILE), 0, 0, 0),
                         ("label%sTotalLauncherHardpoints", lambda: fit.ship.getModifiedItemAttr('launcherSlotsLeft'), 0, 0, 0),
                         ("label%sUsedDronesActive", lambda: fit.activeDrones, 0, 0, 0),
                         ("label%sTotalDronesActive", lambda: fit.extraAttributes["maxActiveDrones"], 0, 0, 0),
                         ("label%sUsedCalibrationPoints", lambda: fit.calibrationUsed, 0, 0, 0),
                         ("label%sTotalCalibrationPoints", lambda: fit.ship.getModifiedItemAttr('upgradeCapacity'), 0, 0, 0),
                         ("label%sUsedPg", lambda: fit.pgUsed, 4, 0, 9),
                         ("label%sUsedCpu", lambda: fit.cpuUsed, 4, 0, 9),
                         ("label%sTotalPg", lambda: fit.ship.getModifiedItemAttr("powerOutput"), 4, 0, 9),
                         ("label%sTotalCpu", lambda: fit.ship.getModifiedItemAttr("cpuOutput"), 4, 0, 9),
                         ("label%sUsedDroneBay", lambda: fit.droneBayUsed, 3, 0, 9),
                         ("label%sUsedDroneBandwidth", lambda: fit.droneBandwidthUsed, 3, 0, 9),
                         ("label%sTotalDroneBay", lambda: fit.ship.getModifiedItemAttr("droneCapacity"), 3, 0, 9),
                         ("label%sTotalDroneBandwidth", lambda: fit.ship.getModifiedItemAttr("droneBandwidth"), 3, 0, 9))
        panel = "Full"
        usedTurretHardpoints = 0
        totalTurretHardpoints = 0
        usedLauncherHardpoints = 0
        totalLauncherHardPoints = 0

        for labelName, value, prec, lowest, highest in stats:
            label = getattr(self, labelName % panel)
            value = value() if fit is not None else 0
            value = value if value is not None else 0
            if labelName % panel == "label%sUsedTurretHardpoints" % panel:
                usedTurretHardpoints = value
                labelUTH = label

            if labelName % panel == "label%sTotalTurretHardpoints" % panel:
                totalTurretHardpoints = value
                labelTTH = label

            if labelName % panel == "label%sUsedLauncherHardpoints" % panel:
                usedLauncherHardpoints = value
                labelULH = label

            if labelName % panel == "label%sTotalLauncherHardpoints" % panel:
                totalLauncherHardPoints = value
                labelTLH = label

            if labelName % panel == "label%sUsedDronesActive" % panel:
                usedDronesActive = value
                labelUDA = label

            if labelName % panel == "label%sTotalDronesActive" % panel:
                totalDronesActive = value
                labelTDA = label

            if labelName % panel == "label%sUsedCalibrationPoints" % panel:
                usedCalibrationPoints = value
                labelUCP = label

            if labelName % panel == "label%sTotalCalibrationPoints" % panel:
                totalCalibrationPoints = value
                labelTCP = label

            if isinstance(value, basestring):
                label.SetLabel(value)
                label.SetToolTip(wx.ToolTip(value))
            else:
                label.SetLabel(formatAmount(value, prec, lowest, highest))
                label.SetToolTip(wx.ToolTip("%.1f" % value))

        colorWarn = wx.Colour(204, 51, 51)
        colorNormal = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT)

        if usedTurretHardpoints > totalTurretHardpoints:
            colorT = colorWarn
        else:
            colorT = colorNormal
        if usedLauncherHardpoints > totalLauncherHardPoints:
            colorL = colorWarn
        else:
            colorL = colorNormal
        if usedDronesActive > totalDronesActive:
            colorD = colorWarn
        else:
            colorD = colorNormal
        if usedCalibrationPoints > totalCalibrationPoints:
            colorC = colorWarn
        else:
            colorC = colorNormal

        labelUTH.SetForegroundColour(colorT)
        labelTTH.SetForegroundColour(colorT)
        labelULH.SetForegroundColour(colorL)
        labelTLH.SetForegroundColour(colorL)
        labelUDA.SetForegroundColour(colorD)
        labelTDA.SetForegroundColour(colorD)
        labelUCP.SetForegroundColour(colorC)
        labelTCP.SetForegroundColour(colorC)

        if fit is not None:
            resMax = (lambda: fit.ship.getModifiedItemAttr("cpuOutput"),
                    lambda: fit.ship.getModifiedItemAttr("powerOutput"),
                    lambda: fit.ship.getModifiedItemAttr("droneCapacity"),
                    lambda: fit.ship.getModifiedItemAttr("droneBandwidth"))

        i = 0
        for resourceType in ("cpu", "pg", "droneBay", "droneBandwidth"):
            if fit is not None:
                capitalizedType = resourceType[0].capitalize() + resourceType[1:]

                gauge = getattr(self, "gauge%s%s" % (panel, capitalizedType))
                resUsed = getattr(fit,"%sUsed" % resourceType)

                gauge.SetValueRange(resUsed or 0, resMax[i]() or 0)

                i+=1
            else:
                capitalizedType = resourceType[0].capitalize() + resourceType[1:]

                gauge = getattr(self, "gauge%s%s" % (panel, capitalizedType))

                gauge.SetValueRange(0, 0)

                i+=1

        self.panel.Layout()
        self.headerPanel.Layout()

ResourcesViewFull.register()
