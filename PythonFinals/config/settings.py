"""
Application Configuration Settings
"""
# config/settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Set your MySQL password here
    'database': 'workxtrackr',
    'port': 3306
}

# Application Settings
APP_NAME = "WorkXTrackr"
APP_VERSION = "1.0.0"

# Time Settings
DEFAULT_WORK_START_TIME = "09:00:00"
DEFAULT_WORK_END_TIME = "17:00:00"
GRACE_PERIOD_MINUTES = 15
OVERTIME_THRESHOLD_HOURS = 8

# Paths
IMAGE_PATH = "images/"
LOGO_PATH = "reallogo.png"
USER_PROFILE_PATH = "default_profile.png"