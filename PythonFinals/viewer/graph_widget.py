import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QFrame, QAbstractItemView, QHeaderView)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta
from database.database import Database


class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.COLORS = {
            'present': '#2ecc71', 'late': '#f1c40f', 'absent': '#e74c3c',
            'total': '#3498db', 'leave': '#9b59b6', 'text': '#2D3436'
        }
        self.setup_ui()

    def setup_ui(self):

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)


        # LEFT SIDE: GRAPH (Maximized)
        self.left_container = QFrame()
        # Remove background colors and fancy borders
        self.left_container.setStyleSheet("background-color: white; border: none;")

        # Use minimal layout margins so the graph expands to fill the box
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)

        # Simple Title: Bold Black Text only (No background eyesore)
        self.graph_title = QLabel("ANALYTICS")
        self.graph_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_title.setStyleSheet("""
            font-size: 14pt; 
            font-weight: bold; 
            color: black; 
            border: none;
            background: transparent;
        """)
        left_layout.addWidget(self.graph_title)

        # Matplotlib Figure
        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        left_layout.addWidget(self.canvas)


        # RIGHT SIDE: TABLE (Clean & Simple)
        self.right_container = QFrame()
        self.right_container.setStyleSheet("background-color: white; border: none;")

        right_layout = QVBoxLayout(self.right_container)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        # Simple Title: Bold Black Text only
        self.table_title = QLabel("DETAILED LOG")
        self.table_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_title.setStyleSheet("""
            font-size: 14pt; 
            font-weight: bold; 
            color: black; 
            border: none;
            background: transparent;
        """)
        right_layout.addWidget(self.table_title)

        # Clean Table (No fancy selection colors or heavy borders)
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setShowGrid(False)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Simple, Neutral Table Styling
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F2F2F2;
                font-size: 10pt;
                border: 1px solid #DDDDDD;
                color: black;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #3498db; /* Subtle blue line indicator */
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        right_layout.addWidget(self.table_widget)

        #Split: Give the Graph much more room than the Table
        main_layout.addWidget(self.left_container, 7)
        main_layout.addWidget(self.right_container, 3)

    def update_table(self, data, headers):
        """Robust table update to prevent N/A output"""
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, header in enumerate(headers):
                val = ""
                if header == "ID":
                    val = f"EMP{row.get('id', '??')}"
                elif header == "Name":
                    val = row.get('full_name') or row.get('username') or "Unknown"
                elif header == "Clock In":
                    val = str(row.get('clock_in')) if row.get('clock_in') else "--:--"
                elif header == "Late":
                    val = f"{row.get('late_minutes', 0)}m"
                elif header == "Role":
                    val = str(row.get('role', 'staff')).capitalize()
                elif header == "Type":
                    val = row.get('request_type', "N/A")

                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(i, j, item)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def draw_empty_message(self, message):
        """Utility to show a message instead of crashing on empty data"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12, color='gray', fontweight='bold')
        ax.axis('off')
        self.canvas.draw()

    def draw_pizza_pie(self, sizes, labels, colors, title):
        if sum(sizes) == 0:
            self.draw_empty_message(f"No Data for {title}")
            return

        self.figure.clear()
        # Increase padding around the plot so labels don't hit the edges
        ax = self.figure.add_subplot(111)

        # 'Explode' only slices that have value > 0
        explode = [0.08 if s > 0 else 0 for s in sizes]

        patches, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%', startangle=140,
            colors=colors, explode=explode, shadow=True,
            pctdistance=0.75, labeldistance=1.1
        )

        # Make the percentage text white and bold for visibility
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_weight('bold')
            autotext.set_fontsize(9)

        ax.set_title(title, pad=25, fontweight='bold', fontsize=12)
        # Fix the "Cut off" issue
        self.figure.tight_layout(pad=3.0)
        self.canvas.draw()

    def draw_line_trend(self, x_data, y_data, color, title, x_label):
        """Draws a trend line with strictly whole numbers and no negative values"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Draw the line
        ax.plot(x_data, y_data, marker='o', color=color, linewidth=3,
                markersize=8, markerfacecolor='white', markeredgewidth=2)
        ax.fill_between(x_data, y_data, alpha=0.15, color=color)

        # Set Titles and Labels
        ax.set_title(title, fontweight='bold', pad=20, fontsize=12)
        ax.set_xlabel(x_label, fontweight='bold', labelpad=10)
        ax.set_ylabel("Count", fontweight='bold')

        # --- FIX: Y-AXIS SCALING ---
        ax.set_ylim(bottom=0)  # Never show negative numbers

        # If all data points are 0, force the Y-axis to show 0 to 5
        # so the 'Whole Number' locator has actual numbers to show
        if max(y_data) == 0:
            ax.set_ylim(0, 5)
        else:
            # Otherwise, add a little room at the top for clarity
            ax.set_ylim(0, max(y_data) + 1)

        # Force whole numbers (1, 2, 3...)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Styling
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Professional padding
        self.figure.tight_layout(pad=3.5)
        self.canvas.draw()

    # --- 1. PRESENT TODAY (Line Graph - Last 7 Days) ---
    def plot_present_graph(self):
        self.graph_title.setText("WEEKLY ATTENDANCE TREND")
        dates, counts = [], []
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i)).date()
            dates.append(d.strftime('%b %d'))
            res = self.db.fetch_one(
                "SELECT COUNT(*) as c FROM attendance WHERE date=%s AND (status='present' OR status='late')", (d,))
            counts.append(res['c'] if res else 0)
        self.draw_line_trend(dates, counts, self.COLORS['present'], "Daily Presence Count", "Last 7 Days")

        today = datetime.now().date()
        data = self.db.execute_query(
            "SELECT u.id, u.full_name, a.clock_in FROM users u JOIN attendance a ON u.id=a.user_id WHERE a.date=%s",
            (today,))
        self.update_table(data, ["ID", "Name", "Clock In"])

    # --- 2. LATE TODAY (Pizza/Pie Graph) ---
    def plot_late_graph(self):
        self.graph_title.setText("PUNCTUALITY ANALYSIS")
        today = datetime.now().date()
        on_time = \
        self.db.fetch_one("SELECT COUNT(*) as c FROM attendance WHERE date=%s AND status='present'", (today,))['c']
        late = self.db.fetch_one("SELECT COUNT(*) as c FROM attendance WHERE date=%s AND status='late'", (today,))['c']

        self.draw_pizza_pie([on_time, late], ['On-Time', 'Late'], [self.COLORS['present'], self.COLORS['late']],
                            "Today's Late Ratio")

        data = self.db.execute_query(
            "SELECT u.id, u.full_name, a.late_minutes FROM users u JOIN attendance a ON u.id=a.user_id WHERE a.date=%s AND a.status='late'",
            (today,))
        self.update_table(data, ["ID", "Name", "Late"])

    # --- 3. ABSENT TODAY (Pizza/Pie Graph) ---
    def plot_absent_graph(self):
        self.graph_title.setText("ABSENCE DISTRIBUTION")
        today = datetime.now().date()
        total_staff = self.db.fetch_one("SELECT COUNT(*) as c FROM users WHERE role='staff'")['c']
        present_count = \
        self.db.fetch_one("SELECT COUNT(DISTINCT user_id) as c FROM attendance WHERE date=%s", (today,))['c']
        absent_count = max(0, total_staff - present_count)

        self.draw_pizza_pie([present_count, absent_count], ['Present', 'Absent'],
                            [self.COLORS['total'], self.COLORS['absent']], "Attendance Gap")

        data = self.db.execute_query(
            "SELECT id, full_name FROM users WHERE role='staff' AND id NOT IN (SELECT user_id FROM attendance WHERE date=%s)",
            (today,))
        self.update_table(data, ["ID", "Name"])

    # --- 4. TOTAL EMPLOYEES (Line Graph - Monthly Trend) ---
    def plot_total_employee_graph(self):
        self.graph_title.setText("MONTHLY HEADCOUNT TREND")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        current_year = datetime.now().year
        counts = []

        for m in range(1, 13):
            # Showing total users registered up to that month/year
            # Since your table doesn't have join_date, we'll show current total across months for the trend
            q = "SELECT COUNT(*) as c FROM users WHERE role='staff'"
            res = self.db.fetch_one(q)
            counts.append(res['c'] if res else 0)

        self.draw_line_trend(months, counts, self.COLORS['total'], f"Workforce Capacity ({current_year})", "Month")

        data = self.db.execute_query("SELECT id, full_name, role FROM users WHERE role != 'admin'")
        self.update_table(data, ["ID", "Name", "Role"])

    # --- 5. ON LEAVE TODAY (Line Graph - Monthly Trend) ---
    def plot_on_leave_graph(self):
        """Changed from Monthly to 7-Day Trend to match the 'Today' KPI context"""
        # 1. Update the Header to match the KPI Card
        self.graph_title.setText("ON-LEAVE TREND")

        # 2. Generate data for the Last 7 Days (Instead of 12 Months)
        dates = []
        counts = []
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i)).date()
            # X-axis will now show dates like "Feb 05"
            dates.append(d.strftime('%b %d'))

            res = self.db.fetch_one("""
                SELECT COUNT(*) as c FROM requests 
                WHERE DATE(request_date) = %s 
                AND status = 'approved' 
                AND request_type LIKE '%%Leave%%'
            """, (d,))
            counts.append(res['c'] if res else 0)

        # 3. Draw the line graph (Using 'Last 7 Days' as the X-axis label)
        self.draw_line_trend(dates, counts, self.COLORS['leave'], "Daily Leave Count", "Last 7 Days")

        # 4. Update the table to show who is specifically on leave TODAY
        today = datetime.now().date()
        data = self.db.execute_query("""
            SELECT u.id, u.full_name, r.request_type 
            FROM users u 
            JOIN requests r ON u.id = r.user_id 
            WHERE DATE(r.request_date) = %s 
            AND r.status = 'approved' 
            AND r.request_type LIKE '%%Leave%%'
        """, (today,))

        # Ensures headers match your screenshot: ID, Name, Type
        self.update_table(data, ["ID", "Name", "Type"])