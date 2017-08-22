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

ser = serial.Serial()
ser.baudrate = 57600
ser.port = 'COM5'
ser.timeout = 1


class UI_Main(QtWidgets.QWidget):
    def __init__(self, MainWindow):
        super(UI_Main, self).__init__()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.DIV_graph_pix = QtGui.QPixmap(None)
        self.DIV_graph = QtWidgets.QLabel(self.centralwidget)
        self.DIV = vbox(self.centralwidget)
        self.Rsh_measuredText = QtWidgets.QLabel(self.centralwidget)
        self.Rsh_measuredLabel = QtWidgets.QLabel(self.centralwidget)
        self.Rsh_measured = hbox(self.centralwidget)
        self.Rs_measuredText = QtWidgets.QLabel(self.centralwidget)
        self.Rs_measuredLabel = QtWidgets.QLabel(self.centralwidget)
        self.Rs_measured = hbox(self.centralwidget)
        self.sample_measuredText = QtWidgets.QLabel(self.centralwidget)
        self.sample_measuredLabel = QtWidgets.QLabel(self.centralwidget)
        self.sample_measured = hbox(self.centralwidget)
        self.btn_measure = QtWidgets.QPushButton(self.centralwidget)
        self.buttons_layout = vbox(self.centralwidget)
        self.filepath_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.filepath_label = QtWidgets.QLabel(self.centralwidget)
        self.filepath = vbox(self.centralwidget)
        self.sample_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.sample_label = QtWidgets.QLabel(self.centralwidget)
        self.sample = vbox(self.centralwidget)
        self.operator_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.operator_label = QtWidgets.QLabel(self.centralwidget)
        self.operator = vbox(self.centralwidget)
        self.verticalLayout2 = vbox(self.centralwidget)
        self.verticalLayout1 = vbox(self.centralwidget)
        self.horizontalLayout1 = hbox(self.centralwidget)

        self.setupUI(parent)

        self.retranslateUI(parent)
        self.btn_measure.clicked.connect(self.UpdateUI)
        self.show()

    def setupUI(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.centralwidget.setObjectName("centralwidget")

        self.horizontalLayout1.setObjectName("horizontalLayout1")

        self.verticalLayout1.setObjectName("verticalLayout1")

        self.verticalLayout2.setObjectName("verticalLayout2")

        # if data['type'] == 'value':
        #     self.value = QtWidgets.QSpinBox()
        #     self.value.setMinimum(data['min'])
        #     self.value.setMaximum(data['max'])
        #     self.value.valueChanged.connect(self.valueChanged)
        #     self.value.setValue(data['value'])
        #     hbox(centralwidget)
        # elif data['type'] == 'text':
        #     self.line = QtWidgets.QLineEdit()
        #     self.line.textChanged.connect(self.textChanged)
        #     self.line.setText(data['text'])
        #     hbox.addWidget(self.line)
        # elif data['type'] == 'checkbox':
        #     self.check = QtWidgets.QCheckBox()
        #     self.check.stateChanged.connect(self.checkstateChanged)
        #     self.check.setCheckState(data['state'])
        #     hbox.addWidget(self.check)

        self.operator.setObjectName("operator")
        self.operator_label.setObjectName("operator_label")
        self.operator.addWidget(self.operator_label)
        self.operator_edit.setObjectName("operator_edit")
        self.operator.addWidget(self.operator_edit)
        self.verticalLayout1.addLayout(self.operator)

        self.sample.setObjectName("sample")
        self.sample_label.setObjectName("sample_label")
        self.sample.addWidget(self.sample_label)
        self.sample_edit.setObjectName("sample_edit")
        self.sample.addWidget(self.sample_edit)
        self.verticalLayout1.addLayout(self.sample)

        self.filepath.setObjectName("filepath")
        self.filepath_label.setObjectName("filepath_label")
        self.filepath.addWidget(self.filepath_label)
        self.filepath_edit.setObjectName("filepath_edit")
        self.filepath.addWidget(self.filepath_edit)
        self.verticalLayout1.addLayout(self.filepath)

        self.buttons_layout.setObjectName("buttons_layout")
        self.btn_measure.setEnabled(True)
        self.btn_measure.setObjectName("btn_measure")
        self.buttons_layout.addWidget(self.btn_measure)
        self.verticalLayout1.addLayout(self.buttons_layout)

        self.sample_measured.setObjectName("sample_measured")
        self.sample_measuredLabel.setObjectName("sample_measuredLabel")
        self.sample_measured.addWidget(self.sample_measuredLabel)
        self.sample_measuredText.setObjectName("sample_measuredText")
        self.sample_measured.addWidget(self.sample_measuredText)
        self.verticalLayout2.addLayout(self.sample_measured)

        self.Rs_measured.setObjectName("Rs_measured")
        self.Rs_measuredLabel.setObjectName("Rs_measuredLabel")
        self.Rs_measured.addWidget(self.Rs_measuredLabel)
        self.Rs_measuredText.setObjectName("Rs_measuredText")
        self.Rs_measured.addWidget(self.Rs_measuredText)
        self.verticalLayout2.addLayout(self.Rs_measured)

        self.Rsh_measured.setObjectName("Rsh_measured")
        self.Rsh_measuredLabel.setObjectName("Rsh_measuredLabel")
        self.Rsh_measured.addWidget(self.Rsh_measuredLabel)
        self.Rsh_measuredText.setObjectName("Rsh_measuredText")
        self.Rsh_measured.addWidget(self.Rsh_measuredText)
        self.verticalLayout2.addLayout(self.Rsh_measured)

        self.DIV_graph.resize(688, 473)
        self.DIV_graph.setPixmap(self.DIV_graph_pix)
        self.DIV_graph.setObjectName("DIV_graph")
        self.DIV.addWidget(self.DIV_graph)
        self.verticalLayout2.addLayout(self.DIV)

        self.horizontalLayout1.addLayout(self.verticalLayout1)
        self.horizontalLayout1.addLayout(self.verticalLayout2)

        self.setCentralWidget(self.centralwidget)

    def retranslateUI(self, MainWindow: object):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DIV Testing Window"))
        self.operator_label.setText(_translate("MainWindow", "Operator:"))
        self.sample_label.setText(_translate("MainWindow", "Sample:"))
        self.filepath_label.setText(_translate("MainWindow", "Filename:"))
        self.btn_measure.setText(_translate("MainWindow", "Measure"))
        self.sample_measuredLabel.setText(_translate("MainWindow", "Measured Sample: "))

    def UpdateUI(self):
        print(3)
        self.getMeasurement = BeginMeasurements()
        print(str(type(self.getMeasurement)))
        print(2)
        self.sample_measuredText.setText(self.sample_edit.text())
        print(4)
        self.getMeasurement.measurement.connect(self.change)
        self.getMeasurement.finished.connect(self.done)
        self.getMeasurement.start()
        # self.Rs_measuredText.setText(self.getMeasurement.message_to_listsubmissions.connect(Rs_min))
        # print(5)
        # self.Rsh_measuredText.setText(self.getMeasurement.message_to_listsubmissions.connect(Rsh_mean))
        # print(6)
        # self.DIV_graph_pix = QtGui.QPixmap(self.getMeasurement.message_to_listsubmissions.connect(fig))
        # print(7)
        # self.Rs_measuredText.setText("hi")
        # print(5)
        # self.Rsh_measuredText.setText("no")
        # print(6)
        # self.DIV_graph_pix = QtGui.QPixmap("C:\\Users\\eso\\Documents\\Python Scripts\\Python Project DIV\\Test.png")
        # # print(7)
        # self.DIV_graph.setPixmap(self.DIV_graph_pix)
        print(8)

    def change(self):
        print(9)
        _translate = QtCore.QCoreApplication.translate
        print(10)
        self.Rs_measuredText.setText(_translate("MainWindow", "test"))
        # for i in range(list):
        #     if i == 0:
        #         self.Rs_measuredText.setText(list[i])
        #         print(rs)
        #     elif i ==1:
        #         self.Rsh_measuredText.setText(list[i])
        #         print(rsh)
        #     elif i == 2:
        #         self.DIV_graph_pix = QtGui.QPixmap(list[i])
        #         self.DIV_graph.setPixmap(self.DIV_graph_pix)
        #         print(fig)

    def done(self):
        """
        Show the message that fetching posts is done.
        Disable Stop button enable the Start one and reset progress bar to 0.
        :return:
        """
        QMessageBox.information(self, "Done!", "Done fetching posts!")


class BeginMeasurements(QThread):
    measurement = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super(BeginMeasurements, self).__init__(parent)
        # QThread.__init__(self)
        # self.measurement.connect()
        # self.finished.connect()

    #
    # def __del__(self):
    #     self.wait()

    def TakeMeasurement(self):
        #         def WriteToFile(message, OutputFile):
        #             file = open(OutputFile + '.txt', 'a')
        #             file.write(message)
        #             file.close()
        #
        #         rootdir = 'C:\\Users\\python\\Desktop\\DIV Results'
        #         savename = input("Please enter a unique name to save the file: ")
        #         # savename = 'testing'
        #         timestamp = time.time()
        #         date_time = str(datetime.now())
        #         first_time_seconds = str(math.floor(timestamp))
        #
        #         start_current = str(5)
        #         stop_current = str(4)
        #         current_step = str(-1e-1)
        #         start_current_shunt = str(0.00011)
        #         stop_current_shunt = str(0.00001)
        #         current_step_shunt = str(-1e-5)
        #         voltage_protection = str(10)
        #         number_steps = str(11)  # 21 or fewer
        #         number_steps_int = int(number_steps)
        #         source_delay = str(0.01)  # choose 10 ms for this to reduce heating
        #         timeout_sec = str(float(number_steps) * float(source_delay) + 1)
        #
        #         ser
        #         ser.open()
        #
        #         ser.write(str.encode('*IDN?\n'))
        #         ident = ser.read(200)
        #         print(ident)
        #
        #         ser.reset_input_buffer()
        #         ser.reset_output_buffer()
        #
        #         time.sleep(0.001)
        #
        #         ser.write(str.encode(':ROUT:TERM FRON\n'))
        #         ser.write(str.encode(':ROUT:TERM?\n'))
        #         print(ser.read(10))
        #
        #         ser.write(str.encode(':SENS:FUNC:CONC OFF\n'))
        #         ser.write(str.encode(':SYST:RSEN ON\n'))  # chooses 4wire measurement setting
        #         ser.write(str.encode(':SOUR:FUNC CURR\n'))
        #         ser.write(str.encode(":SENS:FUNC 'VOLT:DC'\n"))
        #         ser.write(str.encode(':SENS:VOLT:PROT ' + voltage_protection + '\n'))
        #         ser.write(str.encode(':SOUR:CURR:START ' + start_current_shunt + '\n'))  # start current
        #         ser.write(str.encode(':SOUR:CURR:STOP ' + stop_current_shunt + '\n'))  # stop current
        #         ser.write(str.encode(':SOUR:CURR:STEP ' + current_step_shunt + '\n'))  # increment
        #         ser.write(str.encode(':SOUR:CURR:MODE SWE\n'))
        #         ser.write(str.encode(':SOUR:SWE:RANG AUTO\n'))
        #         ser.write(str.encode(':SOUR:SWE:SPAC LIN\n'))
        #         ser.write(str.encode(':TRIG:COUN ' + number_steps + '\n'))  # number of points to measure
        #         ser.write(str.encode(':SOUR:DEL ' + source_delay + '\n'))  # source delay in sec
        #         ser.write(str.encode(':OUTP ON\n'))  # starts the sweep
        #         ser.write(str.encode(':READ?\n'))  # requests the data from the 2440
        #
        #         # get all of the data out
        #         b = bytes.decode(
        #             ser.readline())  # super important because it reads the entire buffer rather than just the number of bytes you specify in the read() command
        #         # print (b)
        #         b = b.split(',')  # turns this into an array instead of a string with a bunch of commas
        #         print(len(b))
        #         ##print b
        #         DIVoutput = np.zeros((int(len(b)) // 5, 6))
        #         Header = ['Rs Voltage (V)', 'Rs Current (A)', 'Series Resistance (mohm)', 'Rsh Voltage (V)', 'Rsh Current (A)',
        #                   'Shunt Resistance (ohm)']
        #
        #         for i in range(len(b) // 5):
        #             DIVoutput[i, 3] = b[i * 5]  # voltages
        #             DIVoutput[i, 4] = b[i * 5 + 1]  # current
        #
        #         for i in range(len(b) // 5 - 1):
        #             DIVoutput[i + 1, 5] = (DIVoutput[i + 1, 3] - DIVoutput[i, 3]) / (DIVoutput[i + 1, 4] - DIVoutput[i, 4])
        #
        #         RSH_MEAN = sum(DIVoutput[1:-1, 5]) / float(len(DIVoutput[1:-1, 5]))
        #         print(savename)
        #         print("Rsh Mean")
        #         print(RSH_MEAN)
        #
        #         ##ser
        #         ##ser.open()
        #
        #         ##ser.write(str.encode('*IDN?\n')
        #         ##ident = ser.read(200)
        #         ##print ident
        #         time.sleep(0.25)
        #
        #         ser.reset_input_buffer()
        #         ser.reset_output_buffer()
        #
        #         time.sleep(0.001)
        #
        #         ser.write(str.encode(':ROUT:TERM FRON\n'))
        #         ser.write(str.encode(':ROUT:TERM?\n'))
        #         print(ser.read(10))
        #
        #         ser.write(str.encode(':SENS:FUNC:CONC OFF\n'))
        #         ser.write(str.encode(':SYST:RSEN ON\n'))  # chooses 4wire measurement setting
        #         ser.write(str.encode(':SOUR:FUNC CURR\n'))
        #         ser.write(str.encode(":SENS:FUNC 'VOLT:DC'\n"))
        #         ser.write(str.encode(':SENS:VOLT:PROT ' + voltage_protection + '\n'))
        #         ser.write(str.encode(':SOUR:CURR:START ' + start_current + '\n'))  # start current
        #         ser.write(str.encode(':SOUR:CURR:STOP ' + stop_current + '\n'))  # stop current
        #         ser.write(str.encode(':SOUR:CURR:STEP ' + current_step + '\n'))  # increment
        #         ser.write(str.encode(':SOUR:CURR:MODE SWE\n'))
        #         ser.write(str.encode(':SOUR:SWE:RANG AUTO\n'))
        #         ser.write(str.encode(':SOUR:SWE:SPAC LIN\n'))
        #         ser.write(str.encode(':TRIG:COUN ' + number_steps + '\n'))  # number of points to measure
        #         ser.write(str.encode(':SOUR:DEL ' + source_delay + '\n'))  # source delay in sec
        #         ser.write(str.encode(':OUTP ON\n'))  # starts the sweep
        #         ser.write(str.encode(':READ?\n'))  # requests the data from the 2440
        #
        #         # get all of the data out
        #         a = bytes.decode(
        #             ser.readline())  # super important because it reads the entire buffer rather than just the number of bytes you specify in the read() command
        #         a = a.split(',')  # turns this into an array instead of a string with a bunch of commas
        #
        #         # clean up the 2440 and the port (turn off output and close port)
        #         ser.write(str.encode(':OUTP OFF\n'))
        #         ser.close()
        #
        #         Header = ['Rs Voltage (V)', 'Rs Current (A)', 'Series Resistance (mohm)', 'Rsh Voltage (V)', 'Rsh Current (A)',
        #                   'Shunt Resistance (mohm)']
        #
        #         for i in range(len(a) // 5):
        #             DIVoutput[i, 0] = a[i * 5]  # voltages
        #             DIVoutput[i, 1] = a[i * 5 + 1]  # current
        #
        #         for i in range(len(a) // 5 - 1):
        #             DIVoutput[i + 1, 2] = 1000 * (DIVoutput[i + 1, 0] - DIVoutput[i, 0]) / (
        #             DIVoutput[i + 1, 1] - DIVoutput[i, 1])
        #
        #         RS_MIN = min(DIVoutput[1:-1, 2])
        #         print("Rs min (m-ohm)")
        #         print(RS_MIN)
        #         print("")
        #
        #         time.sleep(0.25)
        #         #################  Rsh is below
        #
        #
        #         ##
        #         ### clean up the 2440 and the port (turn off output and close port)
        #         ##ser.write(str.encode(':OUTP OFF\n')
        #         ##ser.close()
        #
        #         font = {'family': 'sans-serif',
        #                 'weight': 'bold',
        #                 'size': 16}
        #         title_font = {'fontname': 'Arial', 'size': '12', 'color': 'black', 'weight': 'normal',
        #                       'verticalalignment': 'bottom'}  # Bottom vertical alignment for more space
        #         matplotlib.rc('font', **font)
        #
        #         fig, ax1 = plt.subplots()
        #
        #         ax1.plot(DIVoutput[:, 0], DIVoutput[:, 1], 'b.')
        #         ax1.set_xlabel('V (V)')
        #         # Make the y-axis label and tick labels match the line color.
        #         ax1.set_ylabel('I (A)', color='b')
        #         for tl in ax1.get_yticklabels():
        #             tl.set_color('b')
        #
        #         ax2 = ax1.twinx()
        #         # s2 = np.sin(2*np.pi*t)
        #         ax2.plot(DIVoutput[1:, 0], DIVoutput[1:, 2], 'r.')
        #         ax2.set_ylabel('Rs (Ohms)', color='r')
        #         for tl in ax2.get_yticklabels():
        #             tl.set_color('r')
        #         plt.title(savename)
        #         ##plt.show()
        #         self.Rs_min = RS_MIN
        #         self.Rsh_mean = RSH_MEAN
        #         output = str(savename) + "," + str(RS_MIN) + "," + str(RSH_MEAN) + "," + str(date_time) + "\n"
        #         ##WriteToFile("SampleID, Rs_min (mohm), Rsh_mean (ohm)\n",rootdir + '\\data\\SummaryFile')
        #         WriteToFile(output, rootdir + '\\data\\SummaryFile')
        #         fig.savefig(rootdir + '\\data\\' + savename + '.png', bbox_inches='tight')
        #         np.savetxt(rootdir + '\\data\\' + savename + '.txt', DIVoutput)

        Rs_min = 2.5
        # self.Rs_min = "hello"
        # self.Rsh_mean = 2
        # self.fig = "C:\\Users\\eso\\Documents\\Python Scripts\\Python Project DIV\\Test.png"
        # self.message_to_listsubmissions.emit(str(self.Rs_min))
        # self.info = [self.Rs_min, self.Rsh_mean, self.fig]
        return Rs_min

    def run(self):
        print(y)
        Rs_min = str(self.TakeMeasurement())
        print(yes1)
        self.measurement.emit(Rs_min)
        print(yes2)
        time.sleep(2)
        self.finished.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = U()
    sys.exit(app.exec_())



self.Rs_measuredLabel.setText(_translate("MainWindow", "Measured Rs: "))
self.Rs_measuredText.setText(_translate("MainWindow", "Waiting for Measurement Data"))
self.Rsh_measuredLabel.setText(_translate("MainWindow", "Measured Rsh: "))
self.Rsh_measuredText.setText(_translate("MainWindow", "Waiting for Measurement Data"))
