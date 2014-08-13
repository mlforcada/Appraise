# coding=utf-8
__author__ = 'Sereni'
"""
This module generates LaTeX tables from XML result files output from Appraise.
"""
import xml.etree.ElementTree as ET
import click
from itertools import product
import math

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def calculate_completion_rate(xml):  # this is what JA refers to as method 2 no average
    """
    Input: a stream from xml file, as in file.read()
    Output: a float representing average completion rate for the task.
    """
    root = ET.fromstring(xml.read())
    sum_correct = 0
    sum_total = 0
    for item in root[0]:
        if item.tag == 'gisting-item':
            correct, total = item.attrib['result'].split(',')[0].split(': ')[1].split('/')
            sum_correct += int(correct)
            sum_total += int(total)
    completion_rate = float(sum_correct)/float(sum_total) * 100
    return completion_rate


def calculate_standard_deviation(xml):
    """
    Calculates average and standard deviation for correct answers to one task.
    """
    root = ET.fromstring(xml.read())
    num_of_evals = 0
    rates = []
    for item in root[0]:
        if item.tag == 'gisting-item':
            num_of_evals += 1
            correct, total = item.attrib['result'].split(',')[0].split(': ')[1].split('/')
            rate = float(correct)/float(total) * 100
            rates.append(rate)
    avg = sum(rates) / num_of_evals
    diff_squared_sum = sum([(rate-avg)**2 for rate in rates])
    sd = math.sqrt(diff_squared_sum/float(num_of_evals))
    return avg, sd


def calculate_time(xml):

    def format_time(t):
        m, s = divmod(t, 60)
        if s < 10:
            f = '%d:0%d' % (int(m), int(s))
        else:
            f = '%d:%d' % (int(m), int(s))
        return f

    root = ET.fromstring(xml.read())
    total_results = 0
    times = []
    for item in root[0]:
        if item.tag == 'gisting-item':
            total_results += 1
            minutes, seconds = item.attrib['duration'].split(':')[-2:]
            times.append(float(minutes)*60 + float(seconds))
    avg_time = sum(times) / total_results
    diff_squared_sum = sum([(time-avg_time)**2 for time in times])
    sd = math.sqrt(diff_squared_sum/float(total_results))
    return format_time(avg_time), format_time(sd)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('data', nargs=-1)
@click.option('--output', '-o', help='Specify output file path')
@click.option('--title', '-t', help='Table title')
@click.option('--par1', help='Name of the first parameter')
@click.option('--par2', help='Name of the second parameter')
@click.option('--mode', '-m', default='percentage', type=click.Choice(['average', 'percentage', 'time', 'holes']),
              help='Calculate average with standard deviation ("average") or percentage of holes filled. Defaults to'
                   '"percentage". "time" mode displays average time spent on each task type.')
def render_table(*args, **options):
    """
    This script calculates completion rates for evaluation tasks based on result XML exported from Appraise evaulation
    system and formats them as a LaTeX table.

    DATA - an arbitrary number of result XML files exported from Appraise evaluation system and their parameters
    formatted as follows: /path/to/file:parameter1:parameter2.

    Parameters provided will be used to name table rows and columns. For example, to construct a table for 4 tasks with
    gap densities of 10 and 20 percent, with and without machine translation, the DATA argument would look like this:

    1.xml:10:MT 2.xml:20:MT 3.xml:10:noMT 4.xml:20:noMT

    Specify parameter names in options if you wish them to be included into the table. In our example, this would be

    -- par1 "gap density" --par2 "machine translation"

    The -mode option lets you select whether the numbers calculated are average and standard deviation, or the
    percentage of holes filled correctly by all evaluators. For example, if three evaluators correctly answered 3/4, 2/3
     and 1/5 questions respectively, the "average" mode will be calculated as follows:

    average = (75 + 66 + 20) / 3 = 52.6, where numbers in parentheses are rates of correct answers for each evaluator
    multiplied by 100;
    standard deviation = 29.5

    In "percentage" mode, the rate is calculated as follows:

    rate = 100 * (3 + 2 + 1) / (4 + 3 + 5) = 50, which indicates a total fraction of correct answers given by all
    evaluators.
    """

    par1_values = set([])
    par2_values = set([])
    cell_dict = {}

    for item in options['data']:
        path, label1, label2 = item.strip("'").split(':')
        par1_values.add(label1)
        par2_values.add(label2)
        xml_file = open(path)
        if options['mode'] == 'percentage':
            completion_rate = calculate_completion_rate(xml_file)
            cell_dict[(label1, label2)] = '%.2f' % completion_rate  # this is used to fill in the appropriate cells
        elif options['mode'] == 'average':
            average, deviation = calculate_standard_deviation(xml_file)
            cell_dict[(label1, label2)] = '%.2f' % average + ' +/- ' + '%.2f' % deviation
        elif options['mode'] == 'time':
            time, deviation = calculate_time(xml_file)
            cell_dict[(label1, label2)] = '{0} +/- {1}'.format(time, deviation)


    param_pairs = product(sorted(par1_values), sorted(par2_values))

    if options['output']:
        out = open(options['output'].strip("'"), 'w')
    else:
        out = open('evaluation_result.tex', 'w')
    out.write('\\begin{{table}}\r\n\\centering\r\n\\begin{{tabular}}{{|r |*{{{0}}}{{c}}|}}\r\n\hline\r\n'.
              format(str(len(par2_values))))
    out.write(' &\multicolumn{{{0}}}'.format(len(par2_values)))
    try:
        label = options['par2'].strip("'")
    except KeyError:
        label = ''
    out.write('{{c|}}{{{0}}}\\\\\r\n\hline\r\n'.format(label.replace('%', '\%')))
    try:
        label = options['par1'].strip("'")
    except KeyError:
        label = ''
    out.write(label.replace('%', '\%') + ' & ' + ' & '.join(sorted(par2_values)) + '\\\\\r\n')
    out.write('\hline\r\n')
    for pair in param_pairs:
        try:
            cell_dict[pair]
        except KeyError:
            cell_dict[pair] = '-'
    for l1 in sorted(par1_values):
        line = [l1]
        for l2 in sorted(par2_values):
            line.append(str(cell_dict[(l1, l2)]))
        out.write('&'.join(line) + '\\\\\r\n')
    out.write('\hline\r\n\end{tabular}\r\n')
    if options['title']:
        out.write('\caption {{{0}}} \label{{tab:title}} \r\n'.format(options['title'].strip("'")))
    out.write('\end{table}\r\n')
    out.close()
    return


if __name__ == '__main__':
    render_table()