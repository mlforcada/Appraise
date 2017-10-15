#!/usr/bin/env python
# Read one document-level gisting job and one result file
# And pair keys and results 
# select one specific user
# write results  to standard output
#
# MLF  20171015
import argparse
from xml.etree.ElementTree import Element, fromstring, tostring

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("jobfile",   help="Input job file uploaded to Appraise")
parser.add_argument("resultfile",help="Input job file uploaded to Appraise")
parser.add_argument("user",help="Select records from this user")
args=parser.parse_args()

# Get job
inxml=open(args.jobfile).read()
intree = fromstring(inxml)
# tree = fromstring(xml.encode("utf-8"))
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
assert(outtree.tag == "appraise-results")

outwords=dict()
for child in outtree: 
	assert(child.tag == "document-level-gisting-result")
        for i,grandchild in enumerate(child) : # each grandchild is the results for one task
			segid=grandchild.attrib["id"]
        		attrs = grandchild.attrib  # a dictionary with all attributes
                        if attrs["user"] == args.user :
                           outwords.update({segid:((grandchild.attrib["result"].split(":"))[2]).split(",")})
			   # print ((grandchild.attrib["result"].split(":"))[2]).split(",")
#print inwords
#print "-----"
#print outwords

# Compare dictionaries and generate tentative synonym list
for key in inwords :
    if key in outwords : 
       assert(len(inwords[key])==len(outwords[key])) # sanity check
       for i in range(len(inwords[key])) :
           # if inwords[key][i].strip()!=outwords[key][i].strip() :
               print key, i, inwords[key][i], outwords[key][i]
