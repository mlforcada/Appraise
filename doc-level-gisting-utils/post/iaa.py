# pairwise Pearson correlation for 36 problems among 3 annotators

import csv
from scipy.stats.stats import pearsonr

sets=[]
for i in range(20) :
	_set=[]
	_set.append("inf{0}".format(i))
	_set.append("inf{0}".format(i+20))
	_set.append("inf{0}".format(i+40))
	sets.append(_set)
   
   
rows = []
with open("results.csv") as csvfile :
	reader=csv.DictReader(csvfile)
	for row in reader :
		rows.append(row)
		
# brute force, could be better
# Careful if one set is different!
for k,s in enumerate(sets):		
	_a=[]
	_b=[] 
	_c=[]
	_sa=0
	_sb=0
	_sc=0
	for row in rows :
		if row["Informant"]==s[0] :
			_a.append(float(row["Score"]))
			_sa=_sa+float(row["Score"])
		if row["Informant"]==s[1] :
			_b.append(float(row["Score"]))
			_sb=_sb+float(row["Score"])
		if row["Informant"]==s[2] :
			_c.append(float(row["Score"]))
			_sc=_sc+float(row["Score"])
	_out = "Configuration {0} Informants {1},{2},{3}:".format(k,s[0],s[1],s[2])
	_out = _out + "[{0:5.3f},{1:5.3f},{2:5.3f}]".format(_sa/len(_a),_sb/len(_b),_sc/len(_c))
	if len(_a)==len(_b):
	   _r12,_p=pearsonr(_a,_b)
	   _out=_out+"r12={0:5.3f},".format(_r12)
	if len(_a)==len(_c):
	   _r13,_p=pearsonr(_a,_c)
	   _out=_out+"r13={0:5.3f},".format(_r13)
	if len(_b)==len(_c):		
	   _r23,_p=pearsonr(_b,_c)
	   _out=_out+"r23={0:5.3f}".format(_r23)
	print _out
