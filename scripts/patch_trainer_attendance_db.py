import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "sports_club_db")

def main():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cur = conn.cursor()
        
        print("Adding classId to TrainerAttendance...")
        cur.execute("ALTER TABLE TrainerAttendance ADD COLUMN classId VARCHAR(36) NULL AFTER attendanceDate;")
        print("Adding Foreign Key constraint...")
        cur.execute("ALTER TABLE TrainerAttendance ADD CONSTRAINT fk_trainer_attendance_class FOREIGN KEY (classId) REFERENCES Classes(id) ON DELETE SET NULL ON UPDATE CASCADE;")
        
        conn.commit()
        print("Successfully updated database schema!")
        
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()

if __name__ == "__main__":
    main()
