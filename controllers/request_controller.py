# controllers/request_controller.py
"""
Request Controller
"""
from models.request_data import Request


class RequestController:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.request_model = Request()

    def submit_request(self, request_type, request_date, reason):
        """Submit a new request"""
        if not self.user_id:
            return {"success": False, "message": "User not logged in"}

        if not all([request_type, request_date, reason]):
            return {"success": False, "message": "All fields are required"}

        if len(reason.strip()) < 10:
            return {"success": False, "message": "Reason must be at least 10 characters"}

        # Validate request type
        all_types = self.request_model.get_all_request_types()
        if request_type not in all_types:
            return {"success": False, "message": "Invalid request type"}

        result = self.request_model.create_request(self.user_id, request_type, request_date, reason)

        if result["success"]:
            return {
                "success": True,
                "message": "Request submitted successfully!",
                "request_id": result["request_id"]
            }
        else:
            return result

    def get_my_requests(self):
        """Get current user's requests"""
        if not self.user_id:
            return []

        return self.request_model.get_user_requests(self.user_id)

    def get_pending_requests(self):
        """Get all pending requests (for admin)"""
        return self.request_model.get_pending_requests()

    def get_request_details(self, request_id):
        """Get details of a specific request"""
        return self.request_model.get_request_by_id(request_id)

    def approve_request(self, request_id):
        """Approve a request (admin only)"""
        return self.request_model.update_request_status(request_id, 'approved')

    def decline_request(self, request_id):
        """Decline a request (admin only)"""
        return self.request_model.update_request_status(request_id, 'declined')

    def get_request_stats(self):
        """Get request statistics"""
        if self.user_id:
            return self.request_model.get_request_stats(self.user_id)
        return self.request_model.get_request_stats()

    def get_request_types(self):
        """Get available request types"""
        return self.request_model.get_request_types_by_category()

    def get_all_request_types_list(self):
        """Get all request types as a flat list"""
        return self.request_model.get_all_request_types()