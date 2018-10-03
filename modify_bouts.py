import sys
import csv
import time
#tool to build changelist for bout splitting on basis of preprocessing by process-for-Python tool (in iterate over the world mode)
# we take in a change_from list, and process it into sets of "dates after which you should modify team ids like this"
#    - we then process a bouts list in the appropriate way (using a sorted list of keys for efficiency)

f = open(sys.argv[1],'r')
timedict = {}
tmp = {}
key = None
for l in f.readlines():
	#if we have a new time
	if l[:3] == 'Ref':
		if key is not None:
			timedict[key] = tmp 
		key = int(l.strip().split(':')[1].split('.')[0]) #key is unixtime to adjust things *after*
		tmp = {}
	else:
		v = l.strip().split('|')
		tmp[v[0]] = v[1]
f.close()

#sentinel value - 2038, the last date in 32bit unixtime
timedict[2147483645] = {}

sortedkeys = sorted(timedict.keys())
print [ (tk, len(timedict[tk])) for tk in sortedkeys ]


#process bouts
f = open(sys.argv[2], 'r')
g = open(sys.argv[2]+'.split', 'w')

f.readline()

#csv parsing

boutreader = csv.reader(f)
boutwriter = csv.writer(g,quoting=csv.QUOTE_ALL)

nextkeyid = 0
nextkey = sortedkeys[0]
keydict = {}
for row in boutreader:
	teams = [row[4],row[6]]
	d = time.mktime(time.strptime(row[1],'%Y-%m-%d'))
	if d > nextkey: #if we're in a new key applicability regime
		print "New key: {}".format(nextkey)
		keydict = timedict[nextkey]
		nextkeyid += 1
		nextkey = sortedkeys[nextkeyid]
	if row[4] in keydict:
		row[4] = keydict[row[4]]
	if row[6] in keydict:
		row[6] = keydict[row[6]]
	boutwriter.writerow(row)

f.close()
g.close()
