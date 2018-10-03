import timeit
import numpy as np
import exagony
import scipy.optimize as optimize
import statsmodels.api as sm
import sys
import shutil
import time
from itertools import product

#minimiser testbed - uses inequalities for bounds on 0 values, and allows you to use different Lp norms, and different minimiser routines
# currently runs each calculation 5 times - 4 times in timeit for an estimate of the time needed, and 1 time to get an actual sample result 

teams = [i.upper() for i in exagony.teamnames] #teams from exagony
rr = []

if len(sys.argv) < 2:
	print "Specify bout list"
	sys.exit(1)

f = open(sys.argv[1],'r')
for line in f.readlines():
	if line[0] == '#': #skip comment lines
		continue
	try:
		t1,s1,t2,s2,w,_,_,_,_ = line.strip().split('|')
	except:
		print line
		sys.exit(1)
	if t1[0] == '#': #comment
		continue
	if t1[0] == '*': #start of row marker
		t1 = t1[1:]
	if s1 == '*' or s1 == '-': #not done yet
		continue 
	#shouldn't need this bit because we have an external teams list
	if t1 not in teams:
		teams.append(t1)
	if t2 not in teams:
		teams.append(t2)
	op = '='
	if s1 == '0':
		op = '<'
		s1 = '1'
	if s2 == '0':
		op = '>'
		s2 = '1'
	#Keener factor 1 on scores, so all safe
	rr.append([{'name':t1,'score':float(s1)},{'name':t2,'score':float(s2)},float(w), op])
f.close()

tot_cols = len(rr) #total number of results
tot_rows = len(teams)
#indexing function, maps teamnames to row
idx = { i[0]:i[1] for i in zip(teams,range(len(teams)))}
col = 0
A = [ [1,1] for i in range(tot_cols) ]
Y = np.zeros(tot_cols)
W = np.zeros(tot_cols)
O = [ '=' for i in range(tot_cols) ] #operation to test, can also be < or >
for r in rr:
	#make A, Y matrices
	A[col] = (idx[r[0]['name']],idx[r[1]['name']])  #+1, -1 parts of the linear difference (A-B)
	Y[col] = np.log(r[0]['score']/r[1]['score'])
	W[col] = r[2] #weights are proportional to 1/variance, not 1/sigma
	O[col] = r[3]
	col += 1
#and solve by least squares for B
# should be WLS, with W as weight fector
#res = sm.OLS(Y,A).fit_regularized(L1_wt=1.0) #Lasso (L2 w/ L1 reg)

def total_error(test_vector, P=1):
	err = 0
	for Ai,Yi,Wi,Oi in zip(A,Y,W,O):
		pred = test_vector[Ai[0]] - test_vector[Ai[1]]
		obs = Yi
		delta = (obs - pred) * Wi
		if Oi == '=':
			err += np.abs(delta)**P #or delta if L1 (P=1), delta**2 if L2 (P=2)
		elif Oi == '<' and delta < 0: #if we need things to be less than, and pred was greater than
			err += np.abs(delta)**P
		elif Oi == '>' and delta > 0: #if we need things to be greater than, and pred was less than
			err += np.abs(delta)**P
	return err

def optimiser_wrapper(t_="Nelder-Mead", P=1):
	if t_=="Nelder-Mead" or t_=="Powell":
		def w_():
			return optimize.minimize(total_error, [1 for i in range(tot_rows)], method=t_, args=(P,), options={"maxiter":1000000, "maxfev":1000000})
	elif t_=="DiffEvo":
		def w_():
			return optimize.differential_evolution(total_error, [(0,9) for i in range(tot_rows)], args=(P,)) 
	return w_

#res = optimize.minimize(total_error, [1 for i in range(tot_rows)], method="Nelder-Mead")
#res = optimize.differential_evolution(total_error, [(0,9) for i in range(tot_cols)])

test_P = [1.5]
test_M = ["Nelder-Mead","Powell", "DiffEvo"]

test_sets = list(product(test_M, test_P))

for tt in test_sets:
	test = optimiser_wrapper(tt[0],tt[1])
	time_taken = timeit.timeit(test, number=4)
	res = test()
	print "****************************************************"
	print "Test {0} L{1}. Average time {2}".format(tt[0],tt[1],time_taken)
	print "Success? {0}".format(res.success)
	if res.success == False:
		print "****"
		print "Failure, dump of result object:"
		print res
		print "****"
	print "Rating output:"
	min_p = min(res.x)
	for t,p in zip(teams, res.x):
		 print '{0} {1}'.format(t,np.exp(p-min_p))


sys.exit()
#print "Optimized Params"
#print res.x


#res = sm.WLS(Y,A,W).fit()
#print res.summary()
#print res.params

tmp_massey = {}
min_p = min(res.x)
#print min_p
for t,p in zip(teams,res.x):
	tmp_massey[t] = p
#	print p
#	print min_p
#	print p-min_p
	print '{0} {1}'.format(t,np.exp(p-min_p))

