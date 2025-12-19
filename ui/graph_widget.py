# ui/graph_widget.py - ORIGINAL DESIGNS
"""
Graph Widget for Admin Dashboard - ORIGINAL DESIGNS
"""
import sys
import os

# Try to import matplotlib with error handling
try:
    import matplotlib

    matplotlib.use('Qt5Agg')

    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np

    MATPLOTLIB_AVAILABLE = True
    print("✅ Matplotlib loaded successfully")

except Exception as e:
    print(f"❌ Matplotlib import error: {e}")
    MATPLOTLIB_AVAILABLE = False
    FigureCanvas = None
    Figure = None
    np = None

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QHeaderView, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta
from database.database import Database


class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.current_graph_type = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI for graphs"""
        # Main layout with side-by-side arrangement
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Left side: Graph area with header
        left_container = QFrame()
        left_container.setObjectName("leftContainer")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)

        # Graph header
        graph_header = QLabel("VISUALIZATION")
        graph_header.setObjectName("graphHeader")
        graph_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(graph_header)

        # Create matplotlib figure for graph
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(6, 4), dpi=100, facecolor='#E6F7FF')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("""
                background-color: #E6F7FF; 
                border: 1px solid #00aaff; 
                border-radius: 8px;
            """)
            left_layout.addWidget(self.canvas)
        else:
            # Fallback if matplotlib not available
            self.figure = None
            self.canvas = None
            self.graph_placeholder = QLabel("Graphs Loading...")
            self.graph_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.graph_placeholder.setStyleSheet("""
                background-color: #E6F7FF;
                border: 1px solid #00aaff;
                border-radius: 8px;
                padding: 40px;
                font-size: 12pt;
                color: #1C6099;
                min-height: 250px;
            """)
            left_layout.addWidget(self.graph_placeholder)

        # Graph info label
        self.graph_info_label = QLabel("")
        self.graph_info_label.setObjectName("graphInfoLabel")
        self.graph_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_info_label.setWordWrap(True)
        left_layout.addWidget(self.graph_info_label)

        # Right side: Employee data area with header
        right_container = QFrame()
        right_container.setObjectName("rightContainer")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        # Data header
        data_header = QLabel("EMPLOYEE DATA")
        data_header.setObjectName("dataHeader")
        data_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(data_header)

        # Create table widget for data
        self.table_widget = QTableWidget()
        self.table_widget.setObjectName("employeeTable")
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("""
            QTableWidget#employeeTable {
                background-color: white;
                alternate-background-color: #f8f8f8;
                gridline-color: #e0e0e0;
                font-size: 10pt;
                font-family: 'Segoe UI', Arial;
                border: 1px solid #00aaff;
                border-radius: 8px;
            }
            QTableWidget#employeeTable::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableWidget#employeeTable::item:selected {
                background-color: #e6f7ff;
                color: black;
                border: none;
            }
            QHeaderView::section {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #73DFF3, stop:1 #1C6099);
                color: white;
                font-weight: bold;
                padding: 10px;
                border: 1px solid #00aaff;
                font-size: 10pt;
                font-family: 'Segoe UI', Arial;
            }
        """)

        # Set table properties
        self.table_widget.setShowGrid(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        right_layout.addWidget(self.table_widget)

        # Data summary label
        self.data_summary_label = QLabel("")
        self.data_summary_label.setObjectName("dataSummaryLabel")
        self.data_summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.data_summary_label)

        # Add both sides to main layout
        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(right_container, 1)

        # Set styles
        self.setStyleSheet("""
            QWidget {
                background-color: #E6F7FF;
            }
            QFrame#leftContainer, QFrame#rightContainer {
                background-color: #E6F7FF;
                border: 1px solid #00aaff;
                border-radius: 8px;
            }
            QLabel#graphHeader, QLabel#dataHeader {
                font-size: 14pt;
                font-weight: bold;
                font-family: 'Segoe UI';
                color: #004c8c;
                padding: 8px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #DFFFFF, stop:1 #73DFF3);
                border: 1px solid #00aaff;
                border-radius: 6px;
                margin-bottom: 5px;
            }
            QLabel#graphInfoLabel, QLabel#dataSummaryLabel {
                font-size: 10pt;
                font-weight: bold;
                color: #1C6099;
                padding: 6px;
                background-color: white;
                border: 1px solid #00aaff;
                border-radius: 6px;
                margin-top: 5px;
            }
        """)

    # Data fetching methods
    def get_present_data_from_db(self):
        """Get present employees data from database"""
        try:
            today = datetime.now().date().strftime('%Y-%m-%d')
            query = """
            SELECT 
                u.id,
                u.full_name,
                u.username,
                u.email,
                a.clock_in,
                a.status,
                a.late_minutes
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE DATE(a.date) = %s 
            AND (a.status = 'present' OR a.status = 'late')
            AND u.role = 'staff'
            ORDER BY a.clock_in
            """
            return self.db.execute_query(query, (today,))
        except Exception as e:
            print(f"Error getting present data: {e}")
            return []

    def get_late_data_from_db(self):
        """Get late employees data from database"""
        try:
            today = datetime.now().date().strftime('%Y-%m-%d')
            query = """
            SELECT 
                u.id,
                u.full_name,
                u.username,
                u.email,
                a.late_minutes,
                a.clock_in
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE DATE(a.date) = %s 
            AND a.status = 'late'
            AND u.role = 'staff'
            ORDER BY a.late_minutes DESC
            """
            return self.db.execute_query(query, (today,))
        except Exception as e:
            print(f"Error getting late data: {e}")
            return []

    def get_absent_data_from_db(self):
        """Get absent employees data from database"""
        try:
            today = datetime.now().date().strftime('%Y-%m-%d')

            # Get all staff
            staff_query = """
            SELECT 
                u.id,
                u.full_name,
                u.username,
                u.email
            FROM users u
            WHERE u.role = 'staff'
            ORDER BY u.full_name
            """
            all_staff = self.db.execute_query(staff_query)

            # Get staff who clocked in today
            present_query = """
            SELECT DISTINCT user_id 
            FROM attendance 
            WHERE DATE(date) = %s
            """
            present_staff_ids = self.db.execute_query(present_query, (today,))
            present_ids = [str(item['user_id']) for item in present_staff_ids]

            # Filter absent staff
            absent_staff = []
            for staff in all_staff:
                if str(staff['id']) not in present_ids:
                    absent_staff.append(staff)

            return absent_staff

        except Exception as e:
            print(f"Error getting absent data: {e}")
            return []

    def get_all_employees_data(self):
        """Get all employees data"""
        try:
            query = """
            SELECT 
                u.id,
                u.full_name,
                u.username,
                u.email
            FROM users u
            WHERE u.role = 'staff'
            ORDER BY u.full_name
            """
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Error getting all employees data: {e}")
            return []

    def get_on_leave_data_from_db(self):
        """Get on leave data from database"""
        try:
            today = datetime.now().date().strftime('%Y-%m-%d')
            query = """
            SELECT DISTINCT
                u.id,
                u.full_name,
                u.username,
                u.email,
                r.request_type as leave_type
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE u.role = 'staff' 
            AND r.status = 'approved'
            AND (r.request_type LIKE '%Leave%' OR r.request_type LIKE '%leave%')
            AND DATE(r.request_date) = %s
            ORDER BY u.full_name
            """
            return self.db.execute_query(query, (today,))
        except Exception as e:
            print(f"Error getting on-leave data: {e}")
            return []

    def update_table(self, employees, headers, title="Employee Data"):
        """Update the table widget with employee data"""
        self.table_widget.clear()
        self.table_widget.setRowCount(len(employees))
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        for i, emp in enumerate(employees):
            for j, header in enumerate(headers):
                if header == 'ID':
                    item = QTableWidgetItem(f"EMP{emp['id']}")
                elif header == 'Name':
                    item = QTableWidgetItem(emp['full_name'] or emp['username'] or 'N/A')
                elif header == 'Email':
                    item = QTableWidgetItem(emp['email'] or 'N/A')
                elif header == 'Clock In':
                    clock_in = emp.get('clock_in', '--:--')
                    if clock_in and not isinstance(clock_in, str):
                        clock_in = str(clock_in)
                    item = QTableWidgetItem(clock_in)
                elif header == 'Status':
                    item = QTableWidgetItem(emp.get('status', 'Present').title())
                elif header == 'Late (min)':
                    item = QTableWidgetItem(str(emp.get('late_minutes', 0) or 0))
                elif header == 'Leave Type':
                    item = QTableWidgetItem(emp.get('leave_type', 'N/A'))
                else:
                    item = QTableWidgetItem('')

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont("Segoe UI", 9))
                self.table_widget.setItem(i, j, item)

        # Resize columns
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setStretchLastSection(True)

        # Update label
        count = len(employees)
        self.data_summary_label.setText(
            f"Showing {count} employees | Last updated: {datetime.now().strftime('%I:%M %p')}")

    # ORIGINAL GRAPH DESIGNS
    def plot_present_graph(self):
        """Plot LINE GRAPH for present employees (ORIGINAL DESIGN)"""
        employees = self.get_present_data_from_db()
        self.current_graph_type = 'present'

        # Update table
        headers = ['ID', 'Name', 'Clock In', 'Status', 'Late (min)']
        self.update_table(employees, headers, "Present Employees")

        # Plot LINE GRAPH if matplotlib is available
        if MATPLOTLIB_AVAILABLE and self.figure:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#E6F7FF')
            self.figure.patch.set_facecolor('#E6F7FF')

            if employees:
                # Get data for last 7 days for line graph
                dates = []
                present_counts = []

                for i in range(7):
                    date = datetime.now().date() - timedelta(days=6 - i)
                    date_str = date.strftime('%Y-%m-%d')

                    query = """
                    SELECT COUNT(DISTINCT user_id) as count
                    FROM attendance 
                    WHERE DATE(date) = %s 
                    AND status IN ('present', 'late')
                    """
                    result = self.db.fetch_one(query, (date_str,))
                    count = result['count'] if result else 0

                    dates.append(date.strftime('%b %d'))
                    present_counts.append(count)

                # Plot line graph
                ax.plot(dates, present_counts, marker='o', linewidth=2, color='#4CAF50', markersize=8)
                ax.fill_between(dates, present_counts, alpha=0.3, color='#4CAF50')

                ax.set_xlabel('Date', fontsize=10, fontweight='bold', color='#1C6099')
                ax.set_ylabel('Number of Present Employees', fontsize=10, fontweight='bold', color='#1C6099')
                ax.set_title('Present Employees Trend (Last 7 Days)',
                             fontsize=12, fontweight='bold', color='#004c8c', pad=15)

                ax.tick_params(axis='both', colors='#1C6099', labelsize=9)
                ax.grid(True, alpha=0.3, linestyle='--', color='#00aaff')

                # Add value labels
                for i, (date, value) in enumerate(zip(dates, present_counts)):
                    ax.text(i, value + 0.1, str(value), ha='center', va='bottom',
                            fontsize=9, fontweight='bold', color='#1C6099')

                today_present = len(employees)
                avg_present = sum(present_counts) / len(present_counts) if present_counts else 0
                self.graph_info_label.setText(f"Today: {today_present} present | 7-day average: {avg_present:.1f}")
            else:
                ax.text(0.5, 0.5, 'No Present Employees Data\nNo attendance records found',
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax.transAxes,
                        fontsize=12,
                        fontweight='bold',
                        color='#FF9800')
                ax.axis('off')
                self.graph_info_label.setText("No attendance data available for last 7 days")

            self.figure.tight_layout()
            self.canvas.draw()
        else:
            self.graph_info_label.setText(f"Present Employees Today: {len(employees)}")

    def plot_late_graph(self):
        """Plot PIE CHART for late employees (ORIGINAL DESIGN)"""
        employees = self.get_late_data_from_db()
        self.current_graph_type = 'late'

        # Update table
        headers = ['ID', 'Name', 'Late (min)', 'Clock In']
        self.update_table(employees, headers, "Late Employees")

        # Plot PIE CHART if matplotlib is available
        if MATPLOTLIB_AVAILABLE and self.figure:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#E6F7FF')
            self.figure.patch.set_facecolor('#E6F7FF')

            if employees:
                # Get total employees for comparison
                all_employees = self.get_all_employees_data()
                total_employees = len(all_employees) if all_employees else 0

                if total_employees > 0:
                    late_count = len(employees)
                    on_time_count = total_employees - late_count

                    # Create pie chart
                    labels = ['On Time', 'Late']
                    sizes = [on_time_count, late_count]
                    colors = ['#4CAF50', '#FF9800']
                    explode = (0, 0.1)  # Explode the "Late" slice

                    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                                      autopct=lambda
                                                          pct: f'{pct:.1f}%\n({int(pct / 100. * sum(sizes))})',
                                                      startangle=90,
                                                      wedgeprops={'edgecolor': '#00aaff', 'linewidth': 1})

                    # Style the text
                    for text in texts:
                        text.set_fontsize(10)
                        text.set_fontweight('bold')
                        text.set_color('#1C6099')

                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                        autotext.set_fontsize(9)

                    ax.axis('equal')
                    ax.set_title('Late Employees Today', fontsize=12, fontweight='bold',
                                 color='#004c8c', pad=15)

                    total_late_minutes = sum(emp.get('late_minutes', 0) for emp in employees)
                    avg_late = total_late_minutes / late_count if late_count > 0 else 0
                    self.graph_info_label.setText(f"Late Employees: {late_count} | Avg Late: {avg_late:.1f} min")
                else:
                    ax.text(0.5, 0.5, 'No Employee Data Available',
                            horizontalalignment='center',
                            verticalalignment='center',
                            transform=ax.transAxes,
                            fontsize=12,
                            fontweight='bold',
                            color='#FF9800')
                    ax.axis('off')
                    self.graph_info_label.setText("No employee data available")
            else:
                ax.text(0.5, 0.5, 'No Late Employees Today\nAll on time!',
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax.transAxes,
                        fontsize=12,
                        fontweight='bold',
                        color='#4CAF50')
                ax.axis('off')
                self.graph_info_label.setText("No late employees today")

            self.figure.tight_layout()
            self.canvas.draw()
        else:
            self.graph_info_label.setText(f"Late Employees Today: {len(employees)}")

    def plot_absent_graph(self):
        """Plot PIE CHART for absent employees (ORIGINAL DESIGN)"""
        employees = self.get_absent_data_from_db()
        self.current_graph_type = 'absent'

        # Update table
        headers = ['ID', 'Name', 'Email']
        self.update_table(employees, headers, "Absent Employees")

        # Plot PIE CHART if matplotlib is available
        if MATPLOTLIB_AVAILABLE and self.figure:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#E6F7FF')
            self.figure.patch.set_facecolor('#E6F7FF')

            # Get total employees for comparison
            all_employees = self.get_all_employees_data()
            total_employees = len(all_employees) if all_employees else 0

            if total_employees > 0:
                absent_count = len(employees)
                present_count = total_employees - absent_count

                # Create pie chart
                labels = ['Present', 'Absent']
                sizes = [present_count, absent_count]
                colors = ['#4CAF50', '#f44336']
                explode = (0, 0.1)  # Explode the "Absent" slice

                wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                                  autopct=lambda pct: f'{pct:.1f}%\n({int(pct / 100. * sum(sizes))})',
                                                  startangle=90,
                                                  wedgeprops={'edgecolor': '#00aaff', 'linewidth': 1})

                # Style the text
                for text in texts:
                    text.set_fontsize(10)
                    text.set_fontweight('bold')
                    text.set_color('#1C6099')

                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)

                ax.axis('equal')
                ax.set_title('Absent Employees Today', fontsize=12, fontweight='bold',
                             color='#004c8c', pad=15)

                attendance_rate = (present_count / total_employees * 100) if total_employees > 0 else 0
                self.graph_info_label.setText(
                    f"Attendance Rate: {attendance_rate:.1f}% | Absent: {absent_count}/{total_employees}")
            else:
                ax.text(0.5, 0.5, 'No Employee Data Available',
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax.transAxes,
                        fontsize=12,
                        fontweight='bold',
                        color='#FF9800')
                ax.axis('off')
                self.graph_info_label.setText("No employee data available")

            self.figure.tight_layout()
            self.canvas.draw()
        else:
            self.graph_info_label.setText(f"Absent Employees Today: {len(employees)}")

    def plot_total_employee_graph(self):
        """NO GRAPH - Only table for total employees (ORIGINAL DESIGN)"""
        employees = self.get_all_employees_data()
        self.current_graph_type = 'total'

        # Update table
        headers = ['ID', 'Name', 'Email']
        self.update_table(employees, headers, "All Employees")

        # NO GRAPH - Only message
        if MATPLOTLIB_AVAILABLE and self.figure:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#E6F7FF')
            self.figure.patch.set_facecolor('#E6F7FF')

            ax.text(0.5, 0.5, 'Employee Overview\n(No Graph - See Table for Details)',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    fontsize=14,
                    fontweight='bold',
                    color='#1C6099')
            ax.axis('off')

            self.figure.tight_layout()
            self.canvas.draw()

        self.graph_info_label.setText(f"Total Employees: {len(employees)} | See table for details")

    def plot_on_leave_graph(self):
        """Plot PIE CHART for on leave employees (ORIGINAL DESIGN)"""
        employees = self.get_on_leave_data_from_db()
        self.current_graph_type = 'on_leave'

        # Update table
        headers = ['ID', 'Name', 'Leave Type']
        self.update_table(employees, headers, "Today's Leaves")

        # Plot PIE CHART if matplotlib is available
        if MATPLOTLIB_AVAILABLE and self.figure:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#E6F7FF')
            self.figure.patch.set_facecolor('#E6F7FF')

            # Get total employees for comparison
            all_employees = self.get_all_employees_data()
            total_employees = len(all_employees) if all_employees else 0

            if total_employees > 0:
                on_leave_count = len(employees)
                working_count = total_employees - on_leave_count

                # Create pie chart
                labels = ['Working', 'On Leave']
                sizes = [working_count, on_leave_count]
                colors = ['#4CAF50', '#9C27B0']
                explode = (0, 0.1)  # Explode the "On Leave" slice

                wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                                  autopct=lambda pct: f'{pct:.1f}%\n({int(pct / 100. * sum(sizes))})',
                                                  startangle=90,
                                                  wedgeprops={'edgecolor': '#00aaff', 'linewidth': 1})

                # Style the text
                for text in texts:
                    text.set_fontsize(10)
                    text.set_fontweight('bold')
                    text.set_color('#1C6099')

                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)

                ax.axis('equal')
                ax.set_title(f"Today's Leaves\nOn Leave: {on_leave_count}",
                             fontsize=12, fontweight='bold', color='#004c8c', pad=15)

                self.graph_info_label.setText(f"{on_leave_count} employees on leave today")
            else:
                ax.text(0.5, 0.5, 'No Employee Data Available',
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax.transAxes,
                        fontsize=12,
                        fontweight='bold',
                        color='#FF9800')
                ax.axis('off')
                self.graph_info_label.setText("No employee data available")

            self.figure.tight_layout()
            self.canvas.draw()
        else:
            self.graph_info_label.setText(f"Employees on Leave Today: {len(employees)}")