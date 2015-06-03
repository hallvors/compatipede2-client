from compatipedelib import make_tab, run_js, grab_screenshot, close
import json, time, argparse, os, re, glob, datetime, base64, tldextract

datafiledir = os.path.join('data', 'bugs') + os.path.sep
uadatafile = os.path.join('data', 'uadata.json')

today = str(datetime.date.today())
resultsdir = 'results-%s' % today
if not os.path.exists(resultsdir):
    os.mkdir(resultsdir)

uadata = json.load(open(uadatafile))

helper_trigger_js = "function(){return hasHandheldFriendlyMeta() + '\\t' + hasViewportMeta() + '\\t' + hasMobileOptimizedMeta() + '\\t' + mobileLinkOrScriptUrl() + '\\t' + hasVideoTags() + '\\t' + pageWidthFitsScreen() + '\\t' + hasHtmlOrBodyMobileClass()}"

def host_from_url(url):
    tmp = tldextract.extract(url)
    if not tmp.subdomain in ['www', '']:
        tmp = '%s.%s.%s' % (tmp.subdomain, tmp.domain, tmp.suffix)
    else:
        tmp = '%s.%s' % (tmp.domain, tmp.suffix)
    return tmp


idx = 0
run_until = None
all_results = []

parser = argparse.ArgumentParser(description=("Test a list of sites, by bug number"))
parser.add_argument("-b", dest='bugnumber', type=int, help="bug number you want to run a test for", default=None)
parser.add_argument("-s", dest='start_at', type=int, help="start at a certain index in list, 0-based", default=0)
parser.add_argument("-e", dest='end', type=int, help="end at a certain index in list, 0-based", default=0)
parser.add_argument("-f", dest='file', type=str, help="URL list file (plain text)", default=None)
args = parser.parse_args()
start_at = args.start_at
run_until = args.end
urlfile = args.file
if urlfile is not None:
    if not os.path.exists(urlfile):
        print('WARNING: file %s found.' % str(urlfile))
        quit()
    else:
        url_list = open(urlfile, 'r').read().split('\n')
        data = {}
        bugnumbers = []
else: # args.bugnumber is None, run all bugs
    print('-f file.txt argument is required')
    quit()

print 'Will run tests for %i urls' % len(url_list)
for url in url_list:
    csv = ''
    result = ''
    result_wk = ''
    stats_wk = ''
    try:
        print '%i: %s' % (idx, url)
        if idx < start_at:
            idx += 1
            continue
        if (run_until and idx > run_until):
            quit()
        host = host_from_url(url)
        if not host in data:
            data[host] = {'title': host, 'steps': [
                # Second run: we first try to find a 'video' or 'watch' link..
                """function(){
                    for(var i=0,l;l=document.links[i];i++){
                        if((l.textContent + l.href).indexOf("video")>-1)l.click();
                    }
                    // hi accuweather
                    for(var i=0,o;o=document.getElementsByTagName("option")[i];i++){
                        if(o.value.indexOf("video"))o.click();
                    }
                }""",
                # Let's first look for the tell-tale scripts
                """function(){
                    for(var i=0,f; f=document.getElementsByTagName("iframe")[i]; i++){
                        if(f.src.indexOf("players.brightcove.net")>-1)return "new";
                        if(f.src.indexOf("c.brightcove.com")>-1)return "old";
                    }
                    for(var i=0,s; s=document.scripts[i];i++){
                        if(s.src.indexOf("players.brightcove.net")>-1)return "new";
                        if(/(brightcove\\.js|BrightcoveExperiences?\\.js|admin\\.brightcove\\.com|c\\.brightcove\\.com)/i.test(s.src))return "old";} return "none";}"""
            ]}

        print('new tab coming up')
        service_url = make_tab(url, uadata['FirefoxAndroid'])
        print('will run steps')
        for step in data[host]['steps']:
            print('step %s' % str(step))
            result = run_js(service_url, step)
            if result is 'delay-and-retry':
                print('(waiting..)')
                time.wait(15)
                result = run_js(service_url, step)
        stats = run_js(service_url, helper_trigger_js)
        if result == False:
            service_url_wk = make_tab(url, uadata['iPhone'], 'webkit')
            print('Retesting in WebKit.. will run steps')
            for step in data[host]['steps']:
                print('step %s' % str(step))
                result_wk = run_js(service_url, step)
                if result_wk is 'delay-and-retry':
                    print('(waiting..)')
                    time.wait(15)
                    result_wk = run_js(service_url, step)
            stats_wk = run_js(service_url, helper_trigger_js)
            b64image = grab_screenshot(service_url_wk)
            fh = open(resultsdir + os.path.sep + str(host) + "_wk.png", "wb")
            fh.write(base64.b64decode(b64image))
            fh.close()
            close(service_url_wk)

        csv = "%s\t%s\t%s\t%s\tG:\t%s\tW:\t%s\n" % (host, data[host]['title'], str(result), str(result_wk),stats, stats_wk)
        fh = open(resultsdir + os.path.sep + str(host) + '.csv', 'w')
        fh.write(csv)
        fh.close()
        b64image = grab_screenshot(service_url)
        fh = open(resultsdir + os.path.sep + str(host) + ".png", "wb")
        fh.write(base64.b64decode(b64image))
        fh.close()

        close(service_url)
    except Exception:
        print 'WARNING: exception happened while testing %s' % url

    if csv:
        print(csv)
        all_results.append(csv)
    idx += 1

fh = open(resultsdir + os.path.sep + 'all_results.csv', "w")
fh.write('\n'.join(all_results))
fh.close()
