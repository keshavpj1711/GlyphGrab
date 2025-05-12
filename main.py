# to access cmd line args
import sys 

# QApplication, the application handler and 
# QWidget, a basic empty GUI widget
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget


class GlyphGrabMainWindow(QMainWindow):
  def __init__(self):
    super().__init__()  # super() fn calls the __init__() fn of the parent class
    self.setWindowTitle("GlyphGrab")
    self.setFixedSize(400, 500) 
    
    # Creating a label for search bar
    self.label = QLabel()

    self.input = QLineEdit()
    self.input.textChanged.connect(self.label.setText)

    layout = QVBoxLayout()
    layout.addWidget(self.input)
    layout.addWidget(self.label)

    container = QWidget()
    container.setLayout(layout)

    # Set the central widget of the Window.
    self.setCentralWidget(container)


def main():
  app = QApplication(sys.argv)
  window = GlyphGrabMainWindow() 
  window.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()