import requests
import json
import sys
import time
import pdb
import os

# The "secret" service we're connecting to
_init_url = ""
_js_to_inject = "function(){%s}" % (open('data' + os.path.sep + 'lib' + os.path.sep + 'stdTests.js').read(5000))
_command_url = ''

def do_command(command, data={}, url=''):
    if not url:
        url = _command_url
    #print "executing %s/%s" % (url, command),
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post('%s/%s' % (url, command),
                             data=json.dumps(data), headers=headers)
    print command + ' complete, status: ' + str(response.status_code)
    #print response.text.encode('utf-8').strip()
    #if response.status_code == 500:
    #    sys.exit(1)
    return response


def make_tab(url, uastring, country='gb', city='london'):
    global _command_url
    # Get a tab from the Great Britain
    data = {'country': country, 'city': city}
    response = do_command("new", data, _init_url)
    # The tab url from the previous request, all upcomin requests will be sent to that url
    _command_url = json.loads(response.text)["url"]
    # Set User Agent
    data = {'userAgent': uastring}
    response = do_command("setUserAgent", data)
    # Open URL
    data = {'url':url}
    response = do_command("open", data)
    # Insert helper method
    response = do_command("evaluate", {"script":_js_to_inject})
    return url;

def run_js(js):
    data = {'script':js}
    response = do_command('evaluate', data)
    return json.loads(response.text)['result']

def grab_screenshot():
    response = do_command("getScreenshot")
    base64 = json.loads(response.text)["data"]
    return base64

def close():
    do_command('destroy')

