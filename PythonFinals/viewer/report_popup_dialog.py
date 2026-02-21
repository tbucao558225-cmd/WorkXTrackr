# viewer/report_popup_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QFrame, QScrollArea, QWidget, QAbstractItemView)
from PyQt6.QtCore import Qt, QEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PyQt6.QtGui import QColor
import numpy as np


class ReportPopupDialog(QDialog):
    def __init__(self, parent, title, stats_data, table_data, report_type):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1150, 900)
        self.setStyleSheet("background-color: white;")

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        header_panel = QFrame()
        header_panel.setStyleSheet("background-color: white; border-bottom: 1px solid #DFE6E9;")
        header_lay = QVBoxLayout(header_panel)
        display_title = report_type.upper()
        if "Daily" in report_type: display_title = "DAILY ATTENDANCE LOG"
        self.header_label = QLabel(display_title)
        self.header_label.setStyleSheet("font-size: 22pt; font-weight: bold; color: #004c8c; padding: 10px;")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_lay.addWidget(self.header_label)
        self.main_layout.addWidget(header_panel)

        # 2. SCROLL AREA
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setStyleSheet("border: none; background-color: white;")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 20, 30, 20)
        self.content_layout.setSpacing(30)

        self.setup_ui_elements(stats_data, table_data, report_type)

        self.scroll.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll)

        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet("background-color: #f8f9fa; border-top: 1px solid #e0e0e0;")
        footer_lay = QHBoxLayout(footer)
        close_btn = QPushButton("CLOSE REPORT")
        close_btn.setFixedSize(250, 45)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("background-color: #00aaff; color: white; font-weight: bold; border-radius: 6px;")
        close_btn.clicked.connect(self.accept)
        footer_lay.addWidget(close_btn)
        self.main_layout.addWidget(footer)

    def setup_ui_elements(self, stats, data, report_type):
        # Stats Cards
        stats_layout = QHBoxLayout()
        for key, value in stats.items():
            card = QFrame()
            card.setStyleSheet("background-color: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 10px;")
            cl = QVBoxLayout(card)
            display_key = key.replace('_', ' ').title()
            if "Present" in display_key: display_key = "Total Presence"
            v = QLabel(str(value))
            v.setStyleSheet("font-size: 20pt; font-weight: bold; color: #00aaff; border: none;")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            k = QLabel(display_key)
            k.setStyleSheet("font-size: 9pt; color: #666; border: none;")
            k.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(v);
            cl.addWidget(k)
            stats_layout.addWidget(card)
        self.content_layout.addWidget(QLabel("<b>KEY PERFORMANCE INDICATORS</b>"))
        self.content_layout.addLayout(stats_layout)

        # Graph
        fig = Figure(figsize=(9, 5), dpi=100)
        self.canvas = FigureCanvas(fig)
        self.canvas.setMinimumHeight(450)

        self.canvas.installEventFilter(self)

        ax = fig.add_subplot(111)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        if "Daily" in report_type:
            ax.bar(['On-Time', 'Late', 'Absent'],
                   [stats.get('present_today', 0), stats.get('late_today', 0), stats.get('absent_today', 0)],
                   color=['#4CAF50', '#FF9800', '#F44336'])
        elif "Monthly" in report_type:
            names = [row['full_name'].split()[0] for row in data[:8]]
            x = np.arange(len(names))
            # Use specific keys for the Monthly Bar Graph
            ax.bar(x - 0.2, [r['present_days'] for r in data[:8]], 0.2, label='On-Time', color='#4CAF50')
            ax.bar(x, [r['late_days'] for r in data[:8]], 0.2, label='Late', color='#FFC107')
            ax.bar(x + 0.2, [r['absent_days'] for r in data[:8]], 0.2, label='Absent', color='#F44336')
            ax.set_xticks(x);
            ax.set_xticklabels(names);
            ax.legend()
        else:
            # ANNUAL GRAPH FIX: Plot 'total_presence' (which is On-time + Late combined)
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            ax.plot(months, [row.get('total_presence', 0) for row in data], marker='o', label="Total Presence")
            ax.plot(months, [row.get('absent_days', 0) for row in data], marker='x', color='red', linestyle='--',
                    label="Absence")
            ax.legend()

        fig.tight_layout()
        self.content_layout.addWidget(self.canvas)

        # Table
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevents keyboard stealing scroll

        # --- SCROLL FIX: Redirect wheel events from Table to ScrollArea ---
        self.table.viewport().installEventFilter(self)

        headers = ['ID', 'FULL NAME', 'STATUS', 'CLOCK IN', 'CLOCK OUT', 'HOURS'] if "Daily" in report_type else [
            'NAME/MONTH', 'ON-TIME', 'LATE', 'ABSENT', 'TOTAL HOURS']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            if "Daily" in report_type:
                self.table.setItem(i, 0, QTableWidgetItem(f"EMP{row.get('employee_id')}"))
                self.table.setItem(i, 1, QTableWidgetItem(str(row.get('full_name'))))
                st = row.get('status') or "Absent"
                item = QTableWidgetItem(st.capitalize())
                if st.lower() == "absent": item.setForeground(QColor(220, 20, 60))
                self.table.setItem(i, 2, item)
                self.table.setItem(i, 3, QTableWidgetItem(str(row.get('clock_in') or '--:--')))
                self.table.setItem(i, 4, QTableWidgetItem(str(row.get('clock_out') or '--:--')))
                self.table.setItem(i, 5, QTableWidgetItem(f"{float(row.get('hours_worked', 0)):.2f}"))
            else:
                label = row.get('full_name') if "Monthly" in report_type else row.get('month_name')
                self.table.setItem(i, 0, QTableWidgetItem(str(label)))
                self.table.setItem(i, 1, QTableWidgetItem(str(row.get('present_days', 0))))
                self.table.setItem(i, 2, QTableWidgetItem(str(row.get('late_days', 0))))
                self.table.setItem(i, 3, QTableWidgetItem(str(row.get('absent_days', 0))))
                self.table.setItem(i, 4, QTableWidgetItem(f"{float(row.get('total_hours_worked', 0)):.2f}"))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        # Calculate exactly how tall the table needs to be so it doesn't have its own scrollbar
        table_height = (len(data) * 40) + 60
        self.table.setFixedHeight(table_height)

        self.table.setStyleSheet(
            "QHeaderView::section { background-color: #1C6099; color: white; font-weight: bold; padding: 5px; }")
        self.content_layout.addWidget(QLabel("📊 <b>DETAILED STATISTICAL LOGS</b>"))
        self.content_layout.addWidget(self.table)

    # --- THE MAGIC SCROLL FUNCTION ---
    def eventFilter(self, source, event):
        """Catch wheel events on the table/graph and send them to the main scroll area"""
        if event.type() == QEvent.Type.Wheel:
            # Manually trigger the scroll area's wheel event
            self.scroll.wheelEvent(event)
            return True
        return super().eventFilter(source, event)