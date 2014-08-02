# coding=utf-8
__author__ = 'Sereni'
"""
This module generates LaTeX tables from XML result files output from Appraise.
"""
import xml.etree.ElementTree as ET
import click
from itertools import product

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def calculate_completion_rate(xml):
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


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('data', nargs=-1)
@click.option('--output', '-o', help='Specify output file path')
@click.option('--title', '-t', help='Table title')
@click.option('--par1', help='Name of the first parameter')
@click.option('--par2', help='Name of the second parameter')
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
    """


    par1_values = set([])
    par2_values = set([])
    cell_dict = {}

    for item in options['data']:
        path, label1, label2 = item.split(':')
        par1_values.add(label1)
        par2_values.add(label2)
        xml_file = open(path)
        completion_rate = calculate_completion_rate(xml_file)
        cell_dict[(label1, label2)] = completion_rate  # this is used to fill in the appropriate cells

    param_pairs = product(sorted(par1_values), sorted(par2_values))

    if options['output']:
        out = open(options['output'], 'w')
    else:
        out = open('evaluation_result.tex', 'w')
    out.write('\\begin{{table}}\r\n\\centering\r\n\\begin{{tabular}}{{|r |*{{{0}}}{{c}}|}}\r\n\hline\r\n'.
              format(str(len(par2_values))))
    out.write(' &\multicolumn{{{0}}}'.format(len(par2_values)))
    try:
        label = options['par2']
    except KeyError:
        label = ''
    out.write('{{c|}}{{{0}}}\\\\\r\n\hline\r\n'.format(label))
    try:
        label = options['par1']
    except KeyError:
        label = ''
    out.write(label + ' & ' + ' & '.join(sorted(par2_values)) + '\\\\\r\n')
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
        out.write('\caption {{{0}}} \label{{tab:title}} \r\n'.format(options['title']))
    out.write('\end{table}\r\n')
    out.close()
    return

if __name__ == '__main__':
    render_table()