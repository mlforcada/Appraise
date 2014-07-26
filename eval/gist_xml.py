# coding=utf-8
__author__ = 'Sereni'
import click
from gaps import prepare_xml
import uuid
import sh

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def validate_pos(ctx, param, value):
    try:
        value = value.strip('"')
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
# @click.argument('tags', type=click.File('r', encoding='utf-8'))
@click.argument('tags', type=click.Path(exists=True))
@click.argument('task', default='task.xml', type=click.Path())
@click.option('--lang', '-l', default='?-?',
              help="Codes for source and target languages, separated by hyphen, e.g. 'eo-en'.")
@click.option('--doc',
              help='Document ID. Used to calculate context for sentences from the same text.')
@click.option('--set', help='Set ID. A unique and descriptive name for the task.')
# @click.option('--machine', '-mt', type=click.File('r', encoding='utf-8'),
#               help='Original text translated through Apertium, if the task should contain machine '
#                    'translation for assistance')
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
@click.option('--pos', '-p', default='blah', callback=validate_pos,
              help='Specify parts of speech to be removed based on Apertium POS tags, e.g. "n, vblex"')
@click.option('--hide_orig', '-hd', default=False, flag_value=True, help='Hide source-language sentences from the task.')
@click.option('--batch', '-b', default=False, flag_value=True,
              help='Batch create files with all assistance mode and the same gaps.')
def gist_xml(*args, **options):
    """
    The gist_xml program produces sets of tasks for gisting evaluation of machine
    translation output from Apertium system, formatted for import into Appraise
    evaluation platform. Reference, original,
    machine and tags are text files containing the following data:

    \b
    original - an untranslated text;
    reference - a literary translation of original;
    tags - the reference translation put through Apertium POS tagger.
    You may also specify path to Apertium POS tagger here, e.g.
    /foo/bar/apertium-eo-en/modes/en-eo-tagger.mode
    In this case, the file will be generated using this tagger;
    machine - (optional) original text translated through Apertium,
    if the task should contain machine translation for assistance.

    The program generates task to path specified in TASK.

    If no mode is specified, the words will simply be removed from the text.
    In multiple choice mode, a choice of three options will be given for each gap,
    including the correct answer. In lemmas mode, each gap will contain a lemma, and
    the user will be prompted to enter the correct word form.
    """
    def launch_apertium(value, input):
        if value.endswith('.mode'):
            chunks = value.split('/')
            mode = chunks[-1].split('.')[0]
            path = '/'.join(chunks[:-2])
            p = sh.apertium('-u -d {0}'.format(path), mode, _in=input.encode('utf-8'), _encoding='utf-8')
            output = p.stdout.decode('utf-8')
        elif value.endswith('.txt'):
            output = open(value).read()
        else:
            raise click.BadParameter('Invalid argument. Please specify either'
                                     'path to .txt file or path to'
                                     'Apertium translator / POS tagger for your language pair.')
        return output

    def generate_anmor(value, text):

        # from tagger or translation mode, try to guess morphological analyzer mode
        if value.endswith('.mode'):
            chunks = value.split('/')
            mode = chunks[-1].split('.')[0]
            path = '/'.join(chunks[:-2])
            if mode.endswith('tagger'):
                mode = '-'.join(mode.split('-')[:-1])
            mode += '-anmor'
            p = sh.apertium('-u -d {0}'.format(path), mode, _in=text.encode('utf-8'), _encoding='utf-8')
            output = p.stdout.decode('utf-8')
        else:
            output = None  # well, should do without it
        return output

    # open or generate tagged text
    original = options['original'].read()
    reference = options['reference'].read()
    tags = launch_apertium(options['tags'], reference)

    # open or generate machine translation
    try:
        if options['machine']:
            mt = launch_apertium(options['machine'], original)
        else:
            mt = None
    except KeyError:
        mt = None

    # experimental: generate a morphological analysis to resolve pos ambiguity
    # use all possible ways to determine the name of the analyzer
    try:
        morph = generate_anmor(options['tags'], reference)
    except KeyError:
        morph = None

    # determine task type
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

    # if ids not specified, generate an ugly but hopefully unique id
    if not options['doc']:
        options['doc'] = uuid.uuid4().hex
    if not options['set']:
        options['set'] = uuid.uuid4().hex
    source, target = options['lang'].split('-')

    try:
        tags = tags.decode('utf-8')
        mt = mt.decode('utf-8')
    except UnicodeEncodeError:  # if it was unicode already
        pass
    except AttributeError:  # or if it's None
        pass

    prepare_xml(reference,
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
                source,
                target,
                options['doc'],
                options['set'],
                options['hide_orig'],
                morph,
                options['batch']
                )

if __name__ == '__main__':
    gist_xml()