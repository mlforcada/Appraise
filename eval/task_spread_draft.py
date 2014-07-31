__author__ = 'Sereni'
"""This module is a draft of an algorithm that spreads different sentences in different modes
between evaluators"""

import random
import copy
import click


def divide(a, b):
    floor = a / b
    result = []
    for i in range(b):
        result.append(floor)
    remainder = a - sum(result)
    i = 0
    while remainder:
        result[i] += 1
        remainder -= 1
        i = (i + 1) % b
    # randomize instead of taking combinations. should work well on large groups. may need to be changed though
    random.shuffle(result)
    return result


def find_next(start, exclude, maximum):
    current = start
    while True:
        if current in exclude:
            current = (current + 1) % maximum
            if current == start:
                break  # checked everything and returned to starting value -- must be repeating
        else:
            break
    return current


def spread(sentences, by_modes):
    columns = []
    rows = []  # this will check that users don't get one sentence in two or more modes

    # for output, use the same structure as placeholder
    distributed = copy.copy(by_modes)
    sent_num = 0

    # for each group
    for i in range(len(by_modes)):

        # create placeholders for sentences
        distributed[i] = [''] * len(distributed[i])

        # for each mode in a group
        for j in range(len(by_modes[i])):

            # create a "column" that checks if a sentence has already been evaluated in a given mode
            try:
                columns[j]
            except IndexError:
                columns.append([])

            # get a sentence number as many times as specified for each mode (the number in by_modes)
            for k in range(by_modes[i][j]):
                if sent_num in columns[j]:
                    num = find_next(sent_num, columns[j], sentences)
                    distributed[i][j] += str(num) + ';'
                    columns[j].append(num)
                else:
                    distributed[i][j] += str(sent_num) + ';'
                    columns[j].append(sent_num)
                sent_num = (sent_num + 1) % sentences
        distributed[i] = [item.strip(';') for item in distributed[i]]
    return distributed


def horizontal_check(dist, warning):
    for group in dist:
        values = []
        for item in group:
            values += item.split(';')
        control = set(values)
        if len(values) != len(control):
            warning = True
    return warning


def pretty_print(data):
    for i in range(len(data)):
        print 'Group {0}:'.format(str(i+1))
        for j in range(len(data[i])):
            print 'Mode {0}: {1}'.format(str(j+1), data[i][j])

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('sentences', type=click.INT)
@click.argument('modes', type=click.INT)
@click.argument('groups', type=click.INT)
def distribute(*args, **options):
    """
    This script is a draft for sentence distribution algorithm

    SENTENCES - a number of sentences to be evaluated. Note that same sentences with different gaps are counted
    as different sentences;

    MODES - a number of modes, e.g. with MT, without help, etc;

    GROUPS - a number of evaluators or groups of evaluators among which the sentences should be distributed.
    """
    # this determines how many sentences each group should get (as even as possible)
    sentences = options['sentences']
    modes = options['modes']
    groups = options['groups']

    sent_each = divide(sentences * modes, groups)

    # this determines how many sentences of each mode each group will get
    sent_by_modes = [divide(sent_each[i], modes) for i in range(len(sent_each))]

    distr = spread(sentences, sent_by_modes)
    pretty_print(distr)
    return

if __name__ == '__main__':
    distribute()