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
from gitm_goatstro.scripts.animation_sequencer.NamedObject import NamedObject


class AnimSequenceAsset(NamedObject):

    def __init__(self, **kwargs): # name, range_min, range_max, isLoop, isActive, animLayers=list()
        super().__init__(**kwargs)
        self.set(**self.details_core())
        self.set(**kwargs)

    @staticmethod
    def details_core():
        """
        Overriding ObjectAsset details_core because of minimum writing to node setup
        """
        return{'name': None,
               'range_min': 0,
               'range_max': 1,
               'isActive': True,
               'isLoop': False,
               'animLayers': []}

    @property
    def isActive(self):
        return self.details.isActive

    def show_content(self):
        print(f"{self.details.isActive: <2}{self.details.name: <40}{self.details.range_min: <5}"
              f"<::>{self.details.range_max: <4}{self.details.isLoop}---{self.details.animLayers}")

    def activate_animation_layers(self):
        active_layer = []
        deactive_layer = []
        anim_layers_dict = self.get_anim_layers()
        if len(self.animLayers):
            for anim_layer in anim_layers_dict['childrenLayers']:
                if str(anim_layer) in self.animLayers:
                    active_layer.append(anim_layer)
                else:
                    deactive_layer.append(anim_layer)
            for layer in active_layer:
                pm.animLayer(layer, e=True, mute=False)
            for layer in deactive_layer:
                pm.animLayer(layer, e=True, mute=True)
        # turn on baseAnimation
        else:
            for layer in anim_layers_dict['childrenLayers']:
                pm.animLayer(layer, e=True, mute=True)

    def add_animation_layers(self, animation_layers):
        for layer in animation_layers:
            if str(layer) not in self.animLayers:
                self.animLayers.append(str(layer))

    def remove_animation_layers(self, animation_layers):
        for layer in animation_layers:
            if str(layer) in self.animLayers:
                self.animLayers.remove(str(layer))

    @staticmethod
    def get_anim_layers():
        root_layer = pm.animLayer(q=True, r=True)
        if root_layer is not None:
            kid_layers = pm.animLayer(root_layer, q=True, c=True)
            return {"rootLayer": root_layer, "childrenLayers": kid_layers}
        else:
            return None

    @staticmethod
    def flatten_list_to_string(list_to_flatten, separator=','):
        flattened = ''
        for s in list_to_flatten:
            if s == list_to_flatten[0]:
                flattened = s
            else:
                flattened = '{}{}{}'.format(flattened, separator, s)
        return flattened