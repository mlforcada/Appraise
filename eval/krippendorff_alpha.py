'''
Python implementation of Krippendorff's alpha -- inter-rater reliability

(c)2011 Thomas Grill (http://grrrr.org)
license: http://creativecommons.org/licenses/by-sa/3.0/

Python version >= 2.4 required
'''

try:
    import numpy as N
except ImportError:
    N = None
import xml.etree.ElementTree as et
import click
import codecs

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


def find_users(xml):
    return set([gisting_item.attrib['user'] for gisting_item in xml])


def parse_result(result):
    results = {}
    all_users = find_users(result)
    first_run = True
    added_users = set([])
    for gisting_item in result:  # item is a single person's answer, result corresponds to a task

        index = int(gisting_item.attrib['id'].decode('utf-8'))
        if first_run:
            last_index = index
            first_run = False

        # if item id has changed, record 'no answer' for all users not found
        if index != last_index:
            blank_users = all_users.difference(added_users)
            for person in blank_users:
                results[last_index][person] = ['*']*gap_count
            added_users.clear()
        if isinstance(gisting_item.attrib['result'], str):
            res = gisting_item.attrib['result'].decode('utf-8')
        elif isinstance(gisting_item.attrib['result'], unicode):
            res = gisting_item.attrib['result']
        user = gisting_item.attrib['user']
        answers = res.split('answers:')[-1].split(', ')

        try:
            results[index]
        except KeyError:
            results[index] = {}

        results[index][user] = [word.strip(' ').lower() for word in answers]

        gap_count = len(results[index][user])
        added_users.add(user)
        last_index = index
    blank_users = all_users.difference(added_users)
    for person in blank_users:
        results[last_index][person] = ['*']*gap_count

    return results


def check_answers(result, sent):
    checked = {}
    for i in range(len(result)):
        gaps = result[i]
        keys = sent[i][1].split(';')
        for user, answers in gaps.items():
            l = []
            for j in range(len(answers)):
                if answers[j] == '*':
                    l.append(answers[j])
                else:
                    if answers[j] == keys[j]:
                        l.append('1')
                    else:
                        l.append('0')
            try:
                checked[user] += l
            except KeyError:
                checked[user] = l
    return checked


def prepare_data(task, result):
    answers = result.read().encode('utf-8')
    sentences = task.read().encode('utf-8')
    ans_root = et.fromstring(answers)
    sent_root = et.fromstring(sentences)
    raw_ans = parse_result(ans_root[0])
    raw_sent = parse_task(sent_root)
    sent, ans = filter_tasks(raw_sent, raw_ans)
    dat = check_answers(ans, sent)
    formatted = [value for key, value in dat.items()]
    return formatted


def nominal_metric(a, b):
    return a != b


def interval_metric(a, b):
    return (a-b)**2


def ratio_metric(a, b):
    return ((a-b)/(a+b))**2


def krippendorff_alpha(data, metric=interval_metric, force_vecmath=False, convert_items=float, missing_items=None):
    '''
    Calculate Krippendorff's alpha (inter-rater reliability):

    data is in the format
    [
        {unit1:value, unit2:value, ...},  # coder 1
        {unit1:value, unit3:value, ...},   # coder 2
        ...                            # more coders
    ]
    or
    it is a sequence of (masked) sequences (list, numpy.array, numpy.ma.array, e.g.) with rows corresponding to coders and columns to items

    metric: function calculating the pairwise distance
    force_vecmath: force vector math for custom metrics (numpy required)
    convert_items: function for the type conversion of items (default: float)
    missing_items: indicator for missing items (default: None)
    '''

    # number of coders
    m = len(data)

    # set of constants identifying missing values
    maskitems = set((missing_items,))
    if N is not None:
        maskitems.add(N.ma.masked_singleton)

    # convert input data to a dict of items
    units = {}
    for d in data:
        try:
            # try if d behaves as a dict
            diter = d.iteritems()
        except AttributeError:
            # sequence assumed for d
            diter = enumerate(d)

        for it, g in diter:
            if g not in maskitems:
                try:
                    its = units[it]
                except KeyError:
                    its = []
                    units[it] = its
                its.append(convert_items(g))

    units = dict((it, d) for it, d in units.iteritems() if len(d) > 1)  # units with pairable values
    n = sum(len(pv) for pv in units.itervalues())  # number of pairable values

    N_metric = (N is not None) and ((metric in (interval_metric, nominal_metric, ratio_metric)) or force_vecmath)

    Do = 0.
    for grades in units.itervalues():
        if N_metric:
            gr = N.array(grades)
            Du = sum(N.sum(metric(gr, gri)) for gri in gr)
        else:
            Du = sum(metric(gi, gj) for gi in grades for gj in grades)
        Do += Du/float(len(grades)-1)
    Do /= float(n)

    De = 0.
    for g1 in units.itervalues():
        if N_metric:
            d1 = N.array(g1)
            for g2 in units.itervalues():
                De += sum(N.sum(metric(d1,gj)) for gj in g2)
        else:
            for g2 in units.itervalues():
                De += sum(metric(gi,gj) for gi in g1 for gj in g2)
    De /= float(n*(n-1))

    return 1.-Do/De

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('file', nargs=-1)
def main(*args, **options):
    """
    Input: an arbitrary number of path pairs: /path/to/task:/path/to/result
    Output: a Krippendorff Alpha measure for each task
    """
    missing = '*'
    for item in options['file']:
        task_path, result_path = item.split(':')
        task = codecs.open(task_path, 'r', 'utf-8')
        result = codecs.open(result_path, 'r', 'utf-8')
        array = prepare_data(task, result)
        print result_path
        print "nominal metric: %.3f" % krippendorff_alpha(array,nominal_metric,missing_items=missing)
        print "interval metric: %.3f" % krippendorff_alpha(array,interval_metric,missing_items=missing)
        print

    return


if __name__ == '__main__':
    # print "Example from http://en.wikipedia.org/wiki/Krippendorff's_Alpha"

    # data = (
    #     "*    *    *    *    *    3    4    1    2    1    1    3    3    *    3", # coder A
    #     "1    *    2    1    3    3    4    3    *    *    *    *    *    *    *", # coder B
    #     "*    *    2    1    3    4    4    *    2    1    1    3    3    *    4", # coder C
    # )

    # data = prepare_data()
    #
    # missing = '*' # indicator for missing values
    # array = [d.split() for d in data]  # convert to 2D list of string items
    #
    # print "nominal metric: %.3f" % krippendorff_alpha(array,nominal_metric,missing_items=missing)
    # print "interval metric: %.3f" % krippendorff_alpha(array,interval_metric,missing_items=missing)
    main()
