import csv,codecs,cStringIO
import sys
import urllib
import json
import time
import numpy as np
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
# create a subclass and override the handler methods

#htclass_dict = { "leaguename": func, "teamname" : func2,}
scores = []
leagues = []
files = sys.argv[1]
#teamids = sys.argv[1].strip().split(',')
#for i in teamids:
#	model_dict[i] = [""] * 11

#we cannot get gender this way (it's not exposed in a page record)
class MyHTMLParser(HTMLParser):
    def __init__(self, dateid):
	self.dateid = dateid
	self.mode = 0
	self.armed = False
	self.cont = False
	self.col = 0
	self.strtmp = u''
	self.scorecol = None
	self.leaguecol = None
	HTMLParser.__init__(self)
    
    def handle_starttag(self, tag, attrs):
	if tag == 'thead': #read header for file
		self.mode = 1
		self.col = 0
		return
	elif tag == 'tbody': #in body of table
		self.mode = 2
		return
	elif tag == 'th' or tag == 'td': #for each header entry
		self.armed = True
		self.col += 1
		return
	elif tag == 'tr': #in a new data entry line
		self.col = 0 #reset counter
		return
    def handle_endtag(self, tag):
	if tag == 'th' or tag == 'td':
		self.armed = False
		if self.cont:
			if self.col == self.scorecol:
                        	scores.append(float(self.strtmp.replace(u',',u'')))
                        	return
                	if self.col == self.leaguecol:
                        	leagues.append(self.strtmp)
			self.cont = False #continuation flag used to merge data + entityrefs
    def handle_charref(self,name):
	if self.armed:
		if name.startswith('x'):
            		c = unichr(int(name[1:], 16))
       	 	else:
            		c = unichr(int(name))
		if not self.cont:
			self.strtmp = u''
			self.cont = True
		self.strtmp += c
    def handle_data(self, data):
	global scores
	global leagues
	if not self.armed:
		return 
	if self.mode == 1: #scanning
		if data == 'SCORE' or data == 'Score':
			self.scorecol = self.col
			return
		if data == 'LEAGUE' or data == 'League':
			self.leaguecol = self.col
			return
	if self.mode == 2:
		if self.col == self.scorecol or self.col == self.leaguecol:
			if not self.cont:
				self.strtmp = u''
				self.cont = True
                        self.strtmp += data

# instantiate the parser and fed it some HTML

#for i in teamids:
parser = MyHTMLParser('DATE')
html = open(files,'rb').read().decode('utf-8')
parser.feed(html)

#print [':'.join(i) for i in zip(leagues,scores)]


#load the conversion list
with open('wftda-to-fts-mapping' , 'rb') as conv_list:
	fts_list = [ i.decode('utf-8').strip().split(u'|') for i in conv_list.readlines() ]
	fts_dict = { i[0]:i[1] for i in fts_list }

#and get our (ordered) id list
ids = [ fts_dict[l] for l in leagues ]

#for normalised rating
mean = np.mean(scores)
stddev = np.std(scores)

normal = [(i - mean) / stddev for i in scores]

#remove ranking- and .html

outputfilename = files[9:-5]+".out"

#make a rating file in our format
with open(outputfilename,'wb') as lout:
	counter = 1
	for i in zip(ids,scores, normal):
		string = "{0}|{1:d}|{2:d}|{3:.3f}|{4:.2f}|{5:.4f}|{6:.2f}|{7:d}".format(i[0],0, 0,i[1],0,i[2],0,counter)
		counter += 1
		lout.write(string+'\n')

