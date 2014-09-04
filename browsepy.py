# coding: utf-8

import ui
import os
import sys
import json
import apps

def reload_all(mod, name):
    reload(mod)
    for mod in sys.modules:
        if mod.startswith("{}.".format(name)):
            rmod = sys.modules[mod]
            if rmod:
                reload(rmod)

reload_all(apps, "apps")

appsfn  = "apps.json"
appsdir = "apps"

if not os.path.exists(appsfn):
    with open(appsfn, "w") as fp:
        fp.write("{}")

with open(appsfn) as fp:
    appnames = json.load(fp)

if not os.path.exists(appsdir):
    os.mkdir(appsdir)
    with open(os.path.join(appsdir, "__init__.py"), "w"):
        pass

apps = {}
_apps = __import__("apps", fromlist=[str(i) for i in appnames.keys()])
for name, exts in appnames.items():
    apps[getattr(_apps, name).App] = exts

class Delegate(object):
    def __init__(self):
        self.curpath = os.getcwd()
    
    def tableview_did_select(self, tableview, section, row):
        # Called when a row was selected.
        name = tableview.data_source.items[row]
        abspath = os.path.abspath(os.path.join(self.curpath, name))
        if name.endswith("/"):
            _name = name[:-1]
            if os.path.isdir(abspath):
                lst = self.getDirListing(abspath)
                if lst:
                    self.curpath = abspath
                    tableview.data_source.items = lst.items
                    tableview.superview.name = os.path.split(self.curpath)[-1]
        else:
            if os.path.isfile(abspath):
                _, ext = os.path.splitext(abspath)
                for App, exts in apps.items():
                    if ext in exts:
                        return App(view, abspath)

    def getDirListing(self, curpath):
        try:
            all = os.listdir(curpath)
        except OSError:
            return
        folders = [i + "/" for i in all if os.path.isdir(
                                        os.path.join(curpath, i)
                                        )]
        files   = [i for i in all if os.path.isfile(
                                        os.path.join(curpath, i)
                                        )]
        lst = ui.ListDataSource(["../"] + folders + files)
        lst.font = ('Courier', 18)
        return lst

view = ui.View()

table = ui.TableView()
table.flex = "WH"
table.delegate = Delegate()
table.data_source = table.delegate.getDirListing(table.delegate.curpath)

view.name = os.path.split(table.delegate.curpath)[-1]
view.add_subview(table)

view.present("sheet")
