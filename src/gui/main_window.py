from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QFileDialog, QProgressBar,
    QListWidget, QMessageBox, QScrollArea, QLineEdit, QGridLayout,
    QFrame
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPalette, QColor

from ..utils.constants import SUPPORTED_VIDEO_EXTENSIONS
from ..services.processor import FileProcessor

class MetadataEditor(QFrame):
    def __init__(self, result: dict):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        self.result = result
        
        layout = QGridLayout(self)
        
        # File name (non-editable)
        layout.addWidget(QLabel("File:"), 0, 0)
        layout.addWidget(QLabel(result['filename']), 0, 1)
        
        # Series name
        layout.addWidget(QLabel("Series:"), 1, 0)
        self.series_name = QLineEdit(result['parsed_info'].get('series_name', ''))
        layout.addWidget(self.series_name, 1, 1)
        
        # Season number
        layout.addWidget(QLabel("Season:"), 2, 0)
        self.season = QLineEdit(str(result['parsed_info'].get('season_number', '')))
        layout.addWidget(self.season, 2, 1)
        
        # Episode number
        layout.addWidget(QLabel("Episode:"), 3, 0)
        self.episode = QLineEdit(str(result['parsed_info'].get('episode_number', '')))
        layout.addWidget(self.episode, 3, 1)
        
        # Episode title
        layout.addWidget(QLabel("Title:"), 4, 0)
        self.title = QLineEdit(result['parsed_info'].get('episode_title', ''))
        layout.addWidget(self.title, 4, 1)
    
    def get_metadata(self) -> dict:
        """Get the current metadata values"""
        return {
            'series_name': self.series_name.text(),
            'season_number': self.season.text(),
            'episode_number': self.episode.text(),
            'episode_title': self.title.text(),
            'file_path': self.result['file_path'],
            'series_info': self.result['series_info'],
            'episode_info': self.result['episode_info']
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = FileProcessor()
        self.selected_files = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('AppleTV Series Autotagger')
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Drop zone
        self.drop_zone = QLabel('Drag and drop video files here\nor click to select files')
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.setMinimumHeight(100)
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed gray;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                color: palette(text);
            }
        """)
        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.mousePressEvent = self.open_file_dialog
        layout.addWidget(self.drop_zone)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel('Select Tag Language:')
        lang_label.setStyleSheet("color: palette(text);")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem('English')
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # Process button
        self.process_btn = QPushButton('Process Files')
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.process_files)
        layout.addWidget(self.process_btn)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Selected files list
        self.files_label = QLabel('Selected Files:')
        self.files_label.setStyleSheet("color: palette(text);")
        layout.addWidget(self.files_label)
        
        self.files_list = QListWidget()
        self.files_list.setStyleSheet("""
            QListWidget {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid gray;
                border-radius: 5px;
                color: palette(text);
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        layout.addWidget(self.files_list)
        
        # Status label
        self.status_label = QLabel('')
        self.status_label.setStyleSheet("color: palette(text);")
        layout.addWidget(self.status_label)
        
        # Set up drag and drop
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.add_files(files)
        
    def open_file_dialog(self, event):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            f"Video Files ({' '.join(f'*{ext}' for ext in SUPPORTED_VIDEO_EXTENSIONS)})"
        )
        if files:
            self.add_files(files)
            
    def add_files(self, files):
        valid_files = [f for f in files if any(f.lower().endswith(ext) for ext in SUPPORTED_VIDEO_EXTENSIONS)]
        self.selected_files.extend(valid_files)
        self.files_list.clear()
        self.files_list.addItems([f.split('/')[-1] for f in self.selected_files])
        self.process_btn.setEnabled(len(self.selected_files) > 0)
        self.update_status()
        
    def update_status(self):
        count = len(self.selected_files)
        self.status_label.setText(f'Selected {count} file{"s" if count != 1 else ""}')
        
    def process_files(self):
        if not self.selected_files:
            return
            
        self.progress_bar.setMaximum(len(self.selected_files))
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.process_btn.setEnabled(False)
        self.status_label.setText('Analyzing files...')
        
        try:
            # Analyze files
            results = self.processor.analyze_files(self.selected_files)
            
            # Process each file
            for i, result in enumerate(results):
                if result.get('series_info') and result.get('episode_info'):
                    metadata = {
                        'file_path': result['file_path'],
                        'series_name': result['series_info']['name'],
                        'season_number': result['episode_info']['seasonNumber'],
                        'episode_number': result['episode_info']['number'],
                        'episode_title': result['episode_info']['name'],
                        'series_info': result['series_info'],
                        'episode_info': result['episode_info']
                    }
                    
                    success = self.processor.apply_tags(metadata, self.lang_combo.currentText().lower()[:3])
                    if not success:
                        QMessageBox.warning(self, 'Error', f'Failed to process {result["filename"]}')
                        
                self.progress_bar.setValue(i + 1)
                
            self.status_label.setText('Processing complete!')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error processing files: {str(e)}')
            
        finally:
            self.progress_bar.hide()
            self.process_btn.setEnabled(True)
            self.selected_files.clear()
            self.files_list.clear()
            self.update_status() 