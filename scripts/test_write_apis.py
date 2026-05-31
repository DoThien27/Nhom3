import urllib.request, json, http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def api_call(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        'http://localhost:5000' + path,
        data=data,
        headers={'Content-Type': 'application/json'},
        method=method
    )
    try:
        res = json.loads(opener.open(req).read())
        return res
    except urllib.error.HTTPError as e:
        return {'success': False, 'error': e.read().decode()[:200], 'code': e.code}

# 1. Login
res = api_call('POST', '/auth/login', {'username': 'admin', 'password': 'Admin@123'})
print('LOGIN:', res.get('success'))

# 2. Them hoi vien moi (INSERT - khong REPLACE INTO)
res = api_call('POST', '/api/members', {
    'fullName': 'Test Hoi Vien', 'phone': '0987654321', 'email': 'test@test.com',
    'gender': 'Nam', 'status': 'PENDING'
})
print('POST /api/members:', res.get('success'), '| error:', res.get('error',''))
member_id = res.get('member', {}).get('id', '')

# 3. Sua hoi vien (UPDATE)
if member_id:
    res = api_call('PUT', f'/api/members/{member_id}', {
        'fullName': 'Test Hoi Vien Updated', 'phone': '0987654321',
        'gender': 'Nam', 'status': 'PENDING'
    })
    print('PUT /api/members/id:', res.get('success'), '| error:', res.get('error',''))

# 4. Cap the hoi vien
res = api_call('POST', '/api/member-cards', {
    'memberId': 'MBR003',
    'issueDate': '2025-05-01',
    'expiryDate': '2026-05-01'
})
print('POST /api/member-cards:', res.get('success'), '| cardNumber:', res.get('cardNumber', ''), '| error:', res.get('error',''))

# 5. Checkin
res = api_call('POST', '/api/checkins', {'memberId': 'MBR001', 'checkType': 'MANUAL'})
print('POST /api/checkins:', res.get('success'), '| error:', res.get('error', ''))
checkin_id = res.get('checkInId','')

# 6. Checkout
if checkin_id:
    res = api_call('PUT', f'/api/checkins/{checkin_id}/checkout', {})
    print('PUT /api/checkins/id/checkout:', res.get('success'), '| checkOutTime:', res.get('checkOutTime',''))

# 7. Them sport
res = api_call('POST', '/api/sports', {'name': 'Bong da', 'description': 'Tap bong da'})
print('POST /api/sports (name field):', res.get('success'), '| error:', res.get('error',''))

# 8. Them facility
res = api_call('POST', '/api/facilities', {'name': 'San bong', 'location': 'Tang 4'})
print('POST /api/facilities (name field):', res.get('success'), '| error:', res.get('error',''))

# 9. Tao hoa don
res = api_call('POST', '/api/billing', {
    'memberId': 'MBR003', 'totalAmount': 500000, 'paymentMethod': 'CASH', 'paymentStatus': 'PAID'
})
print('POST /api/billing:', res.get('success'), '| error:', res.get('error',''))

# 10. Them HLV moi
res = api_call('POST', '/api/trainers', {
    'username': 'hlv_new', 'password': 'Test@123',
    'fullName': 'Tran Van Test', 'specialty': 'Boxing', 'phone': '0900000009'
})
print('POST /api/trainers:', res.get('success'), '| error:', res.get('error',''))

# 11. Dang ky su kien
res = api_call('POST', '/api/events/EVT001/participants', {'memberId': 'MBR002'})
print('POST /api/events/EVT001/participants:', res.get('success'), '| error:', res.get('error',''))

# 12. Xoa hoi vien test
if member_id:
    res = api_call('DELETE', f'/api/members/{member_id}', None)
    print('DELETE /api/members/test_id:', res.get('success'), '| error:', res.get('error',''))

print()
print('=== ALL TESTS DONE ===')
