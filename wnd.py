
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, QDesktopWidget)
from PyQt5.QtGui import QPainter, QPen

class TranslucentWindow(QMainWindow):
    def ppaintEvent(self, event=None):
        painter = QPainter(self)

        painter.setOpacity(0.7)
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QPen(QtCore.Qt.white))   
        painter.drawRect(self.rect())

class BlendAccessibility(QApplication):

    def __init__(self, args):
        super(BlendAccessibility, self).__init__(args)

        self.ui = TranslucentWindow()
        self.ui.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.ui.setGeometry(QtCore.QRect(0, 0, 110, 51))
        self.ui.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.ui.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.pushButton = QPushButton(self.ui)
        self.pushButton.setGeometry(QtCore.QRect(10, 10, 90, 31))
        self.pushButton.setText("Finished")
        self.pushButton.clicked.connect(self.quit)

        qr = self.ui.frameGeometry()
        cp = self.desktop().availableGeometry().right()
        qr.moveRight(cp)
        self.ui.move(qr.topLeft())

        self.ui.show()

if __name__ == "__main__":
    import sys
    app = BlendAccessibility(sys.argv)
    sys.exit(app.exec_())