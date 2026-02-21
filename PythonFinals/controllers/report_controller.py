# controllers/report_controller.py
from models.report_data import ReportData

class ReportController:
    def __init__(self):
        self.report_model = ReportData()

    def get_monthly_report(self, month, year):
        """Bridge between View and Model for Monthly data"""
        return self.report_model.fetch_monthly_report_data(month, year)

    def get_annual_report(self, year):
        """Bridge between View and Model for Annual data"""
        return self.report_model.fetch_annual_report_data(year)

    def get_daily_audit(self, date):
        return self.report_model.get_daily_audit_report(date)

    def get_daily_summary_stats(self, date):
        return self.report_model.get_daily_stats(date)