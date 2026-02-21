# viewer/add_employee_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox,
                             QFormLayout, QFrame, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import re


class AddEmployeeDialog(QDialog):
    employee_added = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):

        self.setWindowTitle("Register New Personnel")
        self.setFixedSize(550, 650)  # Increased from 450x500

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(35, 30, 35, 30)  # Spacing around the edges

        # --- HEADER ---
        title_label = QLabel("ADD NEW EMPLOYEE")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # --- FORM CONTAINER ---
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")

        # QFormLayout for clean alignment
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(18)  # Vertical gap between fields
        form_layout.setContentsMargins(25, 25, 25, 25)

        # Full Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full legal name")
        form_layout.addRow("Full Name:", self.name_input)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Desired username")
        form_layout.addRow("Username:", self.username_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@workxtrackr.com")
        form_layout.addRow("Email Address:", self.email_input)

        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Staff", "Manager", "Admin"])
        form_layout.addRow("System Role:", self.role_combo)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimum 6 characters")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Initial Password:", self.password_input)

        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-type password to verify")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm Pass:", self.confirm_password_input)

        main_layout.addWidget(form_frame)

        # --- BUTTONS ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Cancel Button
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedHeight(45)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Add Button
        add_btn = QPushButton("REGISTER PERSONNEL")
        add_btn.setObjectName("addButton")
        add_btn.setFixedHeight(45)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_employee)
        button_layout.addWidget(add_btn)

        main_layout.addLayout(button_layout)

        # Status label for errors
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

    def setup_styles(self):

        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel#titleLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #004c8c;
                border: none;
                border-bottom: 2px solid #00aaff;
                padding-bottom: 5px;
                background: transparent;
            }
            QFrame#formFrame {
                background-color: #fcfcfc;
                border: 1px solid #eee;
                border-radius: 10px;
            }
            QLabel {
                font-size: 11pt;
                color: #333;
                border: none;
                background: transparent;
            }
            /* --- FIXED: FORCE WHITE BACKGROUND --- */
            QLineEdit, QComboBox {
                font-size: 11pt;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white; 
            }

            /* Styles the popup list inside the dropbox */
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #ccc;
                selection-background-color: #e6f7ff;
                selection-color: black;
                outline: none;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #00aaff;
            }

            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 35px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #ffffff;
                margin-right: 10px;
            }

            QPushButton#addButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1C6099, stop:1 #00aaff);
                color: white;
                font-weight: bold;
                border-radius: 6px;
                border: none;
                min-width: 200px;
                font-size: 11pt;
            }
            QPushButton#addButton:hover { background: #0088cc; }

            QPushButton#cancelButton {
                background-color: #f1f1f1;
                color: #333;
                font-weight: bold;
                border-radius: 6px;
                border: none;
                min-width: 120px;
                font-size: 11pt;
            }
            QPushButton#cancelButton:hover { background-color: #e5e5e5; }
        """)

    def add_employee(self):
        """Validation and emitting data"""
        full_name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        role = self.role_combo.currentText().lower()
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()

        if not all([full_name, username, email, password]):
            self.show_error("All fields are required")
            return

        if "@" not in email or "." not in email:
            self.show_error("Invalid email address")
            return

        if len(password) < 6:
            self.show_error("Password is too short")
            return

        if password != confirm:
            self.show_error("Passwords do not match")
            return

        # Success
        employee_data = {
            'full_name': full_name,
            'username': username,
            'email': email,
            'role': role,
            'password': password
        }
        self.employee_added.emit(employee_data)
        self.accept()

    def show_error(self, message):
        self.status_label.setText(f"⚠️ {message}")
        self.status_label.setStyleSheet("color: #D75050; font-weight: bold; border: none;")