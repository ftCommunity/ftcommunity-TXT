#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, os
from TxtStyle import *

class LicenseDialog(TxtDialog):
    def __init__(self,title,parent):
        TxtDialog.__init__(self, title, parent)
        
        txt = QTextEdit()
        txt.setReadOnly(True)
        
        font = QFont()
        font.setPointSize(16)
        txt.setFont(font)
    
        # load gpl from disk
        name = os.path.dirname(os.path.realpath(__file__)) + "/gpl.txt"
        text=open(name).read()
        txt.setPlainText(text)

        self.setCentralWidget(txt)

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        self.w = TxtWindow("About")

        self.vbox = QVBoxLayout()
        
        # and add some text
        self.txt = QLabel("Fischertechnik TXT firmware "
                          "community edition V0.0.\n\n"
                          "(c) 2016 the ft:community")
        self.txt.setObjectName("smalllabel")
        self.txt.setWordWrap(True)
        self.txt.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.txt)

        self.lic = QPushButton("License")
        self.lic.clicked.connect(self.show_license)
        self.vbox.addWidget(self.lic)

        self.w.centralWidget.setLayout(self.vbox)

        self.w.show()
        self.exec_()        
 
    def show_license(self):
        dialog = LicenseDialog("GPL", self.w)
        dialog.exec_()
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
