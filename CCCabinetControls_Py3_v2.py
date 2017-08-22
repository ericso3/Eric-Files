# -------------------------------------------------------------------------------
# Name:        CCCabinetControls
# Purpose:
#
# Author:      eso
#
# Created:     22/08/2017
# Copyright:   (c) khan 2017
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Version change notes
# Ver 1.0 is basically functional python code
# list inputs and outputs
# all fans set to same set temp, 8 fans controlled individually, each by two temp sensors

# v1.2 now displays time into cycle
# v1.3 includes smoke sensor lockout that tells arduino to turn pin 14 high, killing TDK output permanently upon smoke signal
# v1.4 uses only one timer in a (hopefully not vain) attempt to solve python.exe from crashing
# v1.5 was a complete flop
# v1.6 implements QThread to give background processes their own thread to not crash the GUI
# v2.0 same code but for Python3

import csv
import datetime
import os
import sys
import sys
import threading
import time
import time

import TDKLambdaDriver_1_0 as TDK
import numpy as np
import serial
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from serial.tools import list_ports

CCCabinetPythonControlsVersion = str(1.6)
first_time_seconds = str('%.0f' % round(time.time(), 1))

# Global Definitions
TMRONESECOND_INTERVAL = 2  # seconds between communication with Arduino
SAVETIME = 10  # save every 10 seconds, make this divisible by TMRONESECOND_INTERVAL
DEFAULT_BIAS_CURRENT = "0"
DEFAULT_BIAS_ON_TIME = "7"
DEFAULT_BIAS_OFF_TIME = "5"
DEFAULT_OVERTEMP_SETPOINT = "100"
DEFAULT_CURRENT_ON_SETPOINT = "85"
DEFAULT_CURRENT_OFF_SETPOINT = "25"
BAUDRATE = "57600"
BIAS_CURRENT_STATUS_INITIAL = 0
INTERLOCK = 0
VOLTAGE_COMPLIANCE = "60"
VERBOSE = 1  # Set to 1 to enable debug print, set to 0 to disable debug print

dict_to_Arduino = {"key1": 1,
                   "key2": 2,
                   "key3": 3, }

dict_to_TDK = {"key1": 1,
               "key2": 2,
               "key3": 3, }

dict_to_GUI = {
    "PowerSupplies": [
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, },
        {"isConnected": "Not Connected", "Current": 0.0, "Voltage": 0.0, }, ],
    "Temperatures": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ],
    "FanSpeeds": [
        0, 0, 0, 0, 0, 0, 0, 0, ],
    "CycleNumber": 0,
    "MinutesIntoCycle": 0,
    "CurrentBiasStatus": 'Off'}


class Window(QtWidgets.QWidget):
    # ================BEGINNING OF FORM INIT FUNCTIONS=========================== TDK power supplies in Gen language,
    #  USB setting for master power supply, ADR 1, RS485 setting for others (2-31 optional, probably use 2-12),
    # baudrate 57600

    # This function fires just once, upon startup. Usually used to define the overall shape of the window, title, etc.
    def __init__(self):
        super(Window, self).__init__()
        self.setup()
        self.setWindowTitle("Current Cycling Controls " + str(CCCabinetPythonControlsVersion))
        self.initUI()

    # This function fires once - use this to init variables4
    def setup(self):
        self.TDK = TDK

    def WriteToFile(self, message, OutputFile, first_time_seconds):
        file = open(OutputFile + first_time_seconds + '.txt', 'a')
        file.write(message)
        file.close()
        # here OutputFile is self.txtSaveFilePathName.text(), first_time_seconds is first_time_seconds

    # ======================END OF FORM INIT FUNCTIONS==========================

    # ==============BEGINNING OF USER INTERFACE FUNCTIONS=======================
    # This function also fires once (it's fired by the last line in the __init__ function. This function is typically used to define buttons, textboxes, etc.
    def initUI(self):
        self.threadPool = []
        self.counter = 0
        # Defines colors
        self.palette_red = QtGui.QPalette()
        self.palette_red.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.palette_green = QtGui.QPalette()
        self.palette_green.setColor(QtGui.QPalette.Foreground, QtCore.Qt.green)

        # Cycle Number
        self.lblCycleNumberLabel = QtWidgets.QLabel("Cycle #: ", self)
        self.lblCycleNumberLabel.move(230, 0)
        self.lblCycleNumberLabel.resize(100, 30)

        # Cycle Number
        self.lblCycleNumber = QtWidgets.QLabel("1", self)
        self.lblCycleNumber.move(300, 0)
        self.lblCycleNumber.resize(130, 30)

        # bias state
        self.lblBiasStateLabel = QtWidgets.QLabel("Bias State: ", self)
        self.lblBiasStateLabel.move(330, 0)
        self.lblBiasStateLabel.resize(100, 30)

        # bias state
        self.lblBiasState = QtWidgets.QLabel("0", self)
        self.lblBiasState.move(400, 0)
        self.lblBiasState.resize(130, 30)

        # Cycle Time
        self.lblCycleTimeLabel = QtWidgets.QLabel("Minutes into Cycle: ", self)
        self.lblCycleTimeLabel.move(180, 15)
        self.lblCycleTimeLabel.resize(150, 30)

        # Cycle Time
        self.lblCycleTime = QtWidgets.QLabel("0", self)
        self.lblCycleTime.move(300, 15)
        self.lblCycleTime.resize(130, 30)

        # User name
        self.lblUser = QtWidgets.QLabel("Operator: ", self)
        self.lblUser.move(25, 400)
        self.lblUser.resize(150, 45)

        # User name input
        self.txtUserName = QtWidgets.QLineEdit(self)
        self.txtUserName.setText('Operator')
        self.txtUserName.move(150, 400)
        self.txtUserName.resize(100, 30)

        # Save file location and name
        self.lblSaveFileLabel = QtWidgets.QLabel("Save Path and Name: ", self)
        self.lblSaveFileLabel.move(25, 450)
        self.lblSaveFileLabel.resize(150, 45)

        # Bias current textbox 6
        self.txtSaveFilePathName = QtWidgets.QLineEdit(self)
        self.txtSaveFilePathName.setText("Y:\\Current Cycling\\Kat's Data\\Data\\CCData_")
        self.txtSaveFilePathName.move(150, 450)
        self.txtSaveFilePathName.resize(400, 30)

        # Reconnect push button
        self.btnReconnect = QtWidgets.QPushButton("Reconnect", self)
        # self.btnReconnect.clicked.connect(self.btnReconnectClicked)
        self.btnReconnect.resize(150, 50)
        self.btnReconnect.move(10, 10)

        # Arduino firmware version label
        self.lblArduinoFWVersion = QtWidgets.QLabel("Arduino firmware version: ", self)
        self.lblArduinoFWVersion.move(10, 60)
        self.lblArduinoFWVersion.resize(150, 30)

        # TDK interlock active?
        self.chkTDKInterlockActive = QtWidgets.QCheckBox('TDK Interlock Active', self)
        self.chkTDKInterlockActive.setChecked(True)
        self.chkTDKInterlockActive.resize(300, 30)
        self.chkTDKInterlockActive.move(600, 450)

        ##        #Bias current label
        ##        self.lblBiasCurrent = QtGui.QLabel("Bias Current: ", self)
        ##        self.lblBiasCurrent.move(200,10)
        ##        self.lblBiasCurrent.resize(150,30)
        ##        self.lblBiasCurrentUnit = QtGui.QLabel("A", self)
        ##        self.lblBiasCurrentUnit.move(305,10)
        ##        self.lblBiasCurrentUnit.resize(50,30)

        # Bias time on label
        self.lblBiasOnTime = QtWidgets.QLabel("Bias On Time: ", self)
        self.lblBiasOnTime.move(200, 40)
        self.lblBiasOnTime.resize(150, 30)
        self.lblBiasOnTimeUnit = QtWidgets.QLabel("min", self)
        self.lblBiasOnTimeUnit.move(305, 40)
        self.lblBiasOnTimeUnit.resize(50, 30)

        # Bias time off label
        self.lblBiasOffTime = QtWidgets.QLabel("Bias Off Time: ", self)
        self.lblBiasOffTime.move(200, 70)
        self.lblBiasOffTime.resize(150, 30)
        self.lblBiasOffTimeUnit = QtWidgets.QLabel("min", self)
        self.lblBiasOffTimeUnit.move(305, 70)
        self.lblBiasOffTimeUnit.resize(50, 30)

        ##        #Bias current textbox
        ##        self.txtBiasCurrent = QtGui.QLineEdit(self)
        ##        self.txtBiasCurrent.setText(DEFAULT_BIAS_CURRENT)
        ##        self.txtBiasCurrent.move(270, 12)
        ##        self.txtBiasCurrent.resize(30, 25)

        # Bias on time textbox
        self.txtBiasOnTime = QtWidgets.QLineEdit(self)
        self.txtBiasOnTime.setText(DEFAULT_BIAS_ON_TIME)
        self.txtBiasOnTime.move(270, 42)
        self.txtBiasOnTime.resize(30, 25)

        # Bias off time textbox
        self.txtBiasOffTime = QtWidgets.QLineEdit(self)
        self.txtBiasOffTime.setText(DEFAULT_BIAS_OFF_TIME)
        self.txtBiasOffTime.move(270, 72)
        self.txtBiasOffTime.resize(30, 25)

        # Current on temperature setpoint label
        self.lblCurrentOnTempSetpoint = QtWidgets.QLabel("Current on temperature set point: ", self)
        self.lblCurrentOnTempSetpoint.move(350, 10)
        self.lblCurrentOnTempSetpoint.resize(200, 30)
        self.lblCurrentOnTempSetpointUnit = QtWidgets.QLabel("deg. C", self)
        self.lblCurrentOnTempSetpointUnit.move(570, 10)
        self.lblCurrentOnTempSetpointUnit.resize(50, 30)

        # Current on temperature setpoint textbox
        self.txtCurrentOnTempSetpoint = QtWidgets.QLineEdit(self)
        self.txtCurrentOnTempSetpoint.setText(DEFAULT_CURRENT_ON_SETPOINT)
        self.txtCurrentOnTempSetpoint.move(535, 12)
        self.txtCurrentOnTempSetpoint.resize(30, 25)

        # Current off temperature setpoint label
        self.lblCurrentOffTempSetpoint = QtWidgets.QLabel("Current off temperature set point: ", self)
        self.lblCurrentOffTempSetpoint.move(350, 40)
        self.lblCurrentOffTempSetpoint.resize(200, 30)
        self.lblCurrentOffTempSetpointUnit = QtWidgets.QLabel("deg. C", self)
        self.lblCurrentOffTempSetpointUnit.move(570, 40)
        self.lblCurrentOffTempSetpointUnit.resize(50, 30)

        # Current off temperature setpoint textbox
        self.txtCurrentOffTempSetpoint = QtWidgets.QLineEdit(self)
        self.txtCurrentOffTempSetpoint.setText(DEFAULT_CURRENT_OFF_SETPOINT)
        self.txtCurrentOffTempSetpoint.move(535, 42)
        self.txtCurrentOffTempSetpoint.resize(30, 25)

        # Overtemp setpoint label
        self.lblOvertempSetpoint = QtWidgets.QLabel("Over-temperature set point: ", self)
        self.lblOvertempSetpoint.move(350, 70)
        self.lblOvertempSetpoint.resize(200, 30)
        self.lblOvertempSetpointUnit = QtWidgets.QLabel("deg. C", self)
        self.lblOvertempSetpointUnit.move(570, 70)
        self.lblOvertempSetpointUnit.resize(50, 30)

        # Overtemp setpoint textbox
        self.txtOvertempSetpoint = QtWidgets.QLineEdit(self)
        self.txtOvertempSetpoint.setText(DEFAULT_OVERTEMP_SETPOINT)
        self.txtOvertempSetpoint.move(535, 72)
        self.txtOvertempSetpoint.resize(30, 25)

        # Start push button
        self.btnStart = QtWidgets.QPushButton("Start", self)
        # self.btnStart.clicked.connect(self.btnStartClicked)
        self.btnStart.resize(100, 45)
        self.btnStart.move(630, 10)

        # Stop push button
        self.btnStop = QtWidgets.QPushButton("Stop", self)
        # self.btnStop.clicked.connect(self.btnStopClicked)
        self.btnStop.resize(100, 40)
        self.btnStop.move(630, 60)

        # Exit push button
        self.btnExit = QtWidgets.QPushButton("Exit", self)
        # self.btnExit.clicked.connect(self.btnExitClicked)
        self.btnExit.resize(100, 40)
        self.btnExit.move(745, 60)

        # Power supply label
        self.lblPowerSupplyLabel = QtWidgets.QLabel("Power Supply: ", self)
        self.lblPowerSupplyLabel.move(10, 100)
        self.lblPowerSupplyLabel.resize(100, 30)

        # Power supply 1
        self.lblPowerSupply1 = QtWidgets.QLabel("NOT CONNECTED - 1 ", self)
        self.lblPowerSupply1.move(10, 100 + 1 * 20)
        self.lblPowerSupply1.resize(130, 30)

        # Power supply 2
        self.lblPowerSupply2 = QtWidgets.QLabel("NOT CONNECTED - 2 ", self)
        self.lblPowerSupply2.move(10, 100 + 2 * 20)
        self.lblPowerSupply2.resize(130, 30)

        # Power supply 3
        self.lblPowerSupply3 = QtWidgets.QLabel("NOT CONNECTED - 3 ", self)
        self.lblPowerSupply3.move(10, 100 + 3 * 20)
        self.lblPowerSupply3.resize(130, 30)

        # Power supply 4
        self.lblPowerSupply4 = QtWidgets.QLabel("NOT CONNECTED - 4", self)
        self.lblPowerSupply4.move(10, 100 + 4 * 20)
        self.lblPowerSupply4.resize(130, 30)

        # Power supply 5
        self.lblPowerSupply5 = QtWidgets.QLabel("NOT CONNECTED - 5", self)
        self.lblPowerSupply5.move(10, 100 + 5 * 20)
        self.lblPowerSupply5.resize(130, 30)

        # Power supply 6
        self.lblPowerSupply6 = QtWidgets.QLabel("NOT CONNECTED - 6", self)
        self.lblPowerSupply6.move(10, 100 + 6 * 20)
        self.lblPowerSupply6.resize(130, 30)

        # Power supply 7
        self.lblPowerSupply7 = QtWidgets.QLabel("NOT CONNECTED - 7", self)
        self.lblPowerSupply7.move(10, 100 + 7 * 20)
        self.lblPowerSupply7.resize(130, 30)

        # Power supply 8
        self.lblPowerSupply8 = QtWidgets.QLabel("NOT CONNECTED - 8", self)
        self.lblPowerSupply8.move(10, 100 + 8 * 20)
        self.lblPowerSupply8.resize(130, 30)

        # Power supply 9
        self.lblPowerSupply9 = QtWidgets.QLabel("NOT CONNECTED - 9", self)
        self.lblPowerSupply9.move(10, 100 + 9 * 20)
        self.lblPowerSupply9.resize(130, 30)

        # Power supply 10
        self.lblPowerSupply10 = QtWidgets.QLabel("NOT CONNECTED - 10", self)
        self.lblPowerSupply10.move(10, 100 + 10 * 20)
        self.lblPowerSupply10.resize(130, 30)

        # Power supply 11
        self.lblPowerSupply11 = QtWidgets.QLabel("NOT CONNECTED - 11", self)
        self.lblPowerSupply11.move(10, 100 + 11 * 20)
        self.lblPowerSupply11.resize(130, 30)

        # Power supply 12
        self.lblPowerSupply12 = QtWidgets.QLabel("NOT CONNECTED - 12", self)
        self.lblPowerSupply12.move(10, 100 + 12 * 20)
        self.lblPowerSupply12.resize(130, 30)

        # Current label
        self.lblCurrentLabel = QtWidgets.QLabel("Current (A): ", self)
        self.lblCurrentLabel.move(140, 100)
        self.lblCurrentLabel.resize(100, 30)

        # Current from power supply - 1
        self.lblCurrent1 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent1.move(140, 100 + 1 * 20)
        self.lblCurrent1.resize(130, 30)

        # Current from power supply - 2
        self.lblCurrent2 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent2.move(140, 100 + 2 * 20)
        self.lblCurrent2.resize(130, 30)

        # Current from power supply - 3
        self.lblCurrent3 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent3.move(140, 100 + 3 * 20)
        self.lblCurrent3.resize(130, 30)

        # Current from power supply - 4
        self.lblCurrent4 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent4.move(140, 100 + 4 * 20)
        self.lblCurrent4.resize(130, 30)

        # Current from power supply - 5
        self.lblCurrent5 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent5.move(140, 100 + 5 * 20)
        self.lblCurrent5.resize(130, 30)

        # Current from power supply - 6
        self.lblCurrent6 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent6.move(140, 100 + 6 * 20)
        self.lblCurrent6.resize(130, 30)

        # Current from power supply - 7
        self.lblCurrent7 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent7.move(140, 100 + 7 * 20)
        self.lblCurrent7.resize(130, 30)

        # Current from power supply - 8
        self.lblCurrent8 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent8.move(140, 100 + 8 * 20)
        self.lblCurrent8.resize(130, 30)

        # Current from power supply - 9
        self.lblCurrent9 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent9.move(140, 100 + 9 * 20)
        self.lblCurrent9.resize(130, 30)

        # Current from power supply - 10
        self.lblCurrent10 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent10.move(140, 100 + 10 * 20)
        self.lblCurrent10.resize(130, 30)

        # Current from power supply - 11
        self.lblCurrent11 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent11.move(140, 100 + 11 * 20)
        self.lblCurrent11.resize(130, 30)

        # Current from power supply - 12
        self.lblCurrent12 = QtWidgets.QLabel("0.0A", self)
        self.lblCurrent12.move(140, 100 + 12 * 20)
        self.lblCurrent12.resize(130, 30)

        # Voltage label
        self.lblVoltageLabel = QtWidgets.QLabel("Voltage (V): ", self)
        self.lblVoltageLabel.move(235, 100)
        self.lblVoltageLabel.resize(100, 30)

        # Voltage from power supply - 1
        self.lblVoltage1 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage1.move(235, 100 + 1 * 20)
        self.lblVoltage1.resize(130, 30)

        # Voltage from power supply - 2
        self.lblVoltage2 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage2.move(235, 100 + 2 * 20)
        self.lblVoltage2.resize(130, 30)

        # Voltage from power supply - 3
        self.lblVoltage3 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage3.move(235, 100 + 3 * 20)
        self.lblVoltage3.resize(130, 30)

        # Voltage from power supply - 4
        self.lblVoltage4 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage4.move(235, 100 + 4 * 20)
        self.lblVoltage4.resize(130, 30)

        # Voltage from power supply - 5
        self.lblVoltage5 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage5.move(235, 100 + 5 * 20)
        self.lblVoltage5.resize(130, 30)

        # Voltage from power supply - 6
        self.lblVoltage6 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage6.move(235, 100 + 6 * 20)
        self.lblVoltage6.resize(130, 30)

        # Voltage from power supply - 7
        self.lblVoltage7 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage7.move(235, 100 + 7 * 20)
        self.lblVoltage7.resize(130, 30)

        # Voltage from power supply - 8
        self.lblVoltage8 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage8.move(235, 100 + 8 * 20)
        self.lblVoltage8.resize(130, 30)

        # Voltage from power supply - 9
        self.lblVoltage9 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage9.move(235, 100 + 9 * 20)
        self.lblVoltage9.resize(130, 30)

        # Voltage from power supply - 10
        self.lblVoltage10 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage10.move(235, 100 + 10 * 20)
        self.lblVoltage10.resize(130, 30)

        # Voltage from power supply - 11
        self.lblVoltage11 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage11.move(235, 100 + 11 * 20)
        self.lblVoltage11.resize(130, 30)

        # Voltage from power supply - 12
        self.lblVoltage12 = QtWidgets.QLabel("0.0V", self)
        self.lblVoltage12.move(235, 100 + 12 * 20)
        self.lblVoltage12.resize(130, 30)

        # Thermistor label
        self.lblThermistorLabel = QtWidgets.QLabel("Thermistor Temp (C): ", self)
        self.lblThermistorLabel.move(310, 100)
        self.lblThermistorLabel.resize(120, 30)

        # Thermistor 1
        self.lblThermistor1 = QtWidgets.QLabel("1: ", self)
        self.lblThermistor1.move(310, 100 + 1 * 20)
        self.lblThermistor1.resize(100, 30)

        # Thermistor Value 1
        self.lblThermistorValue1 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue1.move(340, 100 + 1 * 20)
        self.lblThermistorValue1.resize(100, 30)

        # Thermistor 2
        self.lblThermistor2 = QtWidgets.QLabel("2: ", self)
        self.lblThermistor2.move(310, 100 + 2 * 20)
        self.lblThermistor2.resize(100, 30)

        # Thermistor Value 2
        self.lblThermistorValue2 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue2.move(340, 100 + 2 * 20)
        self.lblThermistorValue2.resize(100, 30)

        # Thermistor 3
        self.lblThermistor3 = QtWidgets.QLabel("3: ", self)
        self.lblThermistor3.move(410, 100 + 1 * 20)
        self.lblThermistor3.resize(100, 30)

        # Thermistor Value 3
        self.lblThermistorValue3 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue3.move(440, 100 + 1 * 20)
        self.lblThermistorValue3.resize(100, 30)

        # Thermistor 4
        self.lblThermistor4 = QtWidgets.QLabel("4: ", self)
        self.lblThermistor4.move(410, 100 + 2 * 20)
        self.lblThermistor4.resize(100, 30)

        # Thermistor Value 4
        self.lblThermistorValue4 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue4.move(440, 100 + 2 * 20)
        self.lblThermistorValue4.resize(100, 30)

        # Thermistor 5
        self.lblThermistor5 = QtWidgets.QLabel("5: ", self)
        self.lblThermistor5.move(310, 100 + 4 * 20)
        self.lblThermistor5.resize(100, 30)

        # Thermistor Value 5
        self.lblThermistorValue5 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue5.move(340, 100 + 4 * 20)
        self.lblThermistorValue5.resize(100, 30)

        # Thermistor 6 new
        self.lblThermistor6 = QtWidgets.QLabel("6: ", self)
        self.lblThermistor6.move(310, 100 + 5 * 20)
        self.lblThermistor6.resize(100, 30)

        # Thermistor Value 6
        self.lblThermistorValue6 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue6.move(340, 100 + 5 * 20)
        self.lblThermistorValue6.resize(100, 30)

        # Thermistor 7
        self.lblThermistor7 = QtWidgets.QLabel("7: ", self)
        self.lblThermistor7.move(410, 100 + 4 * 20)
        self.lblThermistor7.resize(100, 30)

        # Thermistor Value 7
        self.lblThermistorValue7 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue7.move(440, 100 + 4 * 20)
        self.lblThermistorValue7.resize(100, 30)

        # Thermistor 8
        self.lblThermistor8 = QtWidgets.QLabel("8: ", self)
        self.lblThermistor8.move(410, 100 + 5 * 20)
        self.lblThermistor8.resize(100, 30)

        # Thermistor Value 8
        self.lblThermistorValue8 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue8.move(440, 100 + 5 * 20)
        self.lblThermistorValue8.resize(100, 30)

        # Thermistor 9
        self.lblThermistor9 = QtWidgets.QLabel("9: ", self)
        self.lblThermistor9.move(310, 100 + 7 * 20)
        self.lblThermistor9.resize(100, 30)

        # Thermistor Value 9
        self.lblThermistorValue9 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue9.move(340, 100 + 7 * 20)
        self.lblThermistorValue9.resize(100, 30)

        # Thermistor 10
        self.lblThermistor10 = QtWidgets.QLabel("10: ", self)
        self.lblThermistor10.move(310, 100 + 8 * 20)
        self.lblThermistor10.resize(100, 30)

        # Thermistor Value 10
        self.lblThermistorValue10 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue10.move(340, 100 + 8 * 20)
        self.lblThermistorValue10.resize(100, 30)

        # Thermistor 11
        self.lblThermistor11 = QtWidgets.QLabel("11: ", self)
        self.lblThermistor11.move(410, 100 + 7 * 20)
        self.lblThermistor11.resize(100, 30)

        # Thermistor Value 11
        self.lblThermistorValue11 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue11.move(440, 100 + 7 * 20)
        self.lblThermistorValue11.resize(100, 30)

        # Thermistor 12
        self.lblThermistor12 = QtWidgets.QLabel("12: ", self)
        self.lblThermistor12.move(410, 100 + 8 * 20)
        self.lblThermistor12.resize(100, 30)

        # Thermistor Value 12
        self.lblThermistorValue12 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue12.move(440, 100 + 8 * 20)
        self.lblThermistorValue12.resize(100, 30)

        # Thermistor 13
        self.lblThermistor13 = QtWidgets.QLabel("13: ", self)
        self.lblThermistor13.move(310, 100 + 10 * 20)
        self.lblThermistor13.resize(100, 30)

        # Thermistor Value 13
        self.lblThermistorValue13 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue13.move(340, 100 + 10 * 20)
        self.lblThermistorValue13.resize(100, 30)

        # Thermistor 14
        self.lblThermistor14 = QtWidgets.QLabel("14: ", self)
        self.lblThermistor14.move(310, 100 + 11 * 20)
        self.lblThermistor14.resize(100, 30)

        # Thermistor Value 14
        self.lblThermistorValue14 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue14.move(340, 100 + 11 * 20)
        self.lblThermistorValue14.resize(100, 30)

        # Thermistor 15
        self.lblThermistor15 = QtWidgets.QLabel("15: ", self)
        self.lblThermistor15.move(410, 100 + 10 * 20)
        self.lblThermistor15.resize(100, 30)

        # Thermistor Value 15
        self.lblThermistorValue15 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue15.move(440, 100 + 10 * 20)
        self.lblThermistorValue15.resize(100, 30)

        # Thermistor 16
        self.lblThermistor16 = QtWidgets.QLabel("16: ", self)
        self.lblThermistor16.move(410, 100 + 11 * 20)
        self.lblThermistor16.resize(100, 30)

        # Thermistor Value 16
        self.lblThermistorValue16 = QtWidgets.QLabel("0", self)
        self.lblThermistorValue16.move(440, 100 + 11 * 20)
        self.lblThermistorValue16.resize(100, 30)

        # Fan label
        self.lblFanLabel = QtWidgets.QLabel("Fan Command: ", self)
        self.lblFanLabel.move(515, 100)
        self.lblFanLabel.resize(100, 30)

        # Fan Speed Value 1
        self.lblFanSpeedValue1 = QtWidgets.QLabel("0%", self)
        self.lblFanSpeedValue1.move(515, 100 + 2 * 20)
        self.lblFanSpeedValue1.resize(100, 45)

        # Fan Speed Value 2
        self.lblFanSpeedValue2 = QtWidgets.QLabel("0%", self)
        self.lblFanSpeedValue2.move(565, 100 + 2 * 20)
        self.lblFanSpeedValue2.resize(100, 45)

        # Fan Speed Value 3
        self.lblFanSpeedValue3 = QtWidgets.QLabel("0%", self)
        self.lblFanSpeedValue3.move(515, 100 + 5 * 20)
        self.lblFanSpeedValue3.resize(100, 45)

        # Fan Speed Value 4
        self.lblFanSpeedValue4 = QtWidgets.QLabel("0%", self)
        self.lblFanSpeedValue4.move(565, 100 + 5 * 20)
        self.lblFanSpeedValue4.resize(100, 45)

        # Fan Speed Value 5
        self.lblFanSpeedValue5 = QtWidgets.QLabel("0%", self)
        self.lblFanSpeedValue5.move(515, 100 + 8 * 20)
        self.lblFanSpeedValue5.resize(100, 45)

        # Fan Speed Value 6
        self.lblFanSpeedValue6 = QtWidgets.QLabel("0%", self)
        self.lblFanSpeedValue6.move(565, 100 + 8 * 20)
        self.lblFanSpeedValue6.resize(100, 45)

        # Fan Speed Value 7
        self.lblFanSpeedValue7 = QtWidgets.QLabel("0%", self)
        self.lblFanSpeedValue7.move(515, 100 + 11 * 20)
        self.lblFanSpeedValue7.resize(100, 45)

        # Fan Speed Value 8
        self.lblFanSpeedValue8 = QtWidgets.QLabel("0%", self)
        self.lblFanSpeedValue8.move(565, 100 + 11 * 20)
        self.lblFanSpeedValue8.resize(100, 45)

        # Independent Bias current label
        self.lblIndependentBiasCurrent = QtWidgets.QLabel("Bias Current (A): ", self)
        self.lblIndependentBiasCurrent.move(630, 100)
        self.lblIndependentBiasCurrent.resize(150, 30)

        # Bias current textbox 1
        self.txtBiasCurrent1 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent1.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent1.move(630, 110 + 1 * 20)
        self.txtBiasCurrent1.resize(30, 15)

        # Bias current textbox 2
        self.txtBiasCurrent2 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent2.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent2.move(630, 110 + 2 * 20)
        self.txtBiasCurrent2.resize(30, 15)

        # Bias current textbox 3
        self.txtBiasCurrent3 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent3.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent3.move(630, 110 + 3 * 20)
        self.txtBiasCurrent3.resize(30, 15)

        # Bias current textbox 4
        self.txtBiasCurrent4 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent4.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent4.move(630, 110 + 4 * 20)
        self.txtBiasCurrent4.resize(30, 15)

        # Bias current textbox 5
        self.txtBiasCurrent5 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent5.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent5.move(630, 110 + 5 * 20)
        self.txtBiasCurrent5.resize(30, 15)

        # Bias current textbox 6
        self.txtBiasCurrent6 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent6.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent6.move(630, 110 + 6 * 20)
        self.txtBiasCurrent6.resize(30, 15)

        # Bias current textbox 7
        self.txtBiasCurrent7 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent7.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent7.move(630, 110 + 7 * 20)
        self.txtBiasCurrent7.resize(30, 15)

        # Bias current textbox 8
        self.txtBiasCurrent8 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent8.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent8.move(630, 110 + 8 * 20)
        self.txtBiasCurrent8.resize(30, 15)

        # Bias current textbox 9
        self.txtBiasCurrent9 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent9.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent9.move(630, 110 + 9 * 20)
        self.txtBiasCurrent9.resize(30, 15)

        # Bias current textbox 10
        self.txtBiasCurrent10 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent10.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent10.move(630, 110 + 10 * 20)
        self.txtBiasCurrent10.resize(30, 15)

        # Bias current textbox 11
        self.txtBiasCurrent11 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent11.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent11.move(630, 110 + 11 * 20)
        self.txtBiasCurrent11.resize(30, 15)

        # Bias current textbox 12
        self.txtBiasCurrent12 = QtWidgets.QLineEdit(self)
        self.txtBiasCurrent12.setText(DEFAULT_BIAS_CURRENT)
        self.txtBiasCurrent12.move(630, 110 + 12 * 20)
        self.txtBiasCurrent12.resize(30, 15)

        # Variable declarations
        self.intBiasOnTimerSeconds = 0  # # of seconds supply has been on
        self.intBiasOffTimerSeconds = 0
        self.intBiasCurrentState = 0  # Desired state of power supply (on = 1)

        # Shows the main form
        self.setGeometry(600, 50, 900, 700)
        self.show()
        self.activateWindow()

        #  self.layout = QtGui.QVBoxLayout(self)

        # Start push button
        self.btnStart = QtWidgets.QPushButton("Start", self)
        # self.btnStart.clicked.connect(self.btnStartClicked)
        self.btnStart.resize(100, 45)
        self.btnStart.move(130, 10)
        ##
        ##        # Print iterations in the GUI
        ##        self.lbliteration = QtGui.QLabel("Iteration: ", self)
        ##        self.valueiteration = QtGui.QLabel(str(self.counter), self)
        ##        self.lbliteration.move(30, 100 + 1 * 20)
        ##        self.lbliteration.resize(130, 30)
        ##        self.valueiteration.move(30, 100 + 2 * 20)
        ##        self.valueiteration.resize(130, 30)

        # Starts the main timer
        self.intArduinoTimerEnabled = 0
        self.intTDKTimerEnabled = 0
        self.intRun = 1
        # self.threadPool.append(GenericThread(self.tmrMainTimer))
        # self.disconnect(self, QtCore.SIGNAL("UpdateGUI()"), self.UpdateGUI)
        # self.connect(self, QtCore.SIGNAL("UpdateGUI()"), self.UpdateGUI)
        # self.threadPool[len(self.threadPool) - 1].start()


app = QApplication(sys.argv)
test1 = Window()
test1.show()
app.exec_()
