import sys
import os
from pathlib import Path
import shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QCheckBox, 
                             QPushButton, QFileDialog, QListWidget, QGroupBox,
                             QRadioButton, QButtonGroup, QSlider, QFrame,
                             QTextEdit, QGridLayout)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QMouseEvent


class SwitchControl(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setMinimum(0)
        self.setMaximum(1)
        self.setFixedWidth(40)
        self.setFixedHeight(20)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #555555;
                height: 10px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #999999;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                height: 10px;
                border-radius: 5px;
            }
        """)
        # Make the slider clickable
        self.setPageStep(1)
        
    def mousePressEvent(self, event):
        # Toggle value on click
        if event.button() == Qt.LeftButton:
            if self.value() == 0:
                self.setValue(1)
            else:
                self.setValue(0)
            event.accept()
        else:
            super().mousePressEvent(event)


class FileRenamer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Renamer")
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2D2D2D;
                color: white;
            }
            QLineEdit, QTextEdit {
                background-color: #3D3D3D;
                border: 1px solid #555555;
                border-radius: 3px;
                color: white;
                padding: 2px 4px;
            }
            QPushButton {
                background-color: #444444;
                border: 1px solid #555555;
                border-radius: 3px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QListWidget {
                background-color: #3D3D3D;
                border: 1px solid #555555;
                border-radius: 3px;
                color: white;
            }
        """)
        
        self.original_files = []  # To store original filenames for undo
        self.renamed_files = []   # To store renamed filenames
        self.excluded_files = ["file_renamer.py", "file_renamer.exe"]  # Files to exclude from renaming
        self.is_updating = False  # Flag to prevent recursive signal handling
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Text input section
        text_layout = QHBoxLayout()
        text_label = QLabel("Text:")
        self.text_input = QLineEdit()
        self.text_input.textChanged.connect(self.on_settings_changed)
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_input)
        main_layout.addLayout(text_layout)
        
        # Options group
        options_group = QGroupBox("Renamer Options")
        options_layout = QGridLayout()
        
        # Add label for description
        options_layout.addWidget(QLabel("Text:"), 0, 0)
        
        # Mode switch (Add/Remove)
        mode_label = QLabel("Add")
        self.mode_switch = SwitchControl()
        self.mode_switch.valueChanged.connect(self.on_settings_changed)
        mode_label2 = QLabel("Remove")
        
        options_layout.addWidget(mode_label, 1, 0)
        options_layout.addWidget(self.mode_switch, 1, 1)
        options_layout.addWidget(mode_label2, 1, 2)
        
        # Before filename switch
        before_label = QLabel("Before")
        self.before_switch = SwitchControl()
        self.before_switch.valueChanged.connect(self.on_settings_changed)
        
        options_layout.addWidget(before_label, 2, 0)
        options_layout.addWidget(self.before_switch, 2, 1)
        
        # After filename switch
        after_label = QLabel("After")
        self.after_switch = SwitchControl()
        self.after_switch.valueChanged.connect(self.on_settings_changed)
        
        options_layout.addWidget(after_label, 3, 0)
        options_layout.addWidget(self.after_switch, 3, 1)
        
        # Add buttons to options layout
        change_folder_btn = QPushButton("Change Folder")
        change_folder_btn.clicked.connect(self.select_folder)
        start_button = QPushButton("Start Renaming")
        start_button.clicked.connect(self.rename_files)
        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.undo_rename)
        
        options_layout.addWidget(change_folder_btn, 1, 3)
        options_layout.addWidget(start_button, 2, 3)
        options_layout.addWidget(undo_button, 3, 3)
        
        # Set columns stretch
        options_layout.setColumnStretch(0, 1)
        options_layout.setColumnStretch(1, 0)
        options_layout.setColumnStretch(2, 1)
        options_layout.setColumnStretch(3, 2)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Folder selection section
        self.folder_label = QLabel("Current folder: " + os.getcwd())
        self.folder_label.setWordWrap(True)
        main_layout.addWidget(self.folder_label)
        
        # File list display
        main_layout.addWidget(QLabel("Files in selected folder:"))
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        main_layout.addWidget(self.file_list)
        
        # Preview section
        main_layout.addWidget(QLabel("Preview changes"))
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setMinimumHeight(150)
        main_layout.addWidget(self.preview_area)
        
        # Set main widget
        self.setCentralWidget(main_widget)
        
        # Initial file list update
        self.update_file_list()
        
        # Initial preview update - using a timer to avoid recursion during initialization
        QApplication.instance().processEvents()
        self.preview_changes()
    
    def on_settings_changed(self):
        """Single handler for all settings changes to prevent signal cascading"""
        if not self.is_updating:
            self.preview_changes()
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", os.getcwd())
        if folder:
            os.chdir(folder)
            self.folder_label.setText("Current folder: " + folder)
            self.update_file_list()
            self.preview_changes()
            
    def update_file_list(self):
        self.file_list.clear()
        for item in os.listdir():
            if os.path.isfile(item) and item not in self.excluded_files:
                self.file_list.addItem(item)
    
    def get_new_filename(self, filename):
        text = self.text_input.text()
        if not text:
            return filename
            
        before = self.before_switch.value() == 1
        after = self.after_switch.value() == 1
        add_mode = self.mode_switch.value() == 0  # 0 = Add, 1 = Remove
        
        if not (before or after):
            return filename
            
        name, ext = os.path.splitext(filename)
        new_name = name
        
        if add_mode:
            # Add text mode
            if before:
                new_name = text + new_name
            if after:
                new_name = new_name + text
        else:
            # Remove text mode (exact match)
            if before and name.startswith(text):
                new_name = name[len(text):]
            if after and name.endswith(text):
                new_name = name[:-len(text)]
                
        new_filename = new_name + ext
        return new_filename
    
    def preview_changes(self):
        # Set flag to prevent recursive calls
        self.is_updating = True
        
        try:
            self.preview_area.clear()
            text = self.text_input.text()
            if not text:
                self.preview_area.setText("Please enter text to add or remove.")
                return
                
            before = self.before_switch.value() == 1
            after = self.after_switch.value() == 1
            
            if not (before or after):
                self.preview_area.setText("Please select position (Before and/or After).")
                return
                
            mode = "Add" if self.mode_switch.value() == 0 else "Remove"
            changes = []
            
            file_list = [f for f in os.listdir() if os.path.isfile(f) and f not in self.excluded_files]
            
            for filename in file_list:
                new_filename = self.get_new_filename(filename)
                
                if new_filename != filename:
                    changes.append(f"{filename} → {new_filename}")
                    
            if changes:
                self.preview_area.setText(f"Mode: {mode}\n\n" + "\n".join(changes))
            else:
                self.preview_area.setText("No changes will be made with current settings.")
        finally:
            # Reset flag when done
            self.is_updating = False
    
    def rename_files(self):
        text = self.text_input.text()
        if not text:
            return
            
        before = self.before_switch.value() == 1
        after = self.after_switch.value() == 1
        
        if not (before or after):
            return
            
        self.original_files = []
        self.renamed_files = []
        
        for filename in os.listdir():
            if not os.path.isfile(filename):
                continue
                
            # Skip excluded files
            if filename in self.excluded_files:
                continue
                
            new_filename = self.get_new_filename(filename)
            
            if new_filename != filename:
                self.original_files.append(filename)
                self.renamed_files.append(new_filename)
                shutil.move(filename, new_filename)
                
        self.update_file_list()
        self.preview_changes()
    
    def undo_rename(self):
        for i in range(len(self.renamed_files)):
            if os.path.exists(self.renamed_files[i]):
                shutil.move(self.renamed_files[i], self.original_files[i])
                
        self.original_files = []
        self.renamed_files = []
        self.update_file_list()
        self.preview_changes()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileRenamer()
    window.show()
    sys.exit(app.exec())
