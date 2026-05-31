import os

file_path = 'app/routes/class_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

helper_code = """
def check_class_overlap(trainerId, facilityId, start_date_str, end_date_str, time_str, dayOfWeek_str, exclude_class_id=None):
    if not (start_date_str and end_date_str and time_str and dayOfWeek_str):
        return None

    try:
        new_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        new_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except Exception:
        return None

    try:
        t_parts = [t.strip() for t in time_str.split('-')]
        if len(t_parts) != 2: return None
        new_start_mins = int(t_parts[0].split(':')[0])*60 + int(t_parts[0].split(':')[1])
        new_end_mins = int(t_parts[1].split(':')[0])*60 + int(t_parts[1].split(':')[1])
    except Exception:
        return None

    new_days = set([d.strip() for d in dayOfWeek_str.split(',')])

    with get_db_context() as (conn, cur):
        sql = "SELECT * FROM Classes WHERE (trainerId=%s OR facilityId=%s) AND status='ACTIVE'"
        params = [trainerId, facilityId]
        if exclude_class_id:
            sql += " AND id != %s"
            params.append(exclude_class_id)
        cur.execute(sql, tuple(params))
        classes = cur.fetchall()

    for c in classes:
        if not c['startDate'] or not c['endDate']: continue
        if c['endDate'] < new_start_date or c['startDate'] > new_end_date: continue

        if not c['dayOfWeek']: continue
        c_days = set([d.strip() for d in c['dayOfWeek'].split(',')])
        if not new_days.intersection(c_days): continue

        if not c['time']: continue
        try:
            t_parts = [t.strip() for t in c['time'].split('-')]
            if len(t_parts) != 2: continue
            c_start_mins = int(t_parts[0].split(':')[0])*60 + int(t_parts[0].split(':')[1])
            c_end_mins = int(t_parts[1].split(':')[0])*60 + int(t_parts[1].split(':')[1])
        except Exception:
            continue

        if c_end_mins <= new_start_mins or c_start_mins >= new_end_mins: continue
            
        reason = "Huấn luyện viên" if c['trainerId'] == trainerId else "Sân bãi"
        return f"Lớp học bị trùng lịch (trùng {reason}) với lớp: {c['name']} ({c['time']} {c['dayOfWeek']})"

    return None
"""

content = content.replace("class_bp = Blueprint('class_bp', __name__)", "class_bp = Blueprint('class_bp', __name__)\n" + helper_code)

add_class_original = """@class_bp.route('/api/classes', methods=['POST'])
@roles_required('ADMIN', 'PT')
def add_class():
    try:
        data = request.json"""

add_class_new = """@class_bp.route('/api/classes', methods=['POST'])
@roles_required('ADMIN', 'PT')
def add_class():
    try:
        data = request.json
        overlap_err = check_class_overlap(data.get('trainerId'), data.get('facilityId'), data.get('startDate'), data.get('endDate'), data.get('time'), data.get('dayOfWeek'))
        if overlap_err:
            return jsonify({'success': False, 'error': overlap_err}), 400
"""
content = content.replace(add_class_original, add_class_new)

add_class_obj_orig = """        c = BuoiHoc(
            id=str(uuid.uuid4())[:8],
            name=data.get('name'),
            trainerId=data.get('trainerId'),
            sportId=data.get('sportId'),
            facilityId=data.get('facilityId'),
            time=data.get('time'),
            dayOfWeek=data.get('dayOfWeek'),
            capacity=int(data.get('capacity', 20)),
            price=float(data.get('price', 0)),
            status=data.get('status', 'ACTIVE')
        )"""

add_class_obj_new = """        c = BuoiHoc(
            id=str(uuid.uuid4())[:8],
            name=data.get('name'),
            trainerId=data.get('trainerId'),
            sportId=data.get('sportId'),
            facilityId=data.get('facilityId'),
            time=data.get('time'),
            dayOfWeek=data.get('dayOfWeek'),
            capacity=int(data.get('capacity', 20)),
            price=float(data.get('price', 0)),
            status=data.get('status', 'ACTIVE'),
            startDate=data.get('startDate'),
            endDate=data.get('endDate')
        )"""
content = content.replace(add_class_obj_orig, add_class_obj_new)

update_class_orig = """@class_bp.route('/api/classes/<id>', methods=['PUT'])
@roles_required('ADMIN', 'PT')
def update_class(id):
    try:
        data = request.json"""

update_class_new = """@class_bp.route('/api/classes/<id>', methods=['PUT'])
@roles_required('ADMIN', 'PT')
def update_class(id):
    try:
        data = request.json
        overlap_err = check_class_overlap(data.get('trainerId'), data.get('facilityId'), data.get('startDate'), data.get('endDate'), data.get('time'), data.get('dayOfWeek'), id)
        if overlap_err:
            return jsonify({'success': False, 'error': overlap_err}), 400
"""
content = content.replace(update_class_orig, update_class_new)

update_call_orig = """        ClassService.sua(
            id, data.get('name'), data.get('trainerId'), data.get('sportId'),
            data.get('facilityId'), data.get('time'), data.get('dayOfWeek'),
            int(data.get('capacity', 20)), float(data.get('price', 0)), data.get('status', 'ACTIVE')
        )"""

update_call_new = """        ClassService.sua(
            id, data.get('name'), data.get('trainerId'), data.get('sportId'),
            data.get('facilityId'), data.get('time'), data.get('dayOfWeek'),
            int(data.get('capacity', 20)), float(data.get('price', 0)), data.get('status', 'ACTIVE'),
            data.get('startDate'), data.get('endDate')
        )"""
content = content.replace(update_call_orig, update_call_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
