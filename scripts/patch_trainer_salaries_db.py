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
        
        print("Adding bonus and deductions to TrainerSalaries...")
        cur.execute("ALTER TABLE TrainerSalaries ADD COLUMN bonus DECIMAL(12,0) NOT NULL DEFAULT 0 AFTER sessionBonus;")
        cur.execute("ALTER TABLE TrainerSalaries ADD COLUMN deductions DECIMAL(12,0) NOT NULL DEFAULT 0 AFTER bonus;")
        
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
