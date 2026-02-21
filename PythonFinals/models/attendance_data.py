# models/attendance_data.py

from database.database import Database
from datetime import datetime, timedelta, time
import logging


class Attendance:
    def __init__(self):
        self.db = Database()

    def clock_in(self, user_id):
        try:
            current_time = datetime.now()
            today = current_time.date()
            clock_in_only = current_time.time()

            # Get work time settings from database
            from models.system_config_data import SystemConfig
            config = SystemConfig()
            settings = config.get_work_time_settings()
            status = "late"

            if settings: #check if the settings is found in database
                work_start_val = settings.get('work_start_time', '09:00:00')#uses 9am default time
                grace_minutes = settings.get('grace_period_minutes', 15)

                if isinstance(work_start_val, timedelta):
                    total_seconds = int(work_start_val.total_seconds())#convert the total time into seconds
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    work_start_time_obj = time(hour=hours, minute=minutes)
                elif isinstance(work_start_val, str):
                    work_start_time_obj = datetime.strptime(work_start_val, "%H:%M:%S").time()#this is to parse string
                else:
                    work_start_time_obj = time(9, 0)


                # Calculate grace time
                temp_dt = datetime.combine(today, work_start_time_obj) + timedelta(minutes=grace_minutes)
                grace_time = temp_dt.time()

                if clock_in_only <= grace_time:
                    status = "present"
            else:
                if clock_in_only <= time(hour=9, minute=15):
                    status = "present"

            try:
                query = """
                INSERT INTO attendance 
                (user_id, date, clock_in, status, late_minutes, overtime_minutes, total_hours, duration_hours)
                VALUES (%s, %s, %s, %s, 0, 0, 0.00, NULL)
                """
                result = self.db.execute_query(query, (user_id, today, clock_in_only, status))

                if result:
                    print(f"✅ New clock in saved! Status: {status}")
                    return {"success": True, "record_id": result, "clock_in_time": current_time, "status": status}
                return {"success": False}

            except Exception as e:
                # Fallback for unique constraint issues (as in your original code)
                if "Duplicate entry" in str(e):
                    print("⚠️ User already clocked in today.")
                    return {"success": False, "message": "Already clocked in for today"}
                raise e

        except Exception as e:
            import logging
            logging.error(f"Error clocking in: {e}")
            return {"success": False, "message": str(e)}

    def clock_out(self, user_id, clock_in_record_id=None):
        try:
            current_time = datetime.now()
            today = current_time.date()
            clock_out_only = current_time.time()

            print(f"⏰ CLOCK OUT ATTEMPT:")
            print(f"   User ID: {user_id}")
            print(f"   Date: {today}")
            print(f"   Time: {clock_out_only}")

            # Find the latest clock in without clock out
            query = """
            SELECT id, clock_in 
            FROM attendance 
            WHERE user_id = %s AND date = %s AND clock_in IS NOT NULL AND clock_out IS NULL
            ORDER BY id DESC LIMIT 1
            """
            result = self.db.fetch_one(query, (user_id, today))

            if result:
                record_id = result['id']
                clock_in_value = result['clock_in']

                print(f"✅ Found attendance record ID: {record_id}")
                print(f"   Clock in time: {clock_in_value}")
                print(f"   Clock in type: {type(clock_in_value)}")

                # Handle timedelta (if stored as seconds since midnight)
                if isinstance(clock_in_value, timedelta):
                    # Convert timedelta to time object
                    total_seconds = clock_in_value.total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    seconds = int(total_seconds % 60)
                    clock_in_time = time(hour=hours, minute=minutes, second=seconds)
                    print(f"   Converted timedelta to time: {clock_in_time}")
                else:
                    clock_in_time = clock_in_value

                # Calculate duration
                clock_in_dt = datetime.combine(today, clock_in_time)
                clock_out_dt = datetime.combine(today, clock_out_only)

                # Calculate duration in hours
                duration_seconds = (clock_out_dt - clock_in_dt).total_seconds()
                duration_hours = duration_seconds / 3600

                print(f"   Duration calculated: {duration_hours:.2f} hours")

                # Determine if late (arrived after 9:15 AM)
                late_minutes = 0
                if clock_in_time > time(hour=9, minute=15):
                    late_seconds = (clock_in_dt - datetime.combine(today, time(hour=9, minute=15))).total_seconds()
                    late_minutes = int(late_seconds / 60)
                    print(f"   Late by: {late_minutes} minutes")

                # Determine overtime (worked after 5:00 PM)
                overtime_minutes = 0
                if clock_out_only > time(hour=17, minute=0):
                    overtime_seconds = (clock_out_dt - datetime.combine(today, time(hour=17, minute=0))).total_seconds()
                    overtime_minutes = int(overtime_seconds / 60)
                    print(f"   Overtime: {overtime_minutes} minutes")

                # Update the record
                update_query = """
                UPDATE attendance 
                SET clock_out = %s, 
                    total_hours = %s, 
                    duration_hours = %s,
                    late_minutes = %s,
                    overtime_minutes = %s
                WHERE id = %s
                """

                self.db.execute_query(update_query, (
                    clock_out_only,
                    duration_hours,
                    duration_hours,
                    late_minutes,
                    overtime_minutes,
                    record_id
                ))
                print(f"✅ Clock out saved! Duration: {duration_hours:.2f} hours")
                return {"success": True, "clock_out_time": current_time, "duration_hours": duration_hours}
            else:
                print("❌ No clock in found without clock out")
                return {"success": False}

        except Exception as e:
            logging.error(f"Error clocking out: {e}")
            return {"success": False}

    def get_user_attendance(self, user_id, limit=50):
        """Get attendance records for a user - FIX DURATION DISPLAY"""
        try:
            # Get data with proper time formatting and duration calculation
            query = """
            SELECT 
                date,
                CASE 
                    WHEN clock_in IS NOT NULL THEN 
                        CASE 
                            WHEN HOUR(clock_in) >= 12 THEN 
                                CONCAT(LPAD(HOUR(clock_in) - 12, 2, '0'), ':', 
                                       LPAD(MINUTE(clock_in), 2, '0'), ':',
                                       LPAD(SECOND(clock_in), 2, '0'), ' PM')
                            WHEN HOUR(clock_in) = 0 THEN 
                                CONCAT('12:', 
                                       LPAD(MINUTE(clock_in), 2, '0'), ':',
                                       LPAD(SECOND(clock_in), 2, '0'), ' AM')
                            ELSE 
                                CONCAT(LPAD(HOUR(clock_in), 2, '0'), ':', 
                                       LPAD(MINUTE(clock_in), 2, '0'), ':',
                                       LPAD(SECOND(clock_in), 2, '0'), ' AM')
                        END
                    ELSE '--:--:-- --'
                END as clock_in,
                CASE 
                    WHEN clock_out IS NOT NULL THEN 
                        CASE 
                            WHEN HOUR(clock_out) >= 12 THEN 
                                CONCAT(LPAD(HOUR(clock_out) - 12, 2, '0'), ':', 
                                       LPAD(MINUTE(clock_out), 2, '0'), ':',
                                       LPAD(SECOND(clock_out), 2, '0'), ' PM')
                            WHEN HOUR(clock_out) = 0 THEN 
                                CONCAT('12:', 
                                       LPAD(MINUTE(clock_out), 2, '0'), ':',
                                       LPAD(SECOND(clock_out), 2, '0'), ' AM')
                            ELSE 
                                CONCAT(LPAD(HOUR(clock_out), 2, '0'), ':', 
                                       LPAD(MINUTE(clock_out), 2, '0'), ':',
                                       LPAD(SECOND(clock_out), 2, '0'), ' AM')
                        END
                    ELSE '--:--:-- --'
                END as clock_out,
                CASE
                    WHEN total_hours IS NOT NULL AND total_hours > 0 THEN total_hours
                    WHEN clock_in IS NOT NULL AND clock_out IS NOT NULL THEN
                        TIMESTAMPDIFF(SECOND, 
                            CONCAT(date, ' ', clock_in), 
                            CONCAT(date, ' ', clock_out)
                        ) / 3600
                    ELSE 0
                END as calculated_hours,
                status,
                late_minutes,
                overtime_minutes
            FROM attendance 
            WHERE user_id = %s 
            ORDER BY date DESC, id DESC
            LIMIT %s
            """
            records = self.db.execute_query(query, (user_id, limit))

            print(f"📊 Loading attendance history for user {user_id}")
            print(f"   Found {len(records)} records")

            # Format records
            formatted_records = []
            for record in records:
                # Get hours for duration calculation
                hours_to_use = record['calculated_hours'] if 'calculated_hours' in record else record.get('total_hours',
                                                                                                          0)

                duration_str = '--:--'
                if hours_to_use and float(hours_to_use) > 0:
                    hours_float = float(hours_to_use)
                    hours = int(hours_float)
                    minutes = int((hours_float - hours) * 60)
                    duration_str = f"{hours:02d}:{minutes:02d}"
                    print(f"   Duration for record: {hours_float:.2f} hours -> {duration_str}")

                # Create status text
                status = record['status'] or 'Present'
                status_text = status.capitalize()

                if record['late_minutes'] and int(record['late_minutes']) > 0:
                    status_text = f"Late ({record['late_minutes']}min)"

                if record['overtime_minutes'] and int(record['overtime_minutes']) > 0:
                    if 'Late' in status_text:
                        status_text = f"{status_text} +OT"
                    else:
                        status_text = f"OT ({record['overtime_minutes']}min)"

                formatted_record = {
                    'date': str(record['date']),
                    'clock_in': record['clock_in'],
                    'clock_out': record['clock_out'],
                    'duration': duration_str,
                    'status': status_text
                }
                formatted_records.append(formatted_record)

                print(f"   Record: {formatted_record}")

            return formatted_records
        except Exception as e:
            logging.error(f"Error getting user attendance: {e}")
            return []

    def get_today_status(self, user_id):
        """Get today's attendance status - FIX: Return None if clocked out"""
        try:
            today = datetime.now().date()
            query = """
            SELECT status, clock_in, clock_out, late_minutes, overtime_minutes
            FROM attendance 
            WHERE user_id = %s AND date = %s AND clock_out IS NULL
            ORDER BY id DESC LIMIT 1
            """
            result = self.db.fetch_one(query, (user_id, today))

            if result:
                print(f"📊 Today's status for user {user_id}: {result}")
                return result
            else:
                # Check if clocked out today
                clocked_out_query = """
                SELECT status, clock_in, clock_out, late_minutes, overtime_minutes
                FROM attendance 
                WHERE user_id = %s AND date = %s AND clock_out IS NOT NULL
                ORDER BY id DESC LIMIT 1
                """
                clocked_out = self.db.fetch_one(clocked_out_query, (user_id, today))

                if clocked_out:
                    print(f"📊 User {user_id} has clocked out today")
                    # Return None to indicate "Off Shift"
                    return None
                else:
                    print(f"📊 No attendance today for user {user_id}")
                    return None

        except Exception as e:
            logging.error(f"Error getting today status: {e}")
            return None

    def get_attendance_summary(self, user_id, days=30):
        """Get attendance summary for last N days"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            query = """
            SELECT 
                COUNT(CASE WHEN status = 'present' THEN 1 END) as present_days,
                COUNT(CASE WHEN status = 'absent' THEN 1 END) as absent_days,
                COUNT(CASE WHEN status = 'late' THEN 1 END) as late_days,
                COUNT(CASE WHEN overtime_minutes > 0 THEN 1 END) as overtime_days
            FROM attendance 
            WHERE user_id = %s AND date BETWEEN %s AND %s
            """
            result = self.db.fetch_one(query, (user_id, start_date, end_date))

            if result:
                print(f"📊 30-day summary for user {user_id}: {result}")
            else:
                result = {'present_days': 0, 'absent_days': 0, 'late_days': 0, 'overtime_days': 0}
                print(f"📊 No attendance in last 30 days for user {user_id}")

            return result
        except Exception as e:
            logging.error(f"Error getting attendance summary: {e}")
            return {'present_days': 0, 'absent_days': 0, 'late_days': 0, 'overtime_days': 0}

    def get_today_attendance_for_user(self, user_id):
        """Get today's attendance record for a user"""
        try:
            today = datetime.now().date()
            query = """
            SELECT 
                id,
                date,
                clock_in,
                clock_out,
                status,
                total_hours,
                late_minutes,
                overtime_minutes
            FROM attendance 
            WHERE user_id = %s AND date = %s
            ORDER BY id DESC
            LIMIT 1
            """
            result = self.db.fetch_one(query, (user_id, today))
            return result
        except Exception as e:
            logging.error(f"Error getting today's attendance: {e}")
            return None
