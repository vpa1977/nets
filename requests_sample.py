import requests

# http://docs.python-requests.org/en/master/user/advanced/

session = requests.Session()
proxies = {'http' : 'http://ladder.ru' }
session.auth('user', 'pass')
session.headers.update({'key', 'value'})

req = session.get('http://ladder.ru', cookies={'from_me', 'value'})

headers = req.headers

session.post('http://ladder.ru', data = 'key:value')



#GET
import urllib2

req = urllib2.Request('http://www.voidspace.org.uk')
response = urllib2.urlopen(req)
the_page = response.read()


#POST
import urllib
import urllib2

url = 'http://www.someserver.com/cgi-bin/register.cgi'
values = {'name' : 'Michael Foord',
          'location' : 'Northampton',
          'language' : 'Python' }

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()


#headers 

import urllib
import urllib2

url = 'http://www.someserver.com/cgi-bin/register.cgi'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
values = {'name': 'Michael Foord',
          'location': 'Northampton',
          'language': 'Python' }
headers = {'User-Agent': user_agent}

data = urllib.urlencode(values)
req = urllib2.Request(url, data, headers)
response = urllib2.urlopen(req)
the_page = response.read()


#Basic AUTH

# create a password manager
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

# Add the username and password.
# If we knew the realm, we could use it instead of None.
top_level_url = "http://example.com/foo/"
password_mgr.add_password(None, top_level_url, username, password)

handler = urllib2.HTTPBasicAuthHandler(password_mgr)

# create "opener" (OpenerDirector instance)
opener = urllib2.build_opener(handler)

# use the opener to fetch a URL
opener.open(a_url)

# Install the opener.
# Now all calls to urllib2.urlopen use our opener.
urllib2.install_opener(opener)

# USE SSL
#https://code.activestate.com/recipes/456195/
  
# set Proxy 
req.set_proxy('proxy', 'http')

#cookies
opener = urllib2.build_opener()
opener.addheaders.append(('Cookie', 'cookiename=cookievalue'))
f = opener.open("http://example.com/")

import pdb

pdb.set_trace() # breakpoint

print(x)




#CookieJAR

import cookielib
import urllib2

cookies = cookielib.LWPCookieJar()
handlers = [
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    urllib2.HTTPCookieProcessor(cookies)
    ]
opener = urllib2.build_opener(*handlers)

def fetch(uri):
    req = urllib2.Request(uri)
    return opener.open(req)

def dump():
    for cookie in cookies:
        print cookie.name, cookie.value

uri = 'http://www.google.com/'
res = fetch(uri)
dump()

res = fetch(uri)
dump()

# save cookies to disk. you can load them with cookies.load() as well.
cookies.save('mycookies.txt')
 
