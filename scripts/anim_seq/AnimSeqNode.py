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
# from . import AnimSequenceAsset
from gitm_goatstro.scripts.animation_sequencer.AnimSequenceAsset import AnimSequenceAsset


class AnimationSequencerNode:

    def __init__(self, node=None):

        self.node = node
        self.sequences = dict()
        self.sequences_name_index = []
        self.working_range_min = 0
        self.working_range_max = 1

        self.node_name = 'animationSequencerNode'
        self.node_attr = 'anim_sequencer_data'

        if self.node is None:
            for n in pm.ls(type='objectSet'):
                # Look for previous node in scene
                # Changed to not look for referenced in nodes
                # TODO 1.1 put scene name into stored vars for comparison
                if self.node_name == n.nodeName():
                    self.node = n

        if not self.node:
            # Make a node
            anim_sequencer_data = '#None'
            self.node = pm.sets(n=self.node_name, empty=True)
            self.node.addAttr(self.node_attr, dt='string')
            self.node.setAttr(self.node_attr, anim_sequencer_data)

        self.refresh()

    def refresh(self):

        # clear memory
        self.sequences = dict()
        self.sequences_name_index = []
        self.get_details()
        self.get_working_range()

    def get_details(self):
        # parse
        contents = self.node.getAttr(self.node_attr).split('\n')
        index = 0
        if '#None' not in contents:
            for entry in contents:
                if entry: # carriage return makes one extra at the end of reading a line in
                    temp_dict = AttrDict()
                    for pair in entry[1:].split(' '):
                        if '=' in pair:
                            key, value = pair.split('=')
                            if key == 'name':
                                temp_dict['name'] = value
                            elif key == 'animLayers':
                                if value == '[]':
                                    temp_dict[key] = []
                                else:
                                    temp_dict[key] = value.split(',')
                            elif key == 'range_min' or key == 'range_max':
                                temp_dict[key] = int(value)
                            else:
                                temp_dict[key] = bool(value)

                    self.sequences[temp_dict.name] = AnimSequenceAsset(**temp_dict)
                    # stores index and name tuple for order manipulation
                    self.sequences_name_index.append((index, temp_dict['name']))
                    index += 1

    def edit(self, **kwargs):
        # Need to preserve animation layers post edit
        index = 0
        if kwargs['name'] in self.sequences.keys():
            index = self.get_index_by_name(kwargs['name'])
        else:
            # Make index name tuple
            self.sequences_name_index.append((len(self.sequences_name_index), kwargs['name']))

        self.sequences[kwargs['name']] = AnimSequenceAsset(**kwargs)

        if kwargs['old_name'] is not None:
            if kwargs['name'] != kwargs['old_name']:
                self.delete(name=kwargs['old_name'])
                self.reorder(kwargs['name'], index)  # reorder has write() in it
        else:
            self.write()

    def get_entry(self, name):
        if name in list(self.sequences.keys()):
            return self.sequences[name]
        else:
            return None

    def get_number_of_entries(self):
        return len(list(self.sequences.keys()))

    def get_entry_by_index(self, index):
        index, name = self.sequences_name_index[index]
        return self.sequences[name]

    def get_index_by_name(self, entry_name):
        for index, name in self.sequences_name_index:
            if entry_name == name:
                return index

    def reorder(self, name, position):

        current_pos = self.get_index_by_name(name)
        temp_dict = self.sequences
        self.sequences = AttrDict()

        if current_pos != position:
            if 0 <= position < len(self.sequences_name_index):

                self.sequences_name_index.remove((current_pos, name))
                self.sequences_name_index.insert(position, (position, name))

                for pos, name in self.sequences_name_index:
                    self.sequences[name] = temp_dict[name]

            self.write()

    def write(self):
        output = ''
        for index, name in self.sequences_name_index:
            entry = self.sequences[name]

            output += (f"#name={entry.details.name} range_min={entry.details.range_min} "
                       f"range_max={entry.details.range_max} isLoop={entry.details.isLoop} "
                       f"isActive={entry.details.isActive} animLayers={entry.details.animLayers}\n")

        self.node.setAttr(self.node_attr, output)
        self.refresh()

    def delete(self, name=None, index=None):
        if index is not None:
            name = self.get_entry_by_index(index).name

        if name is not None:
            # remove it from dictionary
            self.sequences.pop(name)
            # remove it from index,name
            i = self.get_index_by_name(name)
            self.sequences_name_index.remove((i, name))

        self.write()

    def list(self, output=False):
        if output:
            print("Animation Sequences: ")
            for name, entry in list(self.sequences.items()):
                print(f"   Name:     {entry.name}")
                print(f"   Range:    {entry.range_min} : {entry.range_max}")
                print(f"   isLoop:   {entry.isLoop}")
                print(f"   isActive: {entry.isActive}\n")
        anim_list = []
        if len(list(self.sequences.keys())) > 0:
            for name, entry in list(self.sequences.items()):
                anim_list.append([entry.name,
                                  entry.range_min,
                                  entry.range_max,
                                  entry.isLoop,
                                  entry.isActive,
                                  entry.animLayers]) # entry.flatten_list_to_string(entry.animLayers)
        return anim_list

    def get_working_range(self):

        self.working_range_min = 0
        self.working_range_max = 1

        for key, value in list(self.sequences.items()):
            if value.details.range_min < self.working_range_min:
                self.working_range_min = value.details.range_min
            if value.details.range_max > self.working_range_max:
                self.working_range_max = value.details.range_max

    def set_range_from_entry(self, anim_entry):
        anim_entry = self.get_entry(anim_entry)
        pm.playbackOptions(min=anim_entry.details.range_min, max=anim_entry.details.range_max)

    def set_working_range(self):
        pm.playbackOptions(min=self.working_range_min, max=self.working_range_max)

    @staticmethod
    def get_selected_anim_layer():
        sel_layers = []
        layers = AnimSequenceAsset.get_anim_layers()
        if layers is not None:
            for layer in layers['childrenLayers']:
                if pm.animLayer(layer, q=True, sel=True):
                    sel_layers.append(layer)
        return sel_layers


    @staticmethod
    def get_maya_scene_information():
        """
        Gets the maya information on the scene,
        FileName, playback min max
        :returns
        """
        scene_info = dict()
        scene_info['min'] = int(pm.playbackOptions(q=True, min=True))
        scene_info['max'] = int(pm.playbackOptions(q=True, max=True))
        scene_info['scene_name'] = os.path.splitext(os.path.basename(pm.sceneName()))[0]

        return scene_info