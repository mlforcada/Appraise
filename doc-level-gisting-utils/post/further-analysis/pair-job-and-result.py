#!/usr/bin/env python
# IMPROVE THIS DESCRIPTION
# select one specific user
# write results in CSV format to standard output
# read in synonym file
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


# Read in a synonym file if one is specified
synsub=() # empty just in case, even if no synonyms are read in
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


outxml=open(args.resultfile).read()
outtree = fromstring(outxml)
# outtree = fromstring(outxml.encode("utf-8"))
assert(outtree.tag == "appraise-results")

outwords=dict() # not needed, but let's keep a record
for child in outtree: 
	assert(child.tag == "document-level-gisting-result")
        for i,grandchild in enumerate(child) : # each grandchild is the results for one task
			segid=grandchild.attrib["id"]
        		attrs = grandchild.attrib  # a dictionary with all attributes
                        if attrs["user"] == args.user :
							_docid = attrs["doc-id"].split(":")[0]
							_type = attrs["type"]
							_percentage,_system, _context,_mode = _type.split(":")
							_result = attrs["result"]
							_tmp = _result.split(":")
							if len(_tmp)>1 :
								_ratio = _tmp[1]
								_out = 1 
							else :
								_out= 0 
#							_numerator, _denominator = _ratio.split("/")
#							_denominator = _denominator.split(",")[0]
#							_rate = float(_numerator)/float(_denominator)
							_id = attrs["id"]
							_serial = _id.split(":")[0]
							_informant = _id.split(":")[1]
							_infnumber = _id.split(":")[3]
							_duration = get_sec(attrs["duration"])
							if len(grandchild.attrib["result"].split(":"))>2 :
								owr=((grandchild.attrib["result"].split(":"))[2]).split(",")
								outwords.update({segid:owr})  # As said above, let's keep a record
								assert(len(inwords[segid])==len(owr)) # sanity check
								ngaps=len(inwords[segid])
								hits=ngaps
								for j in range(ngaps) :
									_iw=inwords[segid][j].strip()
									if _iw!=inwords[segid][j] :
										print "***"
									_ow=owr[j].strip()
									if _ow!=owr[j].strip() :
										print "***"
									if _iw!=_ow and not ( _iw in synsub and (_ow in synsub[_iw])) : 
										hits=hits-1
							_rate=float(hits)/float(ngaps)	
							if (_out):
								print '"{0}","{1:4.2f}","{2}","{3}","{4}","{5:8.6f}","{6}","{7}","{8:11.6f}","{9}"'.format(_docid, float(_percentage)/100.00, _system, _context, _mode, _rate, _serial, _informant, _duration, _infnumber)
								

# This may contain some repeated code, will solve later
# Compare results and keys and generate a list of differences if --errors is present.
# Errors are not reported if synonyms are there
if args.errors!=False :
	if args.errors=="-" :
		efn = sys.stdout
	else :
		efn = open(args.errors,"a")
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
					
				
