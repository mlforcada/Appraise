# coding=utf-8
__author__ = 'sereni'

from itertools import izip


def getpairs(i1, i2):
    def splitter(a):
        return [x.strip('#)(.-:,;?!').lower() for x in a.split()]
    return izip(splitter(i1), splitter(i2))


def tagger(input):
    t = input.lstrip('^').rstrip('$').split('<')
    word = t[0]
    if word.startswith('*'):
        tags = []
        word = word.replace('*', '').replace('$', '').replace('^', '')
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