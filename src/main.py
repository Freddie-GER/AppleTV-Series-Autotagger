import sys
from pathlib import Path
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication

from .gui.main_window import MainWindow

def main():
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Create and run application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 