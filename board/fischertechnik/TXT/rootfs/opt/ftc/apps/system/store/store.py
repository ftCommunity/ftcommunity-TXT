#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys, os, io, time
import configparser, zipfile, shutil
from PyQt4.QtNetwork import *

from TouchStyle import *

# url of the "app store"
URL = "https://raw.githubusercontent.com/ftCommunity/ftcommunity-apps/master/packages/"
PACKAGEFILE = "00packages"

# directory were the user installed apps are located
APPBASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
USERAPPBASE = os.path.join(APPBASE, "user")

NET_ERROR_MSG = {
    QNetworkReply.NoError: "No error",
    QNetworkReply.ConnectionRefusedError: "Connection Refused",
    QNetworkReply.RemoteHostClosedError: "Server closed connection",
    QNetworkReply.HostNotFoundError: "Host not found",
    QNetworkReply.TimeoutError: "Connection timed out",
    QNetworkReply.OperationCanceledError: "Connection cancelled",
    QNetworkReply.SslHandshakeFailedError: "SSL handshake failed",
    QNetworkReply.TemporaryNetworkFailureError: "Network Failure"
    }
    
# read an option from a config file and append it to a list if it exists
def append_parameter(package, app, id, parms):
    if package.has_option(app, id):
        parms[id] = package.get(app, id);

# a rotating "i am busy" widget to be shown during network io
class BusyAnimation(QWidget):
    expired = pyqtSignal()

    def __init__(self, parent=None):
        super(BusyAnimation, self).__init__(parent)

        self.resize(64, 64)
        self.move(QPoint(parent.width()/2-32, parent.height()/2-32))

        self.step = 0
        self.percent = -1

        # animate at 5 frames/sec
        self.atimer = QTimer(self)
        self.atimer.timeout.connect(self.animate)
        self.atimer.start(200)

        # create small circle bitmaps for animation
        self.dark = self.draw(16, QColor("#808080"))
        self.bright = self.draw(16, QColor("#fcce04"))
        
    def progress(self, perc):
        self.percent = perc
        self.repaint()
    
    def draw(self, size, color):
        img = QImage(size, size, QImage.Format_ARGB32)
        img.fill(Qt.transparent)

        painter = QPainter(img)
        painter.setPen(Qt.white)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(0, 0, img.width()-1, img.height()-1)
        painter.end()

        return img

    def animate(self):
        self.step += 45
        self.repaint()

    def close(self):
        self.atimer.stop()
        super(BusyAnimation, self).close()

    def paintEvent(self, event):
        radius = min(self.width(), self.height())/2 - 16
        painter = QPainter()
        painter.begin(self)

        if self.percent >= 0:
            font = painter.font()
            # half the size than the current font size 
            if font.pointSize() < 0:
                font.setPixelSize(font.pixelSize() / 3)
            else:
                font.setPointSize(font.pointSize() / 3)
            # set the modified font to the painter */
            painter.setFont(font)

            # draw text in center
            painter.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter, str(self.percent)+"%" )

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(45)
        painter.rotate(self.step)
        painter.drawImage(0,radius, self.bright)
        for i in range(7):
            painter.rotate(45)
            painter.drawImage(0,radius, self.dark)

        painter.end()

class NetworkAccessManager(QNetworkAccessManager):
    networkResult = pyqtSignal(tuple)
    progress = pyqtSignal(int)

    def slotFinished(self):
        reply = self.sender()
        if reply.error() != 0:
            if reply.error() == QNetworkReply.ContentNotFoundError:
                httpStatus = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
                httpStatusMessage = reply.attribute(
                    QNetworkRequest.HttpReasonPhraseAttribute)
                self.networkResult.emit((False, httpStatusMessage + " [" + str(httpStatus) + "]"))
            else:
                if reply.error() in NET_ERROR_MSG:
                    self.networkResult.emit((False, "Network error: " + NET_ERROR_MSG[reply.error()]))
                else:
                    self.networkResult.emit((False, "Unknown network error (" + str(reply.error()) + ")"))
        else:
            self.networkResult.emit((True, b"".join(self.messageBuffer)))

    def slotError(self, code):
        print("Error:", code)
        
    def slotSslErrors(self, errors):
        for e in errors:
            print("SSL Error: ", e.errorString())

    def slotProgress(self, a, b):
        # download makes 50% of progress (zip decrunch will do the rest)
        percent = int(50*a/b)
        if self.progress_percent != percent:
            self.progress.emit(percent)
            self.progress_percent = percent

    #Append current data to the buffer every time readyRead() signal is emitted
    def slotReadData(self):
        # += for byte array has a horrible performance
        # self.messageBuffer += self.reply.readAll()
        self.messageBuffer.append(self.reply.readAll())
    
    def __init__(self, filename):
        QNetworkAccessManager.__init__(self)
        self.messageBuffer = []
        url   = QUrl(URL + filename)
        req   = QNetworkRequest(url)
        self.reply = self.get(req)
        self.reply.ignoreSslErrors()
        self.progress_percent = -1

        self.reply.readyRead.connect(self.slotReadData)
        self.reply.downloadProgress.connect(self.slotProgress)
        self.reply.finished.connect(self.slotFinished)
        self.reply.error.connect(self.slotError)
        self.reply.sslErrors.connect(self.slotSslErrors)

class PackageLoader(NetworkAccessManager):
    result = pyqtSignal(tuple)

    def __init__(self, str):
        NetworkAccessManager.__init__(self, str + ".zip")
        self.networkResult.connect(self.onNetworkResult)

    def onNetworkResult(self, result):
        # forward error message directly
        if not result[0]:
            self.result.emit(result)
            return
            
        print("Received", len(result[1]), "bytes")

        # check if we really received a zip file
        f = io.BytesIO(result[1])
        if not zipfile.is_zipfile(f):
            self.result.emit((False, "Not a valid zip file"))

        unzip_result = self.install_zip(f)
        f.close()
        self.result.emit(unzip_result)

    def install_zip(self,f):
        z = zipfile.ZipFile(f)
        try:
            z.getinfo("manifest")
        except KeyError:
            return((False, "Not a TXT app!"))

        # extract only the manifest to get the uuid which in turn
        # is used as the apps local directory
        manifest_str = io.StringIO(z.read("manifest").decode('utf-8'))
        manifest = configparser.RawConfigParser()
        manifest.readfp(manifest_str)
        if not manifest.has_option('app', 'uuid'):
            return((False, "Manifest does not contain a UUID!"))

        appdir = os.path.join(USERAPPBASE, manifest.get('app', 'uuid'))

        print("Extracting to " + appdir)

        if os.path.exists(appdir):
            print("Target dir exists, overwriting contents.")
        else:
            print("Target dir does not exist, creating it.")
            try:
                os.makedirs(appdir)
            except:
                return((False, "Unable to create target dir!"))

        # unzip with progress update
        cnt = 0
        for name in z.namelist():
            # print("Extracting " + name + " ...")
            cnt += 1
            z.extract(name, appdir)
            self.progress.emit(50+int(50*cnt/len(z.namelist())))
            QCoreApplication.processEvents()
            
        # get various fields from manifest
        executable = os.path.join(appdir, manifest.get('app', 'exec'))
        
        print("Making executable: " + executable)
        os.chmod(executable, 0o744)

        print("done")
        return((True,""))

class AppDialog(TouchDialog):
    # map app key to human readable text.
    labels = { "version": "Version",
               "desc": "Description",
               "author": "Author",
               "firmware": "Firmware",
               "set": "Set",
               "model": "Model",
               "category": "Category"
               }

    def isValid(id):
        return id in AppDialog.labels

    def format(id):
        return AppDialog.labels[id]

    refresh = pyqtSignal()

    def __init__(self,title,parms,inst_ver,parent):
        TouchDialog.__init__(self, title, parent)

        self.package_name = parms['package']
        if 'uuid' in parms:
            self.package_uuid = parms['uuid']
        else:
            self.package_uuid = None

        menu = self.addMenu()

        self.inst_ver = inst_ver
        if not inst_ver:
            menu_inst = menu.addAction("Install")
            menu_inst.triggered.connect(self.on_app_install)
        else:
            # only packages with a valid uuid can be deleted as the
            # uuid is their path name
            if self.package_uuid:
                menu_uninst = menu.addAction("Uninstall")
                menu_uninst.triggered.connect(self.on_app_uninstall)

            if 'version' in parms:
                if inst_ver != parms['version']:
                    # update and installation is actually the same ...
                    menu_update = menu.addAction("Update")
                    menu_update.triggered.connect(self.on_app_install)

        text = QTextEdit()
        text.setReadOnly(True)

        for i in sorted(parms):
            if(AppDialog.isValid(i)):
                value = parms[i]
                # if the version is to be displayed and the installed
                # version differs from the one in the shop then also
                # display the installed version
                if i == 'version' and inst_ver and value != inst_ver:
                    value += " (Inst. " + inst_ver + ")"

                text.append('<h3><font color="#fcce04">' + AppDialog.format(i) + '</font></h3>')
                text.append(value)

        text.moveCursor(QTextCursor.Start)
        self.setCentralWidget(text)
        
    def on_app_install(self):
        if self.inst_ver:
            # check if app resides in the correct directory
            manifestfile = os.path.join(USERAPPBASE, self.package_uuid, "manifest" )
            if not os.path.isfile(manifestfile):
                msgBox = TouchMessageBox("Error", self)
                msgBox.setText("Update app path mismatch.")
                msgBox.exec_()
                return

        self.package_loader = PackageLoader(self.package_name)
        self.package_loader.result.connect(self.onResult)
        self.busy = BusyAnimation(self)
        self.package_loader.progress.connect(self.busy.progress)
        self.busy.show()

    def uninstall(self, name):

        # make sure there's a manifest file
        manifestfile = os.path.join(USERAPPBASE, self.package_uuid, "manifest" )
        if not os.path.isfile(manifestfile):
            return((False, "Delete app path not found!"))

        # remove the whole app dir
        try:
            shutil.rmtree(os.path.join(USERAPPBASE, self.package_uuid))
        except:
            return((False, "Unable to remove app"))

        return((True, ""))

    def on_app_uninstall(self):
        # TODO: Get confirmation from user
        print("Uninstall", self.package_name)
        (ok, msg) = self.uninstall(self.package_name)
        if not ok:
            msgBox = TouchMessageBox("Error", self)
            msgBox.setText(msg)
            msgBox.exec_()
        else:
            self.refresh.emit()

        # close the app dialog
        self.close()

    def onResult(self, result):
        self.busy.close()
        
        if result[0]:
            self.refresh.emit()
            
            # close the app dialog
            self.close()
        else:
            msgBox = TouchMessageBox("Error", self)
            msgBox.setText(result[1])
            msgBox.exec_()

class PackageListLoader(NetworkAccessManager):
    result = pyqtSignal(tuple)

    def __init__(self):
        NetworkAccessManager.__init__(self, PACKAGEFILE)
        self.networkResult.connect(self.onNetworkResult)

    def onNetworkResult(self, result):
        # forward error message directly
        if not result[0]:
            self.result.emit(result)
            return

        # parse result
        packages_str = io.StringIO(result[1].decode('utf-8'))
        packages = configparser.RawConfigParser()
        packages.readfp(packages_str)
        apps = packages.sections() 
        applist = []
        for app in apps:
            appparms = {}
            # name entry is mandatory
            if packages.has_option(app, 'name') and packages.has_option(app, 'uuid'):
                # add everything the gui needs
                appparms['package'] = app
                append_parameter(packages, app, 'name', appparms)
                append_parameter(packages, app, 'uuid', appparms)
                append_parameter(packages, app, 'desc', appparms)
                append_parameter(packages, app, 'category', appparms)
                append_parameter(packages, app, 'model', appparms)
                append_parameter(packages, app, 'set', appparms)
                append_parameter(packages, app, 'author', appparms)
                append_parameter(packages, app, 'version', appparms)
                append_parameter(packages, app, 'firmware', appparms)

                # create a tuple of app name and its parameters
                applist.append((packages.get(app, 'name'), appparms))

        applist.sort(key=lambda tup: tup[0])
        self.result.emit((True, applist))

class AppListWidget(QListWidget):
    def __init__(self, parent=None):
        super(AppListWidget, self).__init__(parent)

        self.setUniformItemSizes(True)
        self.setViewMode(QListView.ListMode)
        self.setMovement(QListView.Static)
        self.setIconSize(QSize(32,32))

        # scan for installed apps
        self.installed_apps = self.scan_installed_app_dirs()

        # start package list download
        self.apps = []
        self.package_list_loader = PackageListLoader()
        self.package_list_loader.result.connect(self.onResult)
        self.busy = BusyAnimation(parent)
        self.busy.show()

        # react on clicks
        self.itemClicked.connect(self.onItemClicked)
        self.setIconSize(QSize(32, 32))

    # return a list of directories containing apps
    # searches under /opt/ftc/apps/<group>/<app>
    # the returned list is srted by the name of the apps
    # as stored in the manifest file
    def scan_installed_app_dirs(self):
        # scan for app group dirs first
        app_groups = os.listdir(APPBASE)
        # then scan for app dirs inside
        app_dirs = []
        for i in app_groups:
            try:
                app_group_dirs = os.listdir(os.path.join(APPBASE, i))
                for a in app_group_dirs:
                    appparms = {}
                    # build full path of the app dir
                    app_dir = os.path.join(APPBASE, i, a)
                    # check if there's a manifest inside that dir
                    manifestfile = os.path.join(app_dir, "manifest")
                    if os.path.isfile(manifestfile):
                        # get app name
                        manifest = configparser.RawConfigParser()
                        manifest.read(manifestfile)

                        # add everything the gui needs
                        append_parameter(manifest, 'app', 'name', appparms)
                        append_parameter(manifest, 'app', 'uuid', appparms)
                        append_parameter(manifest, 'app', 'desc', appparms)
                        append_parameter(manifest, 'app', 'category', appparms)
                        append_parameter(manifest, 'app', 'model', appparms)
                        append_parameter(manifest, 'app', 'set', appparms)
                        append_parameter(manifest, 'app', 'author', appparms)
                        append_parameter(manifest, 'app', 'version', appparms)
                        append_parameter(manifest, 'app', 'firmware', appparms)

                        # create a tuple of app name and its parameters
                        app_dirs.append(appparms)
            except:
                print("Failed: ", i)
                pass
                
        return app_dirs

    # check if a app store  is in the list of installed apps
    # comparisone is done by uuid
    def get_installed_app_info(self, app, apps):
        # check if such an app is already installed
        if 'uuid' in app:
            for x in apps:
                if 'uuid' in x:
                    if x['uuid'] == app['uuid']:
                        return x
        return None

    # store server reply
    def onResult(self, result):
        self.busy.close()

        if not result[0]:
            msgBox = TouchMessageBox("Error", self.parent())
            msgBox.setText(result[1])
            msgBox.exec_()
            return
            
        self.apps = result[1]
        for i in self.apps:
            icn = "not_installed.png"
            # check if such an app is already installed
            x = self.get_installed_app_info(i[1], self.installed_apps)
            if x:
                icn = "installed.png"

                # compare versions and inducate that the
                # installed version is nor the one available
                # in the store. This will also trigger if the
                # installed version is newer than the one in 
                # the store. But that should only happen to
                # developers and they should be able to deal 
                # with that
                if 'version' in x and 'version' in i[1]:
                    if x['version'] != i[1]['version']:
                        icn = "update_available.png"

            if icn:
                item = QListWidgetItem(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),icn)),i[0])
            else:
                item = QListWidgetItem(i[0])

            item.setData(Qt.UserRole, i[1])
            self.addItem(item)

    def onItemClicked(self, item):
        app_parms = item.data(Qt.UserRole)

        installed_version = None
        x = self.get_installed_app_info(app_parms, self.installed_apps)
        if x:
            if 'version' in x: installed_version = x['version']
            else:              installed_version = "no version info"

        # set TouchWindow as parent
        dialog = AppDialog(item.text(), app_parms, installed_version, self.parent())
        dialog.refresh.connect(self.on_refresh)
        dialog.exec_()

    def notify_launcher(self):
        # send a signal so launcher so it reloads the view
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect(("localhost", 9000))
            sock.sendall(bytes("rescan\n", "UTF-8"))
        except socket.error as msg:
            print(("Unable to connect to launcher:", msg))
        finally:
            sock.close()

    def on_refresh(self):
        # do two things: 1. refresh own list, 2. tell launcher to refresh

        # scan for installed apps
        self.installed_apps = self.scan_installed_app_dirs()

        # TODO: We remove the entire list and redo it. That can be optimized
        # later if we have many, many apps in the store ...
        self.model().removeRows( 0, self.model().rowCount() )
        self.onResult((True, self.apps))

        # request launcher refresh
        self.notify_launcher()

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        # create the empty main window
        self.w = TouchWindow("Store")

        self.vbox = QVBoxLayout()

        self.applist = AppListWidget(self.w)
        self.vbox.addWidget(self.applist)

        self.w.centralWidget.setLayout(self.vbox)

        self.w.show()

        self.exec_()

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
