# models/request_data.py
"""
Request Model
"""
from database.database import Database
from datetime import datetime, date
import logging


class Request:
    def __init__(self):
        self.db = Database()

    # Request types
    REQUEST_TYPES = {
        'leave': [
            'Vacation Leave',
            'Sick Leave',
            'Emergency Leave',
            'Maternity Leave',
            'Paternity Leave',
            'Bereavement Leave',
            'Personal Leave'
        ],
        'time_adjustment': [
            'Overtime Request',
            'Undertime Request',
            'Time Correction',
            'Shift Change'
        ],
        'other': [
            'Official Business',
            'Training/Seminar',
            'Equipment Request',
            'Other'
        ]
    }

    def create_request(self, user_id, request_type, request_date, reason):
        """Create a new request"""
        try:
            # Validate request_date
            if isinstance(request_date, str):
                request_date = datetime.strptime(request_date, "%Y-%m-%d").date()

            query = """
            INSERT INTO requests (user_id, request_type, request_date, reason, status)
            VALUES (%s, %s, %s, %s, 'pending')
            """
            result = self.db.execute_query(query, (user_id, request_type, request_date, reason))

            if result:
                print(f"✅ Request created! ID: {result}")
                return {"success": True, "request_id": result}
            else:
                return {"success": False, "message": "Failed to create request"}

        except Exception as e:
            logging.error(f"Error creating request: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_user_requests(self, user_id, limit=50):
        """Get all requests for a specific user"""
        try:
            query = """
            SELECT 
                r.id,
                r.request_type,
                r.request_date,
                r.reason,
                r.status,
                r.created_at,
                u.username as user_name,
                u.full_name
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = %s
            ORDER BY r.request_date DESC, r.created_at DESC
            LIMIT %s
            """
            records = self.db.execute_query(query, (user_id, limit))

            # Format the data
            formatted_records = []
            for record in records:
                formatted_records.append({
                    'id': record['id'],
                    'type': record['request_type'],
                    'date': str(record['request_date']),
                    'reason': record['reason'],
                    'status': record['status'].capitalize(),
                    'created_at': record['created_at'].strftime("%Y-%m-%d %I:%M %p") if record['created_at'] else '',
                    'user_name': record['user_name'],
                    'full_name': record['full_name']
                })

            return formatted_records

        except Exception as e:
            logging.error(f"Error getting user requests: {e}")
            return []

    def get_pending_requests(self, limit=100):
        """Get all pending requests (for admin)"""
        try:
            query = """
            SELECT 
                r.id,
                r.request_type,
                r.request_date,
                r.reason,
                r.status,
                r.created_at,
                u.username as user_name,
                u.full_name,
                u.id as user_id
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.status = 'pending'
            ORDER BY r.created_at ASC
            LIMIT %s
            """
            records = self.db.execute_query(query, (limit,))

            # Format the data
            formatted_records = []
            for record in records:
                formatted_records.append({
                    'id': record['id'],
                    'type': record['request_type'],
                    'date': str(record['request_date']),
                    'reason': record['reason'],
                    'status': record['status'].capitalize(),
                    'created_at': record['created_at'].strftime("%Y-%m-%d %I:%M %p") if record['created_at'] else '',
                    'user_name': record['user_name'],
                    'full_name': record['full_name'],
                    'user_id': record['user_id']
                })

            return formatted_records

        except Exception as e:
            logging.error(f"Error getting pending requests: {e}")
            return []

    def get_request_by_id(self, request_id):
        try:
            query = """
            SELECT 
                r.*,
                u.username,
                u.full_name,
                u.email
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.id = %s
            """
            record = self.db.fetch_one(query, (request_id,))

            if record:
                return {
                    'id': record['id'],
                    'user_id': record['user_id'],
                    'type': record['request_type'],
                    'date': str(record['request_date']),
                    'reason': record['reason'],
                    'status': record['status'],
                    'created_at': record['created_at'],
                    'user_name': record['username'],
                    'full_name': record['full_name'],
                    'email': record['email']
                }
            return None

        except Exception as e:
            logging.error(f"Error getting request by ID: {e}")
            return None

    def update_request_status(self, request_id, status, approved_by=None, notes=None):
        try:
            if status not in ['approved', 'declined', 'pending', 'cancelled']:
                return {"success": False, "message": "Invalid status"}

            query = """
            UPDATE requests 
            SET status = %s
            WHERE id = %s
            """
            self.db.execute_query(query, (status, request_id))

            print(f"✅ Request {request_id} updated to {status}")
            return {"success": True, "message": f"Request {status} successfully"}

        except Exception as e:
            logging.error(f"Error updating request status: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_request_stats(self, user_id=None):
        """Get request statistics"""
        try:
            if user_id:
                query = """
                SELECT 
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                    COUNT(CASE WHEN status = 'declined' THEN 1 END) as declined,
                    COUNT(*) as total
                FROM requests 
                WHERE user_id = %s
                """
                result = self.db.fetch_one(query, (user_id,))
            else:
                query = """
                SELECT 
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                    COUNT(CASE WHEN status = 'declined' THEN 1 END) as declined,
                    COUNT(*) as total
                FROM requests
                """
                result = self.db.fetch_one(query)

            return result or {'pending': 0, 'approved': 0, 'declined': 0, 'total': 0}

        except Exception as e:
            logging.error(f"Error getting request stats: {e}")
            return {'pending': 0, 'approved': 0, 'declined': 0, 'total': 0}

    def get_all_request_types(self):
        all_types = []
        for category, types in self.REQUEST_TYPES.items():
            all_types.extend(types)
        return all_types

    def get_request_types_by_category(self):
        return self.REQUEST_TYPES

    def get_time_adjustment_requests(self, limit=50):
        query = """
        SELECT 
            r.id,
            r.request_type,
            DATE(r.request_date) as request_date,
            r.reason,
            r.status,
            r.created_at,
            u.full_name,
            u.username
        FROM requests r
        JOIN users u ON r.user_id = u.id
        WHERE r.request_type IN ('Overtime Request', 'Undertime Request', 'Time Correction', 'Shift Change')
        ORDER BY r.created_at DESC
        LIMIT %s
        """
        return self.db.execute_query(query, (limit,))