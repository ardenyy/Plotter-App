# This Python file uses the following encoding: utf-8
import cv2
import numpy as np
import threading

from svg_to_gcode.svg_parser import parse_string
from svg_to_gcode.compiler import Compiler, interfaces
from svg_to_gcode import TOLERANCES

from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QImage, QPainter
from PySide2.QtSvg import QSvgRenderer


class ImageProcessor():
    path = "Assets/Created/"
    svg_path = path + "processed_image.svg"
    gcode_path = path + "processed_image.gcode"

    FORMAT = QSize(4200, 2970)

    def process(self, qimage, format=FORMAT):
        ptr = qimage.bits()
        image = np.array(ptr).reshape(qimage.height(), qimage.width(), 3)
        #image = cv2.resize(image, (format.width(), format.height()))
        height, width = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        image = cv2.Canny(image, 100, 200)
        contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        image = np.ones((height, width, 3), dtype=np.uint8)*255
        qimage = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_BGR888)

        qimage = qimage.scaled(format, Qt.KeepAspectRatio, Qt.FastTransformation)

        thread_svg = threading.Thread(target=self.contours_to_svg, args=(contours, width, height), daemon=True)
        thread_svg.start()
        return qimage

    def contours_to_svg(self, contours, width, height, to_gcode=True):
        svg = '<svg width="' + str(width) + '" height="' + str(height) + '" xmlns="http://www.w3.org/2000/svg">'
        for c in contours:
            svg += '<path d="M'
            for i in range(len(c)):
                x, y = c[i][0]
                svg += str(x) + " " + str(y) + " "
            svg += '" style="stroke:black"/>'
        svg += "</svg>"
        with open(self.svg_path, "w+") as f:
            f.write(svg)
        if not to_gcode:
            return
        self.svg_to_gcode(svg, 0.3)
        return

    def svg_to_gcode(self, path=svg_path, tolerance=0.1, pathtosave=gcode_path):
        TOLERANCES['approximation'] = tolerance
        curves = parse_string(path)
        gcode_compiler = Compiler(interfaces.Gcode, movement_speed=25000, cutting_speed=10000, pass_depth=5)
        gcode_compiler.append_curves(curves)
        gcode_compiler.compile_to_file(pathtosave, passes=2)

    def openPreviewImage(self, width, height):
        renderer = QSvgRenderer(self.svg_path)
        qimage = QImage(width, height, QImage.Format_BGR888)
        qimage.fill(0xFFFFFFFF)
        painter = QPainter(qimage)
        renderer.render(painter)
        painter.end()
        ptr = qimage.bits()
        image = np.array(ptr).reshape(qimage.height(), qimage.width(), 3)
        cv2.imshow("Preview", image)
