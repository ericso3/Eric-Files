import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
import serial
import time
import numpy as np
from pylab import *
import matplotlib.pyplot as plt
from datetime import datetime
import os
from PIL import Image

# ser=serial.Serial()
# ser.baudrate = 57600
# ser.port = 'COM5'
# ser.timeout = 1

class UI_MainWindow(QtWidgets.QWidget):

    def __init__(self) -> None:
        super(UI_MainWindow, self).__init__()

        self.measure = Measurements()
        self.measure.measurement_sig.connect(self.change_ui)

        # self.measure.start()

        self.setObjectName("mainWindow")
        self.resize(800,600)

        horizontal_layout1 = QtWidgets.QHBoxLayout()
        horizontal_layout1.setObjectName("horizontal_layout1")

        vertical_layout1 = QtWidgets.QVBoxLayout()
        vertical_layout1.setObjectName("vertical_layout1")

        vertical_layout2 = QtWidgets.QVBoxLayout()
        vertical_layout2.setObjectName("vertical_layout2")

        operator = QtWidgets.QVBoxLayout()
        operator.setObjectName("operator")
        self.operator_label = QtWidgets.QLabel()
        self.operator_label.setObjectName("operator_label")
        operator.addWidget(self.operator_label)
        self.operator_edit = QtWidgets.QLineEdit()
        self.operator_edit.setObjectName("operator_edit")
        operator.addWidget(self.operator_edit)
        vertical_layout1.addLayout(operator)

        sample = QtWidgets.QVBoxLayout()
        sample.setObjectName("sample")
        self.sample_label = QtWidgets.QLabel()
        self.sample_label.setObjectName("sample_label")
        sample.addWidget(self.sample_label)
        self.sample_edit = QtWidgets.QLineEdit()
        self.sample_edit.setObjectName("sample_edit")
        sample.addWidget(self.sample_edit)
        vertical_layout1.addLayout(sample)

        filepath = QtWidgets.QVBoxLayout()
        filepath.setObjectName("filepath")
        self.filepath_label = QtWidgets.QLabel()
        self.filepath_label.setObjectName("filepath_label")
        filepath.addWidget(self.filepath_label)
        self.filepath_edit = QtWidgets.QLineEdit()
        self.filepath_edit.setObjectName("filepath_edit")
        filepath.addWidget(self.filepath_edit)
        vertical_layout1.addLayout(filepath)

        btn_measure = QtWidgets.QPushButton()
        btn_measure.setEnabled(True)
        btn_measure.setObjectName("btn_measure")
        btn_measure.clicked.connect(self.click)
        vertical_layout1.addWidget(btn_measure)

        sample_measured = QtWidgets.QVBoxLayout()
        sample_measured.setObjectName("sample_measured")
        self.sample_measuredLabel = QtWidgets.QLabel()
        self.sample_measuredLabel.setObjectName("sample_measuredLabel")
        sample_measured.addWidget(self.sample_measuredLabel)
        self.sample_measuredText = QtWidgets.QLabel()
        self.sample_measuredText.setObjectName("sample_measuredText")
        sample_measured.addWidget(self.sample_measuredText)
        vertical_layout2.addLayout(sample_measured)

        rs_measured = QtWidgets.QVBoxLayout()
        rs_measured.setObjectName("rs_measured")
        self.rs_measuredLabel = QtWidgets.QLabel()
        self.rs_measuredLabel.setObjectName("rs_measuredLabel")
        rs_measured.addWidget(self.rs_measuredLabel)
        self.rs_measuredText = QtWidgets.QLabel()
        self.rs_measuredText.setObjectName("rs_measuredText")
        rs_measured.addWidget(self.rs_measuredText)
        vertical_layout2.addLayout(rs_measured)

        rsh_measured = QtWidgets.QVBoxLayout()
        rsh_measured.setObjectName("rsh_measured")
        self.rsh_measuredLabel = QtWidgets.QLabel()
        self.rsh_measuredLabel.setObjectName("rsh_measuredLabel")
        rsh_measured.addWidget(self.rsh_measuredLabel)
        self.rsh_measuredText = QtWidgets.QLabel()
        self.rsh_measuredText.setObjectName("rsh_measuredText")
        rsh_measured.addWidget(self.rsh_measuredText)
        vertical_layout2.addLayout(rsh_measured)


        div = QtWidgets.QVBoxLayout()
        self.div_graph = QtWidgets.QLabel()
        # self.div_graph_pix = QtGui.QPixmap('C:/Users/eso/Documents/Python Scripts/Python Project DIV/Test')
        self.div_graph_pix = QtGui.QPixmap(None)
        self.div_graph.resize(688, 473)
        self.div_graph.setPixmap(self.div_graph_pix)
        self.div_graph.setObjectName("div_graph")
        div.addWidget(self.div_graph)
        vertical_layout2.addLayout(div)

        horizontal_layout1.addLayout(vertical_layout1)
        horizontal_layout1.addLayout(vertical_layout2)

        self.setLayout(horizontal_layout1)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("mainWindow", "DIV Testing Window"))
        self.operator_label.setText(_translate("mainWindow", "Operator:"))
        self.sample_label.setText(_translate("mainWindow", "Sample:"))
        self.filepath_label.setText(_translate("mainWindow", "Filename:"))
        btn_measure.setText(_translate("mainWindow", "Measure"))
        self.sample_measuredLabel.setText(_translate("mainWindow", "Measured Sample: "))
        self.sample_measuredText.setText(_translate("mainWindow", "Waiting for Measurement Data"))
        self.rs_measuredLabel.setText(_translate("mainWindow", "Measured Rs: "))
        self.rs_measuredText.setText(_translate("mainWindow", "Waiting for Measurement Data"))
        self.rsh_measuredLabel.setText(_translate("mainWindow", "Measured Rsh: "))
        self.rsh_measuredText.setText(_translate("mainWindow", "Waiting for Measurement Data"))
        self.show()

    def change_ui(self, measurements: str) -> None:
        _translate = QtCore.QCoreApplication.translate
        print(y)
        self.rs_measuredText.setText(_translate("mainWindow", measurements))
        self.sample_measuredText.setText(_translate("mainWindow", "Waiting for Measurement Data"))

    def click(self) ->None :
        print(n)
        self.measure.start()

class Measurements(QThread):

    measurement_sig = pyqtSignal(str)

    def __init__(self) -> None:
        super(Measurements, self).__init__()

    def take_measurement(self) -> float:

        rs_min = 2.5
        return rs_min

    def run(self) -> None:
        print(y)
        rs_min = str(self.take_measurement())
        print(yes1)
        self.measurement_sig.emit(rs_min)
        print(yes2)
        time.sleep(2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = UI_MainWindow()
    sys.exit(app.exec_())





