"""
Copyright 2019 Ira Goeddel
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pymel.core as pm
import os
from gitm_goatstro.scripts.animation_sequencer.AnimationSequencerNode import AnimationSequencerNode


class AnimationSequencerGUI:

    def __init__(self):

        self.winID = 'animation_sequence_manager'
        self.winTitle = 'Animation Sequence Manager'
        self.scene_amm_node = AnimationSequencerNode()
        w = 600
        h = 140

        if pm.window(self.winID, q=True, exists=True):
            pm.deleteUI(self.winID)
        if pm.windowPref(self.winID, q=True, exists=True):
            pm.windowPref(self.winID, remove=True)

        self.window = pm.window(self.winID, title=self.winTitle, widthHeight=(w, h), s=False)

        columnLayout = pm.columnLayout(nch=2)

        pm.text(label=f"On {'Name': <40}{'Min': <5}{'Max': <4}{'Loops  '}{'Layers'}",
                align='left', font='fixedWidthFont', h=20, )

        rowLayout = pm.rowLayout(nch=3, nc=2, parent=columnLayout)

        self.tsl1 = pm.textScrollList(parent=rowLayout,
                                      width=w - 20,
                                      height=h - 22,
                                      font='fixedWidthFont')
        self.rmb_menu()

        reorderButtsColumnLayout = pm.columnLayout(nch=2, p=rowLayout)

        up_butt = pm.iconTextButton(style='iconOnly', image='icon_up_arrow.png',
                                    p=reorderButtsColumnLayout, w=13, h=46,
                                    c=lambda *args: self.reorder_up())
        dn_butt = pm.iconTextButton(style='iconOnly', image='icon_dn_arrow.png',
                                    p=reorderButtsColumnLayout, w=13, h=46,
                                    c=lambda *args: self.reorder_down())

        pm.showWindow()

        self.tsl1.doubleClickCommand(lambda *args: self.dbl_click_cmd())

        pm.scriptJob(parent=self.window, ro=True, event=['SceneOpened', self.update])

        self.update()

    def update(self, sel_index=None):

        sel = self.get_selected_index()

        pm.textScrollList(self.tsl1, e=True, ra=True)

        if list(self.scene_amm_node.ammn_entries.keys()) != [0]:
            # print self.scene_amm_node.ammn_entries.keys()

            for index, anim_name in self.scene_amm_node.sequences_name_index:
                # anim = self.scene_amm_node.sequences[name]
                pm.textScrollList(self.tsl1, e=True, append=self.gen_tsl_string(anim_name))

            if sel is not None:
                if sel < self.scene_amm_node.get_number_of_entries():
                    #1.0.9 docs... finally read them to use pymel syntax
                    if sel_index is not None:
                        sel = sel_index #offset for reorder
                    self.tsl1.selectIndexedItems([sel + 1]) #offset from internal list back to tsl index starting at 1

    def gen_tsl_string(self, anim_name):

        anim_entry = self.scene_amm_node.sequences[anim_name]

        if anim_entry.details.isActive:
            isActive = '*'
        else:
            isActive = '!'

        if anim_entry.details.isLoop:
            isLoop = '@'
        else:
            isLoop = '~'

        min_padding = (7 - len(str(anim_entry.details.range_min)))

        if len(anim_entry.details.animLayers) != 0:
            # if '[]' in self.animLayers:
            #     self.animLayers.remove('[]')
            anim_layers = anim_entry.flatten_list_to_string(anim_entry.details.animLayers)
        else:
            anim_layers = 'none'

        string = f"{isActive: <2}{anim_entry.details.name: <40}{anim_entry.details.range_min: <5}" \
                 f"{anim_entry.details.range_max: <4}{isLoop: <6} {anim_layers}"

        return string

    def dbl_click_cmd(self):
        index = self.get_selected_index()
        min = pm.playbackOptions(q=True, min=True)
        max = pm.playbackOptions(q=True, max=True)

        if index is not None:
            entry = self.scene_amm_node.get_entry_by_index(index)
            if entry.details.range_min == min and entry.details.range_max == max:
                self.set_working_range()
            else:
                self.scene_amm_node.set_range_from_entry(entry.details.name)
        else:
            self.add_entry()

    def reorder_up(self):
        index = self.get_selected_index()
        if index is not None:
            entry = self.scene_amm_node.get_entry_by_index(index)

            if index != 0:
                self.scene_amm_node.reorder(entry.details.name, (index - 1))
                self.update(sel_index=index - 1)

    def reorder_down(self):
        index = self.get_selected_index()
        if index is not None:
            entry = self.scene_amm_node.get_entry_by_index(index)

            if index + 1 < self.scene_amm_node.get_number_of_entries(): #offset to textfieldlist starting at 1
                self.scene_amm_node.reorder(entry.details.name, (index + 1))
                self.update(sel_index=index + 1)

    def get_selected_index(self):
        tsl_index = pm.textScrollList(self.tsl1, q=True, sii=True)
        if tsl_index:
            return tsl_index[0] - 1
        else:
            return None

    def rmb_menu(self):

        popup_menu = pm.popupMenu()

        pm.menuItem(label='Add Entry', c=lambda *args: self.add_entry(), p=popup_menu)
        pm.menuItem(label='Edit Entry', c=lambda *args: self.edit_entry(), p=popup_menu)
        pm.menuItem(d=True, p=popup_menu)
        pm.menuItem(label='Add AnimLayer', c=lambda *args: self.add_anim_layer(), p=popup_menu)
        pm.menuItem(label='Remove AnimLayer', c=lambda *args: self.remove_anim_layer(), p=popup_menu)
        pm.menuItem(d=True, p=popup_menu)
        pm.menuItem(label='Set Working Range', c=lambda *args: self.set_working_range(), p=popup_menu)
        pm.menuItem(d=True, p=popup_menu)
        pm.menuItem(label='Delete Entry', c=lambda *args: self.del_entry(), p=popup_menu)

    def add_entry(self):
        AnimationEntryGui(amm_node=self.scene_amm_node,
                          win=self.window,
                          gui=self)

    def edit_entry(self):
        # get entry from index selection
        index = self.get_selected_index()

        AnimationEntryGui(amm_node=self.scene_amm_node,
                          amm_node_entry=self.scene_amm_node.get_entry_by_index(index),
                          win=self.window,
                          gui=self)

    def add_anim_layer(self):
        index = self.get_selected_index()
        if index is not None:
            layers = self.scene_amm_node.get_selected_anim_layer()

            entry_key = self.scene_amm_node.get_entry_by_index(index)
            entry_key.add_animation_layers(layers)
            self.scene_amm_node.write()
            self.update()

    def remove_anim_layer(self):
        index = self.get_selected_index()
        if index is not None:
            layers = self.scene_amm_node.get_selected_anim_layer()
            if len(layers):
                entry_key = self.scene_amm_node.get_entry_by_index(index)
                entry_key.remove_animation_layers(layers)
                self.scene_amm_node.write()
                self.update()

    def set_working_range(self):
        self.scene_amm_node.set_working_range()

    def del_entry(self):
        index = self.get_selected_index()
        if index is not None:
            self.scene_amm_node.delete(index=index)
            self.update()


class AnimationEntryGui:

    def __init__(self, gui, win=None, amm_node=None, amm_node_entry=None):

        self.winID = 'animation_scenes_entry'
        self.winTitle = 'Animation Scenes Entry'
        self.amm_node = amm_node
        self.parent_class = gui

        if pm.window(self.winID, q=True, exists=True):
            pm.deleteUI(self.winID)
        if pm.windowPref(self.winID, q=True, exists=True):
            pm.windowPref(self.winID, remove=True)

        if win is not None:
            self.window = pm.window(self.winID, title=self.winTitle, widthHeight=(438, 65), p=win, s=False)
        else:
            self.window = pm.window(self.winID, title=self.winTitle, widthHeight=(438, 65), s=False )

        mainColumnLayout = pm.columnLayout(nch=3)

        titleRowLayout = pm.rowLayout(nch=5, nc=5, cw5=(62, 200, 58, 50, 50), p=mainColumnLayout)

        pm.text(' ', p=titleRowLayout)
        pm.text('Name', p=titleRowLayout)
        pm.text('Start', p=titleRowLayout)
        pm.text('End', p=titleRowLayout)
        pm.text('  ', p=titleRowLayout)

        dataRowLayout = pm.rowLayout(nch=5, nc=5, p=mainColumnLayout)

        self.isActive = pm.checkBox(p=dataRowLayout, label='isActive')

        nameRow = pm.rowLayout(nch=2, nc=2, p=dataRowLayout)
        self.nameButton = pm.iconTextButton(style='iconOnly', image='icon_rt_arrow',
                                            p=nameRow, w=10, h=15, c=lambda *args: self.namePop())
        self.nameField = pm.textField(p=nameRow, w=190, h=19)

        startRow = pm.rowLayout(nch=2, nc=2, p=dataRowLayout)
        self.startButton = pm.iconTextButton(style='iconOnly', image='icon_rt_arrow',
                                             p=startRow, w=10, h=15, c=lambda *args: self.startPop())
        self.startField = pm.textField(p=startRow, w=40, h=19)

        endRow = pm.rowLayout(nch=2, nc=2, p=dataRowLayout)
        self.endButton = pm.iconTextButton(style='iconOnly', image='icon_rt_arrow',
                                           p=endRow, w=10, h=15, c=lambda *args: self.endPop())
        self.endField = pm.textField(p=endRow, w=40, h=19)

        self.isLoop = pm.checkBox(p=dataRowLayout, label='isLoop')

        submitRowLayout = pm.rowLayout(p=mainColumnLayout, nch=2, nc=2, cw2=(267, 170), cl2=('right', 'right'))

        self.anim_layer_text = pm.text(label='AnimLayers:', p=submitRowLayout)

        buttonRowLayout = pm.rowLayout(nch=3, nc=3, p=submitRowLayout, w=200)

        self.cancelButton = pm.button(label='Cancel', p=buttonRowLayout, w=66, c=lambda *args: self.cancel())
        self.submitButton = pm.button(label='Submit', p=buttonRowLayout, w=96, c=lambda *args: self.submit())

        self.anim_layer = []

        if amm_node_entry is None:
            min = int(pm.playbackOptions(q=True, min=True))
            max = int(pm.playbackOptions(q=True, max=True))

            pm.checkBox(self.isActive, e=True, v=True)
            pm.textField(self.startField, e=True, tx=min)
            pm.textField(self.endField, e=True, tx=max)

            self.name = None

        else:
            self.name = amm_node_entry.details.name
            name = amm_node_entry.details.name
            range_min = amm_node_entry.details.range_min
            range_max = amm_node_entry.details.range_max
            isLoop = amm_node_entry.details.isLoop
            isActive = amm_node_entry.details.isActive
            self.anim_layer = amm_node_entry.details.animLayers
            flat_anim_layer = amm_node_entry.flatten_list_to_string(self.anim_layer)

            pm.checkBox(self.isActive, e=True, v=isActive)
            pm.textField(self.nameField, e=True, tx=name)
            pm.textField(self.startField, e=True, tx=range_min)
            pm.textField(self.endField, e=True, tx=range_max)
            pm.checkBox(self.isLoop, e=True, v=isLoop)
            pm.text(self.anim_layer_text, e=True, label=f'AnimLayers: {flat_anim_layer}')

        pm.showWindow()

    # Populate Information
    def namePop(self):
        scene_name = os.path.splitext(os.path.basename(pm.sceneName()))[0]
        pm.textField(self.nameField, e=True, tx=scene_name)

    def startPop(self):
        pm.textField(self.startField, e=True, tx=int(pm.currentTime(q=True)))

    def endPop(self):
        pm.textField(self.endField, e=True, tx=int(pm.currentTime(q=True)))

    def cancel(self):
        pm.deleteUI(self.winID)

    def submit(self):
        isActive = pm.checkBox(self.isActive, q=True, v=True)
        nameField = pm.textField(self.nameField, q=True, tx=True)
        startField = pm.textField(self.startField, q=True, tx=True)
        endField = pm.textField(self.endField, q=True, tx=True)
        isLoop = pm.checkBox(self.isLoop, q=True, v=True)

        if len(nameField) > 0:
            print(('Submitting: {0},({1}-{2}), isLoop={3}, isActive={4}'.format(nameField,
                                                                               startField,
                                                                               endField,
                                                                               isLoop,
                                                                               isActive)))

            self.amm_node.edit(old_name=self.name, name=nameField, range_min=startField, range_max=endField,
                               isLoop=isLoop, isActive=isActive)

        self.parent_class.update()
        pm.deleteUI(self.winID)


if __name__ == "__main__":

    AnimationSequencerGUI()
