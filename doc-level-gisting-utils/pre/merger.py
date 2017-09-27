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

import argparse
import string

parser=argparse.ArgumentParser()
parser.add_argument("--setid", dest="setid", help="New set identifier", default="defaultsetid")
parser.add_argument("--outfile", dest="outfile", help="Output file")
parser.add_argument("mergefiles", metavar="mergefile", help="files to merge", nargs='+')
args=parser.parse_args()

nfiles=len(args.mergefiles)

out=open(args.outfile,"w")
out.write('<set id="' + args.setid  + '" source-language="de" target-language="en">\n')

segcounter=0
for _file in args.mergefiles :
    _lines=open(_file).readlines()
    segcounter=segcounter+1 #each file has a single segment; won't work otherwise
    for i in range(1,len(_lines)-1) :
        out.write(_lines[i].replace("editme::", str(segcounter) + ":inf" + args.setid + ":"))
out.write( '</set>'	 )
out.close()
   


