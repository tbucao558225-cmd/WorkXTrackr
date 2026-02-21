# controllers/__init__.py - UPDATE to include ReportController
"""
Controllers Package
"""

from .auth import AuthController
from .staff import StaffController
from .request_controller import RequestController
from .employee_controller import EmployeeController
from .announcement_controller import AnnouncementController
from .report_controller import ReportController

__all__ = [
    'AuthController',
    'StaffController',
    'RequestController',
    'EmployeeController',
    'AnnouncementController',
    'ReportController',
    'SystemConfigController'
]