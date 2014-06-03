import json
import urllib2, urllib

auth_url = "http://localhost:5000/login"
username = raw_input("Enter your NOI username: ")
password = raw_input("Enter your NOI password: ")

request = urllib2.Request(auth_url)
request.add_header('User-Agent', 'Browser')
request.add_header('accept', 'application/json')

params = urllib.urlencode(dict(username=username, password=password))
request.data = params

response = urllib2.urlopen(request)

token_data = json.loads(response.read())

print "AUTHENTICATION SUCCESSFUL"

test_url = "http://localhost:5000/NY/229?token={0}".format(token_data['token'])
request = urllib2.Request(test_url)
request.add_header('User-Agent', 'Browser')
request.add_header('accept', 'application/json')
response = urllib2.urlopen(request)

if response.code >= 200 and response.code < 300:
	print "TEST SUCCESSFUL"
else:
	print "TEST FAILURE"