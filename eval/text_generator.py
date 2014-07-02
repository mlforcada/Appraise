# coding=utf-8
__author__ = 'Sereni'
"""This module is called from gaps.py to generate tasks of
1. original sentence
2. (optional) machine translation
3. reference translation with gaps
and keys for the current task,
and write them to two text files."""

#import codecs
import re


def split_sentences(stream):
    pattern = re.compile('.*?[.?!]+[ ]?')
    sentences = re.findall(pattern, stream)
    sentences = [sentence.strip() for sentence in sentences]
    return sentences


def decorate(sentence, tag):
    return '<' + tag + '>' + sentence + '</' + tag + ''


def zip_sentences(orig, mt, gap):
    return zip(orig, mt, gap)


def generate_task(task, keys, mt, original, output, key):
    """mt: boolean
    task: a stream as in file.read()
    keys: a list of 'n: word'"""
    original_sentences = split_sentences(original.read())
    task_sentences = split_sentences(task)
    if mt:
        machine_sentences = split_sentences(mt.read())
    else:
        machine_sentences = ['' for sentence in original_sentences]  # a placeholder
    tasks = zip_sentences(original_sentences, machine_sentences, task_sentences)
    for i in range(len(tasks)):
        if tasks[i][1]:
            output.write(str(i+1) + ':\r\n' + tasks[i][0] + '\r\n' + tasks[i][1] + '\r\n' + tasks[i][2] + '\r\n')
        else:
            output.write(str(i+1) + ':\r\n' + tasks[i][0] + '\r\n' + tasks[i][2] + '\r\n')
    output.close()
    key.write('\r\n'.join(keys))
    key.close()
    return


# todo write a separate cli for xml, because screw that.
def generate_xml(task, mt, original, output, task_type, doc_id, set_id, source, target):

    def compute_fill_and_keys(sentence, task_type):
        """This extracts values from brackets and generates the parameters fill and keys for xml"""
        keys = []
        fill = []

        if task_type == 'simple':
            keys = [item.strip('{}') for item in re.findall('{[\w ]+}', sentence, flags=re.U)]
            fill = ['']*len(keys)

        # for lemmas, the gaps are {key/lemma}
        elif task_type == 'lemmas':
            for item in re.findall('{[\w /]+}', sentence, flags=re.U):
                key, lemma = item.split('/')
                keys.append(key.strip('{}'))
                fill.append(lemma.strip('{}'))

        elif task_type == 'choices':
            gap_words = [item.split(', ') for item in re.findall('{[\w ,]+}', sentence, flags=re.U)]
            for item in gap_words:
                keys.append(item[0].strip('{}'))
                fill.append(','.join(item).replace('{', '').replace('}', ''))

        sentence = re.sub('{[\w /,]*?}', '{ }', sentence, flags=re.U)
        return ';'.join(keys), ';'.join(fill), sentence

    original_sentences = [u'<{0}>{1}</{0}>'.format('source', item) for item in split_sentences(original.read())]
    #task_sentences = [u'<{0} system="Apertium">{1}</{0}>'.format('translation', item) for item in split_sentences(task)]
    task_sentences = []
    for item in split_sentences(task):
        keys, fill, sentence = compute_fill_and_keys(item, task_type)
        task_sentences.append(u'<{0} system="Apertium" type="{1}" fill="{2}" keys="{3}">{4}</{0}>'.format
                              ('translation', task_type, fill, keys, sentence))
    if mt:
        machine_sentences = [u'<{0}>{1}</{0}>'.format('reference', item) for item in split_sentences(mt.read())]
    else:
        machine_sentences = [u'' for sentence in original_sentences]  # a placeholder

    pre_tasks = zip_sentences(original_sentences, machine_sentences, task_sentences)
    tasks = [u'<{0} id="{2}" doc-id="{3}">{1}</{0}>'.format('seg', '\n'.join(pre_tasks[i]), str(i+1), doc_id)
             for i in range(len(pre_tasks))]
    xml = u'<set id="{0}" source-language="{1}" target-language="{2}">{3}</set>'.format(set_id, source, target,
                                                                                       '\n'.join(tasks))
    output.write(xml)
    output.close()
    return