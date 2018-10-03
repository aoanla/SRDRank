import csv,codecs,cStringIO
import sys
import urllib
import json
import time



class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

ftsdata = []
with open(sys.argv[1],'rb') as ftsteamfile:
	ftsteamfile.readline() #remove the header
	reader = UnicodeReader(ftsteamfile)
	ftsdata = {r[0]:r[1:] for r in reader}

#ftsdata keyed by id

bout_teamset= set()
with open(sys.argv[2],'rb') as ftsboutfile:
	ftsboutfile.readline() #remove the header
	reader = UnicodeReader(ftsboutfile)
	for r in reader:
		bout_teamset.add(r[4]) #push teams in this bout into set
		bout_teamset.add(r[6]) 

#cross-check
ks = ftsdata.keys()

for t in bout_teamset:
	if (t not in ks):
		print str(t)
		urllib.urlretrieve("http://flattrackstats.com/teams/" + str(t),str(t)+".html")
		time.sleep(5)
sys.exit(0)


