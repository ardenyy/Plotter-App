# This Python file uses the following encoding: utf-8
import os
import sys
import cv2
import numpy as np
import threading

from svg_to_gcode.svg_parser import parse_string
from svg_to_gcode.compiler import Compiler, interfaces
from svg_to_gcode import TOLERANCES

from PySide2.QtCore import QSize
from PySide2.QtGui import QImage, QPainter
from PySide2.QtSvg import QSvgRenderer


class ImageProcessor():
    path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "Assets/")
    svg_path = path + "processed_image.svg"
    gcode_path = path + "processed_image.gcode"

    FORMAT = QSize(280, 200)

    def process(self, qimage, format=FORMAT):
        ptr = qimage.bits()
        image = np.array(ptr).reshape(qimage.height(), qimage.width(), 3)

        # image processing code
        contours = self.imageProcessing(image)

        image = np.ones((format.height(), format.width(), 3), dtype=np.uint8) * 255
        cv2.drawContours(image, contours, -1, (0, 0, 0), 3)

        # svg and gcode conversion thread
        thread_svg = threading.Thread(target=self.contours_to_svg, args=(contours, format.width(), format.height()), daemon=True)
        thread_svg.start()
        return image

    def contours_to_svg(self, contours, width, height, to_gcode=True):
        svg = '<svg width="' + str(width) + '" height="' + str(height) + '" xmlns="http://www.w3.org/2000/svg">'
        svg += '<g fill="none">'
        for c in contours:
            svg += '<path d="M'
            for i in range(len(c)):
                x, y = c[i][0]
                svg += str(x) + " " + str(y) + " "
            svg += '" style="stroke:black;fill-rule: evenodd;" />'
        svg += '</g>'
        svg += "</svg>"
        with open(self.svg_path, "w+") as f:
            f.write(svg)
        if not to_gcode:
            return
        self.svg_to_gcode(svg, 0.1)
        return

    def svg_to_gcode(self, svg, tolerance=0.1, pathtosave=gcode_path):
        TOLERANCES['approximation'] = tolerance
        curves = parse_string(svg)
        gcode_compiler = Compiler(interfaces.Gcode, movement_speed=50000, cutting_speed=40000, pass_depth=5)
        gcode_compiler.append_curves(curves)
        gcode_compiler.compile_to_file(pathtosave, passes=1)
        with open(pathtosave, "ab") as f:
            return_home = b"\nG21G90 G0Z5;\nG90 G0 X0 Y0;\nG90 G0 Z0;"
            f.write(return_home)

    def openPreviewImage(self, width, height):
        renderer = QSvgRenderer(self.svg_path)
        qimage = QImage(width, height, QImage.Format_Grayscale8)
        qimage.fill(0xFFFFFFFF)
        painter = QPainter(qimage)
        renderer.render(painter)
        painter.end()
        ptr = qimage.bits()
        image = np.array(ptr).reshape(qimage.height(), qimage.width(), 1)
        cv2.imshow("Preview", image)

    def imageProcessing(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        image = img.copy()
        height, width = image.shape[:2]
        threshold = [100, 200]
        image = cv2.GaussianBlur(image, (5, 5), 1)  # ADD GAUSSIAN BLUR
        image = cv2.Canny(image, threshold[0], threshold[1])  # APPLY CANNY BLUR
        kernel = np.ones((5, 5))
        image = cv2.dilate(image, kernel, iterations=2)  # APPLY DILATION
        image = cv2.erode(image, kernel, iterations=1)  # APPLY EROSION

        contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
        biggest, maxArea = self.biggestContour(contours)
        if biggest.size != 0:
            biggest = self.reorder(biggest)
            pts1 = np.float32(biggest)  # PREPARE POINTS FOR WARP
            pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])  # PREPARE POINTS FOR WARP
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            image = cv2.warpPerspective(img, matrix, (width, height))

            # REMOVE 25 PIXELS FORM EACH SIDE
            image = image[25:image.shape[0] - 25, 25:image.shape[1] - 25]
            image = cv2.resize(image, (width, height))
        else:
            print("Couldn't find the paper!")
            image = img.copy()

        # APPLY ADAPTIVE THRESHOLD
        image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 2)
        image = cv2.bitwise_not(image)
        image = cv2.medianBlur(image, 5)
        image = cv2.Canny(image, 120, 200)
        kernel = np.ones((3, 3))

        image = cv2.dilate(image, kernel, iterations=5)  # APPLY DILATION
        image = cv2.erode(image, kernel, iterations=3)  # APPLY EROSION

        image = cv2.resize(image, (self.FORMAT.width(), self.FORMAT.height()))
        contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
        return contours

    def biggestContour(self, contours):
        biggest = np.array([])
        max_area = 0
        for i in contours:
            area = cv2.contourArea(i)
            if area > 5000:
                peri = cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, 0.02 * peri, True)
                if area > max_area and len(approx) == 4:
                    biggest = approx
                    max_area = area
        return biggest, max_area

    def reorder(self, myPoints):
        myPoints = myPoints.reshape((4, 2))
        myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
        add = myPoints.sum(1)
        myPointsNew[0] = myPoints[np.argmin(add)]
        myPointsNew[3] = myPoints[np.argmax(add)]
        diff = np.diff(myPoints, axis=1)
        myPointsNew[1] = myPoints[np.argmin(diff)]
        myPointsNew[2] = myPoints[np.argmax(diff)]
        return myPointsNew