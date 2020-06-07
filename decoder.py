# -*- coding: cp1252 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_beaconhex
import ui.ui_map
import ui.ui_progress

from constants import *
from webmap import google_map,blank,google_mapbak
from writebch import getFiveCharChecksum
import decodehex2
from Gen2secondgen import SecondGen

import definitions
import sys

VERSION='Beacon Decoder Windows Version ' + WINDOWSVERSION

class MapDlg(QDialog, ui.ui_map.Ui_Dialog):
    def __init__(self, parent=None):
        super(MapDlg, self).__init__(parent)
        msize = '15 digit beacon UIN'
        self.setupUi(self)
        self._lat = 0
        self._long = 0
        self.currentframe = self.mapWebView.page().currentFrame()
        self.mapWebView.loadFinished.connect(self.handleLoadFinished)

    def set_code(self, h):
        self.mapWebView.setHtml(h)

    def handleLoadFinished(self, ok):
        if ok:
            self.get_marker_coordinates()


    def get_marker_coordinates(self):
        self.setWindowTitle("Latitude: {}   Longitude: {}".format(self._lat, self._long))




class Progress(QDialog, ui.ui_progress.Ui_Dialog):
    def __init__(self, parent=None):
        super(Progress, self).__init__(parent)
        self.setupUi(self)




    def updateProgress(self, val):
        self.progressBar.setValue(val)
        if val > 99:

            self.close()




class MainWindow(QMainWindow, ui.ui_beaconhex.Ui_BeaconDecoder):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self._mtype = 'Hex15'
        self.setupUi(self)


        self.settings = QSettings('settings.ini', QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)    # File only, not registry
        self.updateUi()


    def closeEvent(self, event):
        event.accept()
        sys.exit()


    @pyqtSignature("")
    def on_pushButton_clicked(self):
        self.dialog = MapDlg(self)
        self.dialog.show()
        if self._beacon.has_loc():

            self.dialog._lat = unicode(self._beacon.location[0])
            self.dialog._long = unicode(self._beacon.location[1])
            h = google_map.format(self.dialog._lat,self.dialog._long)
            #h = google_map
            print(h)

            #h.format(lat=self.dialog._lat,long=self.dialog._long)
        else:
            h = blank
        self.dialog.set_code(h)
        if self.dialog.exec_():
            self.dialog.close()




    @pyqtSignature("QString")
    def on_hexLineEdit_textChanged(self):
        c = self.hexLineEdit.cursorPosition()
        t = unicode(self.hexLineEdit.text()).upper()
        self.hexLineEdit.setText(t)
        self.hexLineEdit.setCursorPosition(c)
        self.hexLineEdit.setSelection(c, 1)
        hexcode = unicode(self.hexLineEdit.text())
        self._lasthex = hexcode



        try:
            self._beacon = decodehex2.Beacon(hexcode)
            #self._beacon.processHex(hexcode)
            ctry = self._beacon.get_country()

            self.tableWidget.clear()
            if len(hexcode)==15:
                checksum=(getFiveCharChecksum(hexcode.upper()))
                self._beacon.tablebin.append(('','','',str(checksum)))

            for n, lrow in enumerate(self._beacon.tablebin):
                for m, item in enumerate(lrow):
                    if type(item) is  str:
                        newitem = QTableWidgetItem(item)
                        newitem.setFlags(Qt.ItemIsEnabled)
                        self.tableWidget.setItem(n, m, newitem)


            self.tableWidget.setHorizontalHeaderLabels(['Bit range',
                                                        'Bit value',
                                                        'Name',
                                                        'Decoded'])
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeRowsToContents()

        except decodehex2.HexError as e: #Gen2.Gen2Error as e:
            self.tableWidget.clear()
            qb = QMessageBox.critical(self, e.value, e.message)



        finally:
            pass





    def pickHex(self, item):
        s = unicode(item.text())
        # QMessageBox.information(self, "ListWidget", "You clicked: "+s)
        self.hexLineEdit.setText(s.split()[1])


    def updateUi(self):
        self.statusBar().showMessage('Ready')
        #self._beacon = decodehex2.Beacon()
        # Create main menu
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)
        fileMenu = mainMenu.addMenu('&File')
        helpMenu = mainMenu.addMenu('&Help')
        # Add open file
        openButton = QAction('&Open', self)
        openButton.setShortcut('Ctrl+O')
        openButton.setStatusTip('Open a file')
        openButton.setStatusTip('Select file with hexidecimal codes')
        openButton.triggered.connect(self.file_dialog)
        # Add save file
        saveButton1 = QAction('&Save generation FGB', self)
        saveButton1.setShortcut('Ctrl+1')
        saveButton1.setStatusTip('Export decoded results for FGB hex')
        saveButton1.setStatusTip('Export decoded results for FGB hex')
        saveButton1.triggered.connect(self.filesave_dialogGen1)

        saveButton2 = QAction('&Save generation SGB', self)
        saveButton2.setShortcut('Ctrl+2')
        saveButton2.setStatusTip('Export decoded results for SGB hex')
        saveButton2.setStatusTip('Export decoded results for SGB hex')
        saveButton2.triggered.connect(self.filesave_dialogGen2)

        # Add exit button
        exitButton = QAction('&Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)

        # Add about button
        aboutButton = QAction('&About',self)
        aboutButton.setShortcut('Ctrl+A')
        aboutButton.setStatusTip('Version information')
        aboutButton.triggered.connect(self.aboutVersion)



        fileMenu.addAction(openButton)
        fileMenu.addAction(saveButton1)
        fileMenu.addAction(saveButton2)
        fileMenu.addAction(exitButton)
        helpMenu.addAction(aboutButton)


        hexRe = QRegExp(r"[0-9a-fA-F_]{"+'30'+"}")
        self.hexLineEdit.setText('')
        self.hexLineEdit.setValidator(
            QRegExpValidator(hexRe, self))
        self.hexlist.itemClicked.connect(self.pickHex)
        self.hexlist.currentItemChanged.connect(self.pickHex)


    def aboutVersion(self):
        qb = QMessageBox.about(self, 'Beacon Decoder', VERSION)


    def filesave_dialogGen1(self):
        fd = QFileDialog(self)
        self.filesave = fd.getSaveFileName(self, "Export decode file", "", 'Save export as csv (*.csv)')

        if self.filesave != '':

            self.threadclass = ThreadClassSaveGen1(self.filename, self.filesave)
            self.threadclass.start()
            self.connect(self.threadclass, SIGNAL('EXPORT'), self.threadclass.updateProgress)

    def filesave_dialogGen2(self):
        fd = QFileDialog(self)
        self.filesave = fd.getSaveFileName(self, "Export decode file", "", 'Save export as csv (*.csv)')

        if self.filesave != '':

            self.threadclass = ThreadClassSaveGen2(self.filename, self.filesave)
            self.threadclass.start()
            self.connect(self.threadclass, SIGNAL('EXPORT'), self.threadclass.updateProgress)


    def file_dialog(self):
        fd = QFileDialog(self)
        self.filename = fd.getOpenFileName()
        from os.path import isfile
        if isfile(self.filename):
            self.tableWidget.clear()
            self.hexlist.clear()
            self.threadclass = ThreadClassOpen(self.filename, self.hexlist)
            self.threadclass.start()
            self.connect(self.threadclass, SIGNAL('LOAD'), self.threadclass.updateProgress)




class ThreadClassOpen(QThread):
    def __init__(self, filename, hexlist, parent=None):
        super(ThreadClassOpen, self).__init__(parent)

        self.filename = filename
        self.hexlist = hexlist
        self.dialog = Progress()
        self.dialog.show()


    def run(self):
        self.emit(SIGNAL('LOAD'), 50)
        hexcodes = open(self.filename, 'r')

        content = ['{num:05d}  {h}'.format(num=n+1, h=x.strip('\n')) for n,x in enumerate(hexcodes.readlines())]
        self.emit(SIGNAL('LOAD'), 95)
        self.hexlist.addItems(content)
        self.emit(SIGNAL('LOAD'), 100)

        if self.dialog.exec_():
            self.dialog.close()

    def updateProgress(self, val):
        self.dialog.updateProgress(val)




class ThreadClassSaveGen1(QThread):
    def __init__(self, filename, filesave, parent=None):
        super(ThreadClassSaveGen1, self).__init__(parent)
        self.filename = filename
        self.filesave = filesave
        self.dialog = Progress()
        self.dialog.show()


    def run(self):
        count = 0
        thefile = open(self.filename, 'rb')
        while 1:
            buffer = thefile.read(8192*1024)
            if not buffer: break
            count += buffer.count('\n')
        thefile.close()
        hexcodes = open(self.filename)
        decoded = open(self.filesave, 'w')



        i = 0
        decoded.write("""Input Message,Message Type,Self Test,Self Test,15 Hex ID,BCH-2 match,Protocol Type,Test Beacon,Beacon Type,TAC,Country Code,Country Name,Message protocol,Position Source,Course Lat,Course Long,Final Lat,Final Long,Fixed Bits\n""")

        for line in hexcodes.readlines():
            i += 1
            #print i, count, i/float(count),i/float(count)*100
            self.emit(SIGNAL('EXPORT'), i/float(count)*100)
            line = str(line.strip())
            decoded.write('{h},'.format(h=str(line)))
            try:
                c = decodehex2.Beacon(str(line))
                if c.gentype=='first' :
                    c = decodehex2.BeaconFGB(str(line))
                    if str(c.location[0]).find('Error') != -1:
                        finallat = courselat = 'error'
                    elif str(c.location[0]).find('Default') != -1:
                        finallat = courselat = 'default'
                    else:
                        finallat = c.location[0]
                        courselat = c.courseloc[0]
                    if str(c.location[1]).find('Error') != -1:
                        finallong = courselong = 'error'
                    elif str(c.location[1]).find('Default') != -1:
                        finallong = courselong = 'default'
                    else:
                        finallong = c.location[1]
                        courselong = c.courseloc[1]

                    selftest=c.testmsg()
                    if 'Self-test' in selftest:
                        s='True'
                    else:
                        s='False'
                    decoded.write('{},'.format(c.getmtype()))
                    decoded.write('{},'.format(s))
                    decoded.write('{},'.format(selftest))
                    decoded.write('{},'.format(c.hexuin()))
                    decoded.write('{},'.format(c.bch2match()))
                    decoded.write('{},'.format(c.protocolflag()))
                    btype=c.btype()
                    if 'Test' in btype:
                        t='True'
                    else:
                        t='False'
                    decoded.write('{},'.format(t))
                    decoded.write('{},'.format(btype))

                    decoded.write('{},'.format(c.gettac()))
                    decoded.write('{},'.format(c.get_mid()))
                    decoded.write('{},'.format(c.get_country()))
                    decoded.write('{},'.format(c.loctype()))
                    decoded.write('{},'.format(c.getencpos()))
                    decoded.write('{},'.format(courselat))
                    decoded.write('{},'.format(courselong))
                    decoded.write('{},'.format(finallat))
                    decoded.write('{},'.format(finallong))
                    decoded.write('{},'.format(c.fbits()))
                else:
                    decoded.write('Not an FGB long message')


            except decodehex2.HexError as e:

                decoded.write(e.value)




            decoded.write('\n')

        decoded.close()
        self.emit(SIGNAL('EXPORT'), 100)



    def updateProgress(self, val):
        self.dialog.updateProgress(val)


class ThreadClassSaveGen2(QThread):
    def __init__(self, filename, filesave, parent=None):
        super(ThreadClassSaveGen2, self).__init__(parent)
        self.filename = filename
        self.filesave = filesave
        self.dialog = Progress()
        self.dialog.show()


    def run(self):
        count = 0
        thefile = open(self.filename, 'rb')
        while 1:
            buffer = thefile.read(8192*1024)
            if not buffer: break
            count += buffer.count('\n')
        thefile.close()
        hexcodes = open(self.filename)
        decoded = open(self.filesave, 'w')
        i = 0
        decoded.write("""Input Message,23 Hex ID,BCH match,self-test, message protocol,Type Approval, Country code,latitude,longitude\n""")

        for line in hexcodes.readlines():
            i += 1
            #print i, count, i/float(count),i/float(count)*100
            self.emit(SIGNAL('EXPORT'), i/float(count)*100)
            line = str(line.strip())
            decoded.write('{h},'.format(h=str(line)))
            try:
                c = decodehex2.Beacon(str(line))
                if c.gentype!='first':
                    c = SecondGen(str(line))
                    decoded.write('{},'.format(c.hexuin()))
                    decoded.write('{},'.format(c.bchmatch()))
                    decoded.write('{},'.format(c.testmsg()[0]))
                    decoded.write('{},'.format(c.testmsg()[1]))
                    decoded.write('{},'.format(c.gettac()))
                    decoded.write('{},'.format(c.get_country()))
                    decoded.write('{},'.format(c.location[0]))
                    decoded.write('{},'.format(c.location[1]))

                else:
                    decoded.write('Not an SGB')

            except decodehex2.HexError as e:
                decoded.write(e.value)

            decoded.write('\n')
        decoded.close()
        self.emit(SIGNAL('EXPORT'), 100)

    def updateProgress(self, val):
        self.dialog.updateProgress(val)







if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
