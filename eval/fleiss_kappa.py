__author__ = 'Sereni'
"""
This script computes Fleiss' kappa for a given task. Each gap is taken for a subject. The categories are "correct" and
"incorrect".
"""
import click
import codecs
import xml.etree.ElementTree as et
from collections import Counter


def filter_tasks(task, result):
    """
    Suppose that the task file contains all tasks on which we have results in the result file, but may also have
    extra tasks. This drops the tasks from task file which do not have answers in results file.
    """
    filtered_tasks = {}
    for key, value in result.items():
        filtered_tasks[key] = task[key]
    task_list = [filtered_tasks[i] for i in sorted(filtered_tasks)]
    answer_list = [result[i] for i in sorted(result)]
    return task_list, answer_list


def parse_task(task):
    data = {}
    i = 0
    for segment in task:
        index = int(segment.attrib['id'].decode('utf-8'))
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

                data[index] = (sentence, keys)
                i += 1
    #data_list = [data[i] for i in sorted(data)]
    return data


def update_counters(ans, counters):
    """This updates the answer counters from each new answer string and returns new counter lists"""
    for i in range(len(counters)):
            counters[i][ans[i].strip(' ').lower()] += 1
    return counters


def parse_result(result):
    results = {}
    for gisting_item in result:  # item is a single person's answer, result corresponds to a task
        if isinstance(gisting_item.attrib['result'], str):
            res = gisting_item.attrib['result'].decode('utf-8')
        elif isinstance(gisting_item.attrib['result'], unicode):
            res = gisting_item.attrib['result']
        answers = res.split('answers:')[-1].split(', ')
        index = int(gisting_item.attrib['id'].decode('utf-8'))
        try:
            update_counters(answers, results[index])
        except KeyError:
            results[index] = [Counter([word.strip(' ').lower()]) for word in answers]
    #data = [results[i] for i in sorted(results)]
    return results


def matrix(answers, sentences):
    mat = []
    for i in range(len(answers)):
        gaps = answers[i]
        keys = sentences[i][1].split(';')
        for j in range(len(gaps)):
            gap = gaps[j]
            key = keys[j]
            correct = gap[key]
            del gap[key]
            incorrect = sum(gap.values())
            mat.append([correct, incorrect])
    return mat


DEBUG = False

def computeKappa(mat):
    """ Computes the Kappa value
        @param n Number of rating per subjects (number of human raters)
        @param mat Matrix[subjects][categories]
        @return The Kappa value """
    n = checkEachLineCount(mat)   # PRE : every line count must be equal to n
    N = len(mat)
    k = len(mat[0])

    if DEBUG:
        print n, "raters."
        print N, "subjects."
        print k, "categories."

    # Computing p[]
    p = [0.0] * k
    for j in xrange(k):
        p[j] = 0.0
        for i in xrange(N):
            p[j] += mat[i][j]
        p[j] /= N*n
    if DEBUG: print "p =", p

    # Computing P[]
    P = [0.0] * N
    for i in xrange(N):
        P[i] = 0.0
        for j in xrange(k):
            P[i] += mat[i][j] * mat[i][j]
        P[i] = (P[i] - n) / (n * (n - 1))
    if DEBUG: print "P =", P

    # Computing Pbar
    Pbar = sum(P) / N
    if DEBUG: print "Pbar =", Pbar

    # Computing PbarE
    PbarE = 0.0
    for pj in p:
        PbarE += pj * pj
    if DEBUG: print "PbarE =", PbarE

    kappa = (Pbar - PbarE) / (1 - PbarE)
    if DEBUG: print "kappa =", kappa

    return kappa

def checkEachLineCount(mat):
    """ Assert that each line has a constant number of ratings
        @param mat The matrix checked
        @return The number of ratings
        @throws AssertionError If lines contain different number of ratings """
    #n = sum(mat[0])
    n = max([sum(mat[i]) for i in range(len(mat))])

# todo the next line should definitely be active -- find out what to do for inconsistent number of raters
    # assert all(sum(line) == n for line in mat[1:]), "Line count != %d (n value)." % n
    return n


def prepare_data(task, result):
    """
    Input: individual task files. assert 1 result per file
    """
    answers = result.read().encode('utf-8')
    sentences = task.read().encode('utf-8')
    ans_root = et.fromstring(answers)
    sent_root = et.fromstring(sentences)
    # if len(ans_root) != len(sent_root[0]):
    #     print 'Error: result and task files contain different number of tasks. Terminating.'
    #     return
    raw_ans = parse_result(ans_root[0])
    raw_sent = parse_task(sent_root)
    sent, ans = filter_tasks(raw_sent, raw_ans)
    mat = matrix(ans, sent)
    kappa = computeKappa(mat)
    return kappa

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('file', nargs=-1)
def main(*args, **options):
    """
    Input: an arbitrary number of path pairs: /path/to/task:/path/to/result
    Output: a Fleiss' kappa measure for each task
    """
    for item in options['file']:
        task_path, result_path = item.split(':')
        task = codecs.open(task_path, 'r', 'utf-8')
        result = codecs.open(result_path, 'r', 'utf-8')
        kappa = prepare_data(task, result)
        print kappa, result_path
    return

if __name__ == '__main__':
    main()