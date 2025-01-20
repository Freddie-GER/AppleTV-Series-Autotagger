import sys
from pathlib import Path
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TV Series Auto Tagger")
        self.setGeometry(100, 100, 800, 600)
        # TODO: Add GUI components

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 