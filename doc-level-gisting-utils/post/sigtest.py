import numpy as np
from scipy.stats import ttest_ind, ks_2samp
from scipy.special import stdtr

a=open("/tmp/a")
lines=a.readlines()
a.close()
a_set=[]
for line in lines: 
   a_set.append(float(line.strip("\n")))
b=open("/tmp/b")
lines=b.readlines()
b.close()
b_set=[]
for line in lines: 
   b_set.append(float(line.strip("\n")))
   

wt, wp = ttest_ind(a_set, b_set, equal_var=False)
kss, ksp = ks_2samp(a_set, b_set)

print "Welch's test: p={0:6.3f}".format(wp)	
print "Kolmogorov-Smirnov test: stat={0:12.9f} p={1:6.3f}".format(kss,ksp)	
