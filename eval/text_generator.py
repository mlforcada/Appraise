# coding=utf-8
__author__ = 'Sereni'
"""This module is called from gaps.py to generate tasks of
1. original sentence
2. (optional) machine translation
3. reference translation with gaps
and keys for the current task,
and write them to two text files."""

import codecs
import re


def split_sentences(stream):
    pattern = re.compile('.*?[.?!]+[ ]?')
    sentences = re.findall(pattern, stream)
    sentences = [sentence.strip() for sentence in sentences]
    return sentences


def zip_sentences(orig, mt, gap):
    return zip(orig, mt, gap)


def generate_task(task, keys, mt):
    """mt: boolean
    task: a stream as in file.read()
    keys: a list of 'n: word'"""
    original = codecs.open('original.txt', 'r', 'utf-8')
    original_sentences = split_sentences(original.read())
    task_sentences = split_sentences(task)
    original.close()
    if mt:
        machine = codecs.open('machine.txt', 'r', 'utf-8')
        machine_sentences = split_sentences(machine.read())
        machine.close()
    else:
        machine_sentences = ['' for sentence in original_sentences]  # a placeholder
    tasks = zip_sentences(original_sentences, machine_sentences, task_sentences)
    output = codecs.open('task.txt', 'w', 'utf-8')
    for i in range(len(tasks)):
        if tasks[i][1]:
            output.write(str(i+1) + ':\r\n' + tasks[i][0] + '\r\n' + tasks[i][1] + '\r\n' + tasks[i][2] + '\r\n')
        else:
            output.write(str(i+1) + ':\r\n' + tasks[i][0] + '\r\n' + tasks[i][2] + '\r\n')
    output.close()
    key = codecs.open('keys.txt', 'w', 'utf-8')
    key.write('\r\n'.join(keys))
    key.close()
    return