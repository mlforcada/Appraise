#!/usr/bin/env python
# Read one document level gisting result file for a given job
# select one specific user
# write results in CSV format to standard output
#
# MLF  20170804 
import argparse
from xml.etree.ElementTree import Element, fromstring, tostring
import datetime 

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("inputfile",help="Input XML file exported from Appraise")
parser.add_argument("user",help="Select records from this user")
args=parser.parse_args()

def get_sec(time_str): # convert timestamp to seconds
	pt =datetime.datetime.strptime(time_str,'%H:%M:%S.%f')
	return pt.second+pt.minute*60+pt.hour*3600+pt.microsecond/float(1000000)

xml=open(args.inputfile).read()

tree = fromstring(xml)
# tree = fromstring(xml.encode("utf-8"))
assert(tree.tag == "appraise-results")

for child in tree: 
	# there's only one child, but anyway
	assert(child.tag == "document-level-gisting-result")
	for i,grandchild in enumerate(child) : # each grandchild is the results for one task in the job
		# zak=tostring(grandchild)
		attrs = grandchild.attrib  # a dictionary with all attributes of the element
		# print i
		# print attrs
		if attrs["user"] == args.user :
			# print tostring(grandchild)
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
			_numerator, _denominator = _ratio.split("/")
			_denominator = _denominator.split(",")[0]
			_rate = float(_numerator)/float(_denominator)
			_id = attrs["id"]
			_serial = _id.split(":")[0]
			_informant = _id.split(":")[1]
			_infnumber = _id.split(":")[3]
			_duration = get_sec(attrs["duration"])
                        if (_out):
			   print '"{0}","{1:4.2f}","{2}","{3}","{4}","{5:8.6f}","{6}","{7}","{8:11.6f}","{9}"'.format(_docid, float(_percentage)/100.00, _system, _context, _mode, _rate, _serial, _informant, _duration, _infnumber)
exit
