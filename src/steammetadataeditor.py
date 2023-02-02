#!/usr/bin/env python3
#
# A Metadata Editor for Steam Applications
# Copyright (C) 2021  Tomás Ralph
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##################################
#                                #
#       Created by tralph3       #
#   https://github.com/tralph3   #
#                                #
##################################

from hashlib import sha1
import tkinter as tk
from tkinter.ttk import Treeview, Style
from tkinter import filedialog, messagebox
from datetime import datetime
from os import path, getenv, _exit, makedirs
from pathlib import Path
from platform import system
from struct import pack, unpack
from json import load, dump, JSONDecodeError
from configparser import ConfigParser
from copy import deepcopy
from argparse import ArgumentParser
from glob import glob

# defaults
BG = "#23272c"
FG = "#b8b6b4"

ENTRY_FG = "#e9e9e9"
ENTRY_BG = "#1d1b19"
ENTRY_RELIEF = "flat"
ENTRY_PADDING = 5

BTTN_ACTIVE_BG = "#3ea7f3"
BTTN_ACTIVE_FG = "#c3e1f8"
BTTN_BG = "#2f7dde"
BTTN_FG = "#c3e1f8"
BTTN_RELIEF = "flat"
BTTN_FONT_SIZE = 9
BTTN_FONT = "Verdana"

DLT_BTTN_BG = "#c44848"
DLT_BTTN_ACTIVE_BG = "#c46565"

FONT = "Verdana"

CURRENT_OS = system()

HOME_DIR = None
CONFIG_PATH = "config"
IMG_PATH = f"{path.dirname(__file__)}/img"

if CURRENT_OS != "Windows":
    HOME_DIR = getenv("HOME")
    CONFIG_PATH = f"{HOME_DIR}/.local/share/Steam-Metadata-Editor/config"

STEAM_PATH = None


class IncompatibleVDFError(Exception):
    def __init__(self, vdf_version):
        self.vdf_version = vdf_version


class MainWindow:
    def __init__(self, silent, export=None):
        self.modifiedApps = []

        if export is not None:
            self.modifiedApps.extend(export)
            self.load_json()
            self.appInfoVdf = VDF(True, apps=self.modifiedApps)

            for app in self.modifiedApps:
                self.save_original_data(app)

            self.write_json()

        if silent:
            self.load_json()
            self.appInfoVdf = VDF(True, apps=self.modifiedApps)

            for app in self.modifiedApps:
                self.appInfoVdf.parsedAppInfo[app]["sections"] = self.jsonData[
                    str(app)
                ]["modified"]

            self.write_data_to_appinfo(notice=False)

        if not silent and export is None:
            self.create_main_window()

            for app in self.modifiedApps:
                self.appInfoVdf.parsedAppInfo[app]["sections"] = self.jsonData[
                    str(app)
                ]["modified"]

    def create_main_window(self):
        # define main window
        self.window = tk.Tk()
        self.window.title("Steam Metadata Editor")
        self.window.resizable(width=False, height=False)
        self.window.config(padx=10, pady=10, bg=BG)

        # hide to show loading window
        self.window.withdraw()
        loadingWindow = LoadingWindow(self.window)

        # load appinfo
        self.appInfoVdf = VDF()

        # button images
        self.upArrowImage = tk.PhotoImage(file=f"{IMG_PATH}/UpArrow.png")
        self.downArrowImage = tk.PhotoImage(file=f"{IMG_PATH}/DownArrow.png")
        self.deleteImage = tk.PhotoImage(file=f"{IMG_PATH}/Delete.png")

        # treeview style
        self.treeviewStyle = Style()
        self.treeviewStyle.configure(
            "Treeview",
            font=(FONT, 9),
            background=ENTRY_BG,
            foreground=ENTRY_FG,
            fieldbackground=ENTRY_BG,
            rowheight=20,
            relief=ENTRY_RELIEF,
        )
        self.treeviewStyle.configure(
            "Treeview.Heading",
            font=(FONT, 10),
            background=BG,
            foreground=FG,
            relief=ENTRY_RELIEF,
        )

        # string vars
        self.idVar = tk.StringVar()
        self.nameVar = tk.StringVar()
        self.sortAsVar = tk.StringVar()
        self.developerVar = tk.StringVar()
        self.publisherVar = tk.StringVar()
        self.ogRelease1Var = tk.StringVar()
        self.ogRelease2Var = tk.StringVar()
        self.ogRelease3Var = tk.StringVar()
        self.steamRelease1Var = tk.StringVar()
        self.steamRelease2Var = tk.StringVar()
        self.steamRelease3Var = tk.StringVar()
        self.searchBarVar = tk.StringVar()

        # layout setup
        self.leftFrame = tk.LabelFrame(
            self.window, padx=10, pady=10, bg=BG, text="Search:", fg=FG
        )
        self.rightContainerFrame = tk.Frame(self.window, padx=10, pady=10, bg=BG)
        # label specific
        self.rightIdFrame = tk.Frame(self.rightContainerFrame, bg=BG)
        self.rightNameFrame = tk.Frame(self.rightContainerFrame, bg=BG)
        self.rightSortAsFrame = tk.Frame(self.rightContainerFrame, bg=BG)
        self.rightDeveloperFrame = tk.Frame(self.rightContainerFrame, bg=BG)
        self.rightPublisherFrame = tk.Frame(self.rightContainerFrame, bg=BG)
        self.rightOgReleaseFrame = tk.Frame(self.rightContainerFrame, bg=BG)
        self.rightSteamReleaseFrame = tk.Frame(self.rightContainerFrame, bg=BG)
        self.buttonsFrame = tk.Frame(self.rightContainerFrame, bg=BG)

        # widgets
        # left side
        self.searchBar = tk.Entry(
            self.leftFrame,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.searchBarVar,
        )
        self.searchBarVar.trace_add(
            "write", lambda _a, _b, _c: self.locate_app_in_list()
        )
        self.searchBar.focus()

        self.appListScrollbar = tk.Scrollbar(
            self.leftFrame,
            bd=0,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            activebackground=ENTRY_BG,
        )

        self.appList = Treeview(self.leftFrame, columns=("Type", "Mod", "ID"))
        self.appList.heading("#0", text="App Name")
        self.appList.heading("Type", text="Type")
        self.appList.heading("Mod", text="Modified")
        self.appList.heading("ID", text="ID")
        self.appList.column("#0", width=300, stretch=False)
        self.appList.column("Type", width=50, minwidth=20)
        self.appList.column("Mod", width=55, minwidth=20)
        self.appList.column("ID", width=80, minwidth=80)
        self.appList.bind("<ButtonRelease-1>", self.fetch_app_data)

        # right side
        self.idLabel = tk.Label(self.rightIdFrame, text="ID:", font=FONT, bg=BG, fg=FG)
        self.idEntry = tk.Entry(
            self.rightIdFrame,
            width=40,
            relief=ENTRY_RELIEF,
            fg=ENTRY_FG,
            textvariable=self.idVar,
            readonlybackground=ENTRY_BG,
            state="readonly",
        )

        self.nameLabel = tk.Label(
            self.rightNameFrame, text="Name:", font=FONT, bg=BG, fg=FG
        )
        self.nameEntry = tk.Entry(
            self.rightNameFrame,
            width=40,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.nameVar,
        )

        self.sortAsLabel = tk.Label(
            self.rightSortAsFrame, text="Sort As:", font=FONT, bg=BG, fg=FG
        )
        self.sortAsEntry = tk.Entry(
            self.rightSortAsFrame,
            width=40,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.sortAsVar,
        )

        self.developerLabel = tk.Label(
            self.rightDeveloperFrame, text="Developer:", font=FONT, bg=BG, fg=FG
        )
        self.developerEntry = tk.Entry(
            self.rightDeveloperFrame,
            width=40,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.developerVar,
        )

        self.publisherLabel = tk.Label(
            self.rightPublisherFrame, text="Publisher:", font=FONT, bg=BG, fg=FG
        )
        self.publisherEntry = tk.Entry(
            self.rightPublisherFrame,
            width=40,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.publisherVar,
        )

        self.ogReleaseLabel = tk.Label(
            self.rightOgReleaseFrame,
            text="Original Release Date:",
            font=FONT,
            bg=BG,
            fg=FG,
        )
        self.ogReleaseEntry1 = tk.Entry(
            self.rightOgReleaseFrame,
            relief=ENTRY_RELIEF,
            width=4,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.ogRelease1Var,
        )
        self.ogReleaseEntry2 = tk.Entry(
            self.rightOgReleaseFrame,
            relief=ENTRY_RELIEF,
            width=2,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.ogRelease2Var,
        )
        self.ogReleaseEntry3 = tk.Entry(
            self.rightOgReleaseFrame,
            relief=ENTRY_RELIEF,
            width=2,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.ogRelease3Var,
        )

        self.steamReleaseLabel = tk.Label(
            self.rightSteamReleaseFrame,
            text="Steam Release Date:",
            font=FONT,
            bg=BG,
            fg=FG,
        )
        self.steamReleaseEntry1 = tk.Entry(
            self.rightSteamReleaseFrame,
            relief=ENTRY_RELIEF,
            width=4,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.steamRelease1Var,
        )
        self.steamReleaseEntry2 = tk.Entry(
            self.rightSteamReleaseFrame,
            relief=ENTRY_RELIEF,
            width=2,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.steamRelease2Var,
        )
        self.steamReleaseEntry3 = tk.Entry(
            self.rightSteamReleaseFrame,
            relief=ENTRY_RELIEF,
            width=2,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            textvariable=self.steamRelease3Var,
        )

        self.launchMenuButton = tk.Button(
            self.buttonsFrame,
            text="Edit launch menu",
            command=self.create_launch_menu_window,
            activebackground=BTTN_ACTIVE_BG,
            activeforeground=BTTN_ACTIVE_FG,
            relief=BTTN_RELIEF,
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            bg=BTTN_BG,
            fg=BTTN_FG,
        )
        self.revertAppButton = tk.Button(
            self.buttonsFrame,
            text="Revert App",
            command=lambda: self.revert_app(self.idVar.get()),
            activebackground=BTTN_ACTIVE_BG,
            activeforeground=BTTN_ACTIVE_FG,
            relief=BTTN_RELIEF,
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            bg=BTTN_BG,
            fg=BTTN_FG,
        )
        self.saveButton = tk.Button(
            self.buttonsFrame,
            text="Save",
            command=self.write_data_to_appinfo,
            activebackground=BTTN_ACTIVE_BG,
            activeforeground=BTTN_ACTIVE_FG,
            relief=BTTN_RELIEF,
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            bg=BTTN_BG,
            fg=BTTN_FG,
        )

        # pack widgets
        # left side
        self.searchBar.pack(side="top", fill="both", pady=(0, 10))
        self.appListScrollbar.pack(side="right", fill="both")
        self.appList.pack(side="top", fill="both")

        # right side
        self.idLabel.pack(side="left")
        self.idEntry.pack(side="right")
        self.nameLabel.pack(side="left")
        self.nameEntry.pack(side="right")
        self.sortAsLabel.pack(side="left")
        self.sortAsEntry.pack(side="right")
        self.developerLabel.pack(side="left")
        self.developerEntry.pack(side="right")
        self.publisherLabel.pack(side="left")
        self.publisherEntry.pack(side="right")

        self.ogReleaseLabel.pack(side="left")
        self.ogReleaseEntry3.pack(side="right", padx=(10, 0))
        self.ogReleaseEntry2.pack(side="right", padx=10)
        self.ogReleaseEntry1.pack(side="right", padx=(0, 10))

        self.steamReleaseLabel.pack(side="left")
        self.steamReleaseEntry3.pack(side="right", padx=(10, 0))
        self.steamReleaseEntry2.pack(side="right", padx=10)
        self.steamReleaseEntry1.pack(side="right", padx=(0, 10))

        self.launchMenuButton.pack(side="left")
        self.revertAppButton.pack(side="left")
        self.saveButton.pack(side="right")

        # frames
        self.leftFrame.pack(side="left", fill="both")
        self.rightContainerFrame.pack(side="right", fill="both")

        self.rightIdFrame.pack(side="top", fill="both", pady=(0, ENTRY_PADDING))
        self.rightNameFrame.pack(side="top", fill="both", pady=ENTRY_PADDING)
        self.rightSortAsFrame.pack(side="top", fill="both", pady=ENTRY_PADDING)
        self.rightDeveloperFrame.pack(side="top", fill="both", pady=ENTRY_PADDING)
        self.rightPublisherFrame.pack(side="top", fill="both", pady=ENTRY_PADDING)
        self.rightOgReleaseFrame.pack(side="top", fill="both", pady=ENTRY_PADDING)
        self.rightSteamReleaseFrame.pack(
            side="top", fill="both", pady=(ENTRY_PADDING, 0)
        )
        self.buttonsFrame.pack(side="bottom", fill="both")

        # extra config
        self.appList.config(yscrollcommand=self.appListScrollbar.set)
        self.appListScrollbar.config(command=self.appList.yview)

        self.load_json()
        self.mark_installed_games()
        self.populate_app_list()

        # destroy loading window and show main one
        # after appinfo finishes loading
        loadingWindow.destroy()
        self.window.deiconify()

        # center window
        self.window.update()
        self.window.update_idletasks()
        self.center_window(self.window)

    def mark_installed_games(self):
        lbryPath = path.join(STEAM_PATH, "steamapps", "libraryfolders.vdf")
        with open(lbryPath, "r") as libraries:
            libraries = self.parse_library_folders(libraries.read())

        for library in libraries.values():
            appIDs = [
                acf.replace(library, "")[1:]
                for acf in glob(path.join(library, "*.acf"))
            ]
            appIDs = [
                int(acf.replace("appmanifest_", "").replace(".acf", ""))
                for acf in appIDs
            ]

            for app in appIDs:
                self.appInfoVdf.parsedAppInfo[app]["installed"] = True
                self.appInfoVdf.parsedAppInfo[app]["installDir"] = path.join(
                    library,
                    "common",
                    str(self.get_data_from_section(app, "config", "installdir")),
                )

    def parse_library_folders(self, data):
        # delete all irrelevant characters
        data = (
            data.replace("\t", "")
            .replace("\n", "")
            .replace('"LibraryFolders"', "")
            .replace("{", "")
            .replace("}", "")
        )

        # remove first and last character because they are trailing quotes
        parsedData = data[1:-1].split('""')
        lbryDict = {}
        lbryDict["0"] = path.join(STEAM_PATH, "steamapps")

        for key, value in zip(*[iter(parsedData)] * 2):
            lbryDict[key] = path.join(value, "steamapps")

        # sometimes these are missing
        if "TimeNextStatsReport" in lbryDict.keys():
            del lbryDict["TimeNextStatsReport"]

        if "ContentStatsID" in lbryDict.keys():
            del lbryDict["ContentStatsID"]

        return lbryDict

    def write_json(self):
        with open(f"{CONFIG_PATH}/modifications.json", "w") as mod:
            for app in self.modifiedApps:
                self.jsonData[str(app)]["modified"] = self.appInfoVdf.parsedAppInfo[
                    app
                ]["sections"]
            dump(self.jsonData, mod, indent=2)

    def save_original_data(self, appID):
        appData = deepcopy(self.appInfoVdf.parsedAppInfo[appID]["sections"])
        self.jsonData[str(appID)] = {}
        self.jsonData[str(appID)]["original"] = appData

    def load_json(self):
        try:
            with open(f"{CONFIG_PATH}/modifications.json", "r") as mod:
                self.jsonData = load(mod)
                for app in self.jsonData:
                    app = int(app)
                    if app not in self.modifiedApps:
                        self.modifiedApps.append(app)
        except (FileNotFoundError, JSONDecodeError):
            self.jsonData = {}

    def get_data_from_section(self, appID, *sections, error=""):
        data = self.appInfoVdf.parsedAppInfo[appID]["sections"]["appinfo"]
        for section in sections:
            try:
                data = data[section]
            except KeyError:
                return error

        return data

    # given a var, it removes the callback, sets the value
    # and reassigns the callback
    def set_var_no_callback(self, var, value, callback):
        try:
            callbackId = var.trace_vinfo()[0][1]
            var.trace_remove("write", callbackId)
        except IndexError:
            pass

        var.set(value)
        var.trace_add("write", callback)

    def set_data_from_section(self, appID, value, *sections):
        appID = int(appID)

        if appID not in self.modifiedApps:
            self.save_original_data(appID)
            self.modifiedApps.append(appID)

        data = self.appInfoVdf.parsedAppInfo[appID]["sections"]["appinfo"]
        # access all but the last element
        for section in sections[0 : len(sections) - 1]:
            try:
                data = data[section]
            except KeyError:
                data[section] = {}
                data = data[section]

        data[sections[-1]] = value

    def get_unix_time(self, year, month, day):
        return int(datetime(year, month, day).timestamp())

    def set_timestamps(self, stampId):
        appID = int(self.idVar.get())

        def validate_date_format(year, month, day):
            if len(str(year)) > 4 or year < 1970:
                return False
            try:
                if datetime(year, month, day) > datetime.today():
                    return False
            except ValueError:
                return False

            return True

        if stampId == "original":

            try:
                year = int(self.ogRelease1Var.get())
                month = int(self.ogRelease2Var.get())
                day = int(self.ogRelease3Var.get())
            # this happens when the field is empty
            except ValueError:
                return

            if validate_date_format(year, month, day):

                appOgReleaseDate = self.get_unix_time(year, month, day)
                self.set_data_from_section(
                    appID, appOgReleaseDate, "common", "original_release_date"
                )
        elif stampId == "steam":

            try:
                year = int(self.steamRelease1Var.get())
                month = int(self.steamRelease2Var.get())
                day = int(self.steamRelease3Var.get())
            # this happens when the field is empty
            except ValueError:
                return

            if validate_date_format(year, month, day):

                appSteamReleaseDate = self.get_unix_time(year, month, day)
                self.set_data_from_section(
                    appID, appSteamReleaseDate, "common", "steam_release_date"
                )

    def write_data_to_appinfo(self, notice=True):
        self.write_json()

        for app in self.modifiedApps:
            self.appInfoVdf.update_app(self.appInfoVdf.parsedAppInfo[app])

        self.appInfoVdf.write_data()

        if notice:
            messagebox.showinfo(
                title="Success!",
                message="Your changes " + "have been successfully applied!",
            )

    def revert_app(self, appID):
        appID = int(appID)

        if appID in self.modifiedApps:
            if messagebox.askyesno(
                title="Revert Game",
                message="Are you "
                + "sure you want to rever this game? All your "
                + "modifications will be erased, this cannot be undone.",
            ):

                # fetch original data and replace it
                originalData = deepcopy(self.jsonData[str(appID)]["original"])
                self.appInfoVdf.parsedAppInfo[appID]["sections"] = originalData

                # delete app from modified apps
                # to not save it in the json again
                if appID in self.modifiedApps:
                    self.modifiedApps.remove(appID)

                # delete data from json
                del self.jsonData[str(appID)]
                self.write_json()

                appinfo = self.appInfoVdf.parsedAppInfo[appID]
                self.appInfoVdf.update_app(appinfo)
                self.appInfoVdf.write_data()

                # update app list
                self.appList.delete(*self.appList.get_children())
                self.populate_app_list()

    def fetch_app_data(self, _event):
        # data from list
        currentItem = self.appList.focus()
        currentItemData = self.appList.item(currentItem)
        appID = currentItemData["values"][-1]
        # fetched data
        appName = self.get_data_from_section(appID, "common", "name")
        appSortAs = self.get_data_from_section(appID, "common", "sortas")
        appDeveloper = self.get_data_from_section(appID, "extended", "developer")
        appPublisher = self.get_data_from_section(appID, "extended", "publisher")
        appSteamReleaseDate = self.get_data_from_section(
            appID, "common", "steam_release_date"
        )
        appOgReleaseDate = self.get_data_from_section(
            appID, "common", "original_release_date"
        )

        if not appSteamReleaseDate:
            appSteamReleaseDate = 0
        if not appOgReleaseDate:
            appOgReleaseDate = appSteamReleaseDate
        if not appSortAs:
            appSortAs = appName

        appSteamReleaseDate = datetime.fromtimestamp(appSteamReleaseDate)
        appOgReleaseDate = datetime.fromtimestamp(appOgReleaseDate)

        self.idVar.set(appID)

        self.set_var_no_callback(
            self.nameVar,
            appName,
            lambda _a, _b, _c: (
                self.set_data_from_section(
                    int(self.idVar.get()), self.nameVar.get(), "common", "name"
                ),
                self.sortAsVar.set(self.nameVar.get()),
            ),
        )

        self.set_var_no_callback(
            self.sortAsVar,
            appSortAs,
            lambda _a, _b, _c: self.set_data_from_section(
                int(self.idVar.get()), self.sortAsVar.get(), "common", "sortas"
            ),
        )

        self.set_var_no_callback(
            self.developerVar,
            appDeveloper,
            lambda _a, _b, _c: (
                self.set_data_from_section(
                    int(self.idVar.get()),
                    self.developerVar.get(),
                    "extended",
                    "developer",
                ),
                self.set_data_from_section(
                    int(self.idVar.get()),
                    self.developerVar.get(),
                    "common",
                    "associations",
                    "0",
                    "name",
                ),
            ),
        )

        self.set_var_no_callback(
            self.publisherVar,
            appPublisher,
            lambda _a, _b, _c: (
                self.set_data_from_section(
                    int(self.idVar.get()),
                    self.publisherVar.get(),
                    "extended",
                    "publisher",
                ),
                self.set_data_from_section(
                    int(self.idVar.get()),
                    self.publisherVar.get(),
                    "common",
                    "associations",
                    "1",
                    "name",
                ),
            ),
        )

        self.set_var_no_callback(
            self.ogRelease1Var,
            f"{appOgReleaseDate:%Y}",
            lambda _a, _b, _c: self.set_timestamps("original"),
        )
        self.set_var_no_callback(
            self.ogRelease2Var,
            f"{appOgReleaseDate:%m}",
            lambda _a, _b, _c: self.set_timestamps("original"),
        )
        self.set_var_no_callback(
            self.ogRelease3Var,
            f"{appOgReleaseDate:%d}",
            lambda _a, _b, _c: self.set_timestamps("original"),
        )

        self.set_var_no_callback(
            self.steamRelease1Var,
            f"{appSteamReleaseDate:%Y}",
            lambda _a, _b, _c: self.set_timestamps("steam"),
        )
        self.set_var_no_callback(
            self.steamRelease2Var,
            f"{appSteamReleaseDate:%m}",
            lambda _a, _b, _c: self.set_timestamps("steam"),
        )
        self.set_var_no_callback(
            self.steamRelease3Var,
            f"{appSteamReleaseDate:%d}",
            lambda _a, _b, _c: self.set_timestamps("steam"),
        )

    def insert_app_in_list(self, app):
        self.appList.insert(
            parent="", index="end", text=app[0], values=(app[1], app[2], app[3])
        )

    def locate_app_in_list(self):
        query = self.searchBar.get().lower()

        # clear list to fill it with results
        self.appList.delete(*self.appList.get_children())

        if query:
            for app in self.appData:
                if query in app[0].lower():
                    self.insert_app_in_list(app)
        else:
            # update app list
            self.populate_app_list()

    def center_window(self, window):
        screenWidth = window.winfo_screenwidth()
        screenHeight = window.winfo_screenheight()
        windowWidth = window.winfo_reqwidth()
        windowHeight = window.winfo_reqheight()

        windowX = (screenWidth / 2) - (windowWidth / 2)
        windowY = (screenHeight / 2) - (windowHeight / 2)

        window.geometry(
            f"{windowWidth}x{windowHeight}+" + f"{int(windowX)}+{int(windowY)}"
        )

    def ask_to_create_launch_option(self, appID):
        self.launchMenuWindow.withdraw()
        answer = messagebox.askyesno(
            "No Launch Options",
            "This app has no launch options. Do you wish to create one?",
        )
        if answer:
            self.add_launch_option(appID)
            self.launchMenuWindow.deiconify()
        else:
            self.launchMenuWindow.destroy()

    def move_launch_option(self, appID, optionNumber, direction):
        launchOption = self.get_data_from_section(
            appID, "config", "launch", optionNumber
        )

        if direction == "up":
            newOptionNumber = str(int(optionNumber) - 1)
            # check if the location exists
            nextLaunchOption = self.get_data_from_section(
                appID, "config", "launch", newOptionNumber, error=False
            )

            if nextLaunchOption is not False:
                self.set_data_from_section(
                    appID, nextLaunchOption, "config", "launch", optionNumber
                )
                self.set_data_from_section(
                    appID, launchOption, "config", "launch", newOptionNumber
                )
            else:
                return
            self.update_launch_menu_window(appID)
        elif direction == "down":
            newOptionNumber = str(int(optionNumber) + 1)
            # check if the location exists
            prevLaunchOption = self.get_data_from_section(
                appID, "config", "launch", newOptionNumber, error=False
            )

            if prevLaunchOption is not False:
                self.set_data_from_section(
                    appID, prevLaunchOption, "config", "launch", optionNumber
                )
                self.set_data_from_section(
                    appID, launchOption, "config", "launch", newOptionNumber
                )
            else:
                return
            self.update_launch_menu_window(appID)
        else:
            return

    def delete_launch_option(self, appID, optionNumber):
        launchOptions = self.get_data_from_section(appID, "config", "launch")

        found = False
        keys = list(launchOptions.keys())
        for launchOption in keys:
            if not found:
                if launchOption == optionNumber:
                    found = True
            else:
                newOptionNumber = str(int(launchOption) - 1)
                self.set_data_from_section(
                    appID,
                    launchOptions[launchOption],
                    "config",
                    "launch",
                    newOptionNumber,
                )
        del launchOptions[keys[-1]]
        self.update_launch_menu_window(appID)

    def add_launch_option(self, appID):
        launchOptions = self.get_data_from_section(appID, "config", "launch")
        newEntryNumber = str(len(launchOptions))
        self.set_data_from_section(appID, {}, "config", "launch", newEntryNumber)

        self.update_launch_menu_window(appID)

    def split_directory(self, directory):
        allparts = []
        while True:
            parts = path.split(directory)
            if parts[0] == directory:
                allparts.insert(0, parts[0])
                break
            else:
                directory = parts[0]
                allparts.insert(0, parts[1])
        return allparts

    def calculate_parent_folders(self, executablePath, appID, steamDir):
        # splits all folders in the path into strings
        steamDir = self.split_directory(steamDir)
        execDir = self.split_directory(executablePath)

        if CURRENT_OS == "Windows":
            del steamDir[0]
            del execDir[0]

        while "" in steamDir:
            steamDir.remove("")
        while "" in execDir:
            execDir.remove("")

        parentFolders = None

        for index, folder in enumerate(steamDir):
            # count how many folders are needed to reach the earliest common
            # parent folder
            if index == len(execDir) or folder != execDir[index]:
                parentFolders = len(steamDir) - index
                break

        if parentFolders != None:
            return "../" * parentFolders + "/".join(execDir[index:])
        elif execDir[index:] == steamDir[index]:
            return ""
        else:
            return "/".join(execDir[index + 1 :])

    def generate_launch_option_string(self, appID, execVar, wkngDirVar, pathType):
        installDir = self.appInfoVdf.parsedAppInfo[appID]["installDir"]

        if pathType == "exe":

            exePath = filedialog.askopenfilename(
                parent=self.launchMenuWindow, initialdir=installDir
            )
            if exePath == () or exePath == "":
                return

            exePath = self.calculate_parent_folders(exePath, appID, installDir)

            wkngDirPath = path.split(exePath)[0]

            execVar.set(exePath)
            if CURRENT_OS == "Windows":
                wkngDirVar = wkngDirVar.replace("/", "\\")
            wkngDirVar.set(wkngDirPath)

        elif pathType == "wkngDir":

            wkngDirPath = filedialog.askdirectory(
                parent=self.launchMenuWindow, initialdir=installDir
            )
            if wkngDirPath == () or wkngDirPath == "":
                return

            wkngDirPath = self.calculate_parent_folders(wkngDirPath, appID, installDir)

            if CURRENT_OS == "Windows":
                wkngDirVar = wkngDirVar.replace("/", "\\")
            wkngDirVar.set(wkngDirPath)

    def write_os_list(self, appID, winVar, macVar, linVar, launchOption):
        oslist = []
        if winVar.get():
            oslist.append("windows")
        if macVar.get():
            oslist.append("macos")
        if linVar.get():
            oslist.append("linux")

        oslist = ",".join(oslist)

        self.set_data_from_section(
            appID, oslist, "config", "launch", launchOption, "config", "oslist"
        )

    def create_launch_option(
        self,
        frame,
        appID,
        number,
        description,
        executable,
        wkngDir,
        arguments,
        platforms,
    ):

        # frames
        padding = 20
        mainFrame = tk.LabelFrame(
            frame, bg=BG, padx=padding, pady=padding, text=number, font=FONT, fg=FG
        )
        descFrame = tk.Frame(mainFrame, bg=BG, padx=padding)
        execFrame = tk.Frame(mainFrame, bg=BG, padx=padding)
        wkngDirFrame = tk.Frame(mainFrame, bg=BG, padx=padding)
        argFrame = tk.Frame(mainFrame, bg=BG, padx=padding)
        platformFrame = tk.Frame(mainFrame, bg=BG, padx=padding)
        buttonsFrame = tk.Frame(mainFrame, bg=BG, padx=padding)

        # string vars
        descVar = tk.StringVar()
        wkngDirVar = tk.StringVar()
        execVar = tk.StringVar()
        argVar = tk.StringVar()

        winVar = tk.BooleanVar()
        linVar = tk.BooleanVar()
        macVar = tk.BooleanVar()

        # widgets
        descLabel = tk.Label(descFrame, text="Description:", font=FONT, bg=BG, fg=FG)
        descEntry = tk.Entry(
            descFrame,
            bg=ENTRY_BG,
            textvariable=descVar,
            fg=ENTRY_FG,
            relief=ENTRY_RELIEF,
            width=60,
        )

        execLabel = tk.Label(execFrame, text="Executable:", font=FONT, bg=BG, fg=FG)
        execEntry = tk.Entry(
            execFrame,
            readonlybackground=ENTRY_BG,
            textvariable=execVar,
            fg=ENTRY_FG,
            relief=ENTRY_RELIEF,
            width=55,
            state="readonly",
        )
        execButton = tk.Button(
            execFrame,
            bg=BTTN_BG,
            activebackground=BTTN_ACTIVE_BG,
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            activeforeground=BTTN_ACTIVE_FG,
            fg=BTTN_FG,
            relief=BTTN_RELIEF,
            text="...",
            command=lambda: self.generate_launch_option_string(
                appID, execVar, wkngDirVar, "exe"
            ),
        )

        wkngDirLabel = tk.Label(
            wkngDirFrame, text="Working Directory:", font=FONT, bg=BG, fg=FG
        )
        wkngDirEntry = tk.Entry(
            wkngDirFrame,
            readonlybackground=ENTRY_BG,
            textvariable=wkngDirVar,
            fg=ENTRY_FG,
            relief=ENTRY_RELIEF,
            width=55,
            state="readonly",
        )
        wkngDirButton = tk.Button(
            wkngDirFrame,
            bg=BTTN_BG,
            activebackground=BTTN_ACTIVE_BG,
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            activeforeground=BTTN_ACTIVE_FG,
            fg=BTTN_FG,
            relief=BTTN_RELIEF,
            text="...",
            command=lambda: self.generate_launch_option_string(
                appID, execVar, wkngDirVar, "wkngDir"
            ),
        )

        argLabel = tk.Label(argFrame, text="Launch Arguments:", font=FONT, bg=BG, fg=FG)
        argEntry = tk.Entry(
            argFrame,
            bg=ENTRY_BG,
            textvariable=argVar,
            fg=ENTRY_FG,
            relief=ENTRY_RELIEF,
            width=60,
        )

        # platform checkbuttons
        winCheck = tk.Checkbutton(
            platformFrame,
            text="Windows",
            bg=BG,
            fg=ENTRY_FG,
            relief=ENTRY_RELIEF,
            selectcolor=ENTRY_BG,
            variable=winVar,
        )
        linCheck = tk.Checkbutton(
            platformFrame,
            text="Linux",
            bg=BG,
            fg=ENTRY_FG,
            relief=ENTRY_RELIEF,
            selectcolor=ENTRY_BG,
            variable=linVar,
        )
        macCheck = tk.Checkbutton(
            platformFrame,
            text="Mac",
            bg=BG,
            fg=ENTRY_FG,
            relief=ENTRY_RELIEF,
            selectcolor=ENTRY_BG,
            variable=macVar,
        )

        deleteButton = tk.Button(
            buttonsFrame,
            image=self.deleteImage,
            command=lambda: self.delete_launch_option(appID, number),
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            bg=DLT_BTTN_BG,
            fg=BTTN_FG,
            activebackground=DLT_BTTN_ACTIVE_BG,
            activeforeground=BTTN_ACTIVE_FG,
            relief=BTTN_RELIEF,
        )
        upButton = tk.Button(
            buttonsFrame,
            image=self.upArrowImage,
            command=lambda: self.move_launch_option(appID, number, "up"),
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            bg=BTTN_BG,
            fg=BTTN_FG,
            activebackground=BTTN_ACTIVE_BG,
            activeforeground=BTTN_ACTIVE_FG,
            relief=BTTN_RELIEF,
        )
        downButton = tk.Button(
            buttonsFrame,
            image=self.downArrowImage,
            command=lambda: self.move_launch_option(appID, number, "down"),
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            bg=BTTN_BG,
            fg=BTTN_FG,
            activebackground=BTTN_ACTIVE_BG,
            activeforeground=BTTN_ACTIVE_FG,
            relief=BTTN_RELIEF,
        )

        # pack widgets
        descLabel.pack(side="left", fill="both")
        descEntry.pack(side="right", fill="both")

        wkngDirLabel.pack(side="left", fill="both")
        wkngDirButton.pack(side="right", fill="both")
        wkngDirEntry.pack(side="right", fill="both")

        execLabel.pack(side="left", fill="both")
        execButton.pack(side="right", fill="both")
        execEntry.pack(side="right", fill="both")

        argLabel.pack(side="left", fill="both")
        argEntry.pack(side="right", fill="both")

        winCheck.pack(side="left", fill="both")
        linCheck.pack(side="left", fill="both")
        macCheck.pack(side="left", fill="both")

        deleteButton.pack(side="right")
        downButton.pack(side="right")
        upButton.pack(side="right")

        # pack frames
        mainFrame.pack(expand="yes")
        descFrame.pack(side="top", fill="both", pady=(padding, 0))
        execFrame.pack(side="top", fill="both")
        wkngDirFrame.pack(side="top", fill="both")
        argFrame.pack(side="top", fill="both")
        platformFrame.pack(side="top")
        buttonsFrame.pack(side="top", fill="both", pady=(0, padding))

        # insert data
        for platform in platforms.split(","):
            if platform == "windows":
                winVar.set(True)
            elif platform == "linux":
                linVar.set(True)
            elif platform == "macos":
                macVar.set(True)

        winVar.trace_add(
            "write",
            lambda _a, _b, _c: self.write_os_list(
                appID, winVar, macVar, linVar, number
            ),
        )
        linVar.trace_add(
            "write",
            lambda _a, _b, _c: self.write_os_list(
                appID, winVar, macVar, linVar, number
            ),
        )
        macVar.trace_add(
            "write",
            lambda _a, _b, _c: self.write_os_list(
                appID, winVar, macVar, linVar, number
            ),
        )

        self.set_var_no_callback(
            descVar,
            description,
            lambda _a, _b, _c: self.set_data_from_section(
                appID, descVar.get(), "config", "launch", number, "description"
            ),
        )

        self.set_var_no_callback(
            wkngDirVar,
            wkngDir,
            lambda _a, _b, _c: self.set_data_from_section(
                appID, wkngDirVar.get(), "config", "launch", number, "workingdir"
            ),
        )

        self.set_var_no_callback(
            execVar,
            executable,
            lambda _a, _b, _c: self.set_data_from_section(
                appID, execVar.get(), "config", "launch", number, "executable"
            ),
        )

        self.set_var_no_callback(
            argVar,
            arguments,
            lambda _a, _b, _c: self.set_data_from_section(
                appID, argVar.get(), "config", "launch", number, "arguments"
            ),
        )

        # update to return correct values
        mainFrame.update()
        return [
            mainFrame.winfo_reqwidth() + padding,
            mainFrame.winfo_reqheight(),
            padding,
        ]

    def update_launch_menu_window(self, appID):
        # clear frame and store current scroll position
        scrollbarPosition = 0
        for widget in self.scrollFrame.scrollableFrame.winfo_children():
            scrollbarPosition = self.scrollFrame.scrollbar.get()[0]
            widget.destroy()

        # read launch options and gather data
        appLaunchOptions = self.get_data_from_section(appID, "config", "launch")
        if not appLaunchOptions:
            self.ask_to_create_launch_option(appID)
            return

        frameCount = 0
        for launchOption in appLaunchOptions.keys():
            description = self.get_data_from_section(
                appID, "config", "launch", launchOption, "description"
            )
            executable = self.get_data_from_section(
                appID, "config", "launch", launchOption, "executable"
            )
            wkngDir = self.get_data_from_section(
                appID, "config", "launch", launchOption, "workingdir"
            )
            arguments = self.get_data_from_section(
                appID, "config", "launch", launchOption, "arguments"
            )
            platforms = self.get_data_from_section(
                appID,
                "config",
                "launch",
                launchOption,
                "config",
                "oslist",
                error="Not specified",
            )

            geometry = self.create_launch_option(
                self.scrollFrame.scrollableFrame,
                appID,
                launchOption,
                description,
                executable,
                wkngDir,
                arguments,
                platforms,
            )

            if frameCount < 2:
                frameCount += 1

        # add widgets for adding new entries
        newEntryFrame = tk.Frame(self.scrollFrame.scrollableFrame, bg=BG)
        newEntryButton = tk.Button(
            newEntryFrame,
            text="Add New Entry",
            command=lambda: self.add_launch_option(appID),
            relief=BTTN_RELIEF,
            bg=BTTN_BG,
            activebackground=BTTN_ACTIVE_BG,
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            activeforeground=BTTN_ACTIVE_FG,
            fg=BTTN_FG,
        )

        padding = 10
        newEntryButton.pack(side="top", anchor="n")
        newEntryFrame.pack(side="bottom", pady=(padding, 0))

        # offsets size of scrollbar and
        # takes padding (geometry[2]) into account
        self.scrollFrame.scrollbar.update()
        geometry[0] += self.scrollFrame.scrollbar.winfo_reqwidth()
        geometry[1] *= frameCount
        geometry[1] += geometry[2] * 2
        geometry[1] += newEntryFrame.winfo_reqheight() + padding

        # resizes window depending on the number of launch options
        self.scrollFrame.canvas.config(width=geometry[0], height=geometry[1])
        self.scrollFrame.canvas.yview_moveto(scrollbarPosition)

    def create_launch_menu_window(self):
        appName = self.nameVar.get()
        appID = int(self.idVar.get())

        self.launchMenuWindow = tk.Toplevel(self.window)
        self.launchMenuWindow.resizable(False, False)
        self.launchMenuWindow.title(f"Launch Menu Editor for {appName} ({appID})")

        self.scrollFrame = ScrollableFrame(self.launchMenuWindow)
        self.scrollFrame.scrollableFrame.config(bg=BG, padx=20, pady=20)

        self.update_launch_menu_window(appID)

        self.scrollFrame.pack()

        self.launchMenuWindow.update()
        self.center_window(self.launchMenuWindow)
        # prevent the use of the main window while this one exists
        self.launchMenuWindow.grab_set()
        self.launchMenuWindow.mainloop()

    def populate_app_list(self):
        # get all aplications found in appinfo.vdf
        keys = list(self.appInfoVdf.parsedAppInfo.keys())

        self.appData = []

        for app in keys[2:]:
            appID = app
            appType = self.get_data_from_section(appID, "common", "type")
            modified = appID in self.modifiedApps
            appName = self.get_data_from_section(appID, "common", "name")
            if appName == "" or appType == "":
                pass
            else:
                self.appData.append([str(appName), appType, modified, appID])

        # sort case insensitive
        self.appData.sort(key=lambda x: str(x[0]).lower())

        for app in self.appData:
            self.insert_app_in_list(app)


class VDF:
    def __init__(self, chooseApps=False, apps=None):
        self.offset = 0

        self.COMPATIBLE_VERSIONS = [0x107564428]

        self.SEPARATOR = b"\x00"
        self.TYPE_DICT = b"\x00"
        self.TYPE_STRING = b"\x01"
        self.TYPE_INT32 = b"\x02"
        self.SECTION_END = b"\x08"

        self.INT_SEPARATOR = int.from_bytes(self.SEPARATOR, "little")
        self.INT_TYPE_DICT = int.from_bytes(self.TYPE_DICT, "little")
        self.INT_TYPE_STRING = int.from_bytes(self.TYPE_STRING, "little")
        self.INT_TYPE_INT32 = int.from_bytes(self.TYPE_INT32, "little")
        self.INT_SECTION_END = int.from_bytes(self.SECTION_END, "little")

        ### LOAD VDF FILE ###
        vdfPath = path.join(STEAM_PATH, "appcache", "appinfo.vdf")
        with open(vdfPath, "rb") as vdf:
            self.appinfoData = bytearray(vdf.read())

        # load only the modified apps
        if chooseApps:
            self.parsedAppInfo = {}
            for app in apps:
                self.parsedAppInfo[app] = self.read_app(app)
        else:
            self.parsedAppInfo = self.read_all_apps()

    ### READ DATA ###
    def read_string(self):
        strEnd = self.appinfoData.find(self.INT_SEPARATOR, self.offset)
        try:
            string = self.appinfoData[self.offset : strEnd].decode("utf-8")
        except UnicodeDecodeError:
            # latin-1 == iso8859-1
            string = self.appinfoData[self.offset : strEnd].decode("latin-1")
            # control character used to determine encoding
            string += "\x06"
        self.offset += strEnd - self.offset + 1
        return string

    def read_int64(self):
        int64 = unpack("<Q", self.appinfoData[self.offset : self.offset + 8])[0]
        self.offset += 8
        return int64

    def read_int32(self):
        int32 = unpack("<I", self.appinfoData[self.offset : self.offset + 4])[0]
        self.offset += 4
        return int32

    def read_byte(self):
        byte = self.appinfoData[self.offset]
        self.offset += 1
        return byte

    def parse_subsections(self):
        subsection = {}
        value_parsers = {
            self.INT_TYPE_DICT: self.parse_subsections,
            self.INT_TYPE_STRING: self.read_string,
            self.INT_TYPE_INT32: self.read_int32,
        }

        while True:
            value_type = self.read_byte()
            if value_type == self.INT_SECTION_END:
                break

            key = self.read_string()
            value = value_parsers[value_type]()

            subsection[key] = value

        return subsection

    def read_header(self):
        keys = [
            "appid",
            "size",
            "state",
            "last_update",
            "access_token",
            "checksum_text",
            "change_number",
            "checksum_binary",
        ]

        formats = [
            ["<I", 4],
            ["<I", 4],
            ["<I", 4],
            ["<I", 4],
            ["<Q", 8],
            ["<20s", 20],
            ["<I", 4],
            ["<20s", 20],
        ]

        headerData = {}

        for fmt, key in zip(formats, keys):
            value = unpack(
                fmt[0], self.appinfoData[self.offset : self.offset + fmt[1]]
            )[0]
            self.offset += fmt[1]
            headerData[key] = value

        return headerData

    def verify_vdf_version(self):
        version = self.read_int64()
        if version not in self.COMPATIBLE_VERSIONS:
            raise IncompatibleVDFError(version)

    def read_app(self, appID):
        # all relevant apps will have a previous section ending before them
        # this ensures we are indeed getting an appid instead of some other
        # random number
        self.verify_vdf_version()
        byteData = self.SECTION_END + pack("<I", appID)
        self.offset = self.appinfoData.find(byteData) + 1
        if self.offset == 0:
            print(f"App {appID} not found")
            _exit(2)
        app = self.read_header()
        app["sections"] = self.parse_subsections()
        app["installed"] = False
        return app

    def read_all_apps(self):
        self.verify_vdf_version()
        apps = {}
        # the last appid is 0 but there's no actual data for it,
        # we skip it by checking 4 less bytes to not get into
        # another loop that would raise exceptions
        while self.offset < len(self.appinfoData) - 4:
            app = self.read_header()
            app["sections"] = self.parse_subsections()
            app["installed"] = False
            apps[app["appid"]] = app
        return apps

    ### ENCODE DATA ###
    def encode_header(self, data):
        return pack(
            "<4IQ20sI20s",
            data["appid"],
            data["size"],
            data["state"],
            data["last_update"],
            data["access_token"],
            data["checksum_text"],
            data["change_number"],
            data["checksum_binary"],
        )

    def encode_string(self, string):
        if "\x06" in string:
            return string[:-1].encode("latin-1") + self.SEPARATOR
        else:
            return string.encode() + self.SEPARATOR

    def encode_int(self, integer):
        return pack("<I", integer)

    def encode_subsections(self, data):
        encodedData = bytearray()

        for key, value in data.items():

            if type(value) == dict:
                encodedData += (
                    self.TYPE_DICT
                    + self.encode_string(key)
                    + self.encode_subsections(value)
                )
            elif type(value) == str:
                encodedData += (
                    self.TYPE_STRING
                    + self.encode_string(key)
                    + self.encode_string(value)
                )
            elif type(value) == int:
                encodedData += (
                    self.TYPE_INT32 + self.encode_string(key) + self.encode_int(value)
                )

        # if it got to this point, this particular dictionary ended
        encodedData += self.SECTION_END
        return encodedData

    def get_text_checksum(self, data):
        formatted_data = self.format_data(data)
        hsh = sha1(formatted_data)
        return hsh.digest()

    def get_binary_checksum(self, data):
        hsh = sha1(data)
        return hsh.digest()

    def update_size_and_checksum(self, header, size, checksum_text, checksum_binary):
        header = bytearray(header)
        header[4:8] = pack("<I", size)
        header[24:44] = pack("<20s", checksum_text)
        header[48:68] = pack("<20s", checksum_binary)

        return header

    def update_app(self, appinfo):
        # encode new data
        header = self.encode_header(appinfo)
        sections = self.encode_subsections(appinfo["sections"])
        checksum_text = self.get_text_checksum(appinfo["sections"])
        # appid and size don't count, so we skip them
        # by removing 8 bytes from the header
        size = len(sections) + len(header) - 8

        # find where the app is in the file
        # based on the unmodified header
        appLocation = self.appinfoData.find(header)
        if appLocation == -1:
            appID = pack("<I", appinfo["appid"])
            appLocation = self.appinfoData.find(self.SECTION_END + appID)

        # use the stored size to determine the end of the app
        appEndLocation = appLocation + appinfo["size"] + 8
        checksum_binary = self.get_binary_checksum(sections)

        header = self.update_size_and_checksum(
            header, size, checksum_text, checksum_binary
        )

        # replace the current app data with the new one
        if appLocation != -1:
            self.appinfoData[appLocation:appEndLocation] = header + sections
        else:
            self.appinfoData.extend(header + sections)

    def write_data(self):
        vdfPath = path.join(STEAM_PATH, "appcache", "appinfo.vdf")
        with open(vdfPath, "wb") as vdf:
            vdf.write(self.appinfoData)

    def format_data(self, data, numberOfTabs=0):
        """
        Formats a python dictionary into the vdf text format.
        """

        formatted_data = b""
        # set a string with a fixed number of tabs for this instance
        tabs = b"\t" * numberOfTabs

        # re-encode strings with their original encoding
        for key in data.keys():
            if type(data[key]) == dict:
                numberOfTabs += 1

                formatted_data += (
                    tabs
                    + b'"'
                    + key.replace("\\", "\\\\").encode()
                    + b'"'
                    + b"\n"
                    + tabs
                    + b"{"
                    + b"\n"
                    + self.format_data(data[key], numberOfTabs)
                    + tabs
                    + b"}\n"
                )

                numberOfTabs -= 1
            else:
                # \x06 character means the string was decoded with iso8859-1
                # the character gets removed when encoding
                if type(data[key]) == str and "\x06" in data[key]:
                    formatted_data += (
                        tabs
                        + b'"'
                        + key.replace("\\", "\\\\").encode()
                        + b'"'
                        + b"\t\t"
                        + b'"'
                        + data[key][:-1].replace("\\", "\\\\").encode("latin-1")
                        + b'"'
                        + b"\n"
                    )
                else:
                    formatted_data += (
                        tabs
                        + b'"'
                        + key.replace("\\", "\\\\").encode()
                        + b'"'
                        + b"\t\t"
                        + b'"'
                        + str(data[key]).replace("\\", "\\\\").encode()
                        + b'"'
                        + b"\n"
                    )

        return formatted_data


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            bd=0,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            activebackground=ENTRY_BG,
        )
        self.scrollableFrame = tk.Frame(self.canvas)

        self.scrollableFrame.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollableFrame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # X11
        self.canvas.bind_all("<Button-4>", self.scroll_canvas)
        self.canvas.bind_all("<Button-5>", self.scroll_canvas)
        # everything else
        self.canvas.bind_all("<MouseWheel>", self.scroll_canvas)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def scroll_canvas(self, event):
        if event.num == 5 or event.delta < 0:
            direction = 1
        elif event.num == 4 or event.delta > 0:
            direction = -1

        self.canvas.yview_scroll(direction, "units")


class LoadingWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.title("Steam Metadata Editor (Loading)")
        self.resizable(width=False, height=False)
        self.config(bg=BG)

        self.loadingLabel = tk.Label(
            self, text="Loading appinfo.vdf...", bg=BG, fg=FG, font=(FONT, 9)
        )

        self.loadingLabel.pack(padx=30, pady=30)

        # wait for widgets to actually load in
        # else they are sometimes not displayed,

        # TODO: Figure out why this hangs some systems
        # self.loadingLabel.wait_visibility()
        # self.wait_visibility()

        self.update()


def create_steam_path_window():
    finalPath = ""

    def set_steam_path():
        steamPath = filedialog.askdirectory()
        steamPath = Path(steamPath)
        steamPath = steamPath.resolve()
        directoryEntry.delete(0, "end")
        directoryEntry.insert(0, steamPath)

    def validate_path():
        if verify_steam_path(directoryEntry.get()):
            nonlocal finalPath
            finalPath = directoryEntry.get()
            window.destroy()
        else:
            messagebox.showerror(
                title="Invalid Steam Path",
                message="The provided path is invalid or there's no appinfo "
                + 'file, make sure that the "appcache" and "steamapps" '
                + 'folders are in the directory, and that "appcache" '
                + 'contains "appinfo.vdf".',
            )

    # window
    window = tk.Tk()
    window.resizable(width=False, height=False)
    window.title("Select Steam Path")
    window.config(padx=30, pady=30, bg=BG)
    window.protocol("WM_DELETE_WINDOW", lambda: _exit(0))

    # widgets
    info = tk.Label(
        window,
        text="Steam couldn't be located in your system,"
        + "\nplease point to it's installation directory.",
        font=(FONT, 10),
        bg=BG,
        fg=FG,
        justify="center",
    )

    directoryFrame = tk.Frame(window, bg=BG, pady=5)
    directoryEntry = tk.Entry(directoryFrame, width=40, fg=ENTRY_FG, bg=ENTRY_BG)
    directoryButton = tk.Button(
        directoryFrame,
        text="...",
        fg=BTTN_FG,
        bg=BTTN_BG,
        activebackground=BTTN_ACTIVE_BG,
        relief=BTTN_RELIEF,
        activeforeground=BTTN_ACTIVE_FG,
        font=(BTTN_FONT, BTTN_FONT_SIZE),
        command=set_steam_path,
    )

    buttonFrame = tk.Frame(window, bg=BG)
    okButton = tk.Button(
        buttonFrame,
        text="Ok",
        fg=BTTN_FG,
        bg=BTTN_BG,
        activebackground=BTTN_ACTIVE_BG,
        activeforeground=BTTN_ACTIVE_FG,
        relief=BTTN_RELIEF,
        font=(BTTN_FONT, BTTN_FONT_SIZE),
        command=validate_path,
    )
    exitButton = tk.Button(
        buttonFrame,
        text="Exit",
        fg=BTTN_FG,
        bg=BTTN_BG,
        activebackground=BTTN_ACTIVE_BG,
        activeforeground=BTTN_ACTIVE_FG,
        relief=BTTN_RELIEF,
        font=(BTTN_FONT, BTTN_FONT_SIZE),
        command=lambda: _exit(0),
    )

    info.pack(side="top", fill="both")
    directoryFrame.pack(side="top", fill="both")
    directoryButton.pack(side="right")
    directoryEntry.pack(side="right")
    buttonFrame.pack(side="top")
    okButton.pack(side="right")
    exitButton.pack(side="left")

    window.mainloop()

    return finalPath


def verify_steam_path(steamPath):
    appinfoDirectory = path.join(steamPath, "appcache", "appinfo.vdf")

    if path.isdir(steamPath) and path.isfile(appinfoDirectory):
        return True
    else:
        return False


def get_steam_path():
    if "STEAMPATH" in config:
        if verify_steam_path(config.get("STEAMPATH", "Path")):
            return config.get("STEAMPATH", "Path")

    defaultLocations = {
        "Windows": "C:\\Program Files (x86)\\Steam",
        "Linux": f"{HOME_DIR}/.local/share/Steam",
        "Darwin": f"{HOME_DIR}/Library/Application Support/Steam",  # Mac
    }

    try:
        steamPath = defaultLocations[CURRENT_OS]
    except KeyError:
        steamPath = create_steam_path_window()

    if not verify_steam_path(steamPath):
        steamPath = create_steam_path_window()

    config.add_section("STEAMPATH")
    config.set("STEAMPATH", "Path", steamPath)

    with open(f"{CONFIG_PATH}/config.cfg", "w") as cfg:
        config.write(cfg)

    return config.get("STEAMPATH", "Path")


if __name__ == "__main__":
    makedirs(CONFIG_PATH, exist_ok=True)
    if not path.isfile(f"{CONFIG_PATH}/config.cfg"):
        with open(f"{CONFIG_PATH}/config.cfg", "w"):
            pass

    config = ConfigParser()
    config.read(f"{CONFIG_PATH}/config.cfg")

    STEAM_PATH = get_steam_path()

    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="silently patch appinfo.vdf with previously made modifications",
    )
    parser.add_argument(
        "-e",
        "--export",
        nargs="+",
        type=int,
        help="export the contents of all the given appIDs into the JSON",
    )
    args = parser.parse_args()

    try:
        mainWindow = MainWindow(silent=args.silent, export=args.export)
        if not args.silent and args.export is None:
            mainWindow.window.mainloop()
    except IncompatibleVDFError as e:
        messagebox.showerror(
            title="Invalid VDF Version",
            message=f"VDF version {e.vdf_version:#08x} is not supported.",
        )
