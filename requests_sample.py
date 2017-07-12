import requests

# http://docs.python-requests.org/en/master/user/advanced/

session = requests.Session()
proxies = {'http' : 'http://ladder.ru' }
session.auth('user', 'pass')
session.headers.update({'key', 'value'})

req = session.get('http://ladder.ru', cookies={'from_me', 'value'})

headers = req.headers

session.post('http://ladder.ru', data = 'key:value')

