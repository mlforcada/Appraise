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

import kenlm
import sys
from stop_words import get_stop_words
from nltk.tokenize import word_tokenize
import argparse
import numpy 
import math
import string
import random
from gensim.summarization import keywords, summarize

def escape( str ):  # Escape some XML; lifted from http://stackoverflow.com/questions/1546717/python-escaping-strings-for-use-in-xml
    str = str.replace("<", "&lt;")
    str = str.replace(">", "&gt;")
    str = str.replace("&", "&amp;")
    # str = str.replace("\"", "&quot;")
    return str

def extract_sentence(text) :
	# Extracts one sentence from text by reducing the fraction until
	# one sentence is left
    nsent=100 
    fraction=0.5
    while nsent>1 :
       summa=summarize("\n".join(text), split="True", ratio=fraction)
       nsent=len(summa)
       fraction=fraction*0.5
    # Get a position for the best sentence
    # Very dirty trick as sometimes there are 1-character differences
    selected=-1
    minoffset=+float("inf")
    for j,sent in enumerate(text) :
           senta=sent.strip("\n")
           sentb=summa[0]
           offset=abs(len(senta)-len(sentb))
           if offset<minoffset :
              minoffset=offset
              closestpair=j
	   if sent.strip("\n")==summa[0] :
	      closestpair=j
    if selected == -1 :
       selected = closestpair
   
    return summa[0],selected
      
    


reload(sys)
sys.setdefaultencoding("utf-8")

parser = argparse.ArgumentParser()
parser.add_argument("--percentage", dest="percentage", type=float, default=10.0, help="Percentage (default 10%%)")
parser.add_argument("--raw-model", dest="rawmodelfilename", default="/home/mlf/tmp/kenlm/news-commentary-v8.arpa.en", help="Route of raw model (needed for entropy calculation")
parser.add_argument("--binary-model", dest="binarymodelfilename", default="/home/mlf/tmp/kenlm/news-commentary-v8.blm.en", help="Route of raw model (needed for entropy calculation)")
parser.add_argument('-v', '--verbose', help='Verbose Mode', dest="verbose", action='store_true',default=False)
parser.add_argument('--include_stopwords', help="Don't exclude stopwords", dest="include_stopwords", action="store_true", default=False)
parser.add_argument('--include_punctuation', help="Don't exclude punctuation", dest="include_punct", action="store_true", default=False)
parser.add_argument('--no_hint', help="Provide no hint", dest="no_hint", action="store_true", default=False)
parser.add_argument("reftextfile",help="Reference text")
parser.add_argument("hinttextfile",help="Hint text")
parser.add_argument("resultfile",help="Result file")
parser.add_argument('--setid', help='Evaluation set identifier', dest='setid', default="defaultsetid")
parser.add_argument('--docid', help='Document identifier', dest='docid', default="defaultdocid")
parser.add_argument('--sl',help="Source language", dest="sl", default="unk")
parser.add_argument('--tl',help="Target language", dest="tl", default="unk")
parser.add_argument("--system", help="MT system", dest="system", default="unk")
parser.add_argument("--no_entropy", help="Random gaps", dest="no_entropy", action="store_true", default=False)
parser.add_argument("--no_context", help="No context but sentence", dest="no_context", action="store_true", default=False)
parser.add_argument('--adjacent_gaps_not_ok', help="Adjacent gaps are not allowed.", dest="adjacent_gaps_not_ok", action="store_true", default=False)

args = parser.parse_args()

# These should be removed
rawmodelfilename="/home/mlf/tmp/kenlm/news-commentary-v8.arpa.en"
binarymodelfilename="/home/mlf/tmp/kenlm/news-commentary-v8.blm.en"

# Read reference text file and hint text file
reftext=open(args.reftextfile).readlines()


# Extract best 1-sentence summary of the reference text, to punch holes in it
summary, selected =extract_sentence(reftext) 
if args.verbose :
   print summary, "[", selected, "]"
   
hinttext=open(args.hinttextfile).readlines()
if args.no_hint :
	hinttext=["[No hint, you are on your own!]"]
        system="NONE"
else :
        system=args.system
	if args.no_context :
	   hinttext=[hinttext[selected]]
	

   

if args.include_stopwords :
   stop_words=[]
else :
   try :
      stop_words = get_stop_words('args.tl')
      if args.tl=="en" : # needed as a result of NLTK tokenization
		  for sw in [u"n't", u"'s", u"'re"] :
			  stop_words.append(sw)
   except :
      print "Could not get stopwords for language ", args.tl 
      print "Will not consider stopwords"
      stop_words=[]
      
# This punctuation list needs to be improved
punct = [string.punctuation[i] for i in range(len(string.punctuation))]
punct.append("''") # these are generated by word_tokenize. 
punct.append("``")

#punct = [u",", u"?", u".", u":", u";", u"(", u")", u"[", u"]", u"{", u"}", u"%", u"$", u"#", u"!", u"-"]
if not args.include_punct :
   for sw in punct :
       stop_words.append(sw)
       


# Loading of the statistical language model should be 
# performed only once
# Get binary statistical language model
model = kenlm.Model(binarymodelfilename)


# Read unigrams from raw ARPA file --- can surely be improved, but working for now
order=model.order # they have to correspond!
raw = open(rawmodelfilename)
raw.readline() #throw first line
line1=raw.readline().rstrip("\n")
onegramcount=int((line1.split("="))[1])
if args.verbose :
    print "Unigrams used for brute-force entropy calculation:", onegramcount
    print "Maximum possible entropy={%6.2f} bits" % math.log(onegramcount, 2.0)
    if args.include_punct:
       print "Punctuation included"
    else :
       print "Punctuation excluded"
    if args.include_stopwords :
       print "Stopwords included"
    else :
	   print "Stopwords excluded"
for i in range(order+1) :
  raw.readline() # throw order+1 lines
unigrams=[]
unicache=onegramcount * [0]  
for i in range(onegramcount) :
  unigrams.append(raw.readline().split("\t")[1])
# print unigrams

ss = 	word_tokenize(summary)
# ss =  ['<s>'] + ss + ['</s>']
lss = len(ss) 
basesentence=" ".join(ss)
#  for i, (prob, length, oov) in enumerate(model.full_scores(basesentence)):
#      print("i={0} prob={1} length={2}, oov={3} stretch='{4}'".format(i, prob, length, oov, ' '.join(ss[i+2-length:i+2])))
bestdiff=-float("inf")
values = lss * [-float("inf")]
bestk=-1
log102=math.log10(2.0)

for i in range(0,lss) :
   if (ss[i]).lower() not in stop_words :
      if args.no_entropy : # Make entropy a random number 
		   entropy=random.random()*math.log(onegramcount,2.0)
      else : # compute actual entropy
           entropy=0
           denominator=0
           for j, word in enumerate(unigrams) :
              # log probability of sentence with "word" replacing position i
              logprob=model.score(" ".join(ss[0:i])+" "+word+" "+" ".join(ss[i+1:]))/log102
              unicache[j]=math.pow(2.0,logprob)
              denominator = denominator + unicache[j]
           for j, word in enumerate(unigrams) :
              margprob = unicache[j]/denominator
#              print "sentence {0}, position {1}, entropy index {2}".format(m,i,j)
#              print i,j,unigrams[j],logprob,margprob
              entropy=entropy-math.log(margprob,2.0)*margprob # -p log p
#           print "sentence {0}, position {1}, word {2}, entropy={3}".format(m,i, ss[i], entropy)
           values[i]=entropy
           # The entropy is highest when there are many possibilities that share probability
#           print i, entropy, ":", " ".join(ss[0:i])+" <"+ss[i]+"> "+" ".join(ss[i+1:])
           if entropy>bestdiff :
              bestdiff = entropy
              bestk = i
#   print i, ss[i], values[i]

if args.verbose :          
   print "Best position:", i, "(", ss[bestk], ")"

# Rank words according to entropy
nholes = max(1,int(0.5 + lss * args.percentage / 100.0))
if nholes == 0 :
   nholes = 1       # Only for sentences 5 words or shorter 
# print lss, nholes
val = numpy.array(values)
ival = val.argsort()
if args.verbose :
     for i in range(lss-1,-1,-1) : 
        print "{0} {1} {2:7.2f} {3}".format(i,ival[i],values[ival[i]],ss[ival[i]])
anss = ss 
holecount=0
holelist=[]
for i in range(lss-1,-1,-1) :
     if ss[ival[i]].lower() not in stop_words :  # when stopwords list is empty, all holes are OK
#        print ival[i], ss[ival[i]]
        if holecount<nholes :
           will_plug=True # default is plugging
           if args.adjacent_gaps_not_ok :              
              for previoushole in holelist:   # I'm sure I can factor this out in some way.
                  print "current rank", i, "position" , ival[i], "comparing with", previoushole
                  if math.fabs(previoushole-ival[i])==1 : # holes together
                     print "Holes together"
                     will_plug = will_plug and False #  
                  else : # this only needs to be done if stopwords are not taken into account
                     if not(args.include_stopwords) :
                        plug_condition = False # unless a non-stopword is found between the two
                        if previoushole < ival[i]:
                           for pos in range(previoushole+1,ival[i]) :
                              if ss[pos] not in stop_words :
                                 plug_condition = True
                        else:  
                           for pos in range(ival[1]+1,previoushole) :
                              if ss[pos] not in stop_words :
                                 plug_condition = True
                        will_plug = will_plug and plug_condition
           print "will plug", will_plug
           if will_plug :
              if args.verbose:
                 print "{0} in position {3} has rank {1} and entropy {2:.2f}".format(ss[ival[i]], i, values[ival[i]], ival[i])
              anss[ival[i]]=ss[ival[i]] 
              holelist.append(ival[i])
              holecount = holecount + 1
	

res=open(args.resultfile,"w")

res.write('<set id="{0}" source-language="{1}" target-language="{2}">\n'.format(args.setid, args.sl, args.tl))

if args.no_context :
   docmode="-doc"
else :
   docmode="+doc"


if args.no_entropy :
   entmode="-ent"
else :
   entmode="+ent"


res.write('<seg id="{0}{1}" doc-id="{2}" hide-source="True" type="{3}:{4}:{5}:{6}">\n'.format("editme::",args.docid, args.docid, args.percentage, system, docmode, entmode))

res.write('<source>Dummy text, not shown</source>\n') # empty source - we're not using it.

res.write("<reference>") # wrong name, but used like this

print "Hint text: "
temp=""
for j,line in enumerate(hinttext) :
	if j==selected and docmode=="+doc" : # not sure why I need the
                                            # second condition
                                            # but a bug was found
	   print ">>>" + line.strip("\n")
	   temp = temp + "[b]" + line.strip("\n") + "[/b]" + "@@@"
	else :
	   print line.strip("\n")
	   temp = temp + line.strip("\n") + "@@@"
print "________________________________________________"
temp=temp.rstrip("@@@")
temp=escape(temp) # for ampersands and such
res.write(temp)
res.write("</reference>\n")     
	
print "________________________________________________"
print "Problem:"
problem=""
solution=""
# print holelist
for pos, word in enumerate(anss) :
#   print pos, word
   if pos in holelist :
#	   print pos, word, "in holelist"
	   problem = problem + " { }" 
	   solution = solution + ";" + anss[pos]
   else :
	   problem = problem + " " + anss[pos]
solution=solution.lstrip(";")
solution=escape(solution)



# print " ".join(anss)
print problem

print "________________________________________________"
print "Solution:"
print solution
print "________________________________________________"

res.write('<translation system="{0}" type="{1}" fill="{2}" keys="{3}">\n'.format(system, "simple", ";" * (len(holelist)-1), solution))
res.write(escape(problem))
res.write('</translation>\n')
res.write('</seg>\n')
res.write('</set>\n')

# Later we will print a complete job with more than one problem
