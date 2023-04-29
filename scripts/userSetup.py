import pymel.core as pm
import maya
import maya.cmds as cmds
import os

class MenuItem():

    def __init__(self, command_func, kwargs):
        self.command = command_func
        self.label = None
        self.parent = None
        self.edit = False

        if "label" in kwargs.keys():
            self.label = kwargs["label"]
        if "parent" in kwargs.keys():
            self.parent = kwargs["parent"]
        if "edit" in kwargs.keys():
            self.edit = kwargs["edit"]

    def __repr__(self):
        return f"import {self.module} as {self.name}"

    def execute(self):
        self.command()



class MyMenuCommand:
    def __init__(self, command_func):
        self.command_func = command_func

    def execute(self):
        self.command_func()

my_module_command = MyMenuCommand(lambda: __import__('my_module', globals(), locals(), ['fu'], 0))
my_module_command.execute()


class ModuleImporter:
    def __init__(self, module_name):
        self.module_name = module_name

    def generate_import_command(self):
        return lambda: __import__(self.module_name, globals(), locals(), ['fu'], 0)

my_module_importer = ModuleImporter('my_module')
my_module_command = MyMenuCommand(my_module_importer.generate_import_command())
my_module_command.execute()


import pymel.core as pm

class MayaMenuItem:
    def __init__(self, module_name, label, parent, var_name, command_name):
        self.module_name = module_name
        self.label = label
        self.parent = parent
        self.var_name = var_name
        self.command_name = command_name

    def generate_import_command(self):
        return lambda: __import__(self.module_name, globals(), locals(), [self.var_name], 0)

    def generate_execute_command(self):
        return lambda: getattr(globals()[self.var_name], self.command_name)()

    def create_menu_item(self):
        import_command = self.generate_import_command()
        execute_command = self.generate_execute_command()
        pm.menuItem(label=self.label, parent=self.parent, c=execute_command, rp="W", i="pythonFamily.png",
                    dcc=execute_command, ec=execute_command)
        pm.scriptJob(event=["quitApplication", lambda: pm.deleteUI(self.parent)])
        import_command()

my_module_menu_item = MayaMenuItem('my_module', 'My Command', 'My Parent Menu', 'fu', 'my_command')
my_module_menu_item.create_menu_item()



class MayaMenuItem:
    def __init__(self, module_name, label, parent, var_name, command_name):
        self.module_name = module_name
        self.label = label
        self.parent = parent
        self.var_name = var_name
        self.command_name = command_name

    def generate_import_command(self):
        return lambda: __import__(self.module_name, globals(), locals(), [self.var_name], 0)

    def generate_execute_command(self):
        return lambda: getattr(globals()[self.var_name], self.command_name)()

    def create_menu_item(self):
        import_command = self.generate_import_command()
        execute_command = self.generate_execute_command()
        if pm.menuItem(self.label, ex=True, p=self.parent):
            pm.menuItem(label=self.label, e=True, parent=self.parent, c=execute_command, rp="W", i="pythonFamily.png",
                        dcc=execute_command, ec=execute_command)
        else:
            pm.menuItem(label=self.label, parent=self.parent, c=execute_command, rp="W", i="pythonFamily.png",
                        dcc=execute_command, ec=execute_command)
        pm.scriptJob(event=["quitApplication", lambda: pm.deleteUI(self.parent)])
        import_command()

my_module_menu_item = MayaMenuItem('my_module', 'My Command', 'My Parent Menu', 'fu', 'my_command')
my_module_menu_item.create_menu_item()

import sys
if 'userSetup' in sys.modules:
    reload(sys.modules['userSetup'])
else:
    import userSetup