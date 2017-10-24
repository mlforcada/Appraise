#!/usr/bin/env python
# Read one document-level gisting job and one result file
# And pair keys and results 
# select one specific user
	#
# MLF  20171024
import argparse
import sys
from xml.etree.ElementTree import Element, fromstring, tostring
import datetime 

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("jobfile",   help="Input job file uploaded to Appraise")
parser.add_argument("resultfile",help="Input job file uploaded to Appraise")
parser.add_argument("user",help="Select records from this user")
parser.add_argument("--errors",action="store",default=False)
parser.add_argument("--synonym_file",action="store",default=False)	
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
							if len(grandchild.attrib["result"])>2 :
								outwords.update({segid:((grandchild.attrib["result"].split(":"))[2]).split(",")})
			   # print ((grandchild.attrib["result"].split(":"))[2]).split(",")
#print inwords
#print "-----"
#print outwords

# Read in a synonym file
if args.synonym_file!=False :
	sfn= open(args.synonym_file,"r")
	synsub=dict()
	for line in sfn.readlines() :
		sline=line.split()
		assert len(sline)==2, "Lines should contain two words"
		key=sline[0]
		alternative=sline[1]
		synsub.update({key:alternative})
	# print synsub


# Compare results and keys and generate a list of differences if --print_errors is present.
if args.errors!=False :
	if args.errors=="-" :
		efn = sys.stdout
	else :
		efn = open(args.errors,"w")
	for key in inwords :
		if key in outwords : 
			assert(len(inwords[key])==len(outwords[key])) # sanity check
			for i in range(len(inwords[key])) :
				if inwords[key][i].strip()!=outwords[key][i].strip() :
					tobewritten="{0} {1} {2} {3}\n".format(key, i, inwords[key][i].encode("utf-8"), outwords[key][i].encode("utf-8"))
					efn.write(tobewritten)
