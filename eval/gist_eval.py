# coding=utf-8
__author__ = 'Sereni'
import click
from gaps import prepare_text
import sh

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
@click.argument('tags', type=click.Path(exists=True))
@click.argument('task', default='task.txt', type=click.File('w', encoding='utf-8'))
@click.argument('keys', default='keys.txt', type=click.File('w', encoding='utf-8'))
@click.option('--machine', '-mt', type=click.Path(exists=True),
              help='Path to original text translated through Apertium (.txt file),'
                   'or path to Apertium .mode file if the translation needs to be generated,'
                   'e.g. /foo/bar/apertium-eo-en/en-eo.mode')
@click.option('--mode', '-m', default='simple', type=click.Choice(['simple', 'choices', 'lemmas']),
              help='Select task mode: simple gaps, multiple choice gaps or gaps with lemmas')
@click.option('--keyword', '-k', 'keyword', default=False, flag_value=True, help='Remove words based on keyword selection '
                                                                           'rather than at random')
@click.option('--relative', '-r', 'relative', default=False, flag_value=True, help='Calculate keyword density against the '
                                                                             'number of keywords found rather than the '
                                                                             'total number of words in the text')
@click.option('--density', '-d', default=50, type=click.IntRange(0, 100), help='A percentage of words to be removed (0-100)')
@click.option('--pos', '-p', default='blah', callback=validate_pos, help='Specify POS to be removed ("n, vblex")')
@click.option('--hide_orig', '-hd', default=False, flag_value=True, help='Hide source-language sentences from the task.')
def gist_eval(*args, **options):

    """The gist_eval program produces sets of tasks for gisting evaluation
    of machine translation output from Apertium system. Reference, original,
    machine and tags are text files containing the following data:

    \b
    original — an untranslated text;
    reference — a literary translation of original;
    tags — the reference translation put through Apertium morphological analyzer.
    You may also specify path to Apertium morphological analyzer here, e.g.
    /apertium-eo-en/modes/en-eo-morph.mode
    In this case, the file will be generated using this analyzer;
    machine — (optional) original text translated through Apertium,
    if the task should contain machine translation for assistance.
    You may also specify path to Apertium translator for your language
    pair to generate machine translation,
    e.g. /apertium-eo-en/modes-en-eo.mode

    The program will generate the task and the answer keys to paths
    specified in task and keys, respectively. If no output is specified,
    these will be the files task.txt and keys.txt.

    If no mode is specified, the words will simply be removed from the text.
    In multiple choice mode, a choice of three options will be given for each gap,
    including the correct answer. In lemmas mode, each gap will contain a lemma, and
    the user will be prompted to enter the correct word form."""
    def launch_apertium(value, input):
        if value.endswith('.mode'):
            chunks = value.split('/')
            mode = chunks[-1].split('.')[0]
            path = '/'.join(chunks[:-2])
            p = sh.apertium('-d {0}'.format(path), mode, _in=input.encode('utf-8'), _encoding='utf-8')
            output = p.stdout.decode('utf-8')
        elif value.endswith('.txt'):
            output = open(value).read()
        else:
            raise click.BadParameter('Invalid argument. Please specify either'
                                     'path to .txt file or path to'
                                     'Apertium translator / POS tagger for your language pair.')
        return output

    # open or generate tagged text
    original = options['original'].read()
    reference = options['reference'].read()
    tags = launch_apertium(options['tags'], reference)

    # open or generate machine translation
    try:
        mt = launch_apertium(options['machine'], original)
    except KeyError:
        mt = None

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

    try:
        tags = tags.decode('utf-8')
        mt = mt.decode('utf-8')
    except UnicodeEncodeError:  # if it was unicode already
        pass
    except AttributeError:  # or if it's None
        pass

    prepare_text(reference,
                 tags,
                 original,
                 keyword,
                 options['relative'],
                 options['density'] / 100.0,
                 multiple_choice,
                 lemmas,
                 mt,
                 options['pos'],
                 options['task'],
                 options['keys'],
                 options['hide_orig'])

if __name__ == '__main__':
    gist_eval()