# -------------------------------------------------------------------------------
# Name:        CCCabinetControls
# Purpose:
#
# Author:      eso
#
# Created:     25/07/2017
# Copyright:   (c) khan 2017
# Licence:     <your licence>
# -------------------------------------------------------------------------------

## Version change notes
# Ver 1.0 is basically functional python code
# list inputs and outputs
# all fans set to same set temp, 8 fans controlled individually, each by two temp sensors

# v1.2 now displays time into cycle
# v1.3 includes smoke sensor lockout that tells arduino to turn pin 14 high, killing TDK output permanently upon smoke signal
# v1.4 uses only one timer in a (hopefully not vain) attempt to solve python.exe from crashing
# v1.5 was a complete flop
# v1.6 implements QThread to give background processes their own thread to not crash the GUI
# v2.0 same code but for Python3

import sys, time
import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
import threading
import serial
import numpy as np
import time
from serial.tools import list_ports
import TDKLambdaDriver_1_0 as TDK
import datetime
import csv

CCCabinetPythonControlsVersion = str(1.6)
first_time_seconds = str('%.0f' % round(time.time(), 1))