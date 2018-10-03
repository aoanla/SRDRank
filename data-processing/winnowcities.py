import sys
with open("country-vector.uniform") as f:
	ct = set([fi.decode('utf-8').strip().split(u"|")[0] for fi in f.readlines()])

with open(sys.argv[1]) as f:
	cities = [fi.decode('utf-8').strip().split(u"|") for fi in f.readlines()]

winnow = [ cti for cti in cities if cti[2] in ct ]

wiset = set([wi[2] for wi in winnow])


#for human verification of if we're missing country matches (we already know we have to sed 's/ of America//' the namesout to make USA -> US to match
print wiset

print ct - wiset

with open("cities-vector.uniform",'wb') as f:
	for i in winnow:
		f.write( (u'|'.join(i)+'\n').encode('utf-8') )


