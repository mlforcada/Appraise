# coding=utf-8
__author__ = 'Sereni'
"""This module checks the task files filled in by evaluators and gives the number of correct answers.
Input: the keys file generated with tasks and a filled-in task file with unchanged structure:
task number:
original text
(optional) machine translation
reference translation with {gaps} enclosed in brackets"""

import codecs
import re

# todo when calling from command line, this will have to be specified as arguments and opened accordingly. no filenames.
# todo should I try to guess file encodings? chardet module


def determine_task_type(f):
    lines = f.split('\r\n')
    try:
        int(lines[2].strip(':\r\n'))  # if it's a number, tasks have no mt translation
        n = 3
    except ValueError:
        n = 4
    return n  # a number of lines in each task


def find_answers(sentences):
    answers = []
    for sentence in sentences:
        bracketed_words = re.findall('{[\w ]+}', sentence)
        answers += bracketed_words
    return [answer.strip('{}') for answer in answers]


def parse_tasks(task):
    n = determine_task_type(task)
    gapped_sentences = [task.split('\r\n')[i] for i in range(n-1, len(task.split('\r\n'))-1, n)]
    answers = find_answers(gapped_sentences)
    return answers


def extract_keys(keys):
    return [item.split(': ')[1] for item in keys.split('\r\n')]


def compare_answers(user, correct):
    return sum([1 for i in range(len(user)) if user[i] == correct[i]])

# todo normalize input

t = codecs.open('task.txt', 'r', 'utf-8')
k = codecs.open('keys.txt', 'r', 'utf-8')
task = t.read()
keys = k.read()
answers = parse_tasks(task)
answer_key = extract_keys(keys)
score = compare_answers(answers, answer_key)
t.close()
k.close()