# request_dialog.py - FIXED VERSION (White Dropdown List Frame)
"""
Request Submission Dialog - Fixed White Dropdown and Calendar Buttons
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QDateEdit, QTextEdit, QPushButton,
                             QMessageBox, QFormLayout, QFrame,
                             QCalendarWidget, QWidget)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon
import datetime


class RequestDialog(QDialog):
    request_submitted = pyqtSignal(dict)  # Signal when request is submitted

    def __init__(self, parent=None, request_types=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.request_types = request_types or []

        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Submit Request")
        self.setFixedSize(550, 450)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 15, 20, 15)

        # Title
        title_label = QLabel("SUBMIT NEW REQUEST")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Request Form Frame
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Request Type
        type_label = QLabel("Request Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItem("-- Select Request Type --")
        for req_type in self.request_types:
            self.type_combo.addItem(req_type)
        form_layout.addRow(type_label, self.type_combo)

        # Request Date
        date_label = QLabel("Request Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDateRange(QDate.currentDate(), QDate.currentDate().addYears(1))
        form_layout.addRow(date_label, self.date_edit)

        # Reason
        reason_label = QLabel("Reason:")
        self.reason_text = QTextEdit()
        self.reason_text.setPlaceholderText("Enter detailed reason for your request...")
        self.reason_text.setMinimumHeight(120)
        self.reason_text.setMaximumHeight(150)
        form_layout.addRow(reason_label, self.reason_text)

        # Character counter
        self.char_counter = QLabel("0/500 characters")
        self.char_counter.setObjectName("charCounter")
        self.char_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.addRow("", self.char_counter)

        self.reason_text.textChanged.connect(self.update_char_counter)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        submit_btn = QPushButton("Submit Request")
        submit_btn.setObjectName("submitButton")
        submit_btn.clicked.connect(self.submit_request)
        button_layout.addWidget(submit_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)

    def setup_styles(self):
        """Setup all styles with FIXED WHITE background for both button and dropdown frame"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }

            QLabel {
                font-size: 11pt;
                color: #333333;
                background: transparent;
            }

            QLabel#titleLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #004c8c;
                padding-bottom: 5px;
                border-bottom: 2px solid #00aaff;
            }

            QFrame#formFrame {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }

            /* --- FIXED QComboBox --- */
            QComboBox {
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                min-height: 35px;
            }

            /* The actual frame/list that pops up */
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #00aaff;
                selection-background-color: #e6f7ff;
                selection-color: black;
                outline: none;
            }

            QComboBox::drop-down {
                border: none;
                background-color: white; 
                width: 30px;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #ffffff;
                margin-right: 8px;
            }

            /* --- FIXED QDateEdit --- */
            QDateEdit {
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                min-height: 35px;
            }
            QDateEdit::drop-down {
                border: none;
                background-color: white; 
                width: 30px;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #ffffff;
                margin-right: 8px;
            }

            QTextEdit {
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }

            QPushButton#submitButton {
                font-size: 11pt;
                font-weight: bold;
                padding: 8px 25px;
                border-radius: 4px;
                background-color: #00aaff;
                color: white;
                min-width: 140px;
            }
            QPushButton#submitButton:hover { background-color: #0088cc; }

            QPushButton#cancelButton {
                font-size: 11pt;
                padding: 8px 25px;
                border-radius: 4px;
                background-color: #f0f0f0;
                color: #333333;
                border: 1px solid #cccccc;
            }

            /* Calendar Frame */
            QCalendarWidget QWidget { background-color: white; }
            QCalendarWidget QToolButton {
                color: black;
                background-color: transparent;
                font-weight: bold;
            }
        """)

    def update_char_counter(self):
        text = self.reason_text.toPlainText()
        count = len(text)
        self.char_counter.setText(f"{count}/500 characters")
        if count > 450:
            self.char_counter.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.char_counter.setStyleSheet("color: #666666;")

    def submit_request(self):
        request_type = self.type_combo.currentText()
        request_date = self.date_edit.date().toString("yyyy-MM-dd")
        reason = self.reason_text.toPlainText().strip()

        if request_type == "-- Select Request Type --":
            self.show_error("Please select a request type")
            return
        if len(reason) < 10:
            self.show_error("Reason must be at least 10 characters")
            return

        request_data = {'type': request_type, 'date': request_date, 'reason': reason, 'user_id': self.user_id}
        self.request_submitted.emit(request_data)
        self.accept()

    def show_error(self, message):
        self.status_label.setText(f"⚠️ {message}")
        self.status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))