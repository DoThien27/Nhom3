from app.database import get_db_context

def clear_member_auth():
    try:
        with get_db_context() as (conn, cur):
            print("Cleaning up member login credentials...")
            cur.execute("UPDATE Members SET username = NULL, password = NULL")
            conn.commit()
            print("Successfully cleared all member credentials!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_member_auth()
