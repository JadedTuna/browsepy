import ui
import os
import sys
import json
import apps
import console

def reload_all(mod, name):
    reload(mod)
    for mod in sys.modules:
        if mod.startswith("{}.".format(name)):
            rmod = sys.modules[mod]
            if rmod:
                reload(rmod)

reload_all(apps, "apps")

appsfln = "apps.json"
appsdir = "apps"


class Delegate (object):
    def __init__(self, app):
        self.app = app

    def tableview_did_select(self, tableview, section, row):
        name = tableview.data_source.items[row]
        self.app.showInfo(name)

    def tableview_title_for_delete_button(self, tableview, section, row):
        # Return the title for the 'swipe-to-***' button.
        return 'Delete'


class AppInfo (object):
    def __init__(self, info):
        self.setup(info)
    
    def savefunc(self, appname, app, view):
        def wrapper(sender):
            app.apps[appname] = view["extview"].data_source.items
        
        return wrapper

    def makeLabel(self, name, frame):
        label = ui.Label()
        label.text = name
        label.frame = frame
        label.font = ("Courier", 18)

        return label

    def makeTable(self, exts, y):
        lst = ui.ListDataSource([str(i) for i in exts])
        
        table = ui.TableView()
        table.name = "extview"
        table.frame = (10, y, table.frame[2] - 5, 200)
        table.flex = "W"
        table.corner_radius = 10
        table.data_source = lst

        return table

    def setup(self, info):
        view = ui.View()
        view.name = info["appname"]
        view.bg_color = 0.89

        verlabel = self.makeLabel("Version: {}".format(info["version"]),
                                  (10, 10, 500, 32))
        autlabel = self.makeLabel("Author:  {}".format(info["author"]),
                                  (10, 52, 500, 32))
        extlabel = self.makeLabel("Supported file formats: ",
                                  (10, 94, 500, 32))
        table    = self.makeTable(info["exts"], 136)
        
        app      = info["appmng"]
        button   = app.makeButton("Save", (10, 368, 80, 32))
        button.action = self.savefunc(info["appname"], app, view)

        view.add_subview(verlabel)
        view.add_subview(autlabel)
        view.add_subview(extlabel)
        view.add_subview(table)
        view.add_subview(button)
        self.view = view
        self.view.present("sheet")
        self.view.wait_modal()


class AppManager (object):
    def __init__(self):
        self.setup()

    def makeButton(self, title, frame):
        button = ui.Button()
        button.frame = frame
        button.title = title
        button.border_width = 1
        button.corner_radius = 5
        button.border_color = 0.9
        button.bg_color = 1
        button.tint_color = 0
        button.font = ("Courier", 15)

        return button

    def makeTable(self):
        lst = ui.ListDataSource(self.apps.keys())
        delegate = Delegate(self)

        table = ui.TableView()
        table.y = 55
        table.flex = "WH"
        table.data_source = lst
        table.delegate = delegate

        return table

    def getInfo(self, mod, appname):
        info = {}
        info["version"] = getattr(mod, "__version__", "Unknown")
        info["author"]  = getattr(mod, "__author__", "Unknown")
        info["appname"] = appname
        info["exts"]    = self.apps[appname]
        info["appmng"]  = self

        return info

    def showInfo(self, appname):
        appname = str(appname)
        mod  = getattr(__import__("apps", fromlist=[appname]), appname)
        info = self.getInfo(mod, appname)

        app = AppInfo(info)

    def setup(self):
        self.apps = self.load(appsfln)

        view = ui.View()
        view.name = "App Manager"
        view.bg_color = 0.89

        nbutton = self.makeButton("New", (10, 10, 80, 32))
        dbutton = self.makeButton("Download", (100, 10, 111, 32))

        table = self.makeTable()

        view.add_subview(nbutton)
        view.add_subview(dbutton)
        view.add_subview(table)
        self.view = view
        self.view.present("sheet")

    def load(self, fn):
        if not os.path.exists(fn):
            self.save(fn, {})
        with open(fn) as fp:
            data = json.load(fp)
        return data
    
    def save(self, fn, data):
        with open(fn, "w") as fp:
            json.dump(data, fp)


appmanager = AppManager()
appmanager.view.wait_modal()
appmanager.save(appsfln, appmanager.apps)
