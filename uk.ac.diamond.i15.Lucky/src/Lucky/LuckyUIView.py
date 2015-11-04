'''
Created on 3 Nov 2015

@author: wnm24546
'''

from PyQt4 import QtCore, QtGui
from Lucky import LuckyUIModel

class MainWindow(QtGui.QWidget):    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.luckyAppModel = LuckyUIModel.MainWindowModel()
        
        self.setWindowTitle('Lucky')
        #self.SetWindowIcon(QtGui.QIcon('SomeLocalIcon.png'))
        
        #Control buttons
        self.runBtn = QtGui.QPushButton('Run')
        self.runBtn.clicked.connect(self.runBtnPressed)
        
        self.stopBtn = QtGui.QPushButton('Stop')
        self.stopBtn.clicked.connect(self.stopBtnPressed)
        
        quitBtn = QtGui.QPushButton('Quit')
        quitBtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        
        #Layout
        hBoxLayout = QtGui.QHBoxLayout()
        hBoxLayout.addWidget(self.runBtn)
        hBoxLayout.addWidget(self.stopBtn)
        hBoxLayout.addWidget(quitBtn)
        
        self.updateWidgetStates()
        self.setLayout(hBoxLayout)
        
    def runBtnPressed(self):
    	self.luckyAppModel.runLuckyCalcs()
    	self.updateWidgetStates()
    
    def stopBtnPressed(self):
    	self.luckyAppModel.stopLuckyCalcs()
    	self.updateWidgetStates()
    
    def updateWidgetStates(self):
    	self.runBtn.setEnabled(self.luckyAppModel.runEnabled)
    	self.stopBtn.setEnabled(self.luckyAppModel.stopEnabled)