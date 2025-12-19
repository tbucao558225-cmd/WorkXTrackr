staff_table_widget.py
# ui/staff_table_widget.py
"""
Staff Table Widget for Admin Dashboard
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from database.database import Database


class StaffTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.setup_ui()
        self.load_staff_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title_label = QLabel("Staff Accounts")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #004c8c; padding: 5px;")
        layout.addWidget(title_label)

        # Create table
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        layout.addWidget(self.table_widget)

    def load_staff_data(self):
        """Load and display all staff accounts"""
        try:
            # Get all staff accounts
            staff_query = """
            SELECT 
                u.id,
                u.username,
                u.full_name,
                u.email,
                u.role,
                u.created_at,
                ed.department,
                ed.position,
                ed.employment_date,
                ed.contact_number,
                ed.status as employee_status
            FROM users u
            LEFT JOIN employee_details ed ON u.id = ed.user_id
            WHERE u.role = 'staff'
            ORDER BY u.full_name
            """

            staff_results = self.db.execute_query(staff_query)

            if not staff_results:
                self.table_widget.setRowCount(1)
                self.table_widget.setColumnCount(1)
                self.table_widget.setItem(0, 0, QTableWidgetItem("No staff accounts found"))
                return

            # Setup table headers
            headers = ['Employee ID', 'Full Name', 'Username', 'Email',
                       'Department', 'Position', 'Status', 'Contact']
            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)
            self.table_widget.setRowCount(len(staff_results))

            # Fill table with data
            for row, staff in enumerate(staff_results):
                # Employee ID
                id_item = QTableWidgetItem(f"EMP{staff['id']}")
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, 0, id_item)

                # Full Name
                name_item = QTableWidgetItem(staff['full_name'] or 'N/A')
                self.table_widget.setItem(row, 1, name_item)

                # Username
                username_item = QTableWidgetItem(staff['username'] or 'N/A')
                self.table_widget.setItem(row, 2, username_item)

                # Email
                email_item = QTableWidgetItem(staff['email'] or 'N/A')
                self.table_widget.setItem(row, 3, email_item)

                # Department
                dept_item = QTableWidgetItem(staff['department'] or 'N/A')
                dept_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, 4, dept_item)

                # Position
                position_item = QTableWidgetItem(staff['position'] or 'N/A')
                position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, 5, position_item)

                # Status with color coding
                status = staff['employee_status'] or 'active'
                status_item = QTableWidgetItem(status.capitalize())
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if status.lower() == 'active':
                    status_item.setForeground(QColor(76, 175, 80))  # Green
                elif status.lower() == 'inactive':
                    status_item.setForeground(QColor(244, 67, 54))  # Red
                elif status.lower() == 'on_leave':
                    status_item.setForeground(QColor(255, 152, 0))  # Orange
                else:
                    status_item.setForeground(QColor(158, 158, 158))  # Gray

                self.table_widget.setItem(row, 6, status_item)

                # Contact
                contact_item = QTableWidgetItem(staff['contact_number'] or 'N/A')
                self.table_widget.setItem(row, 7, contact_item)

            # Style the table
            self.table_widget.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    alternate-background-color: #f8f8f8;
                    gridline-color: #e0e0e0;
                    font-size: 10pt;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QHeaderView::section {
                    background-color: #00aaff;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border: 1px solid #d0d0d0;
                    font-size: 10pt;
                }
            """)

            # Resize columns to fit content
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.table_widget.horizontalHeader().setStretchLastSection(True)

            # Enable sorting
            self.table_widget.setSortingEnabled(True)

            # Update title with count
            title_label = self.findChild(QLabel)
            if title_label:
                title_label.setText(f"Staff Accounts ({len(staff_results)} Employees)")

        except Exception as e:
            print(f"Error loading staff data: {e}")
            self.table_widget.setRowCount(1)
            self.table_widget.setColumnCount(1)
            self.table_widget.setItem(0, 0, QTableWidgetItem(f"Error loading data: {str(e)}"))
