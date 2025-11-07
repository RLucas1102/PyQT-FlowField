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

        self.windowW = 200
        self.windowH = 200

        self.setWindowTitle("Particle System")
        self.resize(self.windowW, self.windowH)

        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(1, 1)
        self.setCentralWidget(self.imageLabel)

app = QApplication()

window = ParticleWindow()

window.show()

app.exec()

