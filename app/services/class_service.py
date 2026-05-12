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
            
            # Fetch enrollment IDs for each class
            for cl in classes:
                cur.execute("SELECT memberId FROM ClassEnrollments WHERE classId = %s", (cl['id'],))
                cl['enrolledIds'] = [r['memberId'] for r in cur.fetchall()]
                
            return classes

    @staticmethod
    def them(c: BuoiHoc):
        with get_db_context() as (conn, cur):
            sql = """INSERT INTO Classes (id, name, trainerId, sportId, facilityId, time, dayOfWeek, capacity, price, status) 
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql, (c.id, c.name, c.trainerId, c.sportId, c.facilityId, c.time, c.dayOfWeek, c.capacity, c.price, c.status))
            conn.commit()
        return c

    @staticmethod
    def sua(id, name, trainerId, sportId, facilityId, time, dayOfWeek, capacity, price, status):
        with get_db_context() as (conn, cur):
            sql = """UPDATE Classes SET name=%s, trainerId=%s, sportId=%s, facilityId=%s, time=%s, dayOfWeek=%s, capacity=%s, price=%s, status=%s WHERE id=%s"""
            cur.execute(sql, (name, trainerId, sportId, facilityId, time, dayOfWeek, capacity, price, status, id))
            conn.commit()

    @staticmethod
    def xoa(id):
        with get_db_context() as (conn, cur):
            cur.execute("SELECT COUNT(*) as c FROM ClassEnrollments WHERE classId=%s", (id,))
            if cur.fetchone()['c'] > 0:
                raise ValueError("Không thể xóa lớp đang có học viên đăng ký")
            cur.execute("DELETE FROM Classes WHERE id=%s", (id,))
            conn.commit()
