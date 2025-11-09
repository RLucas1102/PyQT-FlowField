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
        # --------------------------------
        num_particles = 200

        # Create array of random particle positions
        positions = np.random.rand(num_particles, 2)

        # Keep in range 256, 256
        np.multiply(positions, self.dim/2, out=positions)

        # Move particle cloud to center
        np.add(positions, self.dim/4, out=positions)

        # Truncate positions to whole numbers
        self.positions_out = positions.astype(int)

        # Create random vectors
        # ---------------------

        # Create a set to randomly choose a value from
        choices = np.array([-1, 0, 1])

        # Choose x and y values separately
        vectorx = np.random.choice(choices, num_particles)

        vectory = np.random.choice(choices, num_particles)

        # Create coordinate pairs by concatenating the vectors laterally
        vectors = np.dstack((vectorx, vectory))

        # If any vectors have no movement (0,0), then pick a random direction to go
        for i in range(num_particles):
            if np.array_equal(vectors[:, i], np.array([[0, 0]])):
                choice = np.random.choice([0, 1], 1)
                vectors[:, i, choice] = 1 

        # Remove vectors from 3D
        self.vectors_out = vectors[0]

        # Set window title and size
        self.setWindowTitle("Particle System")
        self.resize(self.dim, self.dim)

        # Image display label
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(1, 1)
        self.setCentralWidget(self.imageLabel)

        # For each particle position, access that position in the image and set the value to 1
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

        # Restore image to black
        self.npImgCont[:, :] = 0

        # Add vector to position
        np.add(self.positions_out, self.vectors_out, out=self.positions_out)

        # Clamp positions within image space
        self.positions_out = np.minimum(511, np.maximum(0, self.positions_out))

        # For each particle position, access that position in the image and set the value to 1
        np.add.at(self.npImgCont, (self.positions_out[:, 0], self.positions_out[:, 1]), 1)

        # Update pixmap by converting range, to QImage, and setting imageLabel
        fImageData = (self.npImgCont * 255).astype(np.uint8)
        self.pixmap = QPixmap.fromImage(QImage(fImageData.astype(np.uint8).data, fImageData.shape[1], fImageData.shape[0], QImage.Format_Grayscale8))
        self.imageLabel.setPixmap(self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

app = QApplication()

window = ParticleWindow()

window.show()

app.exec()

