#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# TODO:
# + fix GUI hang with network problems
# - fix segfault after network problems

import sys, os, io, time
import configparser, zipfile, shutil
import semantic_version, subprocess
from pathlib import Path

from TouchStyle import *

from PyQt5.QtNetwork import *
from PyQt5 import QtCore

import xml.etree.ElementTree as ET

from launcher import LauncherPlugin

try:
    FW_VERSION = semantic_version.Version(Path('/etc/fw-ver.txt').open().read())
except:
    FW_VERSION = semantic_version.Version("0.10.8")

# url of the "app store"
URL = "https://raw.githubusercontent.com/ftCommunity/ftcommunity-apps/%s/packages/"
MAIN_BRANCH = "master"
ALTERNATE_BRANCH = "v%d.%d.%d" % (FW_VERSION.major, FW_VERSION.minor, FW_VERSION.patch)
PACKAGEFILE = "00packages"

# predefined alternate repositories, currently only githib is supported
GITHUB_URL = "https://raw.githubusercontent.com/%s/%%s/packages/"

# directory were the user installed apps are located
APPBASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
USERAPPBASE = os.path.join(APPBASE, "user")

# on the TX-Pi the store can use apt-get to install dependencies
APT_GET = "/usr/bin/apt-get"

def get_category_name(code):
    category_map = {
        "system":   QCoreApplication.translate("Category", "System"),
        "settings": QCoreApplication.translate("Category", "System"), # deprecated settings category
        "models":   QCoreApplication.translate("Category", "Models"),
        "model":    QCoreApplication.translate("Category", "Models"),
        "tools":    QCoreApplication.translate("Category", "Tools"),
        "tool":     QCoreApplication.translate("Category", "Tools"),
        "demos":    QCoreApplication.translate("Category", "Demos"),
        "demo":     QCoreApplication.translate("Category", "Demos"),
        "tests":    QCoreApplication.translate("Category", "Demos"),   # deprecated "tests" category
        "test":     QCoreApplication.translate("Category", "Demos")    # deprecated "test" category
    };
    
    if code in category_map:
        return category_map[code]
        
    return QCoreApplication.translate("Category", "<unknown>")

# read an option from a config file and append it to a list if it exists
def append_parameter(package, app, id, lkey, parms):
    val = None

    # is there a language key to try?
    if lkey:
        # no app name given: we are parsing a manifest and the languages
        # have seperate sections
        if not app:
            if package.has_option(lkey, id):
                val = package.get(lkey, id);

        # app name was given. we are parsing the 00packages and language 
        # specific entries have the form key_kley: ...
        else:
            if package.has_option(app, id+'_'+lkey):
                val = package.get(app, id+'_'+lkey);

    # nothing language specifg found, try "normal"
    if not app: app = 'app'
    if not val and package.has_option(app, id):
        val = package.get(app, id);

    # category entries need special treatment
    if val and id == 'category':
        val = get_category_name(val.lower())

    # version entries are parsed into semantic versions
    # missing or invalid version entries are interpreted
    # as '0.0.0-missing' or '0.0.0-invalid+...', 
    # i.e. a "version" that is guaranteed to be lower than
    # any real version
    if id == 'version':
        if val:
            try:
                val = semantic_version.Version.coerce(val)
            except ValueError:
                val = semantic_version.Version("0.0.0-invalid+" + val)
        else:
            val = semantic_version.Version("0.0.0-missing")

    # ... and 'firmware' entries into semantic version specs
    if val and id == 'firmware':
        try:
            val = semantic_version.Spec(val)
        except ValueError:
            val = None

    if val:
        parms[id] = val

# a rotating "i am busy" widget to be shown during network io
class BusyAnimation(QWidget):
    expired = pyqtSignal()

    def __init__(self, parent=None):
        super(BusyAnimation, self).__init__(parent)

        self.resize(64, 64)
        self.move(QPoint(parent.width()//2-32, parent.height()//2-32))

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
        radius = min(self.width(), self.height())//2 - 16
        painter = QPainter()
        painter.begin(self)

        if self.percent >= 0:
            font = painter.font()
            # half the size than the current font size 
            if font.pointSize() < 0:
                font.setPixelSize(font.pixelSize() // 3)
            else:
                font.setPointSize(font.pointSize() // 3)
            # set the modified font to the painter */
            painter.setFont(font)

            # draw text in center
            painter.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter, str(self.percent)+"%" )

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width()//2, self.height()//2)
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

    def get_error(self, code):
        NET_ERROR_MSG = {
            QNetworkReply.NoError: QCoreApplication.translate("NetError", "No error"),
            QNetworkReply.ConnectionRefusedError: QCoreApplication.translate("NetError", "Connection Refused"),
            QNetworkReply.RemoteHostClosedError: QCoreApplication.translate("NetError", "Server closed connection"),
            QNetworkReply.HostNotFoundError: QCoreApplication.translate("NetError", "Host not found"),
            QNetworkReply.TimeoutError: QCoreApplication.translate("NetError", "Connection timed out"),
            QNetworkReply.OperationCanceledError: QCoreApplication.translate("NetError", "Connection cancelled"),
            QNetworkReply.SslHandshakeFailedError: QCoreApplication.translate("NetError", "SSL handshake failed"),
            QNetworkReply.TemporaryNetworkFailureError: QCoreApplication.translate("NetError", "Network Failure")
        }

        if code in NET_ERROR_MSG:
            return NET_ERROR_MSG[code]

        return "(" + str(code) + ")"

    def slotFinished(self):
        reply = self.sender()
        if reply.error() != 0:
            if reply.error() == QNetworkReply.ContentNotFoundError:
                if self.ignoreNotFound:
                    self.networkResult.emit((True, b""))
                else:
                    httpStatus = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
                    httpStatusMessage = reply.attribute(
                        QNetworkRequest.HttpReasonPhraseAttribute)
                    self.networkResult.emit((False, httpStatusMessage + " [" + str(httpStatus) + "]"))
            else:
                self.networkResult.emit((False, QCoreApplication.translate("NetError", "Network error:") + " " + self.get_error(reply.error())))
        else:
            self.networkResult.emit((True, b"".join(self.messageBuffer)))
        reply.deleteLater()

    def slotError(self, code):
        print("Error %s while trying to access %s" % (code, self.url))
        
    def slotSslErrors(self, errors):
        for e in errors:
            print("SSL Error: ", e.errorString())

    def slotProgress(self, a, b):
        # download makes 50% of progress (zip decrunch will do the rest)
        if b > 0: percent = int(50*a/b)
        else:     percent = 0
        if self.progress_percent != percent:
            self.progress.emit(percent)
            self.progress_percent = percent

    #Append current data to the buffer every time readyRead() signal is emitted
    def slotReadData(self):
        self.messageBuffer.append(self.sender().readAll())
    
    def __init__(self, filename, url, branch=MAIN_BRANCH, ignoreNotFound=False):
        QNetworkAccessManager.__init__(self)
        self.messageBuffer = []
        url   = QUrl((url % branch) + filename)
        self.url = url.toDisplayString()
        req   = QNetworkRequest(url)
        reply = self.get(req)
        self.progress_percent = -1
        self.ignoreNotFound = ignoreNotFound

        reply.readyRead.connect(self.slotReadData)
        reply.downloadProgress.connect(self.slotProgress)
        reply.finished.connect(self.slotFinished)
        reply.error.connect(self.slotError)
        reply.sslErrors.connect(self.slotSslErrors)

class PackageLoader(NetworkAccessManager):
    result = pyqtSignal(tuple)

    def __init__(self, str, url, branch=MAIN_BRANCH):
        NetworkAccessManager.__init__(self, str + ".zip", url, branch)
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
            self.result.emit((False, QCoreApplication.translate("Error", "Not a valid zip file")))

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
        manifest.read_file(manifest_str)
        if not manifest.has_option('app', 'uuid'):
            return((False, QCoreApplication.translate("Error", "Manifest does not contain a UUID!")))

        appdir = os.path.join(USERAPPBASE, manifest.get('app', 'uuid'))

        print("Extracting to " + appdir)

        if os.path.exists(appdir):
            print("Target dir exists, overwriting contents.")
        else:
            print("Target dir does not exist, creating it.")
            try:
                os.makedirs(appdir)
            except:
                return((False, QCoreApplication.translate("Error", "Unable to create target dir!")))

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

        # handling for apt dependencies
        if manifest.has_option('app', 'depends'):
            print("Manifest contains dependencies. Installing them")
            if os.path.isfile(APT_GET):
                # assemble apt-get command
                cmd = ["sudo", "apt-get", "-y", "install" ]
                # split comma seperated dependencies into a space seperated list
                # and append list to command
                cmd.extend(manifest.get('app', 'depends').split(","))
                try:
                    subprocess.run(cmd, check=True)
                except Exception as e:
                    print("Error running apt-get:", str(e))
                    return((False, "Error running apt-get: "+str(e)))
            else:
                print("Unable to install dependencies: Missing apt-get ...")
                return((False, "Missing apt-get"))
        
        print("done")
        return((True,""))

class NewRepoDialog(TouchDialog):
    new_repo = pyqtSignal(dict)
    
    class EntryWidget(QWidget):        
        def __init__(self, title_str, parent):
            QWidget.__init__(self, parent)
            vbox = QVBoxLayout()
            vbox.setSpacing(0)
            vbox.setContentsMargins(0,0,0,0)
            
            title = QLabel(title_str, self)
            title.setObjectName("smalllabel")
            vbox.addWidget(title)
            
            self.field = QLineEdit(self)
            vbox.addWidget(self.field)
            
            self.setLayout(vbox)

        def text(self):
            return self.field.text()

    def __init__(self, parent):
        TouchDialog.__init__(self, QCoreApplication.translate("NewRepo", "New"), parent)

        conf=self.addConfirm()
        self.setCancelButton()
        
        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0,0,0,0)

        vbox.addStretch()

        self.name = self.EntryWidget(QCoreApplication.translate("NewRepo", "Name:"), self)
        vbox.addWidget(self.name)
        vbox.addStretch()

        # currently only github repositories are supported
        gh = QLabel(QCoreApplication.translate("NewRepo", "Github:"), self)
        gh.setAlignment(Qt.AlignCenter)
        vbox.addWidget(gh)
            
        self.gh_user = self.EntryWidget(QCoreApplication.translate("NewRepo", "User:"), self)
        vbox.addWidget(self.gh_user)
        
        self.gh_repo = self.EntryWidget(QCoreApplication.translate("NewRepo", "Repository:"), self)
        vbox.addWidget(self.gh_repo)
        vbox.addStretch()

        self.centralWidget.setLayout(vbox)
        
    def close(self):
        # user has close the input dialog. Sent updated string 
        # to invoking widget
        TouchDialog.close(self)
        if self.sender().objectName()=="confirmbut":
            self.new_repo.emit( { "name": self.name.text(), "user": self.gh_user.text(), "repo": self.gh_repo.text() } )

class AppDialog(TouchDialog):
    def format(id):
        # map app key to human readable text.
        labels = { "version":  QCoreApplication.translate("AppInfo", "Version"),
                   "desc":     QCoreApplication.translate("AppInfo", "Description"),
                   "author":   QCoreApplication.translate("AppInfo", "Author"),
                   "firmware": QCoreApplication.translate("AppInfo", "Firmware"),
                   "set":      QCoreApplication.translate("AppInfo", "Set"),
                   "model":    QCoreApplication.translate("AppInfo", "Model"),
                   "category": QCoreApplication.translate("AppInfo", "Category"),
                   "depends":  QCoreApplication.translate("AppInfo", "Dependencies")
               }
        if id in labels:
            return labels[id]
        else:
            return None

    refresh = pyqtSignal()

    def __init__(self, title, url, parms, inst_ver, parent):
        TouchDialog.__init__(self, title, parent)

        self.url = url
        
        self.package_name = parms['package']
        if 'uuid' in parms:
            self.package_uuid = parms['uuid']
        else:
            self.package_uuid = None
        if 'branch' in parms:
            self.package_branch = parms['branch']
        else:
            self.package_branch = MAIN_BRANCH

        menu = self.addMenu()

        self.inst_ver = inst_ver
        if not inst_ver:
            menu_inst = menu.addAction(QCoreApplication.translate("Menu", "Install"))
            menu_inst.triggered.connect(self.on_app_install)
        else:
            # only packages with a valid uuid can be deleted as the
            # uuid is their path name
            if self.package_uuid:
                menu_uninst = menu.addAction(QCoreApplication.translate("Menu", "Uninstall"))
                menu_uninst.triggered.connect(self.on_app_uninstall)

            if 'version' in parms:
                if inst_ver != parms['version']:
                    # update and installation is actually the same ...
                    menu_update = menu.addAction(QCoreApplication.translate("Menu", "Update"))
                    menu_update.triggered.connect(self.on_app_install)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setTextInteractionFlags (QtCore.Qt.NoTextInteraction)    
        QScroller.grabGesture(text.viewport(), QScroller.LeftMouseButtonGesture);
        
        for i in sorted(parms):
            if(AppDialog.format(i)):
                value = str(parms[i])
                # if the version is to be displayed and the installed
                # version differs from the one in the shop then also
                # display the installed version
                if i == 'version' and inst_ver and value != inst_ver:
                    value += " ("+QCoreApplication.translate("AppInfo", "Inst.")+" " + str(inst_ver) + ")"

                text.append('<h3><font color="#fcce04">' + AppDialog.format(i) + '</font></h3>')
                text.append(value)

        text.moveCursor(QTextCursor.Start)
        self.setCentralWidget(text)
        
    def on_app_install(self):
        if self.inst_ver:
            # check if app resides in the correct directory
            manifestfile = os.path.join(USERAPPBASE, self.package_uuid, "manifest" )
            if not os.path.isfile(manifestfile):
                msgBox = TouchMessageBox(QCoreApplication.translate("Error", "Error"), self)
                msgBox.setText(QCoreApplication.translate("Error", "Update app path mismatch."))
                msgBox.exec_()
                return

        self.package_loader = PackageLoader(self.package_name, self.url, self.package_branch)
        self.package_loader.result.connect(self.onResult)

        self.busy = BusyAnimation(self)
        self.package_loader.progress.connect(self.busy.progress)
        self.busy.show()

        # make dialog unusable whilte downloading/installing
        self.setDisabled(True)
        self.centralWidget.setGraphicsEffect(QGraphicsBlurEffect(self))
        self.titlebar.setGraphicsEffect(QGraphicsBlurEffect(self))

    def uninstall(self, name):

        # make sure there's a manifest file
        manifestfile = os.path.join(USERAPPBASE, self.package_uuid, "manifest" )
        if not os.path.isfile(manifestfile):
            return((False, QCoreApplication.translate("Error", "Delete app path not found!")))

        # remove the whole app dir
        try:
            shutil.rmtree(os.path.join(USERAPPBASE, self.package_uuid))
        except:
            return((False, QCoreApplication.translate("Error", "Unable to remove app")))

        return((True, ""))

    def on_app_uninstall(self):
        # TODO: Get confirmation from user
        print("Uninstall", self.package_name)
        (ok, msg) = self.uninstall(self.package_name)
        if not ok:
            msgBox = TouchMessageBox(QCoreApplication.translate("Error", "Error"), self)
            msgBox.setText(msg)
            msgBox.exec_()
        else:
            self.refresh.emit()

        # close the app dialog
        self.close()

    def onResult(self, result):
        self.busy.close()

        # Make dialog unusable again. Actually we don't need to
        # do this as we'll close the dialog immediately, anyway.
        # But it doesn't hurt ...
        self.setEnabled(True)
        self.centralWidget.setGraphicsEffect(None)
        self.titlebar.setGraphicsEffect(None)
        
        if result[0]:
            self.refresh.emit()
            
            # close the app dialog
            self.close()
        else:
            msgBox = TouchMessageBox(QCoreApplication.translate("Error", "Error"), self)
            msgBox.setText(result[1])
            msgBox.exec_()

class PackageListLoader(NetworkAccessManager):
    result = pyqtSignal(tuple)

    def __init__(self, url, branch=MAIN_BRANCH):
        NetworkAccessManager.__init__(self, PACKAGEFILE, url, branch, branch!=MAIN_BRANCH)
        self.branch = branch
        self.networkResult.connect(self.onNetworkResult)

    def onNetworkResult(self, result):
        # forward error message directly
        if not result[0]:
            self.result.emit((result[0], result[1], self))
            return

        # get current language key (en,de,...)
        lkey = QLocale.system().name().split('_')[0].lower()

        # parse result
        packages_str = io.StringIO(result[1].decode('utf-8'))
        packages = configparser.RawConfigParser()
        packages.read_file(packages_str)
        apps = packages.sections() 
        applist = []
        for app in apps:
            appparms = {}
            # name and uuid entries are mandatory
            if packages.has_option(app, 'name') and packages.has_option(app, 'uuid'):
                # add everything the gui needs
                appparms['package'] = app
                appparms['branch'] = self.branch
                # name and description may have translations
                append_parameter(packages, app, 'name', lkey, appparms)
                append_parameter(packages, app, 'uuid', None, appparms)
                append_parameter(packages, app, 'desc', lkey, appparms)
                append_parameter(packages, app, 'category', None, appparms)
                append_parameter(packages, app, 'model', None, appparms)
                append_parameter(packages, app, 'set', None, appparms)
                append_parameter(packages, app, 'author', None, appparms)
                append_parameter(packages, app, 'version', None, appparms)
                append_parameter(packages, app, 'firmware', None, appparms)
                append_parameter(packages, app, 'depends', None, appparms)

                # if the app has a firmware spec, check if it matches the
                # current firmware and only append the app if it does
                if (not 'firmware' in appparms) or FW_VERSION in appparms['firmware']:

                    # create a tuple of app name and its parameters
                    # check for language specific name first
                    if packages.has_option(app, 'name_'+lkey):
                        applist.append((packages.get(app, 'name_'+lkey), appparms))
                    else:
                        applist.append((packages.get(app, 'name'), appparms))

        self.result.emit((True, applist, self))

class AppListWidget(QListWidget):
    def __init__(self, parent=None):
        super(AppListWidget, self).__init__(parent)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        QScroller.grabGesture(self.viewport(), QScroller.LeftMouseButtonGesture);
        
        self.setUniformItemSizes(True)
        self.setViewMode(QListView.ListMode)
        self.setMovement(QListView.Static)
        self.setIconSize(QSize(32,32))
        self.parent = parent

        # scan for installed apps
        self.url = URL
        self.installed_apps = self.scan_installed_app_dirs()

        # start package list download
        self.apps = []
        self.apps_by_uuid = {}
        self.active_loaders = {}
        for branch in (MAIN_BRANCH, ALTERNATE_BRANCH):
            loader = PackageListLoader(self.url, branch)
            self.active_loaders[branch] = loader;
            loader.result.connect(self.onLoadPackageList)
        self.busy = BusyAnimation(parent)
        self.busy.show()

        # react on clicks
        self.itemClicked.connect(self.onItemClicked)
        self.setIconSize(QSize(32, 32))

    # collect results from a package list loader
    # and pass those results to onResult when the 
    # last loader has finished
    def onLoadPackageList(self, result):
        success = result[0]
        data = result[1]
        loader = result[2]
        if not self.active_loaders.get(loader.branch):
            return

        if not success:
            # ignore results from all other loaders and
            # pass the error to onResult
            self.active_loaders.clear()
            self.onResult((False, data))
            return

        del self.active_loaders[loader.branch]
        for tup in data:
            app = tup[1]
            existing_app = self.apps_by_uuid.get(app['uuid'], (None, None))[1]
            if existing_app:
                existing_ver = existing_app['version']
                new_ver = app['version']
                if new_ver > existing_ver or (new_ver == existing_ver and loader.branch == MAIN_BRANCH):
                    self.apps_by_uuid[app['uuid']] = tup
            else:
                self.apps_by_uuid[app['uuid']] = tup

        if not self.active_loaders:
            # last loader finished - pass on the results
            self.apps = sorted(self.apps_by_uuid.values(), key=lambda tup: tup[0])
            self.onResult((True, self.apps))


    # return a list of directories containing apps
    # searches under /opt/ftc/apps/<group>/<app>
    # the returned list is srted by the name of the apps
    # as stored in the manifest file
    def scan_installed_app_dirs(self):
        # get current language key (en,de,...)
        lkey = QLocale.system().name().split('_')[0].lower()

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
                        manifest.read_file(open(manifestfile, "r", encoding="utf8"))

                        # add everything the gui needs
                        append_parameter(manifest, None, 'name', lkey, appparms)
                        append_parameter(manifest, None, 'uuid', None, appparms)
                        append_parameter(manifest, None, 'desc', lkey, appparms)
                        append_parameter(manifest, None, 'category', None, appparms)
                        append_parameter(manifest, None, 'model', None, appparms)
                        append_parameter(manifest, None, 'set', None, appparms)
                        append_parameter(manifest, None, 'author', None, appparms)
                        append_parameter(manifest, None, 'version', None, appparms)
                        append_parameter(manifest, None, 'firmware', None, appparms)

                        # create a tuple of app name and its parameters
                        app_dirs.append(appparms)
            except:
                print("Failed to scan app directory: ", i)
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
            msgBox = TouchMessageBox(QCoreApplication.translate("Error", "Error"), self.parent)
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

                # compare versions and indicate if a newer
                # version is available in the store.
                if 'version' in x and 'version' in i[1]:
                    if x['version'] < i[1]['version']:
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
            else:              installed_version = QCoreApplication.translate("Error", "no version info")

        # set TouchWindow as parent
        dialog = AppDialog(item.text(), self.url, app_parms, installed_version, self.parent)
        dialog.refresh.connect(self.on_refresh)

        # exec_ breaks grabGesture: https://bugreports.qt.io/browse/QTBUG-67210
        dialog.show()

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

    def set(self, repo):
        if "url" in repo:
            self.url = repo["url"]
        if "user" in repo and "repo" in repo:
            self.url = GITHUB_URL % (repo["user"]+"/"+repo["repo"])

        self.model().removeRows( 0, self.model().rowCount() )

        self.apps_by_uuid = {}
        self.active_loaders = {}
        for branch in (MAIN_BRANCH, ALTERNATE_BRANCH):
            loader = PackageListLoader(self.url, branch)
            self.active_loaders[branch] = loader;
            loader.result.connect(self.onLoadPackageList)
        self.busy = BusyAnimation(self.parent)
        self.busy.show()
         
        
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

class FtcGuiPlugin(LauncherPlugin):

    def filename(self):
        return os.path.join(os.path.expanduser("~"), ".repositories.xml")

    def __init__(self, application):
        LauncherPlugin.__init__(self, application)

        self.repos = self.load_repos()
        self.repo = "ftc"  # current repository 
        
        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(self.locale(), os.path.join(path, "store_"))
        self.installTranslator(translator)

        # create the empty main window
        self.mainWindow = TouchWindow(QCoreApplication.translate("Main", "Store"))

        # TODO: Load list
        self.menu = self.mainWindow.addMenu()
        menu_new = self.menu.addAction(QCoreApplication.translate("menu", "New"))
        menu_new.triggered.connect(self.on_menu_new)
        self.menu_del = self.menu.addAction(QCoreApplication.translate("menu", "Remove"))
        self.menu_del.setEnabled(False)  # cannot delete default repo
        self.menu_del.triggered.connect(self.on_menu_del)
        self.group = QActionGroup( self.menu )
        self.menu.addSeparator()

        self.menu_ftc = self.menu.addAction(QCoreApplication.translate("menu", "ftc"))
        self.menu_ftc.setCheckable(True)
        self.menu_ftc.setActionGroup(self.group)
        self.menu_ftc.setChecked(True)
        self.menu_ftc.setData( { "name": "ftc", "url": URL } )
        self.menu_ftc.triggered.connect(self.on_menu_select_repo)

        self.repo_menu = { }
        for repo in self.repos:
            menu_repo = self.menu.addAction(repo["name"])
            menu_repo.setCheckable(True)
            menu_repo.setActionGroup(self.group)
            menu_repo.setData( repo )
            menu_repo.triggered.connect(self.on_menu_select_repo)
            self.repo_menu[repo["name"]] = menu_repo
        
        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(0)
        self.vbox.setContentsMargins(0,0,0,0)

        self.applist = AppListWidget(self.mainWindow)
        self.vbox.addWidget(self.applist)

        self.mainWindow.centralWidget.setLayout(self.vbox)

        self.mainWindow.show()

    def load_repos(self):
        repos = [ ]
        
        try:
            tree = ET.parse(self.filename())
            root = tree.getroot()
            if root.tag == "repositories":
                for child in root:
                    if child.tag == "repository":
                        repo = { }
                        repo["name"] = child.attrib["name"]
                        repo["user"] = child.attrib["user"]
                        repo["repo"] = child.attrib["repo"]
                        repos.append(repo)
        except:
            pass
            
        return repos

    def save_repos(self):
        root_element = ET.Element("repositories")
        for r in self.repos:
            repo_element = ET.SubElement(root_element, "repository")
            repo_element.set("name", r["name"])
            repo_element.set("user", r["user"])
            repo_element.set("repo", r["repo"])
        ET.ElementTree(root_element).write(self.filename())

    
    def on_menu_del(self):
        # remove menu entry
        self.menu.removeAction(self.repo_menu[self.repo])
        # remove from repo menu entry list
        self.repo_menu.pop(self.repo)
        # remove from repo list
        for r in self.repos:
            if self.repo == r["name"]:
                self.repos.remove(r)
        
        # and save the new list
        self.save_repos()
        # and finally select the default repo
        self.menu_ftc.trigger()
                    
    def on_menu_new(self):
        dialog = NewRepoDialog(self.mainWindow)
        dialog.new_repo.connect(self.on_new_repo)
        dialog.exec_()

    def on_new_repo(self, repo):
        # do some sanity checks
        if not repo["name"] or not len(repo["name"]): return
        if not repo["user"] or not len(repo["user"]): return
        if not repo["repo"] or not len(repo["repo"]): return

        if repo["name"] == "ftc": return

        # append repo to list of repos
        self.repos.append(repo)

        # create a menu entry
        menu_repo = self.menu.addAction(repo["name"])
        menu_repo.setCheckable(True)
        menu_repo.setActionGroup(self.group)
        menu_repo.setData( repo )
        menu_repo.triggered.connect(self.on_menu_select_repo)
        self.repo_menu[repo["name"]] = menu_repo

        self.save_repos()

    def select_repo(self, repo):
        self.repo = repo["name"]
        self.menu_del.setEnabled( repo["name"] != "ftc" )   # cannot delete default repo
        self.applist.set(repo)
        
    def on_menu_select_repo(self):
        self.select_repo(self.sender().data())

if __name__ == "__main__":
    class FtcGuiApplication(TouchApplication):
        def __init__(self, args):
            super().__init__(args)
            module = FtcGuiPlugin(self)
            self.exec_()
    FtcGuiApplication(sys.argv)
else:
    def createPlugin(launcher):
        return FtcGuiPlugin(launcher)

