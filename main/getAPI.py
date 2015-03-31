import base64
import requests
import json


# Note current URLS that work:
# 'http://social-distribution.herokuapp.com/api/posts'

def getAPI (url, username, password, host):
	basicstring = "Basic "+ base64.b64encode(str(username) + ':' +  str(host) + ':' + str(password))
	headers = {'Authorization': basicstring, 'Host': str(host)}
	req = requests.get(str(url), headers=headers)
	content = json.loads(req.content)
	return content

