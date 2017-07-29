#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

#import modules
import sys  # argv
from TouchStyle import *  # GUI
import time  # time operations
import os  # os operations
from _thread import start_new_thread  # thread management
import zipfile  # zipfile readout
import urllib.request  # web requests
import json  # json readout
import semantic_version  # version management
from pathlib import Path  # local version readout

update_log = "/tmp/update_log.log"  # paths to update log
update_exit = "/tmp/update_exit"
release_api_url = "https://api.github.com/repos/ftCommunity/ftcommunity-TXT/releases"  # github release api url
fw_ver_file = '/etc/fw-ver.txt'  # path to local version file


class UpdateCheckThread(QThread):
    # thread to check the log files for new content
    new_line = pyqtSignal(str)  # new line signal
    error = pyqtSignal(str)  # error signal

    def __init__(self, parent):
        # init thread
        super(UpdateCheckThread, self).__init__(parent)
        self.lines = []

    def run(self):
        time.sleep(1)  # wait a moment
        # start loop
        while True:
            if os.path.isfile(update_exit):  # check exit file exist
                with open(update_exit) as f:  # open exit file
                    self.error.emit(f.read().replace("\n", "").strip())  # read code and emit
                    break

            with open(update_log) as f:  # open log file
                new_lines = f.readlines()  # read file
            if len(new_lines) > len(self.lines):  # check whether new lines are present
                i = len(self.lines)  # get num of already processed lines
                while i <= len(new_lines) - 1:  # process new lines
                    self.new_line.emit(new_lines[i].replace("\n", "").strip())  # emit every new line
                    i += 1  # count up index
                self.lines = new_lines  # update temp list

            time.sleep(0.1)  # wait until next check


def updateStarter(ver):
    # function to start the update
    print("Start")
    # if logfile/exitcodefile exist, remove
    if os.path.isfile(update_log):
        os.remove(update_log)
    if os.path.isfile(update_exit):
        os.remove(update_exit)
    # start update and echo all output to a file, the exitcode to another
    os.system("sudo system-update " + ver + " > " + update_log + " 2>&1 ; echo $? > " + update_exit)


class EntryWidget(QWidget):
    # cool widget used in update progress

    def __init__(self, title, parent=None):
        QWidget.__init__(self, parent)  # init QWidget

        self.layout = QVBoxLayout()  # init layout
        self.layout.setSpacing(0)
        self.title = QLabel(title)  # generate title label
        self.layout.addWidget(self.title)  # add title to layout
        self.value = QLabel("")  # generate data label
        self.value.setObjectName("smalllabel")  # data label is smalllabel
        self.value.setWordWrap(True)  # enable wordwrap
        self.layout.addWidget(self.value)  # add data widget
        self.setLayout(self.layout)  # set widget's layout

    def setText(self, str):
        # function to add data label's test
        self.value.setText(str)


class PlainDialog(QDialog):
    # fullscreen dialog class

    def __init__(self):
        QDialog.__init__(self)
        if platform.machine() == "armv7l":
            size = QApplication.desktop().screenGeometry()
            self.setFixedSize(size.width(), size.height())
        else:
            self.setFixedSize(WIN_WIDTH, WIN_HEIGHT)

        self.setObjectName("centralwidget")

    def exec_(self):
        QDialog.showFullScreen(self)
        QDialog.exec_(self)


class ErrorDialog(TouchDialog):
    # the update finished dialog
    # it is called on error and success

    def __init__(self, parent, err):
        if err != "0":  # check if it is an error or not, 0=success, !=0 => error
            print("Error: " + err)  # print error code on command line
            # define the error codes to translated strings
            err_codes = {"3": QCoreApplication.translate("ErrorCodes", "Up-to-date!"),
                         "4": QCoreApplication.translate("ErrorCodes", "System Files Error!"),
                         "5": QCoreApplication.translate("ErrorCodes", "System Files Error!"),
                         "10": QCoreApplication.translate("ErrorCodes", "Download Error!"),
                         "20": QCoreApplication.translate("ErrorCodes", "Download validation failed!"),
                         "21": QCoreApplication.translate("ErrorCodes", "Download validation failed!"),
                         "30": QCoreApplication.translate("ErrorCodes", "Backup failed!"),
                         "40": QCoreApplication.translate("ErrorCodes", "Installation failed!")}
            if err in err_codes:  # check whether the code is known and can be converted to string
                error = err_codes[err]  # get error string
            else:
                error = QCoreApplication.translate("ErrorCodes", "Unknown Error!")  # use a defalt string
            error = error + "\nCode " + err  # add the code to the string
            title = QCoreApplication.translate("ErrorDialog", "Error")  # translate window title
            self.reboot = False  # set that the TXT should not reboot automatically
        else:
            error = QCoreApplication.translate("ErrorDialog", "TXT will reboot soon!")  # write that the TXT will reboot soon
            title = QCoreApplication.translate("ErrorDialog", "Finished")  # translate window title
            self.reboot = True  # set that the TXT should reboot automatically

        TouchDialog.__init__(self, title, parent)  # init the dialog

        lbl = QLabel(error)  # init the information label
        # style it
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        vbox = QVBoxLayout()  # generate a vbox
        vbox.addStretch()
        vbox.addWidget(lbl)  # add the information label
        vbox.addStretch()
        self.centralWidget.setLayout(vbox)  # add the vbox to the dialog
        QTimer.singleShot(1, self.do_reboot)  # start possible reboot in 1 sec

    def do_reboot(self):
        # function to reboot the TXT
        if self.reboot:  # check whether we need to reboot the TXT
            os.system("sudo reboot")  # initiate the reboot


class ProgressDialog(PlainDialog):
    # main update progress dialog

    def __init__(self, parent, ver):
        PlainDialog.__init__(self)  # init PlainDialog
        self.ver = ver  # save version
        self.parent = parent  # save parent
        self.state = ""  # init an empty state variable
        self.zip_sizes = {}  # init an empty dict for the zip sizes

        self.thread = UpdateCheckThread(self)  # init update check thread
        self.thread.new_line.connect(self.new_line)  # connect on new line
        self.thread.error.connect(self.error)  # connect on error

        self.vbox = QVBoxLayout()  # init vbox
        self.vbox.addStretch()
        title = QLabel(QCoreApplication.translate("ProgressDialog", "Progress"))  # init title label
        title.setAlignment(Qt.AlignCenter)  # move it to the center
        self.vbox.addWidget(title)  # add title widget
        self.init_label = QLabel(QCoreApplication.translate("ProgressDialog", "Initializing Update"))  # init init-label
        self.init_label.setWordWrap(True)  # enable wordwrap for init-label
        self.init_label.setAlignment(Qt.AlignCenter)  # move it to center
        self.vbox.addWidget(self.init_label)  # add init-label
        self.vbox.addStretch()
        self.setLayout(self.vbox)  # set vbox as central layout
        start_timer = QTimer.singleShot(1000, self.start)  # start update in 1000ms
        self.check_timer = QTimer()  # init checker timer
        self.check_timer.timeout.connect(self.checker)  # connect checker on timeout

    def start(self):
        # function to start update
        # get size of download zip and save it
        self.size = int(os.popen("wget -qO- https://api.github.com/repos/ftCommunity/ftcommunity-TXT/releases/tags/v" + self.ver + " | get_size_json.py").read())
        print("Size: " + str(self.size))  # print zip size
        start_new_thread(updateStarter, (self.ver,))  # start the update in extra thread
        self.thread.start()  # start check thread
        self.buildUI()  # build UI
        self.check_timer.start(100)  # start checker timer and check update state every 100ms

    def new_line(self, line):
        # fuction to precess a new line
        print("LINE: " + line)  # print new line
        # if specific line is found, set state
        if line == "fetching archive from github...":
            self.state = "download"
        elif line == "validating update...":
            self.state = "validation"
        elif line == "backing up current system...":
            self.state = "backup"
        elif line == "installing update...":
            self.state = "install"
        print("State: " + self.state)  # print state

    def buildUI(self):
        # fuction to build UI
        self.init_label.setParent(None)  # remove init label
        # add widgets for 4 states
        # Preparation
        self.preparation_widget = EntryWidget(QCoreApplication.translate("ProgressDialog", "Preparation"))
        self.preparation_widget.setText(QCoreApplication.translate("ProgressDialog", "Pending"))
        self.vbox.addWidget(self.preparation_widget)
        # Download
        self.download_widget = EntryWidget(QCoreApplication.translate("ProgressDialog", "Download"))
        self.download_widget.setText(QCoreApplication.translate("ProgressDialog", "Pending"))
        self.vbox.addWidget(self.download_widget)
        # Backup
        self.backup_widget = EntryWidget(QCoreApplication.translate("ProgressDialog", "Backup"))
        self.backup_widget.setText(QCoreApplication.translate("ProgressDialog", "Pending"))
        self.vbox.addWidget(self.backup_widget)
        # Installation
        self.extract_widget = EntryWidget(QCoreApplication.translate("ProgressDialog", "Installation"))
        self.extract_widget.setText(QCoreApplication.translate("ProgressDialog", "Pending"))
        self.vbox.addWidget(self.extract_widget)

    def checker(self):
        # fucntion to refresh the UI
        if self.state == "download":  # To do while download
            self.preparation_widget.setText(QCoreApplication.translate("ProgressDialog", "Done"))  # set Preparation to done
            try:
                current_size = os.stat("/tmp/update-" + self.ver + "/ftcommunity-txt-" + self.ver + ".zip").st_size  # get current_size of download file
            except:
                current_size = 0  # if file is not present the size is 0
            percentage = (current_size / self.size) * 100  # calculate percentage of download size
            self.download_widget.setText(str("{0:.1f}".format(percentage) + "%"))  # write percentage on screen

        elif self.state == "validation":  # To do while validation
            self.preparation_widget.setText(QCoreApplication.translate("ProgressDialog", "Done"))  # set Preparation to done
            self.download_widget.setText(QCoreApplication.translate("ProgressDialog", "Validating..."))  # set Download to validating

        elif self.state == "backup":  # To do while backup
            self.preparation_widget.setText(QCoreApplication.translate("ProgressDialog", "Done"))  # set Preparation to done
            self.download_widget.setText(QCoreApplication.translate("ProgressDialog", "Done"))  # set Download to done
            count = 0  # init a count variable
            base = "/media/sdcard/boot/"  # set base folder
            # check the three files and count missing files
            if not os.path.isfile(base + "am335x-kno_txt.dtb"):
                count += 1
            if not os.path.isfile(base + "rootfs.img"):
                count += 1
            if not os.path.isfile(base + "uImage"):
                count += 1
            self.backup_widget.setText({0: "0%", 1: "33%", 2: "67%", 3: "100%"}[count])  # print percentage on screen

        elif self.state == "install":  # To do while install
            self.preparation_widget.setText(QCoreApplication.translate("ProgressDialog", "Done"))  # set Preparation to done
            self.download_widget.setText(QCoreApplication.translate("ProgressDialog", "Done"))  # set Download to done
            self.backup_widget.setText(QCoreApplication.translate("ProgressDialog", "Done"))  # set Backup to done
            if self.zip_sizes == {}:  # check whether we already know the sizes of the extracted files
                zip_file = zipfile.ZipFile("/tmp/update-" + self.ver + "/ftcommunity-txt-" + self.ver + ".zip")  # init zip file
                for c_file in zip_file.infolist():  # process every file
                    sub_dict = {"target": c_file.file_size}  # get size for every file
                    self.zip_sizes[c_file.filename] = sub_dict  # add file to dict
            base = "/media/sdcard/boot/"  # set base folder
            for name, t_size in self.zip_sizes.items():  # process all files
                try:
                    current_size = os.stat(base + name).st_size  # get file size on sdcard
                except:
                    current_size = 0  # if file is not present the size is 0
                self.zip_sizes[name]["size"] = current_size  # save current size of specific file

            size = 0  # init current size variable
            target_sum = 0  # init total file size variable
            for perc in self.zip_sizes.values():  # process all files
                percentage += perc["size"]  # add file size
                target_sum += perc["target"]  # add total target sum

            percentage = size / target_sum * 100  # calculate current percentage
            self.backup_widget.setText(str("{0:.1f}".format(percentage) + "%"))  # print percentage on screen

    def error(self, err):
        # function to open the ErrorDialog
        dialog = ErrorDialog(self.parent, err)
        dialog.exec_()
        self.close()


class UpdateListWidget(QListWidget):
    # Widget to list all avaible releases from github
    update = pyqtSignal(str)  # Signal to start update

    def __init__(self, releases, parent=None):
        super(UpdateListWidget, self).__init__(parent)  # init UpdateListWidget

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # enable Scroll bar

        lcl = Path(fw_ver_file).read_text().replace('v', '').strip()  # get local version

        id_list = []  # init empty release id list
        # github gives an unique id to each release all over github ascending by date
        # get release id for each release
        for r in releases:
            id_list.append(r["id"])

        mark = ""  # init empty mark variable
        # search in releases for the current installed release
        for r in releases:
            if r["tag_name"].replace("v", "") == lcl:
                mark = r["tag_name"].replace("v", "")  # save tag name of installed version

        id_list = reversed(sorted(id_list))  # reverse id list

        for ID in id_list:  # process all release
            release = self.getReleaseByID(id_list, releases, ID)  # get release data by id
            name = release["tag_name"]  # get name of release
            try:
                # change the name of snapshot releases
                if "snapshot" in name:
                    name = "snapshot" + name.split("snapshot-")[1]
            except:
                pass
            item = QListWidgetItem(name)  # init list item with name
            # mark installed version green
            if mark == release["tag_name"].replace("v", ""):
                item.setBackground(Qt.green)
            # mark prereleases with caution icon
            if release["prerelease"]:
                item.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "prerelease.png")))
            # mark stable releases with a tick
            else:
                item.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "stable.png")))
            item.setData(Qt.UserRole, (release))  # save releas data in list item
            self.addItem(item)  # add item to list
        self.itemClicked.connect(self.onItemClicked)  # add on-click-function

    def onItemClicked(self, item):
        release = item.data(Qt.UserRole)  # get item data
        self.update.emit(release["tag_name"])  # emit update signal

    def getReleaseByID(self, id_list, releases, ID):
        for r in releases:  # process all items
            if ID == r["id"]:  # check whether ID matches
                return(r)  # return first item
        return(None)  # return None if not found


class OkDialog(TouchDialog):
    # simple dialog to check whether th euser really wanzs to update
    ret = None  # init return variable

    def __init__(self, parent, newver):
        TouchDialog.__init__(self, QCoreApplication.translate("OkDialog", "Confirm"), parent)  # init dialog
        cur_ver = Path(fw_ver_file).read_text()  # get current installed version
        # change the name of snapshot releases
        try:
            if "snapshot" in cur_ver:
                cur_ver = "snapshot" + cur_ver.split("snapshot-")[1]
        except:
            pass
        try:
            if "snapshot" in newver:
                newver = "snapshot" + newver.split("snapshot-")[1]
        except:
            pass
        self.addConfirm()  # add confirm button to title bar
        self.titlebar.confbut.clicked.connect(self.pressed)  # add on-click-function
        self.setCancelButton()  # add cancel button to title bar
        self.titlebar.close.clicked.connect(self.pressed)  # add on-click-function
        self.vbox = QVBoxLayout()  # init vbox
        self.label = QLabel(QCoreApplication.translate("OkDialog", "Do you want to update from %s to %s?" % (cur_ver, newver)))  # init info label
        self.label.setObjectName("smalllabel")  # set it as smalllabel
        self.label.setWordWrap(True)  # enable wordwrap
        self.vbox.addStretch()
        self.vbox.addWidget(self.label)  # add info label
        self.vbox.addStretch()
        self.centralWidget.setLayout(self.vbox)  # set vbox as centralWidget

    def pressed(self):
        self.ret = self.sender().objectName()  # save objectName


class TouchGuiApplication(TouchApplication):
    # main application class

    def __init__(self, args):
        TouchApplication.__init__(self, args)  # init TouchApplication

        # init translator
        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(QLocale.system(), os.path.join(path, "update_"))
        self.installTranslator(translator)

        # create the empty main window
        self.w = TouchWindow(QCoreApplication.translate("TouchGuiApplication", "Update"))
        self.dialog = None  # init dialog variable
        self.update_version = ""  # init update_version variable

        self.vbox = QVBoxLayout()  # init vbox
        self.lbl = QLabel(QCoreApplication.translate("TouchGuiApplication", "Searching for updates"))  # init info label
        self.lbl.setWordWrap(True)  # enable wordwrap
        self.vbox.addWidget(self.lbl)  # add info label
        self.but = QPushButton("Update")  # init Update button
        self.but.pressed.connect(self.start)  # conect on-click-function
        self.but.setDisabled(True)  # disable button
        self.vbox.addWidget(self.but)  # add Update button
        self.w.centralWidget.setLayout(self.vbox)  # set vbox as centralWidget
        self.w.show()  # show window
        QTimer.singleShot(0, self.checkUpdate)  # Start Update Check
        self.exec_()  # start event loop

    def start(self, ver=None):
        # function to start the update
        if self.dialog == None:  # check whether no dialog is open
            if ver == None:  # check whether a version was in arguments
                ver = self.update_version  # get update version from variable
            print("updating to: " + ver)  # print update version
            self.dialog = OkDialog(self.w, ver)  # init OkDialog
            self.dialog.exec_()  # open it
            if self.dialog.ret == "confirmbut":  # check whether user pressed ok
                print("ok")  # print ok
            else:
                self.dialog = None  # clean up dialog variable
                print("abort")  # print abort
                return  # abort
            ver = ver.replace('v', '')  # remove any "v" from str
            self.dialog = ProgressDialog(self.w, ver)  # init ProgressDialog
            self.dialog.exec_()  # start update
            self.w.close()  # close application

    def getLatestRelease(self):
        # function to get latest release data
        try:
            raw_data = urllib.request.urlopen(release_api_url).read().decode()  # download release api data
            all_releases = json.loads(raw_data)  # decode json
            i = 0  # init count variable
            while i <= len(all_releases) - 1:  # process all releases
                if all_releases[i]["prerelease"] == False:  # check whether release is prerelease
                    return(all_releases[i])  # return release data
                i += 1  # count one up
        except:
            pass
        return(None)  # return None

    def to_str(self, ver):
        # function to generate a version string
        return(str(ver.major) + "." + str(ver.minor) + "." + str(ver.patch))

    def checkUpdate(self):
        # function to check for updates and maybe build the UI to select a specific release
        lcl_ver = semantic_version.Version(Path(fw_ver_file).read_text().replace('v', ''))  # get current local version
        snapshot = False  # init snapshot install variable
        # check whether snapshot is already installed
        if len(lcl_ver.prerelease) > 1:
            if "snapshot" in lcl_ver.prerelease[1]:  # check whether snapshot is installed
                print("SNAPSHOT DETECTED!")
                snapshot = True  # set variable
        if "install-snapshot" in sys.argv:  # check whether snapshot Installation is enabled via argument
            print("SNAPSHOTS TEPORARY ENABLED BY ARGUMENT!")
            snapshot = True  # set variable
        if snapshot:  # check whether we want to offer snapshot Installation
            try:
                raw_data = urllib.request.urlopen(release_api_url).read().decode()  # download release api data
                all_releases = json.loads(raw_data)  # decode json
            except:  # show error message in case of error
                self.lbl.setText(QCoreApplication.translate("TouchGuiApplication", "Error while checking for updates!\nPlease try again later!\nYou are currently using " + self.to_str(lcl_ver)))
                return

            self.lbl.setParent(None)  # remove info label
            self.but.setParent(None)  # remove update button

            self.info_text = QLabel(QCoreApplication.translate("TouchGuiApplication", "Select one release of the list below:"))  # init new info label
            self.info_text.setWordWrap(True)  # enable wordwrap
            self.vbox.addWidget(self.info_text)  # add new info label

            self.update_list = UpdateListWidget(all_releases)  # init UpdateListWidget
            self.update_list.update.connect(self.start)  # connect on update starter
            self.vbox.addWidget(self.update_list)  # add UpdateListWidget
            return  # return because the rest is for stable Installation

        release = self.getLatestRelease()  # get latest release
        if release == None:  # show error message in case of error
            self.lbl.setText(QCoreApplication.translate("TouchGuiApplication", "Error while checking for updates!\nPlease try again later!\nYou are currently using " + self.to_str(lcl_ver)))
            return
        release_ver = semantic_version.Version(release['tag_name'].replace('v', ''))  # generate a semantic_version object for the latest release

        if lcl_ver < release_ver:  # check whether new version is avaible
            self.update_version = self.to_str(release_ver)  # save update version
            # show new version information
            self.lbl.setText(QCoreApplication.translate("TouchGuiApplication", 'An update to ' + self.update_version + ' is avaible. To Installl press "Update".\nYou are currently using ' + self.to_str(lcl_ver)))
            self.but.setDisabled(False)  # enable update button
        else:
            # show that no new version is avaible
            self.lbl.setText(QCoreApplication.translate("TouchGuiApplication", "No new version found!\nYou are currently using " + self.to_str(lcl_ver)))


if __name__ == "__main__":
    TouchGuiApplication(sys.argv)
