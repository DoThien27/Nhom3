from database.db_connection import get_db_context
from utils.logger import logger

def lay_kpi_tong_quan() -> dict:
    """
    Lấy các chỉ số KPI bằng SQL aggregation thay vì tải toàn bộ bảng vào bộ nhớ.
    """
    try:
        with get_db_context() as (conn, cur):
            kpi = {}
            
            # Đếm số lượng Hội viên, HLV, Môn, Lớp
            cur.execute("SELECT COUNT(*) as c FROM Members WHERE status = 'ACTIVE'")
            kpi['tong_hoi_vien'] = cur.fetchone()['c'] or 0
            
            cur.execute("SELECT COUNT(*) as c FROM Users WHERE role = 'PT'")
            kpi['tong_hlv'] = cur.fetchone()['c'] or 0
            
            cur.execute("SELECT COUNT(*) as c FROM Sports")
            kpi['tong_mon'] = cur.fetchone()['c'] or 0
            
            cur.execute("SELECT COUNT(*) as c FROM Classes")
            kpi['tong_lop'] = cur.fetchone()['c'] or 0
            
            # Tính doanh thu tổng
            cur.execute("SELECT SUM(final_amount) as s FROM Invoices WHERE payment_status = 'PAID'")
            kpi['doanh_thu'] = cur.fetchone()['s'] or 0.0
            
            # Danh sách sự kiện sắp tới (chỉ lấy top 9 cho Dashboard)
            cur.execute(
                "SELECT * FROM Events WHERE status = 'UPCOMING' "
                "ORDER BY date ASC LIMIT 9"
            )
            from models.models import SuKien
            events = []
            for row in cur.fetchall():
                events.append(SuKien(
                    id=str(row['id']),
                    ten=row['name'],
                    mo_ta=row['description'],
                    ngay=str(row['date']),
                    gio=row['time'],
                    dia_diem=row['location'],
                    suc_chua=row['capacity'],
                    gia=float(row['price'] or 0.0),
                    trang_thai=row['status']
                ))
            kpi['su_kien_sap_toi'] = events
            
            return kpi
    except Exception as e:
        logger.error(f"Dashboard Service Error: {e}")
        return {
            'tong_hoi_vien': 0, 'tong_hlv': 0, 'tong_mon': 0, 
            'tong_lop': 0, 'doanh_thu': 0.0, 'su_kien_sap_toi': []
        }

def lay_bao_cao_tong_hop() -> dict:
    try:
        with get_db_context() as (conn, cur):
            bc = {}
            # Doanh thu
            cur.execute("SELECT SUM(final_amount) as s FROM Invoices WHERE payment_status = 'PAID'")
            bc['tong_dt'] = cur.fetchone()['s'] or 0.0
            
            # Hôm nay
            from datetime import date
            thang_nay = date.today().strftime("%Y-%m")
            cur.execute("SELECT SUM(final_amount) as s FROM Invoices WHERE payment_status = 'PAID' AND date LIKE %s", (thang_nay + '%',))
            bc['dt_thang_nay'] = cur.fetchone()['s'] or 0.0

            # KPIs
            cur.execute("SELECT status, COUNT(*) as c FROM Members GROUP BY status")
            bc['hv_active'] = 0
            bc['hv_expired'] = 0
            bc['hv_pending'] = 0
            for row in cur.fetchall():
                if row['status'] == 'ACTIVE': bc['hv_active'] = row['c']
                elif row['status'] == 'EXPIRED': bc['hv_expired'] = row['c']
                elif row['status'] == 'PENDING': bc['hv_pending'] = row['c']
                
            cur.execute("SELECT COUNT(*) as c FROM Events WHERE status = 'UPCOMING'")
            bc['su_kien_upcoming'] = cur.fetchone()['c'] or 0
            
            cur.execute("SELECT COUNT(*) as c FROM ClassEnrollments")
            bc['tong_hoc_vien'] = cur.fetchone()['c'] or 0

            # Doanh thu theo thời gian (ví dụ 6 tháng gần nhất)
            cur.execute("SELECT SUBSTRING(date, 1, 7) as thang, SUM(final_amount) as s "
                        "FROM Invoices WHERE payment_status = 'PAID' GROUP BY thang ORDER BY thang DESC LIMIT 6")
            bc['dt_theo_thang'] = [(row['thang'], float(row['s'] or 0.0)) for row in cur.fetchall()][::-1]

            cur.execute("SELECT COUNT(*) as c FROM Members")
            bc['tong_hoi_vien'] = cur.fetchone()['c'] or 0

            cur.execute("SELECT i.id, i.date, i.final_amount, i.method, m.fullName as ten_hv "
                        "FROM Invoices i LEFT JOIN Members m ON i.memberId = m.id "
                        "ORDER BY i.date DESC LIMIT 10")
            bc['top_invoices'] = []
            for row in cur.fetchall():
                bc['top_invoices'].append({
                    'id': row['id'],
                    'ngay': str(row['date']),
                    'tong_tien': float(row['final_amount'] or 0.0),
                    'phuong_thuc': row['method'],
                    'ten_hv': row['ten_hv'] or "Unknown"
                })

            cur.execute("SELECT COUNT(*) as c FROM Invoices")
            bc['tong_hoa_don'] = cur.fetchone()['c'] or 0

            # Top sản phẩm bán chạy
            cur.execute("""
                SELECT item_name, SUM(quantity) as qty, SUM(line_total) as rev
                FROM InvoiceItems
                GROUP BY item_name
                ORDER BY rev DESC
                LIMIT 6
            """)
            bc['top_sp'] = []
            for row in cur.fetchall():
                bc['top_sp'].append({
                    'ten': row['item_name'],
                    'qty': int(row['qty'] or 0),
                    'rev': float(row['rev'] or 0.0)
                })

            # Tình trạng lớp học
            cur.execute("""
                SELECT c.name, c.capacity, u.fullName as hlv_name,
                       (SELECT COUNT(*) FROM ClassEnrollments ce WHERE ce.classId = c.id) as so_hv
                FROM Classes c
                LEFT JOIN Users u ON c.trainerId = u.id
                LIMIT 10
            """)
            bc['tinh_trang_lop'] = []
            for row in cur.fetchall():
                bc['tinh_trang_lop'].append({
                    'ten': row['name'],
                    'suc_chua': int(row['capacity'] or 0),
                    'hlv_name': row['hlv_name'] or "Unknown",
                    'so_hv': int(row['so_hv'] or 0)
                })

            return bc
    except Exception as e:
        logger.error(f"Dashboard Service Error (Reports): {e}")
        return {
            'tong_dt': 0.0, 'dt_thang_nay': 0.0,
            'hv_active': 0, 'hv_expired': 0, 'hv_pending': 0,
            'su_kien_upcoming': 0, 'tong_hoc_vien': 0,
            'dt_theo_thang': [], 'top_invoices': [],
            'tong_hoi_vien': 0, 'tong_hoa_don': 0
        }
