__author__ = 'Sereni'

import networkx
import itertools
from operator import itemgetter


def similarity(word1, word2, gr, pos_tags):
    pos = ''
    gr.add_edge(word1[0], word1[0], {'weight': 99})  # should always have a choice for the original word in the gap
    for tag in pos_tags:
        if tag in word1[1][1]:
            pos = tag
            break
    # todo think what to do with non-parsed words. random alternatives?
    if pos in word2[1][1]:
        tags1 = set(word1[1][1])
        tags2 = set(word2[1][1])
        common_tags = tags1.intersection(tags2)
        gr.add_edge(word1[0], word2[0], {'weight': len(common_tags)})
    return


def generate_choices(words, kw, n=3):  # n for number of choices
    gr = networkx.Graph()
    pos_tags = ['n', 'vblex', 'vbmod', 'vbser', 'vbhaver', 'vaux', 'adj', 'post', 'adv',
                'preadv', 'postadv', 'mod', 'det', 'prn', 'pr', 'num', 'np', 'ij', 'cnjcoo',
                'cnjsub', 'cnjadv']
    for (word1, word2) in itertools.combinations_with_replacement(words, 2):
        similarity(word1, word2, gr, pos_tags)
    alternatives = {}
    for word in gr.nodes():
        records = sorted([(j, gr[i][j]['weight']) for (i, j) in gr.edges(word)], key=itemgetter(1), reverse=True)
        top = [item for (item, score) in records[:n]]
        alternatives[word] = top
    filtered = [(form, alternatives[form]) for form in kw]
    return filtered