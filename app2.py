import sys
import cv2
import numpy as np
import noise

from PySide6.QtWidgets import ( QApplication, QMainWindow, QLabel, QMenuBar, QMenu, 
                                QFileDialog, QVBoxLayout, QComboBox, QWidget, QSlider, 
                                QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit,)
from PySide6.QtGui import QPixmap, QImage, QColor, QAction
from PySide6.QtCore import Qt, Signal, QTimer, QSize

class Particles():
    def __init__(self, num, windowSize):

        self.dim = windowSize

        # Store number of particles wanted to generate
        self.num_particles = num

        # Create array of random particle positions
        self.positions = np.random.rand(self.num_particles, 2)

        # Keep in range 512, 512
        self.positions *= self.dim

        # Save original positions for updates
        self.origPositions = np.copy(self.positions)

        # Initialize grid and flow field
        self.rows = 0 
        self.cols = 0

        self.flowField = None

        # These are values to change the way the flow field works
        self.zoom = 0.1
        self.curve = 3
        self.cellSize = 20
        self.currCellSize = self.cellSize # Keeps cell size in this class

        # Initialize screen to a beautiful image
        self.generateSymmetricFlow()

    def addParticle(self):

        newPosition = np.random.rand(1, 2)

        newPosition *= self.dim

        self.positions = np.concatenate((self.positions, newPosition))

    def genNewParticles(self, num):

        self.num_particles = num

        self.positions = np.random.rand(self.num_particles, 2)

        self.positions *= self.dim

        self.origPositions = np.copy(self.positions)

    def generateRandomFlow(self):

        # Set new cell size
        self.currCellSize = self.cellSize

        # Create flow field
        self.rows = int(np.floor(self.dim / self.currCellSize))
        self.cols = int(np.floor(self.dim / self.currCellSize))

        # This flow field grid will hold our angles for particles to access
        self.flowField = np.zeros((self.rows, self.cols), dtype=np.float32)

        # Add angles to each position within the flow field
        for y in range(self.rows):
            for x in range(self.cols):
                angle = (((np.random.rand(1) * self.zoom) - 0.5) * np.pi) * self.curve
                self.flowField[y][x] = angle
    
    def generateSymmetricFlow(self):
        
        # Set new cell size
        self.currCellSize = self.cellSize

        # Create flow field
        self.rows = int(np.floor(self.dim / self.currCellSize))
        self.cols = int(np.floor(self.dim / self.currCellSize))

        # This flow field grid will hold our angles for particles to access
        self.flowField = np.zeros((self.rows, self.cols), dtype=np.float32)

        # Add angles to each position within the flow field
        for y in range(self.rows):
            for x in range(self.cols):
                angle = (np.cos(x * self.zoom) + np.sin(y * self.zoom)) * self.curve
                self.flowField[y][x] = angle

    def generatePerlinFlow(self):

        # Perlin parameters
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        seed = np.random.randint(0,100)

        # Set new cell size
        self.currCellSize = self.cellSize

        # Create flow field
        self.rows = int(np.floor(self.dim / self.currCellSize))
        self.cols = int(np.floor(self.dim / self.currCellSize))

        # This flow field grid will hold our angles for particles to access
        self.flowField = np.zeros((self.rows, self.cols), dtype=np.float32)

        # Add angles to each position within the flow field
        for y in range(self.rows):
            for x in range(self.cols):

                scaledX = x * self.zoom
                scaledY = y * self.zoom

                # Apply "Improved Perlin" noise.
                noiseVal = noise.pnoise2(scaledX, scaledY,
                                        octaves=octaves, persistence=persistence, lacunarity=lacunarity,
                                        repeatx=self.dim, repeaty=self.dim,
                                        base=seed)
                
                angle = self.map(noiseVal, 0, 1, 0, np.pi * 2) * self.curve

                self.flowField[y][x] = angle

    def generateRockyFlow(self):

        # Perlin parameters
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        seed = np.random.randint(0,100)

        # Set new cell size
        self.currCellSize = self.cellSize

        # Create flow field
        self.rows = int(np.floor(self.dim / self.currCellSize))
        self.cols = int(np.floor(self.dim / self.currCellSize))

        # This flow field grid will hold our angles for particles to access
        self.flowField = np.zeros((self.rows, self.cols), dtype=np.float32)

        # Add angles to each position within the flow field
        for y in range(self.rows):
            for x in range(self.cols):

                scaledX = x * self.zoom
                scaledY = y * self.zoom

                # Apply "Improved Perlin" noise.
                noiseVal = noise.pnoise2(scaledX, scaledY,
                                        octaves=octaves, persistence=persistence, lacunarity=lacunarity,
                                        repeatx=self.dim, repeaty=self.dim,
                                        base=seed)
                
                angle = self.map(noiseVal, 0, 1, 0, np.pi * 2) * self.curve

                angle = np.round(angle, decimals=int(np.pi/4))

                self.flowField[y][x] = angle

    def generateRichardFlow(self):

        # Set new cell size
        self.currCellSize = self.cellSize

        # Create flow field
        self.rows = int(np.floor(self.dim / self.currCellSize))
        self.cols = int(np.floor(self.dim / self.currCellSize))

        # This flow field grid will hold our angles for particles to access
        self.flowField = np.zeros((self.rows, self.cols), dtype=np.float32)

        # Add angles to each position within the flow field
        for y in range(self.rows):
            for x in range(self.cols):
                left =  (np.cos(x * self.zoom) + np.sin((y - 1) * self.zoom)) * self.curve
                right =  (np.cos(x * self.zoom) + np.sin((y + 1) * self.zoom)) * self.curve
                top =  (np.cos((x + 1) * self.zoom) + np.sin(y * self.zoom)) * self.curve
                bottom =  (np.cos((x - 1) * self.zoom) + np.sin(y * self.zoom)) * self.curve
                
                xgrad = right - left
                ygrad = bottom - top
                total_grad = np.array([xgrad, ygrad])
                
                angle = np.arccos(total_grad.dot(np.array([1, 0]) / (np.sqrt(xgrad**2 + ygrad**2))))
                
                self.flowField[y][x] = angle

    def updateParticlesFlow(self):

        xInGrid = np.zeros(self.positions.shape[0], dtype=np.int32)
        yInGrid = np.zeros(self.positions.shape[0], dtype=np.int32)
        
        xInGrid[:] = np.floor(self.positions[:,0] / self.currCellSize)
        yInGrid[:] = np.floor(self.positions[:,1] / self.currCellSize)

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
    
    def resetParticles(self):
        self.positions = np.copy(self.origPositions)
    
    def setZoom(self, zoomVal):
        self.zoom = zoomVal

    def setCurve(self, curveVal):
        self.curve = curveVal

    def setCellSize(self, cellsVal):
        self.cellSize = cellsVal

    def map(self, value, inStart, inEnd, outStart, outEnd):
        mappedVal = outStart + ((outEnd - outStart) / (inEnd - inStart)) * (value - inStart)
        return mappedVal

class ParticleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize GUI
        self.initGUI()

        self.particles = Particles(2000, self.dim)

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
        
        self.dim = 1024

        # Create numpy array for image pixels
        self.npImgCont = np.zeros((self.dim, self.dim), dtype=np.float32)

        # Set window title and size
        self.setWindowTitle("Particle System")
        self.resize(self.dim, self.dim)

        # Layouts
        # --------------------------------------
        mainLayout = QVBoxLayout()
        toolLayout = QHBoxLayout()

        # Labels
        # --------------------------------------
        
        # Image display label
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(1, 1)

        # Zoom label
        self.zoomLabel = QLabel()
        self.zoomLabel.setText("Zoom:")
        self.zoomLabel.setMinimumSize(1, 1)
        
        # Curve label
        self.curveLabel = QLabel()
        self.curveLabel.setText("Curve:")
        self.curveLabel.setMinimumSize(1, 1)
        
        # Cellsize label
        self.cellLabel = QLabel()
        self.cellLabel.setText("Cell size:")
        self.cellLabel.setMinimumSize(1, 1)

        # Particle count label
        self.particlesLabel = QLabel()
        self.particlesLabel.setText("Number of particles:")
        self.particlesLabel.setMinimumSize(1, 1)

        # Combo box
        # --------------------------------------
        self.flowCombo = QComboBox()
        self.flowCombo.addItem("Random Flow")
        self.flowCombo.addItem("Symmetric Flow")
        self.flowCombo.addItem("Perlin Flow")
        self.flowCombo.addItem("Richard Flow")
        self.flowCombo.addItem("Rocky Flow")
        self.flowCombo.setCurrentIndex(1)
        self.flowCombo.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.flowCombo.currentIndexChanged.connect(self.genFlow)
        self.flowCombo.setEditable(False)

        # Text boxes
        # --------------------------------------

        # Zoom text box
        self.zoomTextBox = QLineEdit("0.1", parent=self)
        self.zoomTextBox.returnPressed.connect(self.setZoom)

        # Curve text box
        self.curveTextBox = QLineEdit("3", parent=self)
        self.curveTextBox.returnPressed.connect(self.setCurve)
        
        # Cell size text box
        self.cellSizeTextBox = QLineEdit("20", parent=self)
        self.cellSizeTextBox.returnPressed.connect(self.setCells)

        # Number of particles text bo
        self.numParticlesTextBox = QLineEdit("2000", parent=self)
        self.numParticlesTextBox.returnPressed.connect(self.genNewParticles)

        # Buttons
        # --------------------------------------
        
        # Add particle button
        self.particleButton = QPushButton()
        self.particleButton.setText("Add 1 Particle")
        self.particleButton.clicked.connect(self.genParticle)

        # Zoom Plus/Minus button
        self.zoomPlus = QPushButton()
        self.zoomPlus.setText("+")
        self.zoomPlus.setFixedSize(20, 20)
        self.zoomPlus.clicked.connect(self.addZoom)
        
        self.zoomMinus = QPushButton()
        self.zoomMinus.setText("-")
        self.zoomMinus.setFixedSize(20, 20)
        self.zoomMinus.clicked.connect(self.subZoom)

        # Curve Plus/Minus Button
        self.curvePlus = QPushButton()
        self.curvePlus.setText("+")
        self.curvePlus.setFixedSize(20, 20)
        self.curvePlus.clicked.connect(self.addCurve)
        
        self.curveMinus = QPushButton()
        self.curveMinus.setText("-")
        self.curveMinus.setFixedSize(20, 20)
        self.curveMinus.clicked.connect(self.subCurve)
        
        # Cellsize Plus/Minus Button
        self.cellsizePlus = QPushButton()
        self.cellsizePlus.setText("+")
        self.cellsizePlus.setFixedSize(20, 20)
        self.cellsizePlus.clicked.connect(self.addCells)

        self.cellsizeMinus = QPushButton()
        self.cellsizeMinus.setText("-")
        self.cellsizeMinus.setFixedSize(20,20)
        self.cellsizeMinus.clicked.connect(self.subCells)
        
        # Build GUI
        # --------------------------------------
        toolLayout.addWidget(self.zoomLabel)
        toolLayout.addWidget(self.zoomTextBox)
        toolLayout.addWidget(self.zoomPlus)
        toolLayout.addWidget(self.zoomMinus)

        toolLayout.addWidget(self.curveLabel)
        toolLayout.addWidget(self.curveTextBox)
        toolLayout.addWidget(self.curvePlus)
        toolLayout.addWidget(self.curveMinus)

        toolLayout.addWidget(self.cellLabel)
        toolLayout.addWidget(self.cellSizeTextBox)
        toolLayout.addWidget(self.cellsizePlus)
        toolLayout.addWidget(self.cellsizeMinus)

        toolLayout.addWidget(self.particlesLabel)
        toolLayout.addWidget(self.numParticlesTextBox)
        toolLayout.addWidget(self.particleButton)

        mainLayout.addWidget(self.imageLabel)
        mainLayout.addWidget(self.flowCombo)
        mainLayout.addLayout(toolLayout)

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

        # This constrains the particles light intensity
        # As they get really small, they flicker
        self.npImgCont = np.clip(self.npImgCont, 0, 1)

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
        numParticlesStr = self.numParticlesTextBox.text()
        numParticles = int(numParticlesStr)
        numParticles += 1
        self.numParticlesTextBox.setText(str(numParticles))

        self.particles.addParticle()

    def genNewParticles(self):
        
        self.clearImage()

        numParticlesStr = self.numParticlesTextBox.text()
        numParticles = int(numParticlesStr)

        if(numParticles > 2000):
            numParticles = 2000

        self.numParticlesTextBox.setText(str(numParticles))

        self.particles.genNewParticles(numParticles)

    def clearImage(self):
        self.npImgCont[:,:] = 0

    def genFlow(self):
        flowState = self.flowCombo.currentIndex()

        self.particles.resetParticles()

        self.clearImage()
        
        match flowState:
            case 0:
                self.particles.generateRandomFlow()
            case 1:
                self.particles.generateSymmetricFlow()
            case 2:
                self.particles.generatePerlinFlow()
            case 3:
                self.particles.generateRichardFlow()
            case 4:
                self.particles.generateRockyFlow()
            case _:
                print("Oops something went wrong!")


    def setZoom(self):
        # Get value and convert to float
        zoomstr = self.zoomTextBox.text()
        zoomVal = float(zoomstr)
        zoomVal = np.round(zoomVal, decimals=4)
        self.zoomTextBox.setText(str(zoomVal))

        # Set respective value in particle system
        self.particles.setZoom(zoomVal)

        # Generate new flow based on new parameters
        self.genFlow()

    def addZoom(self):
        # Get value and convert to float
        zoomStr = self.zoomTextBox.text()
        zoomVal = float(zoomStr)
        zoomVal += 0.1
        zoomVal = np.round(zoomVal, decimals=1)
        self.zoomTextBox.setText(str(zoomVal))

        # Set respective value in particle system
        self.particles.setZoom(zoomVal)

        # Generate new flow based on new parameters
        self.genFlow()
    
    def subZoom(self):
        # Get value and convert to float
        zoomStr = self.zoomTextBox.text()
        zoomVal = float(zoomStr)
        zoomVal -= 0.1
        zoomVal = np.round(zoomVal, decimals=1)
        self.zoomTextBox.setText(str(zoomVal))

        # Set respective value in particle system
        self.particles.setZoom(zoomVal)

        # Generate new flow based on new parameters
        self.genFlow()
    
    def setCurve(self):
        # Get value and convert to float
        curveStr = self.curveTextBox.text()
        curveVal = float(curveStr)
        curveVal = np.round(curveVal, decimals=4)
        self.curveTextBox.setText(str(curveVal))

        # Set respective value in particle system
        self.particles.setCurve(curveVal)

        # Generate new flow based on new parameters
        self.genFlow()
    
    def addCurve(self):
        # Get value and convert to float
        curveStr = self.curveTextBox.text()
        curveVal = float(curveStr)
        curveVal += 0.1
        curveVal = np.round(curveVal, decimals=1)
        self.curveTextBox.setText(str(curveVal))
        
        # Set respective value in particle system
        self.particles.setCurve(curveVal)

        # Generate new flow based on new parameters
        self.genFlow()
    
    def subCurve(self):
        # Get value and convert to float
        curveStr = self.curveTextBox.text()
        curveVal = float(curveStr)
        curveVal -= 0.1
        curveVal = np.round(curveVal, decimals=1)
        self.curveTextBox.setText(str(curveVal))

        # Set respective value in particle system
        self.particles.setCurve(curveVal)

        # Generate new flow based on new parameters
        self.genFlow()

    def setCells(self):
        # Get value and convert to float
        cellsStr = self.cellSizeTextBox.text()
        cellsVal = int(cellsStr)
        cellsVal = np.round(cellsVal)
        self.cellSizeTextBox.setText(str(cellsVal))

        # Set respective value in particle system
        self.particles.setCellSize(cellsVal)

        # Generate new flow based on new parameters
        self.genFlow()

    def addCells(self):
        # Get value and convert to float
        cellsStr = self.cellSizeTextBox.text()
        cellsVal = int(cellsStr)
        cellsVal += 1
        cellsVal = np.round(cellsVal)
        self.cellSizeTextBox.setText(str(cellsVal))
        
        # Set respective value in particle system
        self.particles.setCellSize(cellsVal)
        
        # Generate new flow based on new parameters
        self.genFlow()

    def subCells(self):

        # Get value and convert to float
        cellsStr = self.cellSizeTextBox.text()
        cellsVal = int(cellsStr)
        cellsVal -= 1
        cellsVal = np.round(cellsVal)
        self.cellSizeTextBox.setText(str(cellsVal))
        
        # Set respective value in particle system
        self.particles.setCellSize(cellsVal)
        
        # Generate new flow based on new parameters
        self.genFlow()



app = QApplication([])

window = ParticleWindow()
window.show()

app.exec()
