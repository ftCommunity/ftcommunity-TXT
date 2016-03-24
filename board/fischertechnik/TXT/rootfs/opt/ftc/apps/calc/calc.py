#! /usr/bin/env python
# -*- coding: utf-8 -*-
# based on http://thecodeinn.blogspot.de/2013/07/tutorial-pyqt-calculator.html

import sys, os
from TxtStyle import *

num = 0.0
newNum = 0.0
sumAll = 0.0
operator = ""
 
opVar = False
sumIt = 0

class CalcWidget(QWidget):
            
    def __init__(self):
        QWidget.__init__(self)

        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        self.grid.setContentsMargins(0,0,0,0)
        
        self.line = QLineEdit("0")
        self.line.setReadOnly(True)
        self.line.setAlignment(Qt.AlignRight)
        self.grid.addWidget(self.line,0,0,1,4);

        zero = QPushButton("0")
        self.grid.addWidget(zero,5,0)

        one = QPushButton("1")
        self.grid.addWidget(one,4,0)

        two = QPushButton("2")
        self.grid.addWidget(two,4,1)

        three = QPushButton("3")
        self.grid.addWidget(three,4,2)

        four = QPushButton("4")
        self.grid.addWidget(four,3,0)

        five = QPushButton("5")
        self.grid.addWidget(five,3,1)

        six = QPushButton("6")
        self.grid.addWidget(six,3,2)

        seven = QPushButton("7")
        self.grid.addWidget(seven,2,0)

        eight = QPushButton("8")
        self.grid.addWidget(eight,2,1)

        nine = QPushButton("9")
        self.grid.addWidget(nine,2,2)

        point = QPushButton(".")
        self.grid.addWidget(point,5,1)
        point.clicked.connect(self.Point)

        sign = QPushButton("+/-")
        self.grid.addWidget(sign,5,2)
        sign.clicked.connect(self.Neg)

        c = QPushButton("C")
        self.grid.addWidget(c,1,2,1,2)
        c.clicked.connect(self.C)

        div = QPushButton("/")
        self.grid.addWidget(div,1,0)

        mult = QPushButton("*")
        self.grid.addWidget(mult,1,1)

        plus = QPushButton("+")
        self.grid.addWidget(plus,2,3)

        minus = QPushButton("-")
        self.grid.addWidget(minus,3,3)

        equal = QPushButton("=")
        self.grid.addWidget(equal,4,3,2,1)
        equal.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding);
        equal.clicked.connect(self.Equal)

        self.setLayout(self.grid)        
        

        nums = [zero,one,two,three,four,five,six,seven,eight,nine]
 
        ops = [sign,div,mult,minus,plus,equal]
 
        for i in nums:
            i.clicked.connect(self.Nums)
 
        for i in ops:
            i.setStyleSheet("color:#fcce04;")

        for i in ops[1:5]:
            i.clicked.connect(self.Operator)

            
    def Nums(self):
        global num
        global newNum
        global opVar

        sender = self.sender()
         
        newNum = int(sender.text())
        setNum = str(newNum)

        if opVar == False and self.line.text() != "0":
            self.line.setText(self.line.text() + setNum)
        else:
            self.line.setText(setNum)
            opVar = False

    def Operator(self):
        global num
        global opVar
        global operator
        global sumIt
 
        sumIt += 1
 
        if sumIt > 1:
            self.Equal()
 
        num = self.line.text()
 
        sender = self.sender()
 
        operator = sender.text()
         
        opVar = True
        
    def Point(self):
        global opVar
         
        if "." not in self.line.text():
            self.line.setText(self.line.text() + ".")
            
    def Neg(self):
        global num
         
        try:
            num = int(self.line.text())
             
        except:
            num = float(self.line.text())
      
        num = num - num * 2
 
        numStr = str(num)
         
        self.line.setText(numStr)
     
    def Equal(self):
        global num
        global newNum
        global sumAll
        global operator
        global opVar
        global sumIt
 
        sumIt = 0
 
        newNum = self.line.text()
 
        if operator == "+":
            sumAll = float(num) + float(newNum)
 
        elif operator == "-":
            sumAll = float(num) - float(newNum)
 
        elif operator == "/":
            sumAll = float(num) / float(newNum)
 
        elif operator == "*":
            sumAll = float(num) * float(newNum)
             
        self.line.setText(str(sumAll))
        opVar = True
        
    def C(self):
        global newNum
        global sumAll
        global operator
        global num
         
        self.line.setText("0")
 
        num = 0.0
        newNum = 0.0
        sumAll = 0.0
        operator = ""
    
class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        self.w = TxtWindow("Calc")
        self.w.setCentralWidget(CalcWidget())

        self.w.show() 
        self.exec_()        
 
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
