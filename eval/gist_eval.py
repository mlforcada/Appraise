# coding=utf-8
__author__ = 'Sereni'
import click
from gaps import everything

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def validate_pos(ctx, param, value):
    try:
        default_pos = ['n', 'vblex', 'vbmod', 'vbser', 'vbhaver', 'vaux', 'adj', 'post', 'adv', 'preadv', 'postadv', 'mod',
               'det', 'prn', 'pr', 'num', 'np', 'ij', 'cnjcoo', 'cnjsub', 'cnjadv']
        pos = filter(lambda x: x in default_pos,
                     map(lambda x: x.strip(' '), value.split(','))
                     )
        if not pos:
            pos = default_pos
        return pos
    except ValueError:
        raise click.BadParameter('Invalid parts of speech. Please check POS values against the Apertium list.')
@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('original', type=click.File('r', encoding='utf-8'))
@click.argument('reference', type=click.File('r', encoding='utf-8'))
@click.argument('tags', type=click.File('r', encoding='utf-8'))
@click.argument('task', default='task.txt', type=click.File('w', encoding='utf-8'))
@click.argument('keys', default='keys.txt', type=click.File('w', encoding='utf-8'))
@click.option('--machine', '-mt', type=click.File('r', encoding='utf-8'), help='Original text translated through Apertium, if the task should '
                                                       'contain machine translation for assistance')
@click.option('--mode', '-m', default='simple', type=click.Choice(['simple', 'choices', 'lemmas']),
              help='Select task mode: simple gaps, multiple choice gaps or gaps with lemmas')
@click.option('--keyword', '-k', 'keyword', default=False, flag_value=True, help='Remove words based on keyword selection '
                                                                           'rather than at random')
@click.option('--relative', '-r', 'relative', default=False, flag_value=True, help='Calculate keyword density against the '
                                                                             'number of keywords found rather than the '
                                                                             'total number of words in the text')
@click.option('--density', '-d', default=50, type=click.IntRange(0, 100), help='A percentage of words to be removed (0-100)')
@click.option('--pos', '-p', default='blah', callback=validate_pos, help='Specify POS to be removed ("n, vblex")')
def gist_eval(*args, **options):

    """The gist_eval program produces sets of tasks for gisting evaluation
    of machine translation output from Apertium system. Reference, original,
    machine and tags are text files containing the following data:

    \b
    original — an untranslated text;
    reference — a literary translation of original;
    tags — the reference translation put through Apertium POS-tagger;
    machine — (optional) original text translated through Apertium,
    if the task should contain machine translation for assistance.

    The program will generate the task and the answer keys to paths
    specified in task and keys, respectively. If no output is specified,
    these will be the files task.txt and keys.txt.

    If no mode is specified, the words will simply be removed from the text.
    In multiple choice mode, a choice of three options will be given for each gap,
    including the correct answer. In lemmas mode, each gap will contain a lemma, and
    the user will be prompted to enter the correct word form."""
    keyword = False
    if options['keyword']:
        keyword = True
    multiple_choice = False
    lemmas = False
    if options['mode'] == 'choices':
        multiple_choice = True
    elif options['mode'] == 'lemmas':
        lemmas = True
        keyword = True
    everything(options['reference'],
               options['tags'],
               options['original'],
               keyword,
               options['relative'],
               options['density'] / 100.0,
               multiple_choice,
               lemmas,
               options['machine'],
               options['pos'],
               options['task'],
               options['keys'])

if __name__ == '__main__':
    gist_eval()