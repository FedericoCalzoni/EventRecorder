#!/usr/bin/env python3

from PyQt6.QtWidgets import (
    QApplication, 
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QPlainTextEdit,
    QSizePolicy,
    QLabel,
    QDialog,
    QCheckBox,
    QGridLayout,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import QTimer, QUrl, Qt, QSize
from PyQt6.QtGui import QTextCursor, QDesktopServices, QFont
from datetime import datetime
import csv
import sys
import configparser
import os


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("File Selection")

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
        
        # Set the size of the dialog to its current size and remove the maximize button
        size_hint = self.layout().sizeHint()
        adjusted_size = QSize(size_hint.width() + 20, size_hint.height() + 50)
        self.setFixedSize(adjusted_size)
        self.setWindowFlag(Qt.WindowType.Dialog, True)

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
                
    def create_config(self):
        config = configparser.ConfigParser()
        config['BUTTONS'] = {'Button1': 'These are',
                             'Button2': 'customizable buttons.',
                             'Button3': 'You can',
                             'Button4': 'customize them',
                             'Button5': 'by changing',
                             'Button6': 'the config file.'}
        
        # Choose the directory for the config file based on the operating system
        if os.name == 'nt':  # Windows
            home_dir = os.path.expanduser('~')
            config_dir = os.path.join(home_dir, 'AppData', 'Roaming')
        else:  # Linux and other Unix-like systems
            # Get the XDG_CONFIG_HOME directory, falling back to ~/.config if it's not set
            config_dir = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
                        
        # Create the config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)

        config_file_path = os.path.join(config_dir, 'EventRecorder.ini')

        # Only create the config file if it doesn't already exist
        if not os.path.exists(config_file_path):
            with open(config_file_path, 'w') as configfile:
                configfile.write("; You can add as many buttons as you want!\n")
                configfile.write("; Add new lines with the format:\n")
                configfile.write("; 'ButtonName = ButtonText'\n")
                configfile.write("; Just make sure to have different ButtonName for each button!\n")
                config.write(configfile)
        else: #  replace [DEFAULT] with [BUTTONS] (due to a braking change). TODO: the whole else should be removed in the future. No one should have [DEFAULT] in their config file.
            with open(config_file_path, 'r') as configfile:                 
                file_contents = configfile.read()                           
            file_contents = file_contents.replace('[DEFAULT]', '[BUTTONS]') 
            with open(config_file_path, 'w') as configfile:
                configfile.write(file_contents)

        return config_file_path
    
    def __init__(self):
        super().__init__()
        
        QApplication.instance().focusChanged.connect(self.check_focus)
             
        self.csv_file_path = ''
        self.stop_clock_when_typing = QCheckBox('Stop clock when typing')
        self.event_entry = QPlainTextEdit()
        self.clock_label = QLineEdit()
        
        config_file_path = self.create_config()
        
        
        self.setWindowTitle("Event Recorder")
        self.setGeometry(100, 100, 950, 400)
                
        self.timer = QTimer()
        self.timer.start(200)  # Update every 0.2 seconds
        self.timer.timeout.connect(self.update_clock)
        
        self.main_layout = QHBoxLayout()

        self.left_column_layout = QVBoxLayout()
        self.right_column_layout = QVBoxLayout()
        
        self.file_path_layout = QHBoxLayout()
        self.file_path_layout.addWidget(QLabel("File Path:"))
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.file_path_display.setText(self.csv_file_path) 
        self.file_path_layout.addWidget(self.file_path_display)
        self.left_column_layout.addLayout(self.file_path_layout)
        
        self.load_grid = QGridLayout()
        self.right_column_layout.addLayout(self.load_grid)

        self.save_button = QPushButton('Save to new path')
        self.save_button.clicked.connect(self.choose_save_location)
        self.load_grid.addWidget(self.save_button, 0, 0)

        self.load_button = QPushButton('Load File')
        self.load_button.clicked.connect(self.load_csv)
        self.load_grid.addWidget(self.load_button, 0, 1)
        
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)  # Adjust this to match the number of columns in your CSV
        self.table.setHorizontalHeaderLabels(["Date", "Time", "Event"])  # Adjust these to match the headers of your CSV
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.itemChanged.connect(self.update_table)
        self.table.setFont(QFont("TypeWriter"))
        self.table.itemDoubleClicked.connect(self.copy_to_entry)
        self.left_column_layout.addWidget(self.table)
        
        self.event_entry.setPlaceholderText("Type text here, or copy from table by double-click")
        self.event_entry.setFont(QFont("TypeWriter"))
        self.event_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.event_entry.blockCountChanged.connect(self.check_for_enter)
        self.right_column_layout.addWidget(QLabel("New Event:"))
        self.time_layout = QHBoxLayout()
        self.time_layout.addWidget(self.clock_label)
        self.right_column_layout.addLayout(self.time_layout)
        self.right_column_layout.addWidget(self.event_entry)
        
        #TODO to remove in the future
        self.auto_delete_checkbox = QCheckBox('Clear event after recording')
        self.auto_delete_checkbox.setChecked(True)
        self.right_column_layout.addWidget(self.auto_delete_checkbox)
        
        self.stop_clock_when_typing.setChecked(False)
        self.right_column_layout.addWidget(self.stop_clock_when_typing)

        self.record_button = QPushButton('Record Event (Press Enter)')
        self.record_button.clicked.connect(lambda: self.record_event(self.event_entry.toPlainText().strip(), None, self.update_clock(False)))
        self.right_column_layout.addWidget(self.record_button)

        self.delete_button = QPushButton('Delete Selected')
        self.delete_button.clicked.connect(self.delete_selected)
        self.right_column_layout.addWidget(self.delete_button)
        
        self.button1_grid = QGridLayout()
        
        self.button2_grid = QGridLayout()
                
        self.load_config(config_file_path)

        # Add the grid to the right column layout
        self.left_column_layout.addLayout(self.button2_grid)
        
        self.open_config_button = QPushButton('Open Config File')
        self.reload_button = QPushButton('Reload Config File')
        self.open_config_button.clicked.connect(self.open_config)
        self.button1_grid.addWidget(self.open_config_button, 0, 0)
        self.reload_button.clicked.connect(lambda: self.load_config(config_file_path))
        self.button1_grid.addWidget(self.reload_button, 0, 1)
        self.left_column_layout.addLayout(self.button1_grid)
                
        self.main_layout.addLayout(self.left_column_layout)
        self.main_layout.addLayout(self.right_column_layout)

        self.setLayout(self.main_layout)
        
        # to show the UI before the dialog
        QTimer.singleShot(0, self.choose_file)
        
    def check_focus(self, old, new):
        if new != self.table and new != self.delete_button:
            self.table.clearSelection()
                
    def update_clock(self, forced=False):
        current_time = self.clock_label.text()
        if forced or not self.stop_clock_when_typing.isChecked() or self.event_entry.toPlainText().strip() == '':
            date = datetime.now().strftime("%Y-%m-%d")
            time = datetime.now().strftime("%H:%M:%S")
            current_time = date + ", " + time
            self.clock_label.setText(current_time)
            self.clock_label.setStyleSheet("background-color: rgb(230, 230, 230)")
            self.clock_label.setReadOnly(True)
        else:
            self.clock_label.setReadOnly(False)
            self.clock_label.setStyleSheet("background-color: none")
        return current_time
          
    
    def write_table_to_csv(self):
        with open(self.csv_file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            for row in range(self.table.rowCount()):
                row_data = []
                for column in range(self.table.columnCount()):
                    item = self.table.item(self.table.visualRow(row), column)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                writer.writerow(row_data)

    def record_event(self, text=None, button=None, current_time=None):
        event_text = text if text is not None else self.event_entry.toPlainText().strip()
        
        if not event_text:  # If event_text is empty
            self.event_entry.clear() # to prevent enter key from being recorded
            return  # Return early
        
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, QTableWidgetItem(current_time.split(", ", 1)[0]))
        self.table.setItem(row_count, 1, QTableWidgetItem(current_time.split(", ", 1)[1]))
        self.table.setItem(row_count, 2, QTableWidgetItem(event_text))
        self.table.scrollToItem(self.table.item(row_count, 0))

        self.write_table_to_csv()
        
        if self.auto_delete_checkbox.isChecked() and button is None:        
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
        
        self.update_table()
        
    def update_table(self):
        if self.table.rowCount() == 0:
            # inform user that there are no events
            self.table.setStyleSheet("background-color: rgb(230, 230, 230)")
        else:
            self.table.setStyleSheet("background-color: none")
        
        # Sort the table by date and time
        self.table.sortItems(1)
        self.table.sortItems(0)
        
        self.write_table_to_csv()
                    

    def delete_selected(self):
        selected_rows = list(set(index.row() for index in self.table.selectionModel().selectedRows()))
        if not selected_rows:  # If no whole rows are selected, get rows of selected items
            selected_rows = list(set(item.row() for item in self.table.selectedItems()))
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)

        self.write_table_to_csv()
        self.update_table()

    def choose_save_location(self):
        try:
            file, _ = QFileDialog.getSaveFileName(self,"Select Location to Save CSV File", "untitled.csv","CSV Files (*.csv)")
            if file:
                self.csv_file_path = file
                self.file_path_display.setText(file)
                
                # Write the current events to the new file
                with open(file, mode="w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    for row in range(self.table.rowCount()):
                        row_data = []
                        for column in range(self.table.columnCount()):
                            item = self.table.item(row, column)
                            if item is not None:
                                row_data.append(item.text())
                            else:
                                row_data.append('')
                        writer.writerow(row_data)
                
                # Load the events from the new file
                self.table.setRowCount(0) 
                with open(file, mode="r", newline="") as csv_file:
                    reader = csv.reader(csv_file)
                    for row in reader:
                        row_num = self.table.rowCount()
                        self.table.insertRow(row_num)
                        for col_num, data in enumerate(row):
                            self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
            self.update_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving file: {e}")
            self.choose_file()
    
    def load_csv(self):
        try:
            file, _ = QFileDialog.getOpenFileName(self,"Select CSV File to Open", "","CSV Files (*.csv);;All Files (*)")
            if file:
                self.csv_file_path = file
                self.table.setRowCount(0)  # Clear the table
                with open(file, mode="r", newline="") as csv_file:
                    reader = csv.reader(csv_file)
                    for row in reader:
                        row_num = self.table.rowCount()
                        self.table.insertRow(row_num)
                        for col_num, data in enumerate(row):
                            self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
                self.file_path_display.setText(file)
            self.update_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading file, not a valid CSV: {e}")
            self.choose_file()
        
    #Custom buttons
    def load_config(self, config_file_path):
        try:
            config = configparser.ConfigParser()
            config.read(config_file_path)
            
            # Remove all buttons from the grid layout
            for i in reversed(range(self.button2_grid.count())):
                widget_to_remove = self.button2_grid.itemAt(i).widget()
                self.button2_grid.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)
            
            # Add the buttons from the config file
            for index, (button_name, button_text) in enumerate(config['BUTTONS'].items()):
                # Limit the displayed text to 25 characters
                displayed_text = button_text[:25] + '...' if len(button_text) > 25 else button_text
                button = QPushButton(displayed_text)
                button.clicked.connect(lambda checked, button_text=button_text: self.record_event(button_text, button, self.update_clock(True)))
                row = index // 3  # Integer division to get the row number
                col = index % 3  # Remainder to get the column number
                self.button2_grid.addWidget(button, row, col)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Malformed config file: {e} \n\nPlease check the config file by clicking the 'Open Config File' button.\n\nThe structure should be the following:\n\n[BUTTONS]\nButton1=text1\nButton2=text2\n...")
    
                    
    def choose_file(self):
        dialog = CustomDialog(self)
        dialog.setModal(True)
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
        if item is not None:
            self.event_entry.setPlainText(item.text())
        else:
            self.event_entry.setPlainText("")
        
    def check_for_enter(self):
        text = self.event_entry.toPlainText()
        if text and text[-1] == "\n":
            self.record_event(text.strip(), None, self.update_clock(False))
            
    def open_config(self):
            home_dir = os.path.expanduser('~')

            if os.name == 'nt':  # Windows
                home_dir = os.path.expanduser('~')
                config_dir = os.path.join(home_dir, 'AppData', 'Roaming')
            else:  # Linux and other Unix-like systems
                # Get the XDG_CONFIG_HOME directory, falling back to ~/.config if it's not set
                config_dir = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

            config_file_path = os.path.join(config_dir, 'EventRecorder.ini')

            # Open the config file with the default application
            QDesktopServices.openUrl(QUrl.fromLocalFile(config_file_path))
            

def main():
    app = QApplication(sys.argv)
    
    window = EventRecorder()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()