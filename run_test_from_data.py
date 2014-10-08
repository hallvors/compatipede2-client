from compatipedelib import make_tab, run_js, grab_screenshot, close
import json, time, argparse, os, re, glob, datetime, base64, sys

datafiledir = 'data' + os.path.sep + 'bugs' + os.path.sep
uadatafile = 'data' + os.path.sep + 'uadata.json'

today = str(datetime.date.today())
resultsdir = 'results-%s' % today
if not os.path.exists(resultsdir):
    os.mkdir(resultsdir)

uadata = json.load(open(uadatafile))

idx = 0
run_until = None
all_results = []

# Support some command line arguments, the most important is -b to run test for a specific bug only
parser = argparse.ArgumentParser(description=("Test a list of sites, by bug number"))
parser.add_argument("-b", dest='bugnumber', type=str, help="bug number you want to run a test for", default=None)
parser.add_argument("-s", dest='start_at', type=int, help="start at a certain index in list, 0-based", default=0)
args = parser.parse_args()
start_at = args.start_at
if args.bugnumber is not None:
    if not os.path.exists("%s%s.json" % (datafiledir, args.bugnumber)):
        print('WARNING: no data for bug number %s found.' % str(args.bugnumber))
        sys.exit(1)
    else:
        data = {args.bugnumber:json.load(open('%s%s.json' % (datafiledir,args.bugnumber)))}
        bugnumbers = [args.bugnumber]
else: # args.bugnumber is None, run all bugs

    data = {}
    bugnumbers = []

    for fn in glob.glob('%s*.json' % datafiledir):
        bug = re.search(re.compile('\d+'), fn).group(0)
        f = open(fn)
        data[bug] = json.load(f)
        bugnumbers.append(bug)
        f.close()

bugnumbers.sort()
print 'Will run tests for %i bugs' % len(bugnumbers)

for bug in bugnumbers:
    try:
        print '%i: %s' % (idx, bug)
        if idx < start_at:
            idx += 1
            continue
        if (run_until and idx > run_until):
            quit()

        if not 'title' in data[bug]: # older entries do not quote the bug's summary (not required by the scripts but useful for human review)
            data[bug]['title'] = ''

        service_url = make_tab(data[bug]['url'], uadata[data[bug]['ua']])
        for step in data[bug]['steps']:
            result = run_js(step)
            if result is 'delay-and-retry': # TODO: repeat this up to n times (Slimer JS test script does 10 times w/2.5 sec delay)
                time.wait(15)
                result = run_js(step)
        csv = "%s\t%s\t%s\n" % (bug, data[bug]['title'], str(result))
        fh = open(resultsdir + os.path.sep + str(bug) + '.csv', 'w')
        fh.write(csv)
        fh.close()
        print(csv)
        all_results.append(csv)
        idx += 1
        b64image = grab_screenshot()
        fh = open(resultsdir + os.path.sep + bug + ".png", "wb")
        fh.write(base64.b64decode(b64image))
        fh.close()

        close()
    except Exception, e:
        print 'WARNING: exception happened while testing %s' % bug
        print e

fh = open(resultsdir + os.path.sep + 'all_results.csv', "w")
fh.write('\n'.join(all_results))
fh.close()
