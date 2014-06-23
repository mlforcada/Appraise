# coding=utf-8
__author__ = 'sereni'
"""This module generates keywords from a given text using a list of stopwords."""

import networkx
import codecs
import re
import itertools
from operator import itemgetter
import tag_pairing
import similar_words
from collections import OrderedDict


def splitter(a):
        return [x.strip('#)(.-:,;?!').lower() for x in a.split()]


def candidate_keywords(words, stopwords):
    """Returns phrases found between stopwords"""
    candidates = []
    punctuation = re.compile('[)!?.,:;-]')
    keyword = []
    for i in range(len(words)-1):
        if words[i].strip('()!?,.:;\n').lower() in stopwords:
            if keyword:
                candidates.append(keyword)
            keyword = []
        elif '(' in words[i]:
            candidates.append(keyword)
            keyword = [words[i]]
        elif re.search(punctuation, words[i]):
            keyword.append(words[i].strip('()!?,.:;\n'))
            candidates.append(keyword)
            keyword = []
        else:
            keyword.append(words[i].lower())
    return candidates


def kw_network(keywords, lemmas):
    """Returns a networkx graph containing edges between the words on the same phrase"""
    net = networkx.Graph()
    for keyword in keywords:
        for (i, j) in itertools.combinations_with_replacement(keyword, 2):
            l1 = lemmas[i]
            l2 = lemmas[j]
            try:
                net.edge[l1][l2]['weight'] += 1
            except KeyError:
                net.add_edge(l1, l2, weight=1)
    return net


def scores(keywords, net, lemmas):
    """Ranks keywords by metrics and returns an ordered list of keywords, top scores first"""
    scored_kw = []
    for keyword in keywords:
        kw_score = 0
        for word in keyword:
            freq = len(net.neighbors(lemmas[word]))
            deg = sum([net[i][j]['weight'] for (i, j) in net.edges(lemmas[word])])
            score = deg/freq
            kw_score += score
        scored_kw.append((keyword, kw_score))
    return sorted(scored_kw, key=itemgetter(1), reverse=True)


def pos_filter(dictionary, pos_tags):
    sw_tags = ['pr', 'vbser', 'def', 'ind', 'cnjcoo', 'det', 'rel', 'vaux', 'vbhaver', 'prn', 'itg']
    stop = set([])
    desired = set([])
    for item in dictionary:
        if item[1][0] in stop:
            continue
        tags = item[1][1]
        for tag in sw_tags:
            if tag in tags:
                stop.add(item[0])
        for tag in pos_tags:
            if tag in tags:
                desired.add(item[0])
    return stop, desired


def lemmatize(data):
    dictionary = {}
    for item in data:
        form = item[0]
        try:
            lemma = item[1][0]
        except IndexError:  # the word didn't parse, use marked form instead
            lemma = '*'+form
        try:
            if form not in dictionary[lemma]:
                dictionary[lemma].append(form)
        except KeyError:
            dictionary[lemma] = [form]
    return dictionary


def invert(dictionary):
    inverted = {}
    for key, value in dictionary.items():
        for item in value:
            inverted[item] = key
# what if one form is used in two lemmas?
    return inverted


def generate_keywords(orig, tagged_st, multiple_choice, kw, pos_list):
    words = orig.split(' ')
    dictionary = tag_pairing.start(orig, tagged_st)
    stopwords, good_words = pos_filter(dictionary, pos_list)
    if kw:
        #stopwords, good_words = pos_filter(dictionary, pos_list)
        candidates = candidate_keywords(words, stopwords)
        lemmas = lemmatize(dictionary)
        inv_lemmas = invert(lemmas)
        graph = kw_network(candidates, inv_lemmas)
        ranked = scores(candidates, graph, inv_lemmas)
        ranked_short = []
        for (word, score) in ranked:
            if len(word) > 2:
                continue
            for item in word:
                if item not in good_words:
                    continue
                if item in ranked_short:
                    continue
                ranked_short.append(item)
    else:
        ranked_short = []
        for word in splitter(orig):
            if word not in good_words:
                continue
            if word not in ranked_short:
                ranked_short.append(word)
        inv_lemmas = {}
        lemmas = {}
    if multiple_choice:
        choices = similar_words.generate_choices(dictionary, ranked_short)
    else:
        choices = [(word, []) for word in ranked_short]
    return choices, inv_lemmas