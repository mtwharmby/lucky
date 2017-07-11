'''
Created on 3 Nov 2015

@author: wnm24546
'''

import sys
from PyQt4 import QtGui

# import Lucky.LuckyUIView
from Lucky.AllViews import MainView

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
#     lucky0 = Lucky.LuckyUIView.MainWindow()
#     lucky0.show()
    lucky = MainView()
    lucky.show()
    sys.exit(app.exec_())