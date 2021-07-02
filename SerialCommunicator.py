# This Python file uses the following encoding: utf-8
import os
import sys
import time
from serial import Serial
from serial.tools import list_ports

from PySide2.QtCore import Signal, QObject


class SerialCommunicator(QObject):
    progressUpdate = Signal(float)
    plottingStarted = Signal()
    plottingStopped = Signal()
    connectionTimeout = Signal(str)
    path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), 'Assets/processed_image.gcode')
    timeout = 180 #timeout value for gcode sending.
    #if too long can wait unnecessarily for  worng port
    #if too short can cause error while waiting for commands to execute

    def sendGcode(self, port='com3', gcode_path=path):
        self.plottingStarted.emit()
        s = Serial(port, 115200, timeout=self.timeout)
        f = open(gcode_path, 'r')
        time.sleep(2)
        s.flushInput()

        for i, line in enumerate(f):
            pass
        i += 1
        # Stream g-code
        f.seek(0)
        for index, line in enumerate(f):
            if line.find(';') == -1:
                l = line
            else:
                l = line[:line.index(';')]
            l = l.strip()
            print(l)
            if l.isspace() is False and len(l) > 0:
                s.write((l + '\n').encode())  # Send g-code block
                print("Line printed")
                print("Reading new line")
                grbl_out = s.readline()
                print(grbl_out.decode('utf-8'))
                if not (b'\n' in grbl_out):
                    err = "Connection Timed Out after {time} seconds".format(time=self.timeout)
                    self.connectionTimeout.emit(err)
                    break
            progress = (index+1)*100/i
            self.progressUpdate.emit(progress)
        f.close()
        s.close()
        self.plottingStopped.emit()

    def getSerialPorts(self):
        ports = []
        ports_objs = list_ports.comports()
        for p in ports_objs:
            ports.append(p.name)
        return ports
