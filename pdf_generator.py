# utils/pdf_generator.py
"""
PDF Report Generator
"""
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime
import logging


class PDFGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom styles for PDF"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor('#004c8c')
        )

        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=8,
            textColor=colors.HexColor('#1C6099')
        )

        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )

        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            textColor=colors.black
        )

        # Footer style
        self.footer_style = ParagraphStyle(
            'CustomFooter',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.gray
        )

        # Highlight style
        self.highlight_style = ParagraphStyle(
            'CustomHighlight',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1C6099'),
            fontName='Helvetica-Bold'
        )

    def generate_attendance_report(self, report_data):
        """Generate PDF attendance report"""
        try:
            # Create document
            doc = SimpleDocTemplate(
                self.filename,
                pagesize=A4,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch
            )

            elements = []

            # Add title
            title = Paragraph(f"<b>{report_data['report_title']}</b>", self.title_style)
            elements.append(title)

            # Add date range
            date_range = Paragraph(
                f"Period: {report_data['start_date']} to {report_data['end_date']}",
                self.subtitle_style
            )
            elements.append(date_range)

            # Add employee filter info if applicable
            if report_data.get('employee_name'):
                employee_info = Paragraph(
                    f"Employee: {report_data['employee_name']}",
                    self.subtitle_style
                )
                elements.append(employee_info)

            elements.append(Spacer(1, 0.2 * inch))

            # Add generation date
            generated_at = Paragraph(
                f"Generated on: {report_data['generated_at']}",
                self.footer_style
            )
            elements.append(generated_at)

            elements.append(Spacer(1, 0.3 * inch))

            # Add summary statistics if available
            if report_data.get('statistics'):
                stats = report_data['statistics']
                summary_data = [
                    ['SUMMARY STATISTICS', ''],
                    ['Total Employees', str(stats.get('total_employees', 0))],
                    ['Employees with Records', str(stats.get('attendance_stats', {}).get('employees_with_records', 0))],
                    ['Total Days in Period', str(stats.get('attendance_stats', {}).get('total_days', 0))],
                    ['Present Days', str(stats.get('attendance_stats', {}).get('present_days', 0))],
                    ['Late Days', str(stats.get('attendance_stats', {}).get('late_days', 0))],
                    ['Absent Days', str(stats.get('attendance_stats', {}).get('absent_days', 0))],
                    ['Total Hours Worked', str(stats.get('attendance_stats', {}).get('total_hours_worked', 0))],
                    ['Total Overtime Hours', str(stats.get('attendance_stats', {}).get('total_overtime_hours', 0))],
                    ['Attendance Rate', f"{stats.get('attendance_stats', {}).get('attendance_percentage', 0)}%"],
                ]

                summary_table = Table(summary_data, colWidths=[3 * inch, 1.5 * inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004c8c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ]))

                elements.append(summary_table)
                elements.append(Spacer(1, 0.3 * inch))

            # Generate appropriate table based on report type
            if report_data['report_type'] == 'attendance_daily':
                self.add_daily_attendance_table(elements, report_data['data'])
            elif report_data['report_type'] == 'attendance_summary':
                self.add_summary_table(elements, report_data['data'])
            elif report_data['report_type'] == 'attendance_detailed':
                self.add_detailed_table(elements, report_data['data'])
            elif report_data['report_type'] == 'employee':
                self.add_employee_table(elements, report_data['data'])
            elif report_data['report_type'] == 'leave':
                self.add_leave_table(elements, report_data['data'])
            elif report_data['report_type'] == 'late':
                self.add_late_table(elements, report_data['data'])
            elif report_data['report_type'] == 'overtime':
                self.add_overtime_table(elements, report_data['data'])

            # Add footer with page numbers
            def add_footer(canvas, doc):
                canvas.saveState()
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.gray)
                canvas.drawString(0.5 * inch, 0.5 * inch, f"Page {doc.page}")
                canvas.drawRightString(7.5 * inch, 0.5 * inch, "WorkXTrackr - Attendance Management System")
                canvas.restoreState()

            # Build PDF
            doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

            return True

        except Exception as e:
            logging.error(f"Error generating PDF: {e}")
            return False

    def add_daily_attendance_table(self, elements, data):
        """Add daily attendance table to PDF"""
        if not data:
            elements.append(Paragraph("No data available for the selected period.", self.normal_style))
            return

        table_data = [['Date', 'Day', 'Total', 'Present', 'Late', 'Absent', 'Avg Hours', 'Present %']]

        for row in data:
            table_data.append([
                str(row.get('report_date', '')),
                str(row.get('day_name', '')),
                str(row.get('total_employees', 0)),
                str(row.get('present_count', 0)),
                str(row.get('late_count', 0)),
                str(row.get('absent_count', 0)),
                str(row.get('avg_hours_worked', 0)),
                f"{row.get('present_percentage', 0)}%"
            ])

        table = Table(table_data, colWidths=[0.8 * inch, 0.7 * inch, 0.6 * inch, 0.7 * inch,
                                             0.6 * inch, 0.7 * inch, 0.8 * inch, 0.8 * inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004c8c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        elements.append(table)

    def add_summary_table(self, elements, data):
        """Add summary table to PDF"""
        if not data:
            elements.append(Paragraph("No data available for the selected period.", self.normal_style))
            return

        table_data = [['Employee', 'Days Recorded', 'Present', 'Late', 'Absent', 'Total Hours', 'Attendance %']]

        for row in data:
            table_data.append([
                str(row.get('full_name', '')),
                str(row.get('days_recorded', 0)),
                str(row.get('present_days', 0)),
                str(row.get('late_days', 0)),
                str(row.get('absent_days', 0)),
                str(row.get('total_hours_worked', 0)),
                f"{row.get('attendance_rate', 0)}%"
            ])

        table = Table(table_data, colWidths=[2 * inch, 0.8 * inch, 0.6 * inch, 0.6 * inch,
                                             0.6 * inch, 0.8 * inch, 0.8 * inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004c8c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ]))

        elements.append(table)

    def add_detailed_table(self, elements, data):
        """Add detailed attendance table to PDF"""
        if not data:
            elements.append(Paragraph("No data available for the selected period.", self.normal_style))
            return

        table_data = [['Date', 'Employee', 'Status', 'Clock In', 'Clock Out', 'Hours', 'Late (min)', 'Remarks']]

        for row in data:
            table_data.append([
                str(row.get('date', '')),
                str(row.get('full_name', '')),
                str(row.get('status', '')).title(),
                str(row.get('clock_in', '--:--')),
                str(row.get('clock_out', '--:--')),
                str(row.get('total_hours', 0)),
                str(row.get('late_minutes', 0)),
                str(row.get('work_status', ''))
            ])

        table = Table(table_data, colWidths=[0.8 * inch, 1.2 * inch, 0.7 * inch, 0.7 * inch,
                                             0.7 * inch, 0.6 * inch, 0.7 * inch, 1.0 * inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004c8c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ]))

        elements.append(table)

    def add_employee_table(self, elements, data):
        """Add employee report table to PDF"""
        if not data:
            elements.append(Paragraph("No data available for the selected period.", self.normal_style))
            return

        table_data = [['Date', 'Day', 'Status', 'Clock In', 'Clock Out', 'Hours', 'Late (min)', 'Remarks']]

        for row in data:
            table_data.append([
                str(row.get('attendance_date', '')),
                str(row.get('day_name', '')),
                str(row.get('status', '')).title(),
                str(row.get('clock_in_time', '--:--')),
                str(row.get('clock_out_time', '--:--')),
                str(row.get('total_hours', 0)),
                str(row.get('late_minutes', 0)),
                str(row.get('remarks', ''))
            ])

        table = Table(table_data, colWidths=[0.8 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch,
                                             0.7 * inch, 0.6 * inch, 0.7 * inch, 1.5 * inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004c8c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        elements.append(table)

    def add_leave_table(self, elements, data):
        """Add leave report table to PDF"""
        if not data:
            elements.append(Paragraph("No data available for the selected period.", self.normal_style))
            return

        table_data = [['Employee', 'Leave Type', 'Date', 'Status', 'Reason']]

        for row in data:
            # Truncate reason if too long
            reason = str(row.get('reason', ''))
            if len(reason) > 50:
                reason = reason[:47] + "..."

            table_data.append([
                str(row.get('full_name', '')),
                str(row.get('leave_type', '')),
                str(row.get('request_date', '')),
                str(row.get('status', '')).title(),
                reason
            ])

        table = Table(table_data, colWidths=[1.5 * inch, 1.2 * inch, 0.8 * inch, 0.8 * inch, 2.0 * inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004c8c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
        ]))

        elements.append(table)

    def add_late_table(self, elements, data):
        """Add late report table to PDF"""
        if not data:
            elements.append(Paragraph("No data available for the selected period.", self.normal_style))
            return

        table_data = [['Employee', 'Date', 'Late (min)', 'Clock In', 'Severity']]

        for row in data:
            table_data.append([
                str(row.get('full_name', '')),
                str(row.get('date', '')),
                str(row.get('late_minutes', 0)),
                str(row.get('clock_in_time', '--:--')),
                str(row.get('late_severity', ''))
            ])

        table = Table(table_data, colWidths=[2.0 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 1.0 * inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004c8c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ]))

        elements.append(table)

    def add_overtime_table(self, elements, data):
        """Add overtime report table to PDF"""
        if not data:
            elements.append(Paragraph("No data available for the selected period.", self.normal_style))
            return

        table_data = [['Employee', 'Date', 'Overtime (min)', 'Overtime (hrs)', 'Clock Out']]

        for row in data:
            table_data.append([
                str(row.get('full_name', '')),
                str(row.get('date', '')),
                str(row.get('overtime_minutes', 0)),
                str(row.get('overtime_hours', 0)),
                str(row.get('clock_out_time', '--:--'))
            ])

        table = Table(table_data, colWidths=[2.0 * inch, 0.8 * inch, 1.0 * inch, 1.0 * inch, 0.8 * inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004c8c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ]))

        elements.append(table)