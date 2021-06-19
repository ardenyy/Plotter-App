# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

import Camera
import Presenter

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    presenter = Presenter.Presenter()
    camProvider = Camera.CameraImageProvider()

    engine.rootContext().setContextProperty("presenter", presenter)
    engine.addImageProvider("camera_provider", camProvider)

    engine.load(os.path.join(os.path.dirname(__file__), "Assets/QML/Main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
