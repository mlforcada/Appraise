#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

# MLF 20170517
# Ugly wrapper around prepare_one_2.py to generate a set of tasks
# Will initially write all tasks for a job in a specific directory
# And will merge them later using a shell
# Will later modify prepare_one_2.py to generate snippets that are easier to merge

# For inspiration
# system=google; name=OSU; number=13; echo $system;  python prepare_one_2.py --percentage 20 --raw-model /home/mlf/tmp/kenlm/news-commentary-v8.arpa.en  --binary-model /home/mlf/tmp/kenlm/news-commentary-v8.blm.en ~/Escriptori/durham/sheffield/carol-s-data/creg/human/$name"_"text-id\=$number.txt ~/Escriptori/durham/sheffield/carol-s-data/creg/$system/$name"_"text-id\=$number.txt problems/$name-$number.xml -v --setid $name-$number --docid $name-$number --sl de --tl en --adjacent_gaps_not_ok --system $system

import argparse
import os
import sys # do I need it?

reload(sys)
sys.setdefaultencoding("utf-8")

parser = argparse.ArgumentParser()
parser.add_argument("informant",help="Informant number", type=int)
parser.add_argument('-v', '--verbose', help='Verbose Mode', dest="verbose", action='store_true',default=False)
parser.add_argument('--dry_run', help='Dry run', dest="dry_run", action='store_true',default=False)
args = parser.parse_args()

informant=args.informant

raw_model = "/home/mlf/tmp/kenlm/news-commentary-v8.arpa.en"
binary_model = "/home/mlf/tmp/kenlm/news-commentary-v8.blm.en"
documents_root="/home/mlf/Escriptori/durham/sheffield/carol-s-data/creg/"

target_directory="/tmp/"  

# languages
sl = "de"
tl = "en"

# conditions for configurations
percentages = ["10", "20"]
strategies=["--no_entropy",""]
systems = ["google", "moses", "systran", "bing", "--no_hint"]
realsystems = ["google", "moses", "systran", "bing"]
contexts = ["--no_context", ""]

# file names
files = [("KU","13"),
("KU","15"),
("KU","22"),
("KU","24"),
("KU","30"),
("KU","38"),
("KU","39"),
("KU","46"),
("OSU","103"),
("OSU","109"),
("OSU","110"),
("OSU","113"),
("OSU","114"),
("OSU","117"),
("OSU","118"),
("OSU","13"),
("OSU","1"),
("OSU","29"),
("OSU","30"),
("OSU","31"),
("OSU","38_1"),
("OSU","38_2"),
("OSU","3"),
("OSU","47"),
("OSU","51"),
("OSU","57"),
("OSU","65_1"),
("OSU","67_2"),
("OSU","69_3"),
("OSU","80"),
("OSU","81"),
("OSU","83"),
("OSU","88"),
("TUE","10"),
("TUE","13"),
("TUE","5")]

nfiles=len(files)

# generate configurations
no_hinting_configurations = [[percentage,strategy,"--no_hint", "--no_context"] for percentage in percentages for strategy in strategies ]
hinting_configurations=[[percentage,"",system,context] for percentage in percentages for system in realsystems for context in contexts ]



configurations = no_hinting_configurations + hinting_configurations
nconfig = len(configurations)
if args.verbose :
   print "Number of configurations: " , nconfig
	
# indexing parts of a configuration by name
iPercentage=0
iStrategy=1
iSystem=2
iContext=3

iCondition=0
iFile=1

iName=0
iNumber=1




# current set of configurations for this informant
c = []

# assign jobs for this informant
for d,f in enumerate(range(nfiles)) :
	cid = (informant + d) % nconfig     # c(i,d)=(i+d-1) mod C in paper
	c.append([configurations[cid],files[f]])
 
	
results_directory = target_directory + str(informant)
os.system("mkdir "+  results_directory ) # change to target directory and create a file for informant 	
	
for k,config in enumerate(c) :
    if args.verbose : 
       print "Writing files for", k,":",config
    
    # put together document name
    if config[iCondition][iSystem]=="--no_hint" :
       system_for_hinting = "human" # workaround: have to read something in anyway when --no_hint
       system_for_switch = "NONE"
       hinting_switch = "--no_hint"
    else :
       system_for_hinting=config[iCondition][iSystem]
       system_for_switch= config[iCondition][iSystem]
       hinting_switch = ""  # put together command line
    if config[iCondition][iContext]=="--no_context" :
       context="-doc"
    else :
       context="+doc"
    if config[iCondition][iStrategy]=="--no_entropy" :
       strategy="-ent"
    else :
       strategy="+ent"      
    docname = config[iFile][iName] + "_text-id=" + config[iFile][iNumber] + ".txt"
    docid = config[iFile][iName] + "-" + config[iFile][iNumber] + ":" + str(informant)
    setid = docid + ":" + system_for_switch + ":" + context + ":" + str(informant) + ":" + strategy
    
    command="python prepare_one_2.py" +  \
	  " --percentage " + config[iCondition][iPercentage] + \
	  " --raw-model " + raw_model + \
	  " --binary-model " + binary_model + \
	  " " + documents_root + "human/" + docname + \
	  " " + documents_root + system_for_hinting + "/" + docname + \
	  " " + results_directory + "/" + setid + ".xml" + \
	  " --setid " + setid + \
	  " --docid " + docid + \
	  " --sl " + sl + \
	  " --tl " + tl + \
	  " --adjacent_gaps_not_ok" + \
	  " " + config[iCondition][iStrategy] + \
	  " " + config[iCondition][iContext] + \
	  " --system " + system_for_switch + \
	  " " + hinting_switch + \
	  " -v";
    print "Issuing command: number ", k
    print command
    if not args.dry_run :
       os.system(command)
	
