import requests
import json
import sys
import time
import pdb
import argparse

def do_command(url, command, data={}):
    print "executing %s/%s\n" % (url, command),
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post('%s/%s' % (url, command),
                             data=json.dumps(data), headers=headers)
    print response.status_code
    print response.text.encode('utf-8').strip()
    if response.status_code == 500:
        sys.exit(1)

    return response

def wk2std(css_prop):
    # first strip 'webkit' prefix
    if css_prop[0:6] == 'webkit':
        css_prop = css_prop[6:]
        css_prop = css_prop.lower()
    if css_prop[0:8] == '-webkit-':
        css_prop = css_prop[8:]

    return css_prop

parser = argparse.ArgumentParser(description=("Test a site, output CSS comparison"))
parser.add_argument("-s", dest='site', type=str, help="the site you want to test", default=None)
args = parser.parse_args()
if not args.site:
    print('ERROR: no site argument. Use -s http://www.example.com')
    quit()
# Get two tabs from the Great Britain
data = {'country': 'gb', 'city': 'london', 'engine': 'gecko'}
gecko_engine = do_command("http://127.0.0.1:7331", "new", data)
data['engine'] = 'webkit'
wk_engine = do_command("http://127.0.0.1:7331", "new", data)

# The tab url from the previous request, all upcoming requests will be sent to that url
gurl = gecko_engine.json()["url"]
wurl = wk_engine.json()["url"]


# Set User Agent
data = {'userAgent': 'Mozilla/5.0 (Android; Mobile; rv:30.0) Gecko/30.0 Firefox/30.0'}
response = do_command(gurl, "setUserAgent", data)
data = {'userAgent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'}
response = do_command(wurl, "setUserAgent", data)

# Open URL
data = {'url': args.site}
response = do_command(gurl, "open", data)
response = do_command(wurl, "open", data)

# Run a DOM based javascript, if a result is to be expected it can be found under {'result'} of the json string returned
data = {'script': ""}
f = open('css-analysis.js', 'r')
data['script'] = f.read()
f.close()
gresult = do_command(gurl, "evaluate", data)
wresult = do_command(wurl, "evaluate", data)

gresult = gresult.json()
wresult = wresult.json()

print('Webkit-result: %s' % wresult['result'])
print('Gecko-result: %s' % gresult['result'])

if 'result' in gresult:
    gresult = gresult['result']
if 'result' in wresult:
    wresult = wresult['result']

wobj = json.loads(wresult)
for obj in wobj:
    for prob in obj['problems']:
        css_prop = wk2std(prob['property'])
        js = """
function(){
    return getComputedStyle(document.querySelectorAll("%s")[%i], "")["%s"];
}
    """ % (obj['selector'], obj['index'], css_prop)
        check = do_command(gurl, 'evaluate', {'script':js})
        if 'result' in check.json():
            print('\n * In Webkit: %s{ %s: %s } - in Gecko: %s:%s' % (obj['selector'], prob['property'],
                prob['value'], css_prop, check.json()['result']))


# Destroy Tab
response = do_command(gurl, "destroy")
response = do_command(wurl, "destroy")
