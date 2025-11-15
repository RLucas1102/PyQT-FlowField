import sys
import cv2
import numpy as np
import noise

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenuBar, QMenu, QFileDialog, QVBoxLayout, QComboBox, QWidget, QSlider, QVBoxLayout 
from PySide6.QtGui import QPixmap, QImage, QColor, QAction
from PySide6.QtCore import Qt, Signal, QTimer

class ParticleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Member variables
        self.noiseMult = 0

        # Default dimension for square images
        self.dim = 512

        # Share Numpy arrays for efficiency: xcoords, xycoords
        self.npImgCont = np.zeros((self.dim, self.dim), dtype=np.float32)

        # Create random particle positions
        # --------------------------------
        num_particles = 200

        # Create array of random particle positions
        positions = np.random.rand(num_particles, 2)

        # Keep in range 512, 512
        np.multiply(positions, self.dim, out=positions)

        # Move particle cloud to center
        # np.add(positions, self.dim/4, out=positions)

        # Truncate positions to whole numbers
        self.positions_out = positions

        # Create random vectors
        # ---------------------
        vectorx = np.ones(num_particles)
        vectory = np.ones(num_particles)
        
        vectorx *= np.minimum(0.5 + np.vectorize(noise.pnoise1)(self.positions_out[:, 0], 4), 1)
        
        vectory *= np.minimum(0.5 + np.vectorize(noise.pnoise1)(self.positions_out[:, 1], 4), 1)
        

        # Create coordinate pairs by concatenating the vectors laterally
        vectors = np.dstack((vectorx, vectory))

        # If any vectors have no movement (0,0), then pick a random direction to go
        for i in range(num_particles):
            if np.array_equal(vectors[:, i], np.array([[0, 0]])):
                choice = np.random.choice([0, 1], 1)
                vectors[:, i, choice] = 1 

        # Remove vectors from 3D
        self.vectors_out = vectors[0]

        # Initialize GUI
        self.initGUI()


    def initGUI(self):
        
        # Window properties
        # --------------------------------------
        
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

        # Noise multipler label
        multLabel = QLabel()
        multLabel.setText("Noise Multiplier:")

        # Sliders
        # --------------------------------------

        # Noise multiplier slider
        self.multSlider = QSlider(Qt.Horizontal)
        self.multSlider.setRange(0, 100)
        self.multSlider.setValue(0.0)
        self.multSlider.valueChanged.connect(self.GetNoiseMult)

        # Build GUI
        # --------------------------------------
        mainLayout.addWidget(self.imageLabel)
        mainLayout.addWidget(multLabel)
        mainLayout.addWidget(self.multSlider)

        dummy = QWidget()
        dummy.setLayout(mainLayout)
        self.setCentralWidget(dummy)

        # Timer
        # --------------------------------------

        # Create timer for constant updates
        self.dt = 1000/60

        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update)

        self.timer.start(self.dt)
        
    def GetNoiseMult(self):
        self.noiseMult = self.multSlider.value()

    def update(self):

        # Restore image to black
        self.npImgCont[:, :] = 0

        # Add vector to position
        self.positions_out[:, 0] += self.vectors_out[:, 0]
        self.positions_out[:, 1] += self.vectors_out[:, 1]

        self.positions_out[:, 0] %= self.dim
        self.positions_out[:, 1] %= self.dim

        # Clamp positions within image space
        # self.positions_out = np.minimum(511, np.maximum(0, self.positions_out))

        xi = np.zeros(self.positions_out.shape[0], dtype=np.int32)
        yi = np.zeros(self.positions_out.shape[0], dtype=np.int32)

        xi[:] = np.floor(self.positions_out[:, 0])
        yi[:] = np.floor(self.positions_out[:, 1])

        # For each particle position, access that position in the image and set the value to 1
        np.add.at(self.npImgCont, (xi, yi), 1)

        # Update pixmap by converting range, to QImage, and setting imageLabel
        fImageData = (self.npImgCont * 255).astype(np.uint8)
        self.pixmap = QPixmap.fromImage(QImage(fImageData.astype(np.uint8).data, fImageData.shape[1], fImageData.shape[0], QImage.Format_Grayscale8))
        self.imageLabel.setPixmap(self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

app = QApplication()

window = ParticleWindow()

window.show()

app.exec()

##########################
# dt = st.dt * st.speed
# st.vel += a * dt
# st.pos += st.vel * dt

# st.pos[:, 0] %= st.W
# st.pos[:, 1] %= st.H

# xi = st.xi
# yi = st.yi

# xi[:] = np.floor(st.pos[:, 0]).astype(np.int32)
# xi %= st.W

# yi[:] = np.floor(st.pos[:, 1]).astype(np.int32)
# yi %= st.H

# st.acc *= st.fade
# xo = (xi[:, None] + st.splatOffsets[:, 0]) % st.W
# yo = (yi[:, None] + st.splatOffsets[:, 1]) % st.H
# w  = st.splatWeights[None, :]
# np.add.at(st.acc, (yo, xo), w)