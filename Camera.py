# This Python file uses the following encoding: utf-8
import cv2

from PySide2.QtCore import Slot, Signal, QObject, Qt
from PySide2.QtQuick import QQuickImageProvider
from PySide2.QtGui import QImage

# Cached Image, prevents ui to ask to many requests from camera
# also work as placeholder while app starts
global_image = QImage(0, 0, QImage.Format_BGR888)
# as opencv provides image in BGR format and Qt also support this format,
# throughout the application BGR forma will be used rather than classic RGB


class Camera(QObject):
    finishedStreaming = Signal()
    released = Signal()
    newImage = Signal()

    def __init__(self, width=10000, height=10000, id=0):
        QObject.__init__(self)
        self.camera = cv2.VideoCapture(id)
        if not self.camera.isOpened():
            print("Camera not opened!")
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.streaming = False

    @Slot()
    def stream(self):
        self.streaming = True
        self.finished = False
        while not self.finished:  # main loop for thread, it will only exit when camera no longer needed
            if self.streaming:  # as long as camera is stream mode new frame will be taken
                ret, frame = self.camera.read()
                if ret:
                    image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
                    self.changeGlobalImage(image)
                    self.newImage.emit()
        self.released.emit()

    def stop(self):
        self.streaming = False
        self.finishedStreaming.emit()

    def release(self):
        self.stop()
        self.finished = True
        self.camera.release()

    def changeGlobalImage(self, image):
        global global_image
        global_image = image
        self.newImage.emit()


class CameraImageProvider(QQuickImageProvider):
    def __init__(self):
        super(CameraImageProvider, self).__init__(QQuickImageProvider.Image)

    def requestImage(self, id, size, requestedSize):
        global global_image
        if not requestedSize.width() > 0 and not requestedSize.height() > 0:
            requestedSize.setWidth(global_image.width())
            requestedSize.setHeight(global_image.height())
        image = global_image.scaled(requestedSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return image
