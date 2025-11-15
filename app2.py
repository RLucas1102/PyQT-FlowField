import sys
import cv2
import numpy as np
import noise

from PySide6.QtWidgets import ( QApplication, QMainWindow, QLabel, QMenuBar, QMenu, 
                                QFileDialog, QVBoxLayout, QComboBox, QWidget, QSlider, 
                                QVBoxLayout, QPushButton, )
from PySide6.QtGui import QPixmap, QImage, QColor, QAction
from PySide6.QtCore import Qt, Signal, QTimer

class Particles():
    def __init__(self, num, windowSize):

        self.dim = windowSize

        # Store number of particles wanted to generate
        self.num_particles = num

        # Create array of random particle positions
        self.positions = np.random.rand(self.num_particles, 2)

        # Keep in range 512, 512
        self.positions *= self.dim

        # Create array of random particle vectors (keep [0,1])
        self.vectors = np.random.rand(self.num_particles, 2)

        self.vectors = self.vectors - 0.5

    def addParticles(self):

        newPosition = np.random.rand(1, 2)

        newPosition *= self.dim

        self.positions = np.concatenate((self.positions, newPosition))

        newVector = np.random.rand(1, 2)

        newVector = newVector - 0.5

        self.vectors = np.concatenate((self.vectors, newVector))

class ParticleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize GUI
        self.initGUI()

        self.particles = Particles(200, self.dim)

        self.startTimer()

    def startTimer(self):
        # Create timer for constant updates
        self.dt = 1000/60

        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update)

        self.timer.start(self.dt)

    def initGUI(self):
        
        # Window properties
        # --------------------------------------
        
        self.dim = 512

        # Create numpy array for image pixels
        self.npImgCont = np.zeros((self.dim, self.dim), dtype=np.float32)

        # Set window title and size
        self.setWindowTitle("Particle System")
        self.resize(self.dim, self.dim)

        # Layouts
        # --------------------------------------
        mainLayout = QVBoxLayout()

        # Labels
        # --------------------------------------
        
        # Image display label
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(1, 1)

        # Buttons
        # --------------------------------------
        self.randButton = QPushButton()
        self.randButton.setText("Randomize")
        self.randButton.clicked.connect(self.genParticle)

        # Build GUI
        # --------------------------------------
        mainLayout.addWidget(self.imageLabel)
        mainLayout.addWidget(self.randButton)

        dummy = QWidget()
        dummy.setLayout(mainLayout)
        self.setCentralWidget(dummy)

    def update(self):

        # Multiply the whole image by a small scale 
        # and subtract it from the current image
        # to create a trail effect
        self.npImgCont -= self.npImgCont * 0.005

        self.drawParticles()

        # Update pixmap by converting range, to QImage, and setting imageLabel
        fImageData = (self.npImgCont * 255).astype(np.uint8)
        self.pixmap = QPixmap.fromImage(QImage(fImageData.astype(np.uint8).data, fImageData.shape[1], fImageData.shape[0], QImage.Format_Grayscale8))
        self.imageLabel.setPixmap(self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

    def drawParticles(self):

        # Add vector to position
        self.particles.positions[:, 0] += self.particles.vectors[:, 0] + np.random.rand(1) * 2 - 1
        self.particles.positions[:, 1] += self.particles.vectors[:, 1] + np.random.rand(1) * 2 - 1

        self.particles.positions[:, 0] %= self.dim
        self.particles.positions[:, 1] %= self.dim

        xi = np.zeros(self.particles.positions.shape[0], dtype=np.int32)
        yi = np.zeros(self.particles.positions.shape[0], dtype=np.int32)

        xi[:] = np.floor(self.particles.positions[:, 0])
        yi[:] = np.floor(self.particles.positions[:, 1])

        # For each particle position, access that position in the image and set the value to 1
        np.add.at(self.npImgCont, (xi, yi), 1)

    def genParticle(self):

        self.particles.addParticles()


app = QApplication([])

window = ParticleWindow()
window.show()

app.exec()