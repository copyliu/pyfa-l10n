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
import re
import gui.mainFrame
import bitmapLoader
import sys
import wx.lib.mixins.listctrl  as  listmix
import wx.html
from eos.types import Ship, Module, Skill, Booster, Implant, Drone
from gui.utils.numberFormatter import formatAmount
import service
_ = wx.GetTranslation
class ItemStatsDialog(wx.Dialog):
    counter = 0
    def __init__(self, victim, fullContext=None, pos = wx.DefaultPosition, size = wx.DefaultSize, maximized = False):
        wx.Dialog.__init__(self,
                          gui.mainFrame.MainFrame.getInstance(),
                          wx.ID_ANY, title="Item stats", pos = pos, size = size,
                          style = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX |
                                  wx.MAXIMIZE_BOX | wx.RESIZE_BORDER| wx.SYSTEM_MENU)

        empty = getattr(victim, "isEmpty", False)

        if empty:
            self.Hide()
            self.Destroy()
            return

        srcContext = fullContext[0]
        try:
            itmContext = fullContext[1]
        except IndexError:
            itmContext = None
        item = getattr(victim, "item", None) if srcContext.lower() not in ("projectedcharge", "fittingcharge") else getattr(victim, "charge", None)
        if item is None:
            sMarket = service.Market.getInstance()
            item = sMarket.getItem(victim.ID)
            victim = None
        self.context = itmContext
        if item.icon is not None:
            before,sep,after = item.icon.iconFile.rpartition("_")
            iconFile = "%s%s%s" % (before,sep,"0%s" % after if len(after) < 2 else after)
            itemImg = bitmapLoader.getBitmap(iconFile, "pack")
            if itemImg is not None:
                self.SetIcon(wx.IconFromBitmap(itemImg))
        self.SetTitle("%s: %s" % ("%s Stats" % itmContext if itmContext is not None else "Stats", item.name))

        self.SetMinSize((300, 200))
        self.SetSize((500, 300))
        self.SetMaxSize((500, -1))
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.container = ItemStatsContainer(self, victim, item, itmContext)
        self.mainSizer.Add(self.container, 1, wx.EXPAND)

        if "wxGTK" in wx.PlatformInfo:
            self.closeBtn = wx.Button( self, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
            self.mainSizer.Add( self.closeBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
            self.closeBtn.Bind(wx.EVT_BUTTON, self.closeEvent)

        self.SetSizer(self.mainSizer)

        self.parentWnd = gui.mainFrame.MainFrame.getInstance()

        dlgsize = self.GetSize()
        psize = self.parentWnd.GetSize()
        ppos = self.parentWnd.GetPosition()

        ItemStatsDialog.counter += 1
        self.dlgOrder = ItemStatsDialog.counter

        counter = ItemStatsDialog.counter
        dlgStep = 30
        if counter * dlgStep > ppos.x+psize.width-dlgsize.x or counter * dlgStep > ppos.y+psize.height-dlgsize.y:
            ItemStatsDialog.counter = 1

        dlgx = ppos.x + counter * dlgStep
        dlgy = ppos.y + counter * dlgStep
        if pos == wx.DefaultPosition:
            self.SetPosition((dlgx,dlgy))
        else:
            self.SetPosition(pos)
        if maximized:
            self.Maximize(True)
        else:
            if size != wx.DefaultSize:
                self.SetSize(size)
        self.parentWnd.RegisterStatsWindow(self)

        self.Show()

        self.Bind(wx.EVT_CLOSE, self.closeEvent)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)

    def OnActivate(self, event):
        self.parentWnd.SetActiveStatsWindow(self)

    def closeEvent(self, event):

        if self.dlgOrder==ItemStatsDialog.counter:
            ItemStatsDialog.counter -= 1
        self.parentWnd.UnregisterStatsWindow(self)

        self.Destroy()

###########################################################################
## Class ItemStatsContainer
###########################################################################

class ItemStatsContainer ( wx.Panel ):

    def __init__( self, parent, stuff, item, context = None):
        wx.Panel.__init__ ( self, parent )
        mainSizer = wx.BoxSizer( wx.VERTICAL )

        self.nbContainer = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        mainSizer.Add( self.nbContainer, 1, wx.EXPAND |wx.ALL, 2 )

        self.desc = ItemDescription(self.nbContainer, stuff, item)
        self.nbContainer.AddPage(self.desc, _("Description"))

        self.params = ItemParams(self.nbContainer, stuff, item, context)
        self.nbContainer.AddPage(self.params, _("Attributes"))

        self.reqs = ItemRequirements(self.nbContainer, stuff, item)
        self.nbContainer.AddPage(self.reqs,_( "Requirements"))

        self.effects = ItemEffects(self.nbContainer, stuff, item)
        self.nbContainer.AddPage(self.effects, _("Effects"))

        if stuff is not None:
            self.affectedby = ItemAffectedBy(self.nbContainer, stuff, item)
            self.nbContainer.AddPage(self.affectedby,_( "Affected by"))

        self.nbContainer.Bind(wx.EVT_LEFT_DOWN, self.mouseHit)
        self.SetSizer(mainSizer)
        self.Layout()

    def __del__( self ):
        pass

    def mouseHit(self, event):
        tab, _ = self.nbContainer.HitTest(event.Position)
        if tab != -1:
            self.nbContainer.SetSelection(tab)

###########################################################################
## Class AutoListCtrl
###########################################################################

class AutoListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ListRowHighlighter):

    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ListRowHighlighter.__init__(self)

###########################################################################
## Class AutoListCtrl
###########################################################################

class AutoListCtrlNoHighlight(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ListRowHighlighter):

    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


###########################################################################
## Class ItemDescription
###########################################################################

class ItemDescription ( wx.Panel ):

    def __init__(self, parent, stuff, item):
        wx.Panel.__init__ (self, parent)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainSizer)

        bgcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
        fgcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT)

        self.description = wx.html.HtmlWindow(self)
        desc = item.description.replace("\r", "<br>")
        # Strip font tags
        desc = re.sub("<( *)font( *)color( *)=(.*?)>(?P<inside>.*?)<( *)/( *)font( *)>", "\g<inside>", desc)
        # Strip URLs
        desc = re.sub("<( *)a(.*?)>(?P<inside>.*?)<( *)/( *)a( *)>", "\g<inside>", desc)
        desc = "<body bgcolor='" + bgcolor.GetAsString(wx.C2S_HTML_SYNTAX) + "' text='" + fgcolor.GetAsString(wx.C2S_HTML_SYNTAX) + "' >" + desc + "</body>"

        self.description.SetPage(desc)

        mainSizer.Add(self.description, 1, wx.ALL|wx.EXPAND, 0)
        self.Layout()

###########################################################################
## Class ItemParams
###########################################################################

class ItemParams (wx.Panel):
    def __init__(self, parent, stuff, item, context = None):
        wx.Panel.__init__ (self, parent)
        mainSizer = wx.BoxSizer( wx.VERTICAL )

        self.paramList = AutoListCtrl(self, wx.ID_ANY,
                                     style = #wx.LC_HRULES |
                                      #wx.LC_NO_HEADER |
                                      wx.LC_REPORT |wx.LC_SINGLE_SEL |wx.LC_VRULES |wx.NO_BORDER)
        mainSizer.Add( self.paramList, 1, wx.ALL|wx.EXPAND, 0 )
        self.SetSizer( mainSizer )

        self.toggleView = 1
        self.stuff = stuff
        self.item = item

        self.m_staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        mainSizer.Add( self.m_staticline, 0, wx.EXPAND)
        bSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.totalAttrsLabel = wx.StaticText( self, wx.ID_ANY, u" ", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer.Add( self.totalAttrsLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT)

        self.toggleViewBtn = wx.ToggleButton( self, wx.ID_ANY, u"Toggle view mode", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer.Add( self.toggleViewBtn, 0, wx.ALIGN_CENTER_VERTICAL)

        if stuff is not None:
            self.refreshBtn = wx.Button( self, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize, 0 )
            bSizer.Add( self.refreshBtn, 0, wx.ALIGN_CENTER_VERTICAL)
            self.refreshBtn.Bind( wx.EVT_BUTTON, self.RefreshValues )

        mainSizer.Add( bSizer, 0, wx.ALIGN_RIGHT)

        self.PopulateList()

        self.toggleViewBtn.Bind(wx.EVT_TOGGLEBUTTON,self.ToggleViewMode)

    def UpdateList(self):
        self.Freeze()
        self.paramList.ClearAll()
        self.PopulateList()
        self.Thaw()
        self.paramList.resizeLastColumn(100)

    def RefreshValues(self, event):
        self.UpdateList()
        event.Skip()

    def ToggleViewMode(self, event):
        self.toggleView *=-1
        self.UpdateList()
        event.Skip()

    def PopulateList(self):
        self.paramList.InsertColumn(0,_("Attribute"))
        self.paramList.InsertColumn(1,_("Value"))
        self.paramList.SetColumnWidth(1,150)
        self.paramList.setResizeColumn(1)
        self.imageList = wx.ImageList(16, 16)
        self.paramList.SetImageList(self.imageList,wx.IMAGE_LIST_SMALL)
        if self.stuff is None or self.stuff.item == self.item:
            attrs = self.stuff.itemModifiedAttributes if self.stuff is not None else self.item.attributes
            attrsInfo = self.item.attributes if self.stuff is None else self.stuff.item.attributes
        else:
            attrs = self.stuff.chargeModifiedAttributes if self.stuff is not None else self.item.attributes
            attrsInfo = self.item.attributes if self.stuff is None else self.stuff.charge.attributes

        names = list(attrs.iterkeys())
        names.sort()

        idNameMap = {}
        idCount = 0
        for name in names:
            info = attrsInfo.get(name)


            att = attrs[name]
            val = getattr(att, "value", None)
            value = val if val is not None else att

            if info and info.displayName and self.toggleView == 1:
                attrName = info.displayName
            else:
                attrName = name

            if info:
                if info.icon is not None:
                    iconFile = info.icon.iconFile
                    icon = bitmapLoader.getBitmap(iconFile, "pack")

                    if icon is None:
                        icon = bitmapLoader.getBitmap("transparent16x16", "icons")

                    attrIcon = self.imageList.Add(icon)
                else:
                    attrIcon = self.imageList.Add(bitmapLoader.getBitmap("07_15", "pack"))
            else:
                attrIcon = self.imageList.Add(bitmapLoader.getBitmap("07_15", "pack"))


            index = self.paramList.InsertImageStringItem(sys.maxint, attrName,attrIcon)
            idNameMap[idCount] = attrName
            self.paramList.SetItemData(index, idCount)
            idCount += 1

            if self.toggleView != 1:
                valueUnit = str(value)
            elif info and info.unit:
                valueUnit = self.TranslateValueUnit(value, info.unit.displayName, info.unit.name)
            else:
                valueUnit = formatAmount(value, 3, 0, 0)


            self.paramList.SetStringItem(index, 1, valueUnit)



        self.paramList.SortItems(lambda id1, id2: cmp(idNameMap[id1], idNameMap[id2]))
        self.paramList.RefreshRows()
        self.totalAttrsLabel.SetLabel("%d attributes. " %idCount)
        self.Layout()

    def TranslateValueUnit(self, value, unitName, unitDisplayName):
        def itemIDCallback():
            item = service.Market.getInstance().getItem(value)
            return "%s (%d)" % (item.name, value) if item is not None else str(value)

        def groupIDCallback():
            group = service.Market.getInstance().getGroup(value)
            return "%s (%d)" % (group.name, value) if group is not None else str(value)

        def attributeIDCallback():
            attribute = service.Attribute.getInstance().getAttributeInfo(value)
            return "%s (%d)" % (attribute.name.capitalize(), value)

        trans = {"Inverse Absolute Percent": (lambda: (1-value)*100, unitName),
                 "Inversed Modifier Percent": (lambda: (1-value) * 100, unitName),
                 "Modifier Percent": (lambda: ("%+.2f" if ((value - 1) * 100) % 1 else "%+d") % ((value - 1) * 100), unitName),
                 "Volume": (lambda: value, u"m\u00B3"),
                 "Sizeclass": (lambda: value, ""),
                 "Absolute Percent": (lambda: (value * 100) , unitName),
                 "Milliseconds": (lambda: value / 1000.0, unitName),
                 "typeID": (itemIDCallback, ""),
                 "groupID": (groupIDCallback,""),
                 "attributeID": (attributeIDCallback, "")}

        override = trans.get(unitDisplayName)
        if override is not None:

            if type(override[0]()) == type(str()):
                fvalue = override[0]()
            else:
                v = override[0]()
                if isinstance(v, (int, float, long)):
                    fvalue = formatAmount(v, 3, 0, 0)
                else:
                    fvalue = v
            return "%s %s" % (fvalue , override[1])
        else:
            return "%s %s" % (formatAmount(value, 3, 0),unitName)

###########################################################################
## Class ItemRequirements
###########################################################################

class ItemRequirements ( wx.Panel ):

    def __init__(self, parent, stuff, item):
        wx.Panel.__init__ (self, parent, style = wx.TAB_TRAVERSAL)

        #itemId is set by the parent.
        self.romanNb = ["0","I","II","III","IV","V","VI","VII","VIII","IX","X"]
        self.skillIdHistory=[]
        mainSizer = wx.BoxSizer( wx.VERTICAL )

        self.reqTree = wx.TreeCtrl(self, style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.NO_BORDER)

        mainSizer.Add(self.reqTree, 1, wx.ALL|wx.EXPAND, 0)

        self.SetSizer(mainSizer)
        self.root = self.reqTree.AddRoot("WINRARZOR")
        self.reqTree.SetPyData(self.root, None)

        self.imageList = wx.ImageList(16, 16)
        self.reqTree.SetImageList(self.imageList)
        skillBookId = self.imageList.Add(bitmapLoader.getBitmap("skill_small", "icons"))

        self.getFullSkillTree(item,self.root,skillBookId)

        self.reqTree.ExpandAll()

        self.Layout()

    def getFullSkillTree(self,parentSkill,parent,sbIconId):
        for skill, level in parentSkill.requiredSkills.iteritems():
            child = self.reqTree.AppendItem(parent,"%s  %s" %(skill.name,self.romanNb[int(level)]), sbIconId)
            if skill.ID not in self.skillIdHistory:
                self.getFullSkillTree(skill,child,sbIconId)
                self.skillIdHistory.append(skill.ID)


###########################################################################
## Class ItemEffects
###########################################################################

class ItemEffects (wx.Panel):
    def __init__(self, parent, stuff, item):
        wx.Panel.__init__ (self, parent)
        mainSizer = wx.BoxSizer( wx.VERTICAL )

        self.effectList = AutoListCtrl(self, wx.ID_ANY,
                                     style =
                                      #wx.LC_HRULES |
                                      #wx.LC_NO_HEADER |
                                      wx.LC_REPORT |wx.LC_SINGLE_SEL |wx.LC_VRULES |wx.NO_BORDER)
        mainSizer.Add( self.effectList, 1, wx.ALL|wx.EXPAND, 0 )
        self.SetSizer( mainSizer )

        self.effectList.InsertColumn(0,"Name")
        self.effectList.InsertColumn(1,"Implemented")

        self.effectList.SetColumnWidth(0,385)

        self.effectList.setResizeColumn(0)

        self.effectList.SetColumnWidth(1,80)

        effects = item.effects
        names = list(effects.iterkeys())
        names.sort()

        for name in names:
            index = self.effectList.InsertStringItem(sys.maxint, name)

            try:
                implemented = "Yes" if effects[name].isImplemented else "No"
            except:
                implemented = "Erroneous"

            self.effectList.SetStringItem(index, 1, implemented)

        self.effectList.RefreshRows()
        self.Layout()


###########################################################################
## Class ItemAffectedBy
###########################################################################


class ItemAffectedBy (wx.Panel):
    ORDER = [Ship, Module, Drone, Implant, Booster, Skill]
    def __init__(self, parent, stuff, item):
        wx.Panel.__init__ (self, parent)
        self.stuff = stuff
        self.item = item

        self.toggleView = 1
        self.expand = -1

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.affectedBy = wx.TreeCtrl(self, style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.NO_BORDER)
        mainSizer.Add(self.affectedBy, 1, wx.ALL|wx.EXPAND, 0)

        self.m_staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )

        mainSizer.Add( self.m_staticline, 0, wx.EXPAND)
        bSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.toggleExpandBtn = wx.ToggleButton( self, wx.ID_ANY, u"Expand / Collapse", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer.Add( self.toggleExpandBtn, 0, wx.ALIGN_CENTER_VERTICAL)

        self.toggleViewBtn = wx.ToggleButton( self, wx.ID_ANY, u"Toggle view mode", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer.Add( self.toggleViewBtn, 0, wx.ALIGN_CENTER_VERTICAL)

        if stuff is not None:
            self.refreshBtn = wx.Button( self, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize, 0 )
            bSizer.Add( self.refreshBtn, 0, wx.ALIGN_CENTER_VERTICAL)
            self.refreshBtn.Bind( wx.EVT_BUTTON, self.RefreshTree )

        self.toggleViewBtn.Bind(wx.EVT_TOGGLEBUTTON,self.ToggleViewMode)
        self.toggleExpandBtn.Bind(wx.EVT_TOGGLEBUTTON,self.ToggleExpand)

        mainSizer.Add( bSizer, 0, wx.ALIGN_RIGHT)
        self.SetSizer(mainSizer)
        self.PopulateTree()
        self.Layout()

    def ExpandCollapseTree(self):

        self.Freeze()
        if self.expand == 1:
            self.affectedBy.ExpandAll()
        else:
            try:
                self.affectedBy.CollapseAll()
            except:
                pass

        self.Thaw()

    def ToggleExpand(self,event):
        self.expand *= -1
        self.ExpandCollapseTree()

    def ToggleViewTree(self):
        self.Freeze()

        root = self.affectedBy.GetRootItem()
        child,cookie = self.affectedBy.GetFirstChild(root)
        while child.IsOk():
            item,childcookie = self.affectedBy.GetFirstChild(child)
            while item.IsOk():
                change = self.affectedBy.GetPyData(item)
                display = self.affectedBy.GetItemText(item)
                self.affectedBy.SetItemText(item,change)
                self.affectedBy.SetPyData(item,display)
                item,childcookie = self.affectedBy.GetNextChild(child,childcookie)

            child,cookie = self.affectedBy.GetNextChild(root,cookie)

        self.Thaw()

    def UpdateTree(self):
        self.Freeze()
        self.affectedBy.DeleteAllItems()
        self.PopulateTree()
        self.Thaw()

    def RefreshTree(self, event):
        self.UpdateTree()
        event.Skip()

    def ToggleViewMode(self, event):
        self.toggleView *=-1
        self.ToggleViewTree()
        event.Skip()

    def PopulateTree(self):
        root = self.affectedBy.AddRoot("WINPWNZ0R")
        self.affectedBy.SetPyData(root, None)

        self.imageList = wx.ImageList(16, 16)
        self.affectedBy.SetImageList(self.imageList)


        cont = self.stuff.itemModifiedAttributes if self.item == self.stuff.item else self.stuff.chargeModifiedAttributes
        things = {}
        for attrName in cont.iterAfflictions():
            if cont[attrName] == (cont.getOriginal(attrName) or 0):
                continue

            for fit, afflictors in cont.getAfflictions(attrName).iteritems():
                for afflictor, modifier, amount in afflictors:
                    if afflictor.item is None:
                        continue
                    if afflictor.item.name not in things:
                        things[afflictor.item.name] = [type(afflictor), set(), set()]

                    info = things[afflictor.item.name]
                    info[1].add(afflictor)
                    info[2].add((attrName, modifier, amount))

        order = things.keys()
        order.sort(key=lambda x: (self.ORDER.index(things[x][0]), x))
        for itemName in order:
            info = things[itemName]

            afflictorType, afflictors, attrData = info
            counter = len(afflictors)

            baseAfflictor = afflictors.pop()
            if afflictorType == Ship:
                itemIcon = self.imageList.Add(bitmapLoader.getBitmap("ship_small", "icons"))
            elif baseAfflictor.item.icon:
                bitmap = bitmapLoader.getBitmap(baseAfflictor.item.icon.iconFile, "pack")
                itemIcon = self.imageList.Add(bitmap) if bitmap else -1
            else:
                itemIcon = -1

            child = self.affectedBy.AppendItem(root, "%s" % itemName if counter == 1 else "%s x %d" % (itemName,counter), itemIcon)

            if counter > 0:
                attributes = []
                for attrName, attrModifier, attrAmount in attrData:
                    attrInfo = self.stuff.item.attributes.get(attrName)
                    displayName = attrInfo.displayName if attrInfo else ""

                    if attrInfo:
                        if attrInfo.icon is not None:
                            iconFile = attrInfo.icon.iconFile
                            icon = bitmapLoader.getBitmap(iconFile, "pack")
                            if icon is None:
                                icon = bitmapLoader.getBitmap("transparent16x16", "icons")

                            attrIcon = self.imageList.Add(icon)
                        else:
                            attrIcon = self.imageList.Add(bitmapLoader.getBitmap("07_15", "pack"))
                    else:
                        attrIcon = self.imageList.Add(bitmapLoader.getBitmap("07_15", "pack"))

                    if attrModifier == "s*":
                        attrModifier = "*"
                        penalized = "(penalized)"
                    else:
                        penalized = ""

                    attributes.append((attrName, (displayName if displayName != "" else attrName), attrModifier, attrAmount, penalized, attrIcon))

                attrSorted = sorted(attributes, key = lambda attribName: attribName[0])

                for attr in attrSorted:
                    attrName, displayName, attrModifier, attrAmount, penalized, attrIcon = attr
                    if self.toggleView == 1:
                        treeitem = self.affectedBy.AppendItem(child, "%s %s %.2f %s" % ((displayName if displayName != "" else attrName), attrModifier, attrAmount, penalized), attrIcon)
                        self.affectedBy.SetPyData(treeitem,"%s %s %.2f %s" % (attrName, attrModifier, attrAmount, penalized))
                    else:
                        treeitem = self.affectedBy.AppendItem(child, "%s %s %.2f %s" % (attrName, attrModifier, attrAmount, penalized), attrIcon)
                        self.affectedBy.SetPyData(treeitem,"%s %s %.2f %s" % ((displayName if displayName != "" else attrName), attrModifier, attrAmount, penalized))

        self.ExpandCollapseTree()

