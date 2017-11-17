#!/usr/bin/env python
# Read one document-level gisting job and one result file
# And pair keys and results 
# select one specific user
	#
# MLF  20171117
import argparse
import sys
from xml.etree.ElementTree import Element, fromstring, tostring
import datetime 

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("jobfile",   help="Input job file uploaded to Appraise")
parser.add_argument("resultfile",help="Input job file uploaded to Appraise")
parser.add_argument("user",help="Select records from this user")
parser.add_argument("--errors",action="store",default=False, help="Print differences found ('errors')")
parser.add_argument("--synonym_file",action="store",default=False, help="Input a synonym file")	
args=parser.parse_args()

def get_sec(time_str): # convert timestamp to seconds
	pt =datetime.datetime.strptime(time_str,'%H:%M:%S.%f')
	return pt.second+pt.minute*60+pt.hour*3600+pt.microsecond/float(1000000)

# Get job
inxml=open(args.jobfile).read()
intree = fromstring(inxml)
# intree = fromstring(inxml.encode("utf-8"))
assert(intree.tag == "set")

# Store results in a dictionary? Key is seg id
inwords=dict()
for child in intree: 
	assert(child.tag == "seg")
        segid = child.attrib["id"]
        # the second grandchild is the translation tag
        # containing the keywords           
        inwords.update({segid:(child[2].attrib["keys"]).split(";")})

# debugging printing

outxml=open(args.resultfile).read()
outtree = fromstring(outxml)
# outtree = fromstring(outxml.encode("utf-8"))
assert(outtree.tag == "appraise-results")

outwords=dict()
for child in outtree: 
	assert(child.tag == "document-level-gisting-result")
        for i,grandchild in enumerate(child) : # each grandchild is the results for one task
			segid=grandchild.attrib["id"]
        		attrs = grandchild.attrib  # a dictionary with all attributes
                        if attrs["user"] == args.user :
							if len(grandchild.attrib["result"].split(":"))>2 :
								outwords.update({segid:((grandchild.attrib["result"].split(":"))[2]).split(",")})
			   # print ((grandchild.attrib["result"].split(":"))[2]).split(",")
#print inwords
#print "-----"
#print outwords

# Read in a synonym file --- this is wrong now
synsub=() # empty just in case
if args.synonym_file!=False :
	sfn= open(args.synonym_file,"r")
	synsub=dict()
	for line in sfn.readlines() :
		sline=line.split()
		assert len(sline)==2, "Lines should contain two words"
		key=sline[0]
		alternative=sline[1]
		if key in synsub:
		   synsub[key].append(alternative)
		else :
		   synsub.setdefault(key,[alternative])


# Compare results and keys and generate a list of differences if --print_errors is present.
# Errors are not reported if synonyms are there
if args.errors!=False :
	if args.errors=="-" :
		efn = sys.stdout
	else :
		efn = open(args.errors,"w")
	for key in inwords :
		if key in outwords : 
			assert(len(inwords[key])==len(outwords[key])) # sanity check
			for i in range(len(inwords[key])) :
				_iw=inwords[key][i].strip()
				_ow=outwords[key][i].strip()
				# print "_iw={0} _ow={1}".format(_iw.encode("utf-8"),_ow.encode("utf-8"))
				# print "Different?", _iw != _ow
				# print _iw.encode("utf-8"), " in synonym list?", _iw in synsub
				# if _iw in synsub :
				#	print _ow.encode("utf-8"), " a synonym of ", _iw.encode("utf-8"), "?" , _ow in synsub[_iw] 
				if _iw!=_ow and not ( _iw in synsub and (_ow in synsub[_iw])) : 
					tobewritten="{0} {1} {2} {3}\n".format(key, i, _iw.encode("utf-8"), _ow.encode("utf-8"))
					efn.write(tobewritten)
					
				
