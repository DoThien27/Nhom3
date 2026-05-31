import urllib.request
import json
from http.cookiejar import CookieJar

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def req(url, method='GET', data=None):
    r = urllib.request.Request(url, method=method)
    if data:
        r.data = json.dumps(data).encode('utf-8')
        r.add_header('Content-Type', 'application/json')
    try:
        with opener.open(r) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        if hasattr(e, 'read'):
            return json.loads(e.read().decode('utf-8'))
        return str(e)

print("Login:", req('http://localhost:5000/api/auth/login', 'POST', {'username': 'admin', 'password': 'admin123'}))

trainers = req('http://localhost:5000/api/trainers')['data']
t_id = trainers[0]['id']

facs = req('http://localhost:5000/api/facilities')['data']
f_id = facs[0]['facility_id']

c1 = {
    'name': 'Class 1',
    'trainerId': t_id,
    'sportId': None,
    'facilityId': f_id,
    'dayOfWeek': 'Thứ 2,Thứ 4',
    'time': '08:00 - 09:30',
    'capacity': 20,
    'price': 0,
    'startDate': '2025-06-01',
    'endDate': '2025-06-30'
}
print("Create Class 1:", req('http://localhost:5000/api/classes', 'POST', c1))

c2 = {
    'name': 'Class 2',
    'trainerId': t_id,
    'sportId': None,
    'facilityId': f_id,
    'dayOfWeek': 'Thứ 2,Thứ 6',
    'time': '09:00 - 10:00',
    'capacity': 20,
    'price': 0,
    'startDate': '2025-06-15',
    'endDate': '2025-07-15'
}
print("Create Class 2 (Should Fail):", req('http://localhost:5000/api/classes', 'POST', c2))

c3 = {
    'name': 'Class 3',
    'trainerId': t_id,
    'sportId': None,
    'facilityId': f_id,
    'dayOfWeek': 'Thứ 3,Thứ 5',
    'time': '09:00 - 10:00',
    'capacity': 20,
    'price': 0,
    'startDate': '2025-06-15',
    'endDate': '2025-07-15'
}
print("Create Class 3 (Should Pass):", req('http://localhost:5000/api/classes', 'POST', c3))
