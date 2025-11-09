import sys
import cv2
import numpy as np
import noise

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenuBar, QMenu, QFileDialog, QVBoxLayout, QComboBox, QWidget, QSlider 
from PySide6.QtGui import QPixmap, QImage, QColor, QAction
from PySide6.QtCore import Qt, Signal, QTimer

class ParticleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Default dimension for square images
        self.dim = 512

        # Share Numpy arrays for efficiency: xcoords, xycoords
        self.npImgCont = np.zeros((self.dim, self.dim), dtype=np.float32)

        # Create random particle positions
        num_particles = 200

        positions = np.random.rand(num_particles, 2)

        np.multiply(positions, self.dim/2, out=positions)

        np.add(positions, self.dim/4, out=positions)

        self.positions_out = positions.astype(int)

        # Create random vectors
        choices = np.array([-1, 0, 1])

        vectorx = np.random.choice(choices, num_particles)

        vectory = np.random.choice(choices, num_particles)

        vectors = np.dstack((vectorx, vectory))

        self.vectors_out = vectors[0]

        # Set window title and size
        self.setWindowTitle("Particle System")
        self.resize(self.dim, self.dim)

        # Image display label
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(1, 1)
        self.setCentralWidget(self.imageLabel)

        np.add.at(self.npImgCont, (self.positions_out[:, 0], self.positions_out[:, 1]), 1)

        # Update pixmap by converting range, to QImage, and setting imageLabel
        fImageData = (self.npImgCont * 255).astype(np.uint8)
        self.pixmap = QPixmap.fromImage(QImage(fImageData.astype(np.uint8).data, fImageData.shape[1], fImageData.shape[0], QImage.Format_Grayscale8))
        self.imageLabel.setPixmap(self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

        # Create timer for constant updates
        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update)

        self.timer.start(10)

    def update(self):

        self.npImgCont[:, :] = 0

        np.add(self.positions_out, self.vectors_out, out=self.positions_out)

        np.add.at(self.npImgCont, (self.positions_out[:, 0], self.positions_out[:, 1]), 1)

        # Update pixmap by converting range, to QImage, and setting imageLabel
        fImageData = (self.npImgCont * 255).astype(np.uint8)
        self.pixmap = QPixmap.fromImage(QImage(fImageData.astype(np.uint8).data, fImageData.shape[1], fImageData.shape[0], QImage.Format_Grayscale8))
        self.imageLabel.setPixmap(self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))







app = QApplication()

window = ParticleWindow()

window.show()

app.exec()

