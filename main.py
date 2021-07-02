# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtQml import QQmlApplicationEngine

import Camera
import Presenter

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("Assets/tdu_logo.png")))
    engine = QQmlApplicationEngine()

    presenter = Presenter.Presenter()
    camProvider = Camera.CameraImageProvider()

    engine.rootContext().setContextProperty("presenter", presenter)
    engine.addImageProvider("camera_provider", camProvider)

    engine.load(resource_path("Assets/QML/Main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
