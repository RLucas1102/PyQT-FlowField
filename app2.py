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

        # Create flow field
        self.cellSize = 20
        self.rows = int(np.floor(self.dim / self.cellSize))
        self.cols = int(np.floor(self.dim / self.cellSize))

        self.flowField = np.zeros((self.rows, self.cols), dtype=np.float32)

        # Add angles to each position within the flow field
        for y in range(self.rows):
            for x in range(self.cols):
                angle = (np.cos(x * 0.1) + np.sin(y *0.1)) * 0.9
                self.flowField[y][x] = angle

    def addParticle(self):

        newPosition = np.random.rand(1, 2)

        newPosition *= self.dim

        self.positions = np.concatenate((self.positions, newPosition))

        newVector = np.random.rand(1, 2)

        newVector = newVector - 0.5

        self.vectors = np.concatenate((self.vectors, newVector))

    def updateParticlesRand(self):

        # Add vector to position
        self.positions[:, 0] += self.vectors[:, 0] + np.random.rand(1) * 2 - 1
        self.positions[:, 1] += self.vectors[:, 1] + np.random.rand(1) * 2 - 1

    def updateParticlesFlow(self):

        xInGrid = np.zeros(self.positions.shape[0], dtype=np.int32)
        yInGrid = np.zeros(self.positions.shape[0], dtype=np.int32)
        
        xInGrid[:] = np.floor(self.positions[:,0] / self.cellSize)
        yInGrid[:] = np.floor(self.positions[:,1] / self.cellSize)

        xInGrid %= self.cols
        yInGrid %= self.rows

        angles = np.zeros(self.positions.shape[0])

        for i in range(angles.shape[0]):
            angles[i] = self.flowField[xInGrid[i]][yInGrid[i]]

        velX = np.cos(angles)
        velY = np.sin(angles)

        self.positions[:, 0] += velY
        self.positions[:, 1] += velX

    def getParticles(self):
        return self.positions

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
        self.npImgCont *= 0.9985

        self.particles.updateParticlesFlow()

        self.drawParticles()

        self.npImgCont = np.clip(self.npImgCont, 0.000001, 1)

        # Update pixmap by converting range, to QImage, and setting imageLabel
        fImageData = (self.npImgCont * 255).astype(np.uint8)
        self.pixmap = QPixmap.fromImage(QImage(fImageData.astype(np.uint8).data, fImageData.shape[1], fImageData.shape[0], QImage.Format_Grayscale8))
        self.imageLabel.setPixmap(self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

    def drawParticles(self):

        positions = self.particles.getParticles()

        # Wrap screen
        positions[:, 0] %= self.dim
        positions[:, 1] %= self.dim

        # Create two arrays to hold the x and y positions, respectively
        xi = np.zeros(positions.shape[0], dtype=np.int32)
        yi = np.zeros(positions.shape[0], dtype=np.int32)

        # Make values integers for indexing
        xi[:] = np.floor(positions[:, 0])
        yi[:] = np.floor(positions[:, 1])

        # For each particle position, access that position in the image and set the value to 1
        np.add.at(self.npImgCont, (xi, yi), 1)

    def genParticle(self):

        self.particles.addParticle()


app = QApplication([])

window = ParticleWindow()
window.show()

app.exec()