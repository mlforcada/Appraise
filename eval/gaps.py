# coding=utf-8
__author__ = 'sereni'
import kw_gen
import random
import re
from collections import OrderedDict
from text_generator import generate_task

# todo (maybe) rewrite args as a dictionary


def everything(reference, tagged, original, keyword, relative_density, gap_density, multiple_choice, lemmas, mt, pos,
               output, key):

    def splitter(a):
            return [x.strip('#)(.-:,;?!').lower() for x in a.split()]
    default_pos = ['n', 'vblex', 'vbmod', 'vbser', 'vbhaver', 'vaux', 'adj', 'post', 'adv', 'preadv', 'postadv', 'mod',
                   'det', 'prn', 'pr', 'num', 'np', 'ij', 'cnjcoo', 'cnjsub', 'cnjadv']
    stream = reference.read()
    tagged_stream = tagged.read()

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
        keys = [str(i+1) + ': ' + bracketed_words[i].strip('{}') for i in range(len(bracketed_words))]
        for word in bracketed_words:
            stream = stream.replace(word, '{' + ', '.join(omit[word.strip('{}')]) + '}')
    else:
        keys = [str(i+1) + ': ' + bracketed_words[i].strip('{}') for i in range(len(bracketed_words))]
    if not multiple_choice and not lemmas:
        stream = re.sub('{[\w]*?}', '{ }', stream, flags=re.U)

    generate_task(stream, keys, mt, original, output, key)
