# coding=utf-8
__author__ = 'Sereni'
"""This module checks the task files filled in by evaluators and gives the number of correct answers.
Input: the keys file generated with tasks and a filled-in task file with unchanged structure:
task number:
original text
(optional) machine translation
reference translation with {gaps} enclosed in brackets"""

import click
import re

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def determine_task_type(f):
    lines = f.split('\n')
    try:
        int(lines[2].strip(':\n'))  # if it's a number, tasks have no mt translation
        n = 3
    except ValueError:
        n = 4
    return n  # a number of lines in each task


def find_answers(sentences):
    answers = []
    for sentence in sentences:
        bracketed_words = re.findall('{[\w ]+}', sentence, flags=re.U)
        answers += bracketed_words
    return [answer.strip('{}') for answer in answers]


def parse_tasks(task):
    n = determine_task_type(task)
    gapped_sentences = [task.split('\n')[i] for i in range(n-1, len(task.split('\n'))-1, n)]
    answers = find_answers(gapped_sentences)
    return answers


def extract_keys(keys):
    return [item.split(': ')[1] for item in keys.split('\n')]


def compare_answers(user, correct):
    return sum([1 for i in range(len(user)) if user[i] == correct[i]])


def check_text(text, answer):
    task = text.read()
    keys = answer.read()
    answers = parse_tasks(task)
    answer_key = extract_keys(keys)
    score = compare_answers(answers, answer_key)
    text.close()
    answer.close()
    return score, len(answers)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('task', type=click.File('r', encoding='utf-8'))
@click.argument('keys', type=click.File('r', encoding='utf-8'))
def run_check(*args, **options):
    """The program checks user-filled tasks for gisting evaluation. The task structure should be unchanged for
    the script to work (assume the users only wrote/changed the words in brackets.
    Two arguments are required:
    task - path to the user's text file with the gaps filled in;
    keys - path to answer keys generated with the task.
    The program prints the number of correct answers to terminal.
    """
    score, total = check_text(options['task'], options['keys'])
    click.echo('Correct answers: %d out of %d, or %d percent.' % (score, total, float(score)/float(total) * 100))

if __name__ == '__main__':
    run_check()