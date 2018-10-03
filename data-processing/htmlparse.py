import csv,codecs,cStringIO
import sys
import urllib
import json
import time

from HTMLParser import HTMLParser

# create a subclass and override the handler methods

#htclass_dict = { "leaguename": func, "teamname" : func2,}
mode = 0
model_dict = {};
teamids = sys.argv[1].strip().split(',')
for i in teamids:
	model_dict[i] = [""] * 11
#typedict = {"11":"Travel Team","12":"B Team","13":"Exhibition Team"}

need_parent = False
#we cannot get gender this way (it's not exposed in a page record)
class MyHTMLParser(HTMLParser):
    def __init__(self, teamid):
	global model_dict
	model_dict[teamid][9] = 'X' #gender
	self.mode = 0
	self.teamid = teamid
    	self.need_parent = False
    	self.need_shortname = False
    	self.typedict = {"11":"Travel Team","12":"B Team","13":"Home Team","14":"Exhibition Team"}
	HTMLParser.__init__(self)
    
    def handle_starttag(self, tag, attrs):
	global model_dict
	teamid = self.teamid
	
	attrdict = { i[0]:i[1] for i in attrs }
	if self.mode == 0: #not in a tag we care about 
		if tag == 'div':
			htclass = None
			try:
				htclass = attrdict['class'].strip();
			except:
				htclass = ''
			if htclass == "leaguename" and model_dict[teamid][0] == "":
				print "found a leaguename"
				print attrs
				self.mode = 1 #leaguename mode --- this is actually the name of the team, distressingly, from looking at source for B team pages, for B teams. Basically FTS's schema is awful.
				return 
			elif htclass == "website":
				self.mode = 5 #website
				return 
			elif htclass == "value large" and model_dict[teamid][4] == "": #geography type
				self.mode = 4
				return
			elif 'teamtype-tag' in htclass and model_dict[teamid][3] == "":
				#mode == 3 #get team type
				offset = htclass.rfind("teamtype-")+9 #number at the end of the second teamtype- classname  rfind
				typenum = htclass[offset:offset+2]
				teamtype = self.typedict[typenum]
				model_dict[teamid][3] = teamtype
				if typenum != "11":
					self.need_parent = True #we are in a B team or Exhib team
				else: #if it's a travel team, we need the shortname!
					self.need_shortname = True #we are in a travel team
				return
        #print "Encountered a start tag:", tag
	if self.need_parent == True:
		if tag == "a": #first href after the team type is set
			parentid = attrdict['href'].split('/')[2]
			model_dict[self.teamid][6] = parentid #the parent id, extracted from the url used to link to it ;)
			self.need_parent = False
	if self.need_shortname == True:
		model_dict[teamid][1] = model_dict[teamid][0] #default rule we're using is to just copy the Travel Team's "longname", which is the longname for the league
		#if len(model_dict[teamid][0]) < 10: #we have to make up a shortname, so lets assume that "really short names" are already short enough
		#	model_dict[teamid][1] = model_dict[teamid][0]
		#else: #try to remove Roller Derby, Roller Girls etc from name?

    def handle_endtag(self, tag):
         if (self.mode==1 or self.mode==4 or self.mode==5) and tag=="div":
		self.mode = 0
		return 
    def handle_data(self, data):
	global model_dict
	teamid = self.teamid
	if self.mode == 1:
		model_dict[teamid][0] = data #we found a leaguename -- this is the thing tagged as "leaguename" in FTS pages, but might be a teamname for us?
	#       we need a way to get the "shortname" of the team - I think we can only see this in the "results" listings, as it's used there for the team representation (but only for the travel team)
	#	model_dict[teamid][1] = data #shortname
	#elif mode = 2:
	#	model_dict[teamid][?] = data #we found a "team name" -- this is tagged as "teamname" in FTS pages, but it's not clear what it maps to in the representation (it's not the league name itself)
	elif self.mode == 4:
		model_dict[teamid][4] = data #we found a website
	elif self.mode == 5:
		model_dict[teamid][5]  = data #we found a geographical location
	# 	model_dict[teamid][6] = data #we found a parent teamid
        #print "Encountered some data  :", data

# instantiate the parser and fed it some HTML

for i in teamids:
	parser = MyHTMLParser(i)
	
	
	with open(i+".html",'rb') as infile :
		html = infile.read().decode('utf-8')
	parser.feed(html)

def q(txt):
	return '"'+txt+'"'

with open("output.csv",'wb') as outfile:
	for i in teamids:
		outfile.write(q(i) + ',' + ','.join([q(j) for j in model_dict[i]])+'\n')


