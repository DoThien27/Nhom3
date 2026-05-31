from app.database import get_db_context
from app.models import BuoiHoc

class ClassService:
    @staticmethod
    def lay_tat_ca():
        with get_db_context() as (conn, cur):
            sql = """SELECT c.*, u.fullName as trainerName, s.sport_name as sportName, f.facility_name as facilityName,
                            (SELECT COUNT(*) FROM ClassEnrollments WHERE classId = c.id) as enrolledCount
                     FROM Classes c 
                     LEFT JOIN Users u ON c.trainerId = u.id 
                     LEFT JOIN Sports s ON c.sportId = s.sport_id 
                     LEFT JOIN Facilities f ON c.facilityId = f.facility_id"""
            cur.execute(sql)
            classes = cur.fetchall()
            
            # Convert to dict and fetch enrollments for each class
            result = []
            for cl in classes:
                cl_dict = dict(cl)
                cur.execute("SELECT memberId, status FROM ClassEnrollments WHERE classId = %s", (cl_dict['id'],))
                # Store as a dictionary for easy access in frontend: { memberId: status }
                cl_dict['enrollments'] = {r['memberId']: r['status'] for r in cur.fetchall()}
                cl_dict['enrolledIds'] = list(cl_dict['enrollments'].keys()) # Keep enrolledIds for backward compatibility
                result.append(cl_dict)
                
            return result

    @staticmethod
    def them(c: BuoiHoc):
        with get_db_context() as (conn, cur):
            sql = """INSERT INTO Classes (id, name, trainerId, sportId, facilityId, time, dayOfWeek, capacity, price, status, startDate, endDate) 
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql, (c.id, c.name, c.trainerId, c.sportId, c.facilityId, c.time, c.dayOfWeek, c.capacity, c.price, c.status, c.startDate, c.endDate))
            conn.commit()
        return c

    @staticmethod
    def sua(id, name, trainerId, sportId, facilityId, time, dayOfWeek, capacity, price, status, startDate=None, endDate=None):
        with get_db_context() as (conn, cur):
            sql = """UPDATE Classes SET name=%s, trainerId=%s, sportId=%s, facilityId=%s, time=%s, dayOfWeek=%s, capacity=%s, price=%s, status=%s, startDate=%s, endDate=%s WHERE id=%s"""
            cur.execute(sql, (name, trainerId, sportId, facilityId, time, dayOfWeek, capacity, price, status, startDate, endDate, id))
            conn.commit()

    @staticmethod
    def xoa(id):
        with get_db_context() as (conn, cur):
            cur.execute("SELECT COUNT(*) as c FROM ClassEnrollments WHERE classId=%s", (id,))
            has_enrollments = cur.fetchone()['c'] > 0
            
            if has_enrollments:
                cur.execute("UPDATE Classes SET status='CANCELLED' WHERE id=%s", (id,))
                cur.execute("UPDATE ClassEnrollments SET status='CANCELLED' WHERE classId=%s", (id,))
            else:
                cur.execute("DELETE FROM Classes WHERE id=%s", (id,))
            conn.commit()
