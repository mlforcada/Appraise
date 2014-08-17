# coding=utf-8
__author__ = 'sereni'

from itertools import izip


def getpairs(i1, i2):
    def splitter(a):
        return [x.strip('#)(.-:,;?!').lower() for x in a.split()]
    def tag_splitter(a):
        spl = []
        for x in a.split('$ '):
            if len(x.split()) > 1:
                form = x.split('/')[0]
                for item in form.split():
                    spl.append(item)
            else:
                spl.append(x.strip('#)(.-:,;?!').lower())
       # return [x.strip('#)(.-:,;?!').lower() for x in a.split('$ ')]
        return spl
    return izip(splitter(i1), tag_splitter(i2))


def tagger(input):
    parses = input.lstrip('^').rstrip('$').split('/')

    # if split by slash returns two or more objects, the input comes from anmor. select the first parse and proceed
    if len(parses) > 1:
        t = parses[1].split('<')
    else:
        t = input.lstrip('^').rstrip('$').split('<')
    word = t[0]
    if word.startswith('*'):
        tags = []
        word = word.replace('*', '').replace('$', '').replace('^', '').strip('-.:,;?!')
    else:
        tags = [k.strip('>$^#)(-.:,;?!') for k in t[1::]]
    return [word, tags]


def start(input, aper):
    data = []
    for word, info in getpairs(input, aper):
        data.append([
        word,
        tagger(info)
        ])
    return data