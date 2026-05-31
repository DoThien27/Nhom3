import urllib.request, json, http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
data = json.dumps({'username':'admin','password':'Admin@123'}).encode()
req = urllib.request.Request('http://localhost:5000/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
opener.open(req)

tests = [
    ('/api/classes', 'GET classes'),
    ('/api/facilities', 'GET facilities'),
    ('/api/trainer-attendance?month=5&year=2025', 'GET attendance'),
    ('/api/trainer-payroll?month=5&year=2025', 'GET payroll'),
    ('/api/trainer-salary?month=5&year=2025', 'GET salary'),
    ('/api/users', 'GET users'),
    ('/api/events/EVT001/participants', 'GET event participants'),
]
for path, name in tests:
    req2 = urllib.request.Request('http://localhost:5000' + path, headers={'Content-Type':'application/json'})
    try:
        res = json.loads(opener.open(req2).read())
        cnt = len(res.get('data', []))
        ok = res.get('success')
        print(name + ': OK=' + str(ok) + ' count=' + str(cnt))
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:120]
        print(name + ': ERROR ' + str(e.code) + ' - ' + body)
