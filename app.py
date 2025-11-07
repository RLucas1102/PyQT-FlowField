import sys
import cv2
import numpy as np
import noise

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenuBar, QMenu, QFileDialog, QVBoxLayout, QComboBox, QWidget, QSlider 
from PySide6.QtGui import QPixmap, QImage, QColor, QAction
from PySide6.QtCore import Qt, Signal

class ParticleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Default dimension for square images
        self.dim = 512

        # Share Numpy arrays for efficiency: xcoords, xycoords
        self.npImgCont = np.zeros((self.dim, self.dim), dtype=np.float32)

        x = 256
        y = 256

        p = np.array([[x],[y]])

        self.npImgCont[p[0], p[1]] = 1.0

        # Linearly divide range between 0 and 1 to make np array
        # self.xcoords = np.linspace(0, 1, self.dim)

        # Make similar structure in 2D similar to UV coords
        # x, y = np.meshgrid(self.xcoords, self.xcoords)
        # self.xycoords = np.dstack((x, y))

        # Set window title and size
        self.setWindowTitle("Particle System")
        self.resize(self.dim, self.dim)

        # Image display label
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(1, 1)
        self.setCentralWidget(self.imageLabel)

        # Update npImgCont by broadcasting fcn output (y) over all of the rows of npImgCont (which should be 1s)
        # np.multiply(self.npImgCont, x, out=self.npImgCont)

        # Update pixmap by converting range, to QImage, and setting imageLabel
        fImageData = (self.npImgCont * 255).astype(np.uint8)
        self.pixmap = QPixmap.fromImage(QImage(fImageData.astype(np.uint8).data, fImageData.shape[1], fImageData.shape[0], QImage.Format_Grayscale8))
        self.imageLabel.setPixmap(self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

app = QApplication()

window = ParticleWindow()

window.show()

app.exec()

