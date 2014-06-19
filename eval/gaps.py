# coding=utf-8
__author__ = 'sereni'
import kw_gen
import codecs
import random
import re
from collections import OrderedDict
from text_generator import generate_task
# todo stick the code into functions


def splitter(a):
        return [x.strip('#)(.-:,;?!').lower() for x in a.split()]

#original = codecs.open('original.txt', 'r')
reference = codecs.open('reference.txt', 'r', 'utf-8')
#machine = codecs.open('machine.txt', 'r')
tagged = codecs.open('tag.txt', 'r', 'utf-8')

# options
keyword = True  # false = unmotivated gaps, true = keyword extraction
relative_density = False  # True = percentage calculated from number of keywords, false = from total number of words
multiple_choice = False  # todo in command line: make it so mch and lemmas can't be both true
lemmas = True
mt = True  # whether to output machine translated text into the task

# todo in command line: if no pos specified, use the whole list
pos = ['n', 'vblex', 'adj', 'adv']
default_pos = ['n', 'vblex', 'vbmod', 'vbser', 'vbhaver', 'vaux', 'adj', 'post', 'adv', 'preadv', 'postadv', 'mod',
               'det', 'prn', 'pr', 'num', 'np', 'ij', 'cnjcoo', 'cnjsub', 'cnjadv']
gap_density = 0.7  # 0-1


stream = reference.read()
reference.close()
tagged_stream = tagged.read()
tagged.close()

if multiple_choice or keyword or lemmas or pos != default_pos:
    keywords, inv_lemm = kw_gen.generate_keywords(stream, tagged_stream, multiple_choice, keyword, pos)
else:
    keywords = []
    for word in splitter(stream):
        if (word, []) not in keywords:
            keywords.append((word, []))

if relative_density:
    num_of_words = len(keywords)
else:
    num_of_words = len(splitter(stream))


# this part works with kw density, removing a specified proportion of words
try:
    omit = OrderedDict([keywords[i] for i in sorted(random.sample(range(len(keywords)), int(num_of_words*gap_density)))])
except ValueError:  # if sample is larger than population, take all the keywords
    omit = OrderedDict(keywords)

# this puts brackets around selected keywords, thus gaps
form_stream = stream
for word in omit.keys():
    if lemmas:
        form_stream = re.sub('([^\w{}])('+word+')([^\w{}]+)', '\\1{\\2}\\3', form_stream)
        stream = re.sub('([^\w{}])('+word+')([^\w{}]+)', '\\1{' + inv_lemm[word] + '}\\3', stream)
    else:
        stream = re.sub('([^\w{}])('+word+')([^\w{}]+)', '\\1{\\2}\\3', stream)
if lemmas:
        bracketed_words = re.findall('{[\w ]+}', form_stream, flags=re.U)
else:
    bracketed_words = re.findall('{[\w ]+}', stream, flags=re.U)
if multiple_choice:
    keys = [str(i+1) + ': ' + ', '.join(omit[bracketed_words[i].strip('{}')]) for i in range(len(bracketed_words))]
else:
    keys = [str(i+1) + ': ' + bracketed_words[i].strip('{}') for i in range(len(bracketed_words))]

# this is a writing section
# todo call text_generator here
generate_task(stream, keys, mt)
# gap = codecs.open('gap.txt', 'w')
# gap.write(stream)
# gap.write('\r\n')
# gap.write('; '.join(keys))
# gap.close()