# request_dialog.py - FIXED DATE POPUP VERSION
"""
Request Submission Dialog - Fixed Date Popup
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

        # Request Date - SIMPLIFIED VERSION
        date_label = QLabel("Request Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)  # Enable calendar popup
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        # Set reasonable date range
        self.date_edit.setDateRange(
            QDate.currentDate(),
            QDate.currentDate().addYears(1)
        )

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
        self.char_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.addRow("", self.char_counter)

        # Connect character counter
        self.reason_text.textChanged.connect(self.update_char_counter)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        # Cancel Button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Submit Button
        submit_btn = QPushButton("Submit Request")
        submit_btn.setObjectName("submitButton")
        submit_btn.clicked.connect(self.submit_request)
        button_layout.addWidget(submit_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)

        # Set initial focus
        self.type_combo.setFocus()

    def setup_styles(self):
        """Setup all styles for clean white design"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }

            /* Labels */
            QLabel {
                font-size: 11pt;
                color: #333333;
                background: transparent;
            }

            QLabel[objectName="titleLabel"] {
                font-size: 16pt;
                font-weight: bold;
                color: #004c8c;
                padding-bottom: 5px;
                border-bottom: 2px solid #00aaff;
                background: transparent;
            }

            /* Form Frame */
            QFrame#formFrame {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }

            /* Input Fields */
            QComboBox {
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                min-height: 35px;
            }

            QComboBox:hover {
                border: 1px solid #999999;
            }

            QComboBox::drop-down {
                border: none;
                width: 30px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #666666;
                margin-right: 10px;
            }

            QComboBox QAbstractItemView {
                border: 1px solid #cccccc;
                background-color: white;
                selection-background-color: #e6f7ff;
                selection-color: black;
                padding: 5px;
                font-size: 11pt;
            }

            /* Date Edit - FIXED STYLING */
            QDateEdit {
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                min-height: 35px;
                min-width: 120px;
            }

            QDateEdit:hover {
                border: 1px solid #999999;
            }

            QDateEdit::drop-down {
                border: none;
                width: 30px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }

            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #666666;
            }

            /* Calendar Popup Styling */
            QCalendarWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }

            QCalendarWidget QToolButton {
                background-color: #f8f8f8;
                color: #333333;
                font-weight: bold;
                font-size: 11pt;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px 10px;
                margin: 2px;
                min-width: 60px;
                min-height: 25px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #e8e8e8;
                border: 1px solid #999999;
            }

            QCalendarWidget QToolButton#qt_calendar_prevmonth {
                qproperty-icon: none;
                qproperty-text: "<";
            }

            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                qproperty-icon: none;
                qproperty-text: ">";
            }

            QCalendarWidget QSpinBox {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
                min-width: 80px;
                font-size: 11pt;
            }

            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f8f8f8;
                border-bottom: 1px solid #cccccc;
                padding: 5px;
            }

            QCalendarWidget QAbstractItemView {
                background-color: white;
                selection-background-color: #e0e0e0;
                selection-color: white;
                outline: 0;
            }

            QCalendarWidget QHeaderView::section {
                background-color: #f0f0f0;
                color: #333333;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #e0e0e0;
            }

            /* Text Edit - ADDED BORDER */
            QTextEdit {
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }

            QTextEdit:hover {
                border: 1px solid #999999;
            }

            QTextEdit:focus {
                border: 2px solid #cccccc;
                outline: none;
            }

            /* Buttons */
            QPushButton#submitButton {
                font-size: 11pt;
                font-weight: bold;
                padding: 8px 25px;
                border-radius: 4px;
                border: 1px solid #00aaff;
                background-color: #00aaff;
                color: white;
                min-width: 140px;
            }

            QPushButton#submitButton:hover {
                background-color: #0088cc;
                border: 1px solid #0088cc;
            }

            QPushButton#submitButton:pressed {
                background-color: #006699;
            }

            QPushButton#cancelButton {
                font-size: 11pt;
                font-weight: normal;
                padding: 8px 25px;
                border-radius: 4px;
                border: 1px solid #cccccc;
                background-color: #f0f0f0;
                color: #333333;
                min-width: 100px;
            }

            QPushButton#cancelButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #999999;
            }

            QPushButton#cancelButton:pressed {
                background-color: #d0d0d0;
            }

            /* Character Counter */
            QLabel[objectName="charCounter"] {
                font-size: 9pt;
                color: #666666;
                background: transparent;
            }

            /* Status Label */
            QLabel[objectName="statusLabel"] {
                font-size: 10pt;
                background: transparent;
                padding: 5px;
                min-height: 20px;
            }
        """)

        # Set object names for specific styling
        title_label = self.findChild(QLabel, "", Qt.FindChildOption.FindDirectChildrenOnly)
        if title_label:
            title_label.setObjectName("titleLabel")

        self.char_counter.setObjectName("charCounter")
        self.status_label.setObjectName("statusLabel")

        # Set fonts
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Make labels transparent
        for label in self.findChildren(QLabel):
            label.setStyleSheet("background: transparent;")

    def update_char_counter(self):
        """Update character counter"""
        text = self.reason_text.toPlainText()
        count = len(text)
        self.char_counter.setText(f"{count}/500 characters")

        # Change color if approaching limit
        if count > 450:
            self.char_counter.setStyleSheet("""
                font-size: 9pt;
                color: #ff0000;
                font-weight: bold;
                background: transparent;
            """)
        elif count > 400:
            self.char_counter.setStyleSheet("""
                font-size: 9pt;
                color: #ff9900;
                background: transparent;
            """)
        else:
            self.char_counter.setStyleSheet("""
                font-size: 9pt;
                color: #666666;
                background: transparent;
            """)

    def submit_request(self):
        """Handle request submission"""
        # Validate
        request_type = self.type_combo.currentText()
        request_date = self.date_edit.date().toString("yyyy-MM-dd")
        reason = self.reason_text.toPlainText().strip()

        # Clear any previous status
        self.status_label.setText("")

        if request_type == "-- Select Request Type --":
            self.show_error("Please select a request type")
            self.type_combo.setFocus()
            return

        if not reason:
            self.show_error("Please enter a reason for your request")
            self.reason_text.setFocus()
            return

        if len(reason) < 10:
            self.show_error("Reason must be at least 10 characters")
            self.reason_text.setFocus()
            return

        if len(reason) > 500:
            self.show_error("Reason must be less than 500 characters")
            self.reason_text.setFocus()
            return

        # Validate date (should not be in past)
        selected_date = self.date_edit.date()
        today = QDate.currentDate()
        if selected_date < today:
            self.show_error("Request date cannot be in the past")
            self.date_edit.setFocus()
            return

        # Show submitting status
        self.status_label.setText("Submitting request...")
        self.status_label.setStyleSheet("color: #0066cc; font-weight: bold; background: transparent;")

        # Emit signal with request data
        request_data = {
            'type': request_type,
            'date': request_date,
            'reason': reason,
            'user_id': self.user_id
        }

        # Small delay to show status message
        QTimer.singleShot(300, lambda: self.finalize_submission(request_data))

    def finalize_submission(self, request_data):
        """Finalize the submission after delay"""
        self.request_submitted.emit(request_data)
        self.accept()

    def show_error(self, message):
        """Show error message"""
        self.status_label.setText(f"⚠️ {message}")
        self.status_label.setStyleSheet("""
            color: #ff0000;
            font-weight: bold;
            background: transparent;
        """)

        # Clear error after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Check if submit button has focus
            submit_btn = self.findChild(QPushButton, "submitButton")
            if submit_btn and submit_btn.hasFocus():
                self.submit_request()
            else:
                event.ignore()
        else:
            super().keyPressEvent(event)