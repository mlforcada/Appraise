__author__ = 'Sereni'
"""Input: 1. an XML result file for one gisting task from Appraise evaluation system
          2. a number of users who should give an answer different from the answer key for it to be considered
          3. the task XML file, because this is where sentences and keys come from
   Output: All sentences for which requirements have been met, along with suggested synonyms.
   """

import click
import xml.etree.ElementTree as et
from collections import Counter


def parse_task(task):
    root = et.fromstring(task)
    data = ['']*len(root)
    for segment in root:
        for item in segment:
            if item.tag == 'translation':
                sentence = item.text
                if isinstance(item.attrib['keys'], str):
                    keys = item.attrib['keys'].decode('utf-8')
                elif isinstance(item.attrib['keys'], unicode):
                    keys = item.attrib['keys']
                for key in keys.split(';'):
                    sentence = sentence.replace('{ }', key, 1)
                    pass
                index = segment.attrib['id']
                data[int(index)-1] = (sentence, keys)
    return data


def update_counters(ans, counters):
    """This updates the answer counters from each new answer string and returns new counter lists"""
    for i in range(len(counters)):
            counters[i][ans[i].strip(' ')] += 1
    return counters


def parse_result(result):
    root = et.fromstring(result)
    results = {}
    for child in root:
        for item in child:
            if isinstance(item.attrib['result'], str):
                res = item.attrib['result'].decode('utf-8')
            elif isinstance(item.attrib['result'], unicode):
                res = item.attrib['result']
            answers = res.split('answers:')[-1].split(', ')
            index = item.attrib['id'].decode('utf-8')
            try:
                update_counters(answers, results[index])
            except KeyError:
                results[index] = [Counter([word.strip(' ')]) for word in answers]
    data = ['']*len(results)
    for key, value in results.items():
        data[int(key)-1] = value
    return data


def filter_counters(answer, counter, n):
    del counter[answer]
    for word, count in counter.items():
        if count < n:
            del counter[word]
    return counter


def match(sentences, results, threshold):
    data = []
    for i in range(len(sentences)):
        answers = sentences[i][1].split(';')
        counters = [filter_counters(answers[j], results[i][j], threshold) for j in range(len(results[i]))]
        fill = [(answers[j], counters[j]) if counters[j] else '' for j in range(len(answers))]
        if fill != ['']*len(answers):  # only record if found something interesting
            data.append((sentences[i][0], fill))
    return data


def format_output(l):
    formatted = ''
    for sentence, data in l:
        for item in data:
            if item:
                answer, counter = item
                line = u'Key: {0}; Synonyms: {1}; Sentence: {2}\r\n'.format(answer, ','.join(counter.keys()),
                                                                                               sentence)
                formatted += line
    return formatted


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('task', type=click.File('r', encoding='utf-8'))
@click.argument('result', type=click.File('r', encoding='utf-8'))
@click.argument('output', type=click.File('w', encoding='utf-8'))
@click.argument('threshold', type=click.INT)
def find_synonyms(*args, **options):
    """
    This script finds synonyms for words in gaps based on evaluators' answers.
    Input:

    TASK - the XML file with task that was used to add task to Apppraise evaluation system;

    RESULT - the XML file obtained through result export for this task from Appraise;

    OUTPUT - a .txt file to write the synonyms;

    THRESHOLD - a minimal number of evaluators to give the same answer for it to be considred a synonym.

    For example, in the sentence "I like { }" the intended answer is "apples". The evaulators gave the
    following answers:

    1: apples

    2: oranges

    3: peaches

    4: oranges

    If threshold is set to 2, only "oranges" will appear as a synonym for this gap. If threshold is
    set to 1, it will be "oranges" and "peaches", but not "apples", because this was the original answer.

    The script writes the results to path specified in OUTPUT, giving the sentence, the word and its
    suggested synonyms.
    """
    answers = parse_result(options['result'].read().encode('utf-8'))
    sentences = parse_task(options['task'].read().encode('utf-8'))  # etree does not accept unicode
    data = match(sentences, answers, options['threshold'])
    options['output'].write(format_output(data))
    return

if __name__ == '__main__':
    find_synonyms()