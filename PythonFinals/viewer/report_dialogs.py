from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox
from PyQt6.QtCore import Qt, QDate
from datetime import datetime


# --- 1. PICK TYPE DIALOG ---
class ReportTypeSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Report Type")
        self.setFixedSize(450, 350)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        self.selected_type = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        title = QLabel("WHAT REPORT WOULD YOU\nLIKE TO GENERATE?")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #004c8c; border: none;")
        layout.addWidget(title)

        # Style for all buttons
        btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1C6099, stop:1 #00aaff);
                color: white; font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 12px;
            }
            QPushButton:hover { background: #0088cc; }
        """

        self.btn_daily = QPushButton("DAILY ATTENDANCE")
        self.btn_monthly = QPushButton("MONTHLY SUMMARY")
        self.btn_annual = QPushButton("ANNUAL PERFORMANCE")

        for btn in [self.btn_daily, self.btn_monthly, self.btn_annual]:
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)

        self.btn_daily.clicked.connect(lambda: self.set_choice("Daily"))
        self.btn_monthly.clicked.connect(lambda: self.set_choice("Monthly"))
        self.btn_annual.clicked.connect(lambda: self.set_choice("Annual"))

    def set_choice(self, choice):
        self.selected_type = choice
        self.accept()


# --- 2. MONTHLY INPUT DIALOG ---
class MonthlySelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Monthly Report Settings")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: white; border-radius: 12px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("SELECT MONTH & YEAR")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #004c8c;")
        layout.addWidget(title)

        self.month_combo = QComboBox()
        self.month_combo.addItems(["January", "February", "March", "April", "May", "June",
                                   "July", "August", "September", "October", "November", "December"])
        # Set to current month
        self.month_combo.setCurrentIndex(datetime.now().month - 1)

        self.year_combo = QComboBox()
        curr_year = datetime.now().year
        self.year_combo.addItems([str(curr_year), str(curr_year - 1), str(curr_year - 2)])

        combo_style = "padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 11pt;"
        self.month_combo.setStyleSheet(combo_style)
        self.year_combo.setStyleSheet(combo_style)

        layout.addWidget(QLabel("<b>Month:</b>"))
        layout.addWidget(self.month_combo)
        layout.addSpacing(10)
        layout.addWidget(QLabel("<b>Year:</b>"))
        layout.addWidget(self.year_combo)
        layout.addSpacing(20)

        generate_btn = QPushButton("GENERATE REPORT")
        generate_btn.setStyleSheet(
            "background: #00aaff; color: white; font-weight: bold; padding: 12px; border-radius: 6px;")
        generate_btn.clicked.connect(self.accept)
        layout.addWidget(generate_btn)

    def get_values(self):
        return self.month_combo.currentIndex() + 1, self.year_combo.currentText(), self.month_combo.currentText()


# --- 3. ANNUAL INPUT DIALOG ---
class AnnualSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Annual Report Settings")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background-color: white; border-radius: 12px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("SELECT AUDIT YEAR")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #004c8c;")
        layout.addWidget(title)

        self.year_combo = QComboBox()
        curr_year = datetime.now().year
        self.year_combo.addItems([str(curr_year), str(curr_year - 1), str(curr_year - 2)])
        self.year_combo.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 11pt;")

        layout.addWidget(QLabel("<b>Year:</b>"))
        layout.addWidget(self.year_combo)
        layout.addSpacing(20)

        generate_btn = QPushButton("GENERATE ANNUAL REPORT")
        generate_btn.setStyleSheet(
            "background: #00aaff; color: white; font-weight: bold; padding: 12px; border-radius: 6px;")
        generate_btn.clicked.connect(self.accept)
        layout.addWidget(generate_btn)

    def get_year(self):
        return self.year_combo.currentText()