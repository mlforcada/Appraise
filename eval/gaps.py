# coding=utf-8
__author__ = 'sereni'
import kw_gen
import random
import re
from collections import OrderedDict
from text_generator import generate_task, generate_xml
from math import ceil

# todo (maybe) rewrite args as a dictionary


def generate_morphodict(morph):
    def tagger(t):
        """Takes one morphological analysis and returns a list of tags found there"""
        word = t[0]
        if word.startswith('*'):
            tags = []
        else:
            tags = [k.strip(u'`´>$^#)(-.:,;?!') for k in t[1::]]
        return tags

    morphodict = {}
    items = [x.strip(u'`´#)(.-:,;?!').lower() for x in morph.split()]  # find all analysis chunks
    for item in items:
        # split first, record [0] as word form, and them for the rest of them run tagger to get tag lists
        analysis = item.lstrip('^').rstrip('$').split('/')
        word = analysis[0].replace('*', '')
        tags = []
        for variant in analysis[1:]:
            tags.append(tagger(variant.split('<')))
        morphodict[word] = tags
    return morphodict


def morph_filter(keywords, mdict, pos):
    filtered_keywords = []
    for item in keywords:
        word = item[0]
        try:
            tags = mdict[word]
        except KeyError:
            continue  # todo this catches words with hyphen, treated as two -- fix to accommodate
        keep_word = False
        for tag_set in tags:  # in each tag set, find at least one tag from the allowed pos
            if 'sent' in tag_set or 'cm' in tag_set:
                continue
            keep_word = False
            for tag in pos.split(','):
                if tag in tag_set:
                    keep_word = True
                    break
            if not keep_word:
                break
        if keep_word:  # if each analysis satisfies the allowed pos requirement, allow the word to pass
            filtered_keywords.append(item)
    return filtered_keywords


def generate_gaps(reference, tagged, multiple_choice, keyword, lemmas, pos, relative_density, gap_density, morph):
    def splitter(a):
        return [x.strip('#)(.-:,;?!').lower() for x in a.split()]

    def takespread(array, num):
        length = float(len(array))
        for i in range(num):
            yield array[int(ceil(i * length / num))]

    default_pos = ['n', 'vblex', 'vbmod', 'vbser', 'vbhaver', 'vaux', 'adj', 'post', 'adv', 'preadv', 'postadv', 'mod',
                   'det', 'prn', 'pr', 'num', 'np', 'ij', 'cnjcoo', 'cnjsub', 'cnjadv']
    stream = reference
    tagged_stream = tagged

    if multiple_choice or keyword or lemmas: #or pos != default_pos:
        keywords, inv_lemm = kw_gen.generate_keywords(stream, tagged_stream, multiple_choice, keyword, pos)
    else:
        inv_lemm = None  # placeholder
        keywords = []
        for word in splitter(stream):
            if (word, []) not in keywords:
                keywords.append((word, []))

    if morph:
        mdict = generate_morphodict(morph)
        keywords = morph_filter(keywords, mdict, pos)

    if relative_density:
        num_of_words = len(keywords)
    else:
        num_of_words = len(splitter(stream))

    # this part works with kw density, removing a specified proportion of words

    # # a pretty uneven algorithm
    # try:
    # omit = OrderedDict([keywords[i] for i in sorted(random.sample(range(len(keywords)),
    # int(num_of_words*gap_density)))])
    # except ValueError:  # if sample is larger than population, take all the keywords
    #     omit = OrderedDict(keywords)

    # # a more even algorithm
    # try:
    #     omit = OrderedDict([i for i in takespread(keywords, int(num_of_words*gap_density))])
    # except IndexError:  # attempting to draw more keywords than we've got
    #     omit = OrderedDict(keywords)

    # a super-even algorithm that gives the specified percentage of gaps in every sentence
    # from which we only have one line here, and the rest is done on sentence generation
    omit = OrderedDict(keywords)

    return stream, omit, inv_lemm


def prepare_text(reference, tagged, original, keyword, relative_density, gap_density, multiple_choice, lemmas, mt, pos,
                 output, key, hide_source):
    stream, omit, inv_lemm = generate_gaps(reference, tagged, multiple_choice, keyword, lemmas, pos, relative_density,
                                           gap_density, morph=None)
    # this puts brackets around selected keywords, thus gaps
    form_stream = stream
    for word in omit.keys():
        if lemmas:
            form_stream = re.sub('([^\w{}])(' + word + ')([^\w{}]+)', '\\1{\\2}\\3', form_stream)
            stream = re.sub('([^\w{}])(' + word + ')([^\w{}]+)', '\\1{' + inv_lemm[word] + '}\\3', stream)
        else:
            stream = re.sub('([^\w{}])(' + word + ')([^\w{}]+)', '\\1{\\2}\\3', stream)
    if lemmas:
        bracketed_words = re.findall('{[\w ]+}', form_stream, flags=re.U)
    else:
        bracketed_words = re.findall('{[\w ]+}', stream, flags=re.U)
    if multiple_choice:
        keys = [str(i + 1) + ': ' + bracketed_words[i].strip('{}') for i in range(len(bracketed_words))]
        for word in bracketed_words:
            stream = stream.replace(word, '{' + ', '.join(omit[word.strip('{}')]) + '}')
    else:
        keys = [str(i + 1) + ': ' + bracketed_words[i].strip('{}') for i in range(len(bracketed_words))]
    if not multiple_choice and not lemmas:
        stream = re.sub('{[\w]*?}', '{ }', stream, flags=re.U)

    generate_task(stream, keys, mt, original, output, key, hide_source)


def prepare_xml(reference, tagged, original, keyword, relative_density, gap_density, multiple_choice, lemmas, mt, pos,
                output, source, target, doc_id, set_id, hide_source, morph, batch):

    stream, omit, inv_lemm = generate_gaps(reference, tagged, multiple_choice, keyword, lemmas, pos, relative_density,
                                           gap_density, morph)

    def split_sentences(stream):
        pattern = re.compile('.*?[.?!]+[ ]?')
        sentences = re.findall(pattern, stream)
        sentences = [sentence.strip() for sentence in sentences]
        return sentences

    def gapify_sentence(sentence, keywords, density):
        p = '#)(.-:,;?!'
        length = len(sentence.split(' '))
        index = random.choice(range(length))
        words = sentence.split(' ')
        num_of_gaps = int(round(length * density))
        if num_of_gaps == 0:
            num_of_gaps += 1
        step = int(length/float(num_of_gaps))
        possible_num = len([word for word in words if word.lower().strip(p) in keywords.keys()])
        i = 0
        gaps = set([])
        while i < num_of_gaps and i < possible_num:  # see if we haven't checked all the words already
            if words[index].lower().strip(p) in keywords.keys():
                if (words[index], index) in gaps:  # add the chunk there as-is, just match against it
                    index = (index + 1) % length
                    continue
                else:
                    i += 1
                gaps.add((words[index], index))  # use indices to replace words in [words]
                index = (index + step) % length
                # найденные слова простой заменой в words закрыть в скобки. пунктуация останется
            else:
                index = (index + 1) % length
        for word, index in gaps:
            expression = re.compile('([\w\'-]+)', flags=re.U)
            words[index] = re.sub(expression, u'{'+'\\1'+u'}', words[index])
        gapped_sentence = ' '.join(words)
        return gapped_sentence

    task_type = 'simple'  # required in xml. simple by default, may change by the time we get to xml generator
    # form_stream = stream
    # for word in omit.keys():
    # if lemmas:
    # task_type = 'lemmas'
    #         form_stream = re.sub(u'(?i)([^\w{}])('+word+u')([^\w{}]+)', u'\\1{\\2}\\3', form_stream)
    #         stream = re.sub(u'(?i)([^\w{}])('+word+u')([^\w{}]+)', u'\\1{' + word + u'/' + inv_lemm[word] + u'}\\3', stream)
    #     else:
    #         stream = re.sub(u'(?i)([^\w{}])('+word+u')([^\w{}]+)', u'\\1{\\2}\\3', stream)
    # if multiple_choice:
    #     task_type = 'choices'
    #     bracketed_words = re.findall('{[\w ]+}', stream, flags=re.U)
    #     for word in bracketed_words:
    #         stream = stream.replace(word, '{' + ', '.join(omit[word.strip('{}').lower()]) + '}')

    # щас всё сделаем по-умному
    # todo solve the inner period problem
    stream = ' '.join([gapify_sentence(sentence, omit, gap_density) for sentence in split_sentences(stream)])
    bracketed_words = re.findall('{[\w ]+}', stream, flags=re.U)
    if multiple_choice:
        task_type = 'choices'
        for word in bracketed_words:
            stream = stream.replace(word, '{' + ', '.join(omit[word.strip('{}').lower()]) + '}')
    elif lemmas:
        task_type = 'lemmas'
        for word in bracketed_words:
            stream = stream.replace(word, u'{'+word+u'/'+inv_lemm[word]+u'}')

    # answer keys are not calculated here, and also nothing is removed from gaps. this will be done on xml generation
    generate_xml(stream, mt, original, output, task_type, doc_id, set_id, source, target, hide_source, batch, gap_density)
