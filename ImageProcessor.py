# This Python file uses the following encoding: utf-8
import cv2
import numpy as np
import threading
from skimage.morphology import skeletonize

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

    FORMAT = QSize(840, 594)

    def process(self, qimage, format=FORMAT):
        ptr = qimage.bits()
        image = np.array(ptr).reshape(qimage.height(), qimage.width(), 3)
        # image = cv2.resize(image, (format.width(), format.height()))
        height, width = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # image processing code
        image, contours = self.imageProcessing(image)

        # conversion for QML
        qimage = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)
        qimage = qimage.scaled(format, Qt.KeepAspectRatio, Qt.FastTransformation)

        # svg and gcode conversion thread
        thread_svg = threading.Thread(target=self.contours_to_svg, args=(contours, width, height), daemon=True)
        thread_svg.start()
        return qimage

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
        self.svg_to_gcode(svg, 0.5)
        return

    def svg_to_gcode(self, path=svg_path, tolerance=0.1, pathtosave=gcode_path):
        TOLERANCES['approximation'] = tolerance
        curves = parse_string(path)
        gcode_compiler = Compiler(interfaces.Gcode, movement_speed=50000, cutting_speed=40000, pass_depth=5)
        gcode_compiler.append_curves(curves)
        gcode_compiler.compile_to_file(pathtosave, passes=1)

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
        image = img.copy()
        height, width = image.shape[:2]
        threshold = [100, 200]
        image = cv2.GaussianBlur(image, (5, 5), 1)  # ADD GAUSSIAN BLUR
        image = cv2.Canny(image, threshold[0], threshold[1])  # APPLY CANNY BLUR
        kernel = np.ones((5, 5))
        image = cv2.dilate(image, kernel, iterations=2)  # APPLY DILATION
        image = cv2.erode(image, kernel, iterations=1)  # APPLY EROSION

        contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
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

            # APPLY ADAPTIVE THRESHOLD
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,7, 2)
            image = cv2.bitwise_not(image)
            image = cv2.medianBlur(image, 5)
            image = cv2.Canny(image, 80, 150)
            kernel = np.ones((3, 3))

            image = cv2.dilate(image, kernel, iterations=5)  # APPLY DILATION
            image = cv2.erode(image, kernel, iterations=3)  # APPLY EROSION

            '''
            skeleton method
            image = image >100
            image = skeletonize(image)
            image = image.astype(np.uint8)  #convert to an unsigned byte
            image *= 255
            '''

            contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
        else:
            print("Couldn't find the paper!")
        image = cv2.bitwise_not(image)
        return image, contours

    def biggestContour(self, contours):
        biggest = np.array([])
        max_area = 0
        for i in contours:
            area = cv2.contourArea(i)
            if area > 5000: #5000
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
