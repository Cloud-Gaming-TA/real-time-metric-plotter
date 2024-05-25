from PyQt5.QtWidgets import QMainWindow, QScrollArea, QVBoxLayout, QWidget, QApplication
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar


class MatplotlibFigureScrollableWindow(QMainWindow):
    def __init__(self, plotter) -> None:
        self.plotter = plotter
        self.qapp = QApplication([])
        
        QMainWindow.__init__(self)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(0)

        self.fig = plotter.fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.show()
        self.plotter.animate()
        exit(self.qapp.exec_()) 
    
    def update(self):
        print("start updating")
        self.plotter.update()
        
    def animate(self):
        timer = QtCore.QTimer()
        timer.timeout.connenct(self.update)
        timer.start(1000)