import sys
from PyQt5.QtWidgets import QApplication, QWidget

def main():
    # Create an application object
    app = QApplication(sys.argv)

    # Create a QWidget (a window)
    window = QWidget()
    window.setWindowTitle('Simple PyQt Window')  # Set the window title
    window.setGeometry(100, 100, 300, 200)  # Set the position and size of the window (x, y, width, height)
    window.show()  # Display the window

    # Execute the application's event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()