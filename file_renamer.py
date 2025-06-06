import sys
import os
from pathlib import Path
import shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QCheckBox, 
                             QPushButton, QFileDialog, QListWidget)
from PySide6.QtCore import Qt


class FileRenamer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Renamer")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.original_files = []  # To store original filenames for undo
        self.renamed_files = []   # To store renamed filenames
        self.excluded_files = ["file_renamer.py", "file_renamer.exe"]  # Files to exclude from renaming
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Text input section
        text_layout = QHBoxLayout()
        text_label = QLabel("Text:")
        self.text_input = QLineEdit()
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_input)
        main_layout.addLayout(text_layout)
        
        # Checkbox section
        checkbox_layout = QHBoxLayout()
        self.before_checkbox = QCheckBox("Before filename")
        self.after_checkbox = QCheckBox("After filename")
        checkbox_layout.addWidget(self.before_checkbox)
        checkbox_layout.addWidget(self.after_checkbox)
        main_layout.addLayout(checkbox_layout)
        
        # Folder selection section
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Current folder: " + os.getcwd())
        self.folder_label.setWordWrap(True)
        folder_button = QPushButton("Select Folder")
        folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(folder_button)
        main_layout.addLayout(folder_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        start_button = QPushButton("Start Renaming")
        start_button.clicked.connect(self.rename_files)
        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.undo_rename)
        button_layout.addWidget(start_button)
        button_layout.addWidget(undo_button)
        main_layout.addLayout(button_layout)
        
        # File list display
        self.file_list = QListWidget()
        main_layout.addWidget(QLabel("Files in selected folder:"))
        main_layout.addWidget(self.file_list)
        
        # Set main widget
        self.setCentralWidget(main_widget)
        
        # Initial file list update
        self.update_file_list()
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", os.getcwd())
        if folder:
            os.chdir(folder)
            self.folder_label.setText("Current folder: " + folder)
            self.update_file_list()
            
    def update_file_list(self):
        self.file_list.clear()
        for item in os.listdir():
            if os.path.isfile(item):
                self.file_list.addItem(item)
    
    def rename_files(self):
        text = self.text_input.text()
        if not text:
            return
            
        before = self.before_checkbox.isChecked()
        after = self.after_checkbox.isChecked()
        
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
                
            name, ext = os.path.splitext(filename)
            new_name = name
            
            if before:
                new_name = text + new_name
            if after:
                new_name = new_name + text
                
            new_filename = new_name + ext
            
            if new_filename != filename:
                self.original_files.append(filename)
                self.renamed_files.append(new_filename)
                shutil.move(filename, new_filename)
                
        self.update_file_list()
    
    def undo_rename(self):
        for i in range(len(self.renamed_files)):
            if os.path.exists(self.renamed_files[i]):
                shutil.move(self.renamed_files[i], self.original_files[i])
                
        self.original_files = []
        self.renamed_files = []
        self.update_file_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileRenamer()
    window.show()
    sys.exit(app.exec())