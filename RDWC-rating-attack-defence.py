import numpy as np
import exagony
import statsmodels.api as sm
import sys
import shutil
import time

#modification of rating.py for ATTACK, DEFENCE
teams_ = [i.upper() for i in exagony.teamnames]
teams_a  = [i.upper()+'_A' for i in exagony.teamnames] #teams from exagony
teams_d = [i.upper()+'_D' for i in exagony.teamnames]
teams = teams_a + teams_d

rr = []

if len(sys.argv) < 2:
	print "Specify bout list"
	sys.exit(1)

f = open(sys.argv[1],'r')
for line in f.readlines():
	if line[0] == '#': #skip comment lines
		continue
	try:
		t1,s1,t2,s2,w,p,_,_,_ = line.strip().split('|')
	except:
		print line
		sys.exit(1)
	mul = 1.0
	if p == 'one' or p == 'two':
		mul = 2.0
	if t1[0] == '#': #comment
		continue
	if t1[0] == '*': #start of row marker
		t1 = t1[1:]
	if s1 == '*' or s1 == '-': #not done yet
		continue 
	if s1 == '0':
		s1 = 0.5
	if s2 == '0':
		s2 = 0.5
	#shouldn't need this bit because we have an external teams list
	#if t1 not in teams:
	#	teams.append(t1)
	#if t2 not in teams:
	#	teams.append(t2)
	#Keener factor 1 on scores, so all safe
	rr.append([{'name':t1,'score':float(s1)*mul},{'name':t2,'score':float(s2)*mul},float(w)])
f.close()

tot_cols = len(rr)*2 #total number of results
tot_rows = len(teams)
#indexing function, maps teamnames to row
idx = { i[0]:i[1] for i in zip(teams,range(len(teams)))}
col = 0
A = np.zeros([tot_cols,tot_rows])
Y = np.zeros(tot_cols)
W = np.zeros(tot_cols)
for r in rr:
	#make A, Y matrices
	# 0'A v 1'D
	A[col][idx[r[0]['name']+'_A']] = 1
	A[col][idx[r[1]['name']+'_D']] = -1
	Y[col] = np.log(r[0]['score'])
	W[col] = r[2]*r[2] #weights are proportional to 1/variance, not 1/sigma
	# 0'D v 1'A
	A[col+1][idx[r[0]['name']+'_D']] = -1
	A[col+1][idx[r[1]['name']+'_A']] = 1
	Y[col+1] = np.log(r[1]['score'])
	W[col+1] = r[2]*r[2] #weights are proportional to 1/variance, not 1/sigma
	col += 2

#and solve by least squares for B
# should be WLS, with W as weight fector
#res = sm.OLS(Y,A).fit_regularized(L1_wt=1.0) #Lasso (L2 w/ L1 reg)
res = sm.WLS(Y,A,W).fit()
#print res.summary()
#print res.params

tmp_massey = {}
for t,p in zip(teams,res.params):
	tmp_massey[t] = p

for t in teams:
	print "{0}|{1}".format(t,tmp_massey[t])

team_vector = {}
for t in teams_:
	team_vector[t] = [tmp_massey[t+'_A'],tmp_massey[t+'_D']]

def compare_teams(t1,t2): #compare team scores, which needs us to make a team score for each from the Attack and Defence values
	t1s = team_vector[t1][0]-team_vector[t2][1]
	t2s = team_vector[t2][0]-team_vector[t1][1]
	return cmp(t1s,t2s)

t_sorted = sorted(teams_, cmp=compare_teams)

#print t_sorted
for t in t_sorted:
	print '{0}|{1[0]}|{1[1]}'.format(t, team_vector[t])

sys.exit()




tt = time.localtime()
timestamp = "ratings-"+time.strftime('%b-%d-%Y_%H%M', tt)+".tsv"

shutil.copy("ratings.tsv", timestamp)

f = open('ratings.tsv','wb')
g = open(timestamp, 'rb')

#assumes that the rating.tsv is in the fixed exagony order, which should never be broken by this code
for t in teams:
	tmp = g.readline().strip() + "|{0:.3f}\n".format(tmp_massey[t])
	f.write(tmp)

f.close()
g.close()

#and this output then plugs into the scheduler / matcher
#exagony names are Initial + lowercase -> we need to map those names to ALLCAPS for webpage name building in all cases
