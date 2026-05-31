from app.database import get_db_context
from datetime import datetime, timedelta
from app.utils import generate_sequential_id

class PTService:
    @staticmethod
    def get_profile(user_id):
        with get_db_context() as (conn, cur):
            cur.execute("SELECT id, username, fullName, specialty, phone, address, status FROM Users WHERE id = %s", (user_id,))
            return cur.fetchone()

    @staticmethod
    def get_my_classes(trainer_id):
        with get_db_context() as (conn, cur):
            cur.execute("""
                SELECT c.*, 
                       (SELECT COUNT(*) FROM ClassEnrollments WHERE classId = c.id AND status = 'ACTIVE') as enrolled,
                       s.sport_name as sportName, f.facility_name as facilityName
                FROM Classes c
                LEFT JOIN Sports s ON c.sportId = s.sport_id
                LEFT JOIN Facilities f ON c.facilityId = f.facility_id
                WHERE c.trainerId = %s
                ORDER BY c.createdAt DESC
            """, (trainer_id,))
            return cur.fetchall()

    @staticmethod
    def get_class_students(trainer_id, class_id):
        with get_db_context() as (conn, cur):
            # Verify ownership
            cur.execute("SELECT id FROM Classes WHERE id = %s AND trainerId = %s", (class_id, trainer_id))
            if not cur.fetchone():
                raise Exception("Bạn không phụ trách lớp này")

            cur.execute("""
                SELECT m.id, m.fullName, m.phone, ce.enrolledAt, ce.status
                FROM ClassEnrollments ce
                JOIN Members m ON ce.memberId = m.id
                WHERE ce.classId = %s AND ce.status = 'ACTIVE'
            """, (class_id,))
            return cur.fetchall()

    @staticmethod
    def take_attendance(trainer_id, class_id, date_str, attendance_data):
        with get_db_context() as (conn, cur):
            # Verify ownership
            cur.execute("SELECT id FROM Classes WHERE id = %s AND trainerId = %s", (class_id, trainer_id))
            if not cur.fetchone():
                raise Exception("Bạn không phụ trách lớp này")

            # attendance_data is a list of dicts: {"memberId": "...", "status": "PRESENT"|"ABSENT", "note": "..."}
            for item in attendance_data:
                member_id = item.get("memberId")
                status = item.get("status", "PRESENT")
                note = item.get("note", "")

                cur.execute("""
                    INSERT INTO ClassAttendance (classId, memberId, date, status, note)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status), note = VALUES(note)
                """, (class_id, member_id, date_str, status, note))
            conn.commit()
            return True

    @staticmethod
    def get_attendance_history(trainer_id, class_id, date_str=None):
        with get_db_context() as (conn, cur):
            # Verify ownership
            cur.execute("SELECT id FROM Classes WHERE id = %s AND trainerId = %s", (class_id, trainer_id))
            if not cur.fetchone():
                raise Exception("Bạn không phụ trách lớp này")

            query = """
                SELECT ca.*, m.fullName 
                FROM ClassAttendance ca
                JOIN Members m ON ca.memberId = m.id
                WHERE ca.classId = %s
            """
            params = [class_id]
            if date_str:
                query += " AND ca.date = %s"
                params.append(date_str)
            query += " ORDER BY ca.date DESC, m.fullName ASC"
            
            cur.execute(query, params)
            return cur.fetchall()

    @staticmethod
    def get_my_attendance(trainer_id):
        with get_db_context() as (conn, cur):
            cur.execute("""
                SELECT ta.*, c.name as className 
                FROM TrainerAttendance ta
                LEFT JOIN Classes c ON ta.classId = c.id
                WHERE ta.trainerId = %s 
                ORDER BY ta.attendanceDate DESC
            """, (trainer_id,))
            return cur.fetchall()

    @staticmethod
    def get_my_salary(trainer_id):
        with get_db_context() as (conn, cur):
            cur.execute("""
                SELECT * FROM TrainerSalaries 
                WHERE trainerId = %s 
                ORDER BY year DESC, month DESC
            """, (trainer_id,))
            return cur.fetchall()

    @staticmethod
    def get_today_shifts(trainer_id):
        import datetime as dt
        today_date = dt.datetime.now()
        today_str = today_date.strftime('%Y-%m-%d')
        # Map Python weekday to Vietnamese format used in DB
        # Python: 0 = Monday, 6 = Sunday
        days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
        day_of_week = days[today_date.weekday()]
        
        with get_db_context() as (conn, cur):
            # Lấy các lớp học có lịch dạy hôm nay
            cur.execute("""
                SELECT id, name, time, dayOfWeek
                FROM Classes 
                WHERE trainerId = %s AND status = 'ACTIVE' AND dayOfWeek LIKE %s
            """, (trainer_id, f'%{day_of_week}%'))
            classes = cur.fetchall()
            
            # Lấy trạng thái chấm công hôm nay
            cur.execute("""
                SELECT id, classId, checkIn, checkOut, status
                FROM TrainerAttendance
                WHERE trainerId = %s AND attendanceDate = %s
            """, (trainer_id, today_str))
            attendances = cur.fetchall()
            
            shifts = []
            att_map = {a['classId']: a for a in attendances if a['classId']}
            other_atts = [a for a in attendances if not a['classId']]
            
            for c in classes:
                att = att_map.get(c['id'])
                shifts.append({
                    'type': 'CLASS',
                    'classId': c['id'],
                    'name': c['name'],
                    'time': c['time'],
                    'attendance': att
                })
            
            # Thêm các chấm công không thuộc lớp cụ thể (ngoài ca/PT 1-1)
            for att in other_atts:
                shifts.append({
                    'type': 'OTHER',
                    'classId': None,
                    'name': 'Ca làm khác (PT 1-1, Hành chính)',
                    'time': '--',
                    'attendance': att
                })
                
            return shifts

    @staticmethod
    def pt_check_in(trainer_id, class_id=None):
        today = datetime.now().strftime('%Y-%m-%d')
        now_time = datetime.now().strftime('%H:%M')
        with get_db_context() as (conn, cur):
            if class_id:
                # Kiểm tra xem lớp này đã chấm công hôm nay chưa
                cur.execute("SELECT id FROM TrainerAttendance WHERE trainerId = %s AND attendanceDate = %s AND classId = %s", (trainer_id, today, class_id))
            else:
                # Nếu là ca không lớp, cho phép chấm thêm nhưng kiểm tra xem có ca không lớp nào đang chưa check-out không
                cur.execute("SELECT id FROM TrainerAttendance WHERE trainerId = %s AND attendanceDate = %s AND classId IS NULL AND checkOut IS NULL", (trainer_id, today))
                
            if cur.fetchone():
                raise Exception("Ca này đã được check-in!")
            
            new_id = generate_sequential_id('TrainerAttendance', 'TA')
            cur.execute("""
                INSERT INTO TrainerAttendance (id, trainerId, classId, attendanceDate, checkIn, status, sessionsCount)
                VALUES (%s, %s, %s, %s, %s, 'PRESENT', 1)
            """, (new_id, trainer_id, class_id, today, now_time))
            conn.commit()
            return True

    @staticmethod
    def pt_check_out(trainer_id, attendance_id):
        now_time = datetime.now().strftime('%H:%M')
        with get_db_context() as (conn, cur):
            cur.execute("SELECT id, checkIn, checkOut FROM TrainerAttendance WHERE id = %s AND trainerId = %s", (attendance_id, trainer_id))
            row = cur.fetchone()
            if not row:
                raise Exception("Không tìm thấy bản ghi chấm công!")
            if row['checkOut']:
                raise Exception("Bạn đã check-out rồi!")
            if now_time <= row['checkIn']:
                raise Exception("Giờ check-out không hợp lệ (phải sau giờ check-in)!")
            
            cur.execute("""
                UPDATE TrainerAttendance 
                SET checkOut = %s
                WHERE id = %s
            """, (now_time, row['id']))
            conn.commit()
            return True

    @staticmethod
    def sync_absences():
        import datetime as dt
        today_date = dt.datetime.now()
        yesterday_date = today_date - timedelta(days=1)
        yesterday_str = yesterday_date.strftime('%Y-%m-%d')
        days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
        day_of_week = days[yesterday_date.weekday()]
        
        with get_db_context() as (conn, cur):
            # Lấy tất cả lớp học ACTIVE hôm qua
            cur.execute("""
                SELECT id, trainerId 
                FROM Classes 
                WHERE status = 'ACTIVE' AND dayOfWeek LIKE %s AND trainerId IS NOT NULL
            """, (f'%{day_of_week}%',))
            classes = cur.fetchall()
            
            for c in classes:
                # Kiểm tra xem PT đã chấm công chưa
                cur.execute("""
                    SELECT id FROM TrainerAttendance 
                    WHERE trainerId = %s AND attendanceDate = %s AND classId = %s
                """, (c['trainerId'], yesterday_str, c['id']))
                if not cur.fetchone():
                    new_id = generate_sequential_id('TrainerAttendance', 'TA')
                    cur.execute("""
                        INSERT INTO TrainerAttendance (id, trainerId, classId, attendanceDate, status, sessionsCount, note)
                        VALUES (%s, %s, %s, %s, 'ABSENT', 0, 'Nghỉ không phép')
                    """, (new_id, c['trainerId'], c['id'], yesterday_str))
            conn.commit()
            return True
