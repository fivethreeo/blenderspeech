
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, QDesktopWidget, QLabel, QGridLayout, QLineEdit, QTextEdit)
from PyQt5.QtGui import QPainter, QPen
from speech_recognition import Recognizer, Microphone, WaitTimeoutError, UnknownValueError, RequestError
import time
import re

def get_entries(entries, alt={}, mult=1):
    out = []
    sre = ''
    prob = 1/len(entries)
    for entry in entries:
        out = out + [(entry, alt.get(entry, prob*mult))]
        sre = sre + entry + '|'
    print (out)
    return re.compile('^(%s)' % sre[0:-1]), out

class SpeechRecogniserThread(QtCore.QThread):
    # Create the signal
    recognized = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(SpeechRecogniserThread, self).__init__(parent)

    def run(self):

        import pyautogui

        command_mode = 'waiting'
        keys_down = []

        recognizer = Recognizer()
        microphone = Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening

            while True:
                try:  # listen for 1 second, then check again if the stop function has been called
                    audio = recognizer.listen(source, 1)

                    try:
                        said = ''
                        if command_mode == 'direction':
                            entries = ['front to back', 'side to side', 'up and down']
                            entries_re, entries_kv = get_entries(entries)
                            said = recognizer.recognize_sphinx(audio, keyword_entries=entries_kv)
                            m = entries_re.match(said)
                            if m: 
                                print ("%s\n" % m.group(0))
                                if m.group(0) == 'side to side':
                                    pyautogui.press('x')
                                if m.group(0) == 'front to back':
                                    pyautogui.press('y')
                                if m.group(0) == 'up and down':
                                    pyautogui.press('z')
                                
                                command_mode = 'to_waiting'

                        if command_mode == 'modify':
                            entries = ['big letter', 'control', 'modify']
                            entries_re, entries_kv = get_entries(entries)
                            said = recognizer.recognize_sphinx(audio, keyword_entries=entries_kv)
                            m = entries_re.match(said)
                            if m: 
                                cmd = m.group(0)
                                if cmd == 'big letter':
                                    pyautogui.keyDown('shift')
                                    keys_down.append('shift')
                                if cmd == 'control':
                                    pyautogui.keyDown('ctrl')
                                    keys_down.append('ctrl')
                                if cmd == 'modify':
                                    pyautogui.keyDown('alt')
                                    keys_down.append('ctrl')
                                print ("%s\n" % m.group(0))
                                command_mode = 'to_waiting'

                        if command_mode == 'control':
                            entries = ['direction', 'modify']
                            entries_re, entries_kv = get_entries(entries)
                            said = recognizer.recognize_sphinx(audio, keyword_entries=entries_kv)
                            m = entries_re.match(said)
                            if m: 
                                print ("%s\n" % m.group(0))
                                command_mode = m.group(0)

                        if command_mode == 'waiting':
                            entries = ['control', 'stop holding keys']
                            entries_re, entries_kv = get_entries(entries)
                            said = recognizer.recognize_sphinx(audio, keyword_entries=entries_kv)
                            m = entries_re.match(said)
                            if m: 
                                print ("%s\n" % m.group(0))
                                if m.group(0) == 'stop holding keys':
                                    for key in keys_down:
                                        pyautogui.keyUp(key)
                                else:
                                    command_mode = 'control'

                        if command_mode == 'to_waiting':
                            command_mode = 'waiting'

                        print("Sphinx thinks you said " + said)
                        time.sleep(1)
                    except UnknownValueError:
                        print("Sphinx could not understand audio")
                    except RequestError as e:
                        print("Sphinx error; {0}".format(e))

                except WaitTimeoutError:  # listening timed out, just try again
                    pass

class Example(QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
        
    def initUI(self):
        
        title = QLabel('<strong>Title</strong>')
        '''
        titleEdit = QPushButton('Shift')
        titleEdit.setEnabled(False)
        titleEdit.setDown(True)
        '''
        ttitleEdit = QLabel('Shift')
        ttitleEdit2 = QLabel('Shift')
        ttitleEdit3 = QLabel('Shift')
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)

        grid.addWidget(ttitleEdit, 1, 1)

        grid.addWidget(ttitleEdit2, 1, 2)

        
        grid.addWidget(ttitleEdit3, 1, 3)

        
        self.setLayout(grid) 
        self.show()

class TranslucentWindow(QMainWindow):
    def paintEvent(self, event=None):
        painter = QPainter(self)

        painter.setOpacity(0.7)
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QPen(QtCore.Qt.white))   
        painter.drawRect(self.rect())
        
class BlendAccessibility(QApplication):

    def __init__(self, args):
        super(BlendAccessibility, self).__init__(args)
        self.initUI()

    def initUI(self):
        
        self.ui = TranslucentWindow()
        self.ui.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.ui.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.ui.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.ui.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        '''
        self.pushButton = QPushButton(self.ui)
        self.pushButton.setGeometry(QtCore.QRect(0, 0, 90, 31))
        self.pushButton.setText("Finished")
        self.pushButton.clicked.connect(self.quit)
        '''

        ex = Example()

        self.ui.setCentralWidget(ex)
        self.speechthread = SpeechRecogniserThread()
        self.speechthread.start()
        
        self.ui.show()

        qr = self.ui.frameGeometry()
        cp = self.desktop().availableGeometry().right()
        qr.moveTop(0)
        qr.moveRight(cp-100)
        self.ui.move(qr.topLeft())

    def recognized(self, action):
        print (action)


if __name__ == "__main__":
    import sys
    app = BlendAccessibility(sys.argv)
    sys.exit(app.exec_())