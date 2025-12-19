# controllers/announcement_controller.py
"""
Announcement Controller
"""
from models.announcement_data import Announcement


class AnnouncementController:
    def __init__(self):
        self.announcement_model = Announcement()

    def create_announcement(self, title, content):
        """Create a new announcement"""
        if not title or not content:
            return {"success": False, "message": "Title and content are required"}

        if len(title) > 255:
            return {"success": False, "message": "Title is too long (max 255 characters)"}

        try:
            announcement_id = self.announcement_model.create_announcement(title, content)

            if announcement_id:
                return {
                    "success": True,
                    "message": "Announcement created successfully!",
                    "announcement_id": announcement_id
                }
            else:
                return {"success": False, "message": "Failed to create announcement"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_all_announcements(self):
        """Get all announcements"""
        return self.announcement_model.get_all_announcements()

    def get_recent_announcements(self):
        """Get recent announcements for dashboard"""
        return self.announcement_model.get_recent_announcements()

    def update_announcement(self, announcement_id, title, content):
        """Update an announcement"""
        if not title or not content:
            return {"success": False, "message": "Title and content are required"}

        try:
            success = self.announcement_model.update_announcement(announcement_id, title, content)

            if success:
                return {"success": True, "message": "Announcement updated successfully!"}
            else:
                return {"success": False, "message": "Failed to update announcement"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def delete_announcement(self, announcement_id):
        """Delete an announcement"""
        try:
            success = self.announcement_model.delete_announcement(announcement_id)

            if success:
                return {"success": True, "message": "Announcement deleted successfully!"}
            else:
                return {"success": False, "message": "Failed to delete announcement"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_announcement_details(self, announcement_id):
        """Get announcement details"""
        announcement = self.announcement_model.get_announcement_by_id(announcement_id)

        if announcement:
            return {"success": True, "announcement": announcement}
        else:
            return {"success": False, "message": "Announcement not found"}