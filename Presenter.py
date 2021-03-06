# This Python file uses the following encoding: utf-8
import threading

from PySide2.QtCore import Slot, Signal, QObject, QThread
from PySide2.QtGui import QImage

import Camera
import ImageProcessor
import SerialCommunicator


class Presenter(QObject):
    '''
    Main class for model-view communications
    It communicates via QT Signals and Slots
    '''

    newFrame = Signal()
    finishedStreaming = Signal()
    startedStreaming = Signal()
    cameraClosed = Signal()
    progressUpdate = Signal(float)
    plottingStarted = Signal()
    plottingStopped = Signal()
    serialPorts = Signal(str)
    connectionTimeout = Signal(str)

    def __init__(self):
        QObject.__init__(self)
        self.processor = ImageProcessor.ImageProcessor()
        self.serial = SerialCommunicator.SerialCommunicator()
        self.thread = None
        self.camera = None
        self.isStreaming = False
        self.isCameraOpen = False
        self.startCamera()

    @Slot()
    def startCamera(self):
        if not self.isCameraOpen:
            self.camera = Camera.Camera()
            self.thread = QThread()

            self.camera.moveToThread(self.thread)
            self.camera.newImage.connect(self.newFrame)
            self.camera.released.connect(self.thread.quit)
            self.camera.finishedStreaming.connect(self.finishedStreaming)

            self.thread.started.connect(self.camera.stream)
            self.thread.finished.connect(self.cameraClosed)
            self.thread.start()
        self.camera.streaming = True
        self.isStreaming = True
        self.isCameraOpen = True
        self.startedStreaming.emit()

    @Slot()
    def stopCamera(self):
        if self.isStreaming:
            self.isStreaming = False
            self.camera.stop()
        elif self.isCameraOpen:
            self.isCameraOpen = False
            self.camera.release()

    @Slot()
    def processImage(self):
        image = self.processor.process(Camera.global_image)
        image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_BGR888)
        self.camera.changeGlobalImage(image)
        self.getSerialPorts()
        self.stopCamera()

    @Slot(str)
    def startPlotting(self, port):
        print("Selected Port: ", port)
        self.serial.progressUpdate.connect(self.progressUpdate)
        self.serial.plottingStarted.connect(self.plottingStarted)
        self.serial.connectionTimeout.connect(self.connectionTimeout)
        self.serial.plottingStopped.connect(self.plottingStopped)
        thread_gcode = threading.Thread(target=self.serial.sendGcode, args=(port, ), daemon=True)
        thread_gcode.start()

    @Slot(int, int)
    def openPreviewImage(self, width, height):
        if not self.isCameraOpen:
            self.processor.openPreviewImage(width, height)

    def getSerialPorts(self):
        ports = self.serial.getSerialPorts()
        for port in ports:
            self.serialPorts.emit(port)
