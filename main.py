# coding: utf-8

import sys
import os
from PyQt4 import QtGui, QtCore, uic

from lib.consts import BASE_DIR


class MainWindow(QtGui.QMainWindow):
  def __init__(self):
    QtGui.QMainWindow.__init__(self)
    uic.loadUi(os.path.join(BASE_DIR, 'resources/ui/main.ui'), self)

  def closeEvent(self, event):
    reply = QtGui.QMessageBox.question(self, 'Message',
        'Are you sure to quit?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    if reply == QtGui.QMessageBox.Yes:
      event.accept()
    else:
      event.ignore()


def main():
  app = QtGui.QApplication(sys.argv)
  win = MainWindow()
  win.show()
  sys.exit(app.exec_())


if __name__ == "__main__":
  main()
