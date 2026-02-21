from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDateEdit, QPushButton, QCalendarWidget
from PyQt6.QtCore import QDate, Qt


class DateSelectorDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Daily Report Selection")
        # Made the dialog wider to prevent cropping
        self.setFixedSize(450, 350)
        self.setStyleSheet("background-color: white; border-radius: 12px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 25, 35, 25)
        layout.setSpacing(20)

        # Title
        title = QLabel("SELECT AUDIT DATE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 16pt; 
            font-weight: bold; 
            color: #004c8c; 
            border: none; 
            border-bottom: 2px solid #00aaff; 
            padding-bottom: 5px;
        """)
        layout.addWidget(title)

        # --- THE IMPROVED DATE PICKER ---
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("MMMM dd, yyyy")

        # Set the calendar widget size and fix visibility issues
        calendar = self.date_input.calendarWidget()
        calendar.setMinimumWidth(400)  # Prevents cropping

        # Style specifically to fix the "Invisible Month/Year" problem
        self.date_input.setStyleSheet("""
            QDateEdit {
                padding: 12px; 
                border: 1px solid #ccc; 
                border-radius: 6px; 
                font-size: 12pt; 
                background-color: #fcfcfc;
                color: black;
            }
            QDateEdit::drop-down { 
                border: none; 
                background: transparent; 
                width: 40px; 
            }
            QDateEdit::down-arrow { 
                image: none; 
                border-left: 6px solid transparent; 
                border-right: 6px solid transparent; 
                border-top: 8px solid #white; 
                margin-right: 10px; 
            }

            /* CALENDAR POPUP STYLING - FIXING VISIBILITY */
            QCalendarWidget QWidget { 
                background-color: white; 
            }
            /* The header where Month and Year are */
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: #f8f9fa; 
            }
            /* Prev/Next Buttons and Month/Year labels */
            QCalendarWidget QToolButton {
                color: black;         /* Force text to black */
                font-weight: bold;
                font-size: 11pt;
                icon-size: 20px;
                background-color: transparent;
                border: none;
                margin: 5px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e6f7ff;
                border-radius: 4px;
            }
            /* The Day Numbers */
            QCalendarWidget QAbstractItemView:enabled {
                color: black;
                selection-background-color: #00aaff;
                selection-color: white;
            }
            /* Days in other months */
            QCalendarWidget QAbstractItemView:disabled {
                color: #cccccc;
            }
        """)
        layout.addWidget(self.date_input)

        # Confirm Button
        confirm_btn = QPushButton("GENERATE DAILY REPORT")
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setFixedHeight(50)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1C6099, stop:1 #00aaff);
                color: white; 
                font-weight: bold; 
                border-radius: 6px; 
                border: none; 
                font-size: 11pt;
            }
            QPushButton:hover { background: #0088cc; }
        """)
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)

    def get_selected_date(self):
        return self.date_input.date().toString("yyyy-MM-dd"), self.date_input.date().toString("MMMM d, yyyy")
