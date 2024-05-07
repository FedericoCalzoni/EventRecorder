#!/usr/bin/env python3

from PyQt6.QtWidgets import (
    QApplication, 
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLineEdit,
    QFileDialog,
    QPlainTextEdit,
    QSizePolicy,
    QLabel,
    QDialog,
    QCheckBox
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCursor
from datetime import datetime
import csv
import sys

class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Event Recorder")

        layout = QVBoxLayout()

        label = QLabel("Would you like to create a new file or load an existing one?")
        layout.addWidget(label)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()

        self.newButton = QPushButton("Create New")
        self.newButton.clicked.connect(self.on_new)
        button_layout.addWidget(self.newButton)

        self.loadButton = QPushButton("Load Existing")
        self.loadButton.clicked.connect(self.on_load)
        button_layout.addWidget(self.loadButton)

        # Add the horizontal layout to the main layout
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.clicked_button = None

    def on_new(self):
        self.clicked_button = 'new'
        self.accept()

    def on_load(self):
        self.clicked_button = 'load'
        self.accept()

    def on_exit(self):
        self.clicked_button = 'exit'
        self.reject()

class EventRecorder(QWidget):
    def __init__(self):
        super().__init__()
                
        self.csv_file_path = ''
        
        self.setWindowTitle("Event Recorder")
        self.setGeometry(100, 100, 950, 400)
                
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second
        
        self.main_layout = QHBoxLayout()

        self.left_column_layout = QVBoxLayout()
        self.right_column_layout = QVBoxLayout()
        
        self.file_path_layout = QHBoxLayout()
        self.save_button = QPushButton('Save to new path')
        self.save_button.clicked.connect(self.choose_save_location)
        self.right_column_layout.addWidget(self.save_button)
        self.file_path_layout.addWidget(QLabel("File Path:"))
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.file_path_display.setText(self.csv_file_path) 
        self.file_path_layout.addWidget(self.file_path_display)
        self.left_column_layout.addLayout(self.file_path_layout)
        
        self.load_button = QPushButton('Load File')
        self.load_button.clicked.connect(self.load_csv)
        self.right_column_layout.addWidget(self.load_button)        

        self.listbox_label = QLabel("Event List: (double click to copy)")
        self.left_column_layout.addWidget(self.listbox_label)

        self.listbox = QListWidget()
        self.listbox.itemDoubleClicked.connect(self.copy_to_entry) 
        self.left_column_layout.addWidget(self.listbox)
        
        self.time_layout = QHBoxLayout()
        self.time_layout.addWidget(QLabel("Current Time:"))
        self.clock_label = QLineEdit()
        self.clock_label.setReadOnly(True)
        self.time_layout.addWidget(self.clock_label)
        self.right_column_layout.addLayout(self.time_layout)
        
        self.event_entry = QPlainTextEdit()
        self.event_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.event_entry.blockCountChanged.connect(self.check_for_enter)
        self.right_column_layout.addWidget(QLabel("Enter Event:"))
        self.right_column_layout.addWidget(self.event_entry)
        
        self.auto_delete_checkbox = QCheckBox('Clear event after recording')
        self.auto_delete_checkbox.setChecked(True)
        self.right_column_layout.addWidget(self.auto_delete_checkbox)

        self.record_button = QPushButton('Record Event (Press Enter)')
        self.record_button.clicked.connect(self.record_event)
        self.right_column_layout.addWidget(self.record_button)

        self.delete_button = QPushButton('Delete Selected')
        self.delete_button.clicked.connect(self.delete_selected)
        self.right_column_layout.addWidget(self.delete_button)
        
        self.choose_file()

        self.main_layout.addLayout(self.left_column_layout)
        self.main_layout.addLayout(self.right_column_layout)

        self.setLayout(self.main_layout)
        
    def update_clock(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.setText(current_time)

    def record_event(self):
        event_text = self.event_entry.toPlainText().strip()
        if not event_text:  # If event_text is empty
            return  # Return early

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.listbox.addItem(f"{current_time}: {event_text}")
        self.listbox.scrollToItem(self.listbox.item(self.listbox.count() - 1))  # Scroll to the last item

        # Write to the CSV file
        with open(self.csv_file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            for i in range(self.listbox.count()):
                writer.writerow(self.listbox.item(i).text().split(": ", 1))
        
        if self.auto_delete_checkbox.isChecked():        
            self.event_entry.clear()
        else:
            current_text = self.event_entry.toPlainText()
            parts = current_text.rsplit('\n', 1)
            cleaned_text = ''.join(parts)
            self.event_entry.setPlainText(cleaned_text)
            
            # Move the cursor to the end of the text
            cursor = self.event_entry.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.event_entry.setTextCursor(cursor)
                    

    def delete_selected(self):
        for item in self.listbox.selectedItems():
            self.listbox.takeItem(self.listbox.row(item))

        # Update the CSV file
        with open(self.csv_file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            for i in range(self.listbox.count()):
                writer.writerow(self.listbox.item(i).text().split(": ", 1))

    def choose_save_location(self):
        file, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "","CSV Files (*.csv)")
        if file:
            if not file.endswith('.csv'):
                file += '.csv'
            self.csv_file_path = file
            self.file_path_display.setText(file)
            
            # Write the current events to the new file
            with open(file, mode="w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                for i in range(self.listbox.count()):
                    writer.writerow(self.listbox.item(i).text().split(": ", 1))
            
            # Load the events from the new file
            self.listbox.clear()
            with open(file, mode="r", newline="") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    self.listbox.addItem(f"{row[0]}: {row[1]}")
    
    def load_csv(self):
        file, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","CSV Files (*.csv)")
        if file:
            self.csv_file_path = file
            self.listbox.clear()
            with open(file, mode="r", newline="") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    self.listbox.addItem(f"{row[0]}: {row[1]}")
            self.file_path_display.setText(file)
    
                    
    def choose_file(self):
        dialog = CustomDialog(self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # If "Create New" was clicked in the dialog
            if dialog.clicked_button == 'new':
                self.choose_save_location()
            # If "Load Existing" was clicked in the dialog
            elif dialog.clicked_button == 'load':
                self.load_csv()
        elif result == QDialog.DialogCode.Rejected:
            sys.exit()

        if self.csv_file_path == '':
            self.choose_file()
            
    def copy_to_entry(self, item):
        text_parts = item.text().split(": ", 1)
        if len(text_parts) > 1 and text_parts[1]:
            self.event_entry.setPlainText(text_parts[1])
        else:
            self.event_entry.setPlainText("")
        
    def check_for_enter(self, block_count):
        text = self.event_entry.toPlainText()
        if text and text[-1] == "\n":
            self.record_event()

def main():
    app = QApplication(sys.argv)
    
    window = EventRecorder()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()