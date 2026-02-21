# controllers/announcement_controller.py
class AnnouncementController:
    def __init__(self):
        self.announcement_model = Announcement()

    def create_announcement(self, title, content, announcement_date=None):
        return self.announcement_model.create_announcement(title, content, announcement_date)

    def get_all_announcements(self):
        return self.announcement_model.get_all_announcements()

    def get_recent_announcements(self):
        return self.announcement_model.get_recent_announcements()

    def delete_announcement(self, announcement_id):
        return self.announcement_model.delete_announcement(announcement_id)

    def post_announcement(self, title, content, announcement_date):
        return self.announcement_model.create_announcement_with_date(title, content, announcement_date)