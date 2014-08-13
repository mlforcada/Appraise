__author__ = 'Sereni'
"""This module generates a number of tasks automatically given parallel texts, a number of users and
script parameters"""
import random
import sh
import uuid
from gaps import prepare_xml
from task_spread_draft import dist
import click

# todo when core code is changed, replace tagger with anmor


def draw_sentences(src, ref, mt, tag, morph, n):
    """
    src and ref: files with parallel sentences in two languages, read into strings, each sentence ends with a newline
    mt: src put through Apertium translation
    tag: ref put through Apertium tagger (anmor to appear)
    n: the number of sentences to be drawn
    """
    sent1 = src.split('\r')
    sent2 = ref.split('\r')
    sent_tag = tag.split('\r')
    sent_mt = mt.split('\r')
    sent_morph = morph.split('\r')
    if len(sent1) == 1:
        sent1 = src.split('\n')
        sent2 = ref.split('\n')
        sent_tag = tag.split('\n')
        sent_mt = mt.split('\n')
        sent_morph = morph.split('\n')
    if len(sent1) != len(sent2):
        print 'Error: the parallel texts contain different number of sentences. Please check your files.'
        print 'Source: %d Target: %d' % (len(sent1), len(sent2))
        return
    pairs = [(sent1[i].strip('\r\n'), sent2[i].strip('\r\n'), sent_mt[i].strip('\r\n'),
              sent_tag[i].strip('\r\n'), sent_morph[i].strip('\r\n')) for i in range(len(sent1))
             if len(sent1[i].split(' ')) >= 10]
    if len(pairs) < n:
        print 'Error: trying to draw more sentences (%d) than available (%d)' % (n, len(pairs))
        return

    selection = random.sample(pairs, n)
    return selection  # a list of tuples of parallel sentences


def call_apertium(text, mode_path):
    """
    Call Apertium for the rescue! Accepts a text and a mode path, as in '~/apertium-foo-bar/modes/foo-bar.mode'.
    Returns the text processed with that mode. Therefore, one function for MT, anmor and tagger.
    """
    chunks = mode_path.split('/')
    mode = chunks[-1].split('.')[0]
    path = '/'.join(chunks[:-2])
    p = sh.apertium('-u -d {0}'.format(path), mode, _in=text.encode('utf-8'), _encoding='utf-8')
    output = p.stdout.decode('utf-8')
    return output


def generate_texts(array, numbers):
    """
    array: the corpus of sentences generated in draw_sentences()
    numbers: a string of semicolon-separated integers which correspond to sentence indices
    Generates five text strings to be fed into task generator: source, reference, mt, tagged and morph
    """
    indices = [int(i) for i in numbers.split(';')]
    source = []
    reference = []
    machine = []
    tagged = []
    morph = []
    for i in range(len(array)):
        if i in indices:
            src, ref, mt, tag, mrp = array[i]
            source.append(src.strip('.'))
            reference.append(ref.strip('.'))
            machine.append(mt.strip('.'))
            tagged.append(tag.strip('.'))
            morph.append(mrp.strip('.'))
    return '. '.join(source)+'.', '. '.join(reference)+'.', '. '.join(machine)+'.', '. '.join(tagged)+'.', '. '.join(morph)+'.'


def parse_mode(s):
    def validate_pos(value):
        default_pos = ['n', 'vblex', 'vbmod', 'vbser', 'vbhaver', 'vaux', 'adj', 'post', 'adv', 'preadv', 'postadv', 'mod',
                   'det', 'prn', 'pr', 'num', 'np', 'ij', 'cnjcoo', 'cnjsub', 'cnjadv']
        try:
            value = value.strip('"')
            pos = filter(lambda x: x in default_pos,
                         map(lambda x: x.strip(' '), value.split(','))
                         )
            if not pos:
                pos = default_pos
            return pos
        except ValueError:
            print 'Warning: invalid parts of speech. Please check POS values against the Apertium list. ' \
                  'Falling back to a default list.'
            return default_pos

    options = dict((e if len(e) > 1 else (e[0], True) for e in (elem.split()
                    for elem in ('-'+d for d in s.strip("'").split('-') if d))))

    try:
        val = options['-p']
    except KeyError:
        try:
            val = options['-pos']
        except KeyError:
            val = 'default'
    opt_dict = {}
    opt_dict['pos'] = validate_pos(val)

    mappings = {
        '-mt': '-machine',
        '-m': '-mode',
        '-k': '-keyword',
        '-r': '-relative',
        '-p': '-pos',
        '-hd': '-hide_orig',
        '-d': '-density'
    }

    for key, value in mappings.items():
        try:
            opt_dict[value.strip('-')] = options[key]
        except KeyError:
            try:
                opt_dict[value.strip('-')] = options[value]
            except KeyError:
                opt_dict[value.strip('-')] = None
    return opt_dict


def generate_task_name(group, options):
    """
    This generates a readable task name based on group and mode.
    """
    if options['machine'] and options['hide_orig']:
        mode = 'mt'
    elif options['machine'] and not options['hide_orig']:
        mode = 'both'
    elif not options['machine'] and options['hide_orig']:
        mode = 'none'
    else:
        mode = 'src'
    name = 'group{0}-{1}-{2}.xml'.format(str(group), str(options['density']), mode)
    return name

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument('original', type=click.File('r', encoding='utf-8'))
@click.argument('reference', type=click.File('r', encoding='utf-8'))
@click.argument('sentences', type=click.INT)
@click.argument('groups', type=click.INT)
@click.argument('mt_path', type=click.Path())
@click.argument('tagger_path', type=click.Path())
@click.argument('modes', nargs=-1)
@click.option('--dir', help='Path to the directory where task files will be written.')
@click.option('--lang', '-l', default='?-?',
              help="Codes for source and target languages, separated by hyphen, e.g. 'eo-en'.")
def everything(*args, **options):
    """
    This script generates tasks for evaluation of Apertium language pairs from a pair of parallel texts, and evenly
    distributes sentences in different modes among the evaluators.

    Arguments:

    ORIGINAL - a text file with sentences in source language. Each sentence should begin from a new line;

    REFERENCE - a text file with sentences in target language, parallel to those in ORIGINAL. Each sentence should
    begin from a new line. This is the reference translation of source-language sentences, i.e. produced by humans;

    SENTENCES - an integer indicating how many sentences should be drawn from the provided files;

    GROUPS - an integer indicating among how many groups of evaluators the sentences should be distributed;

    MT PATH - path to Apertium translation mode, e.g. /foo/apertium-eo-en/modes/eo-en.mode. Note that the source
    language code should come first in your mode name, in case of evaluating translation from Esperanto to English
    this would be "eo-en.mode";

    TAGGER PATH - path to Apertium tagger mode, e.g. /foo/apertium-eo-en/modes/en-eo-tagger.mode. Note that in this
    case target language code comes first. For Esperanto to English that would be en-eo-tagger.mode. This mode may
    need to be created first depending on a language pair.

    MODES - an arbitrary number of modes in which you would like to evaluate the sentences. Each mode is an option
    string for a script and should contain the options described below. An example of a mode string:

    "-mt -hd -k -m lemmas -d 30 -r -p vblex,n,adv"

        * -mt, --machine - a boolean flag indicating whether machine translation should be shown as assistance in a task;

        * -hd, --hide_orig - a boolean flag indicating whether source-language sentences should be hidden from the
        evaluators in a given task;

        * -k, --keyword - a boolean flag indicating whether the words to be removed from sentences are to be selected
        arbitrarily or with a keyword selection algorithm;

        * -m, --mode - gap modes, e.g. -m simple - an open answer task, -m lemmas - an open answer task with word lemmas
         provided in gaps for assistance, -m choices - a multiple choice task with three choices of possible words per
          gap. Defaults to 'simple';

        * -d, --density - an integer from 0 to 100 indicating what percentage of words in the sentence should be removed;

        * -r, --relative - a boolean flag indicating whether gap density should be calculated against the total number
        of words in the sentence (not toggled) or against the number of keywords found (toggled).

        * -p, --pos - if only specific parts of speech should be removed, provide their Apertium part-of-speech tags
        separated by commas, e.g. "vblex, n, adj";

        * --set - a unique and descriptive name for a task. Optional but useful when collecting results. If not
        provided, a unique but undescriptive number will be assigned automatically.

    """
    sentences = options['sentences']
    groups = options['groups']
    modes_num = len(options['modes'])
    src = options['original'].read()
    ref = options['reference'].read()
    mt_mode = options['mt_path']
    tagger = options['tagger_path']

    # generate texts
    mt = call_apertium(src, mt_mode)
    tag = call_apertium(ref, tagger)
    morph = call_apertium(ref, tagger.replace('tagger', 'morph'))

    # select a desired number of sentences from the corpus
    sent_array = draw_sentences(src, ref, mt, tag, morph, sentences)

    # distribute requires a dictionary of kwargs. not sure it will work since it's tied to a cli...
    kwargs = {
        'sentences': sentences,
        'groups': groups,
        'modes': modes_num
    }
    distributed = dist(**kwargs)

    for group_num in range(len(distributed)):
        for mode_num in range(len(distributed[group_num])):
            mode = options['modes'][mode_num]
            source, reference, machine, tagged, anmor = generate_texts(sent_array, distributed[group_num][mode_num])
            opt_dict = parse_mode(mode)

            # see if need to pass mt text
            if opt_dict['machine']:
                mode_mt = machine
            else:
                mode_mt = None

            # determine task type based on flags
            keyword = False
            if opt_dict['keyword']:
                keyword = True
            multiple_choice = False
            lemmas = False
            if opt_dict['mode'] == 'choices':
                multiple_choice = True
            elif opt_dict['mode'] == 'lemmas':
                lemmas = True
                keyword = True

            # generate set and doc ids, parse language pair
            try:
                options['doc']
            except KeyError:
                options['doc'] = uuid.uuid4().hex
            try:
                options['set']
            except KeyError:
                options['set'] = uuid.uuid4().hex
            src_lang, target_lang = options['lang'].split('-')

            task = options['dir'] + generate_task_name(group_num, opt_dict)

            prepare_xml(reference,
                        tagged,
                        source,
                        keyword,
                        opt_dict['relative'],
                        float(opt_dict['density']) / 100.0,
                        multiple_choice,
                        lemmas,
                        mode_mt,
                        opt_dict['pos'],
                        task,  # this is an output name, make it pretty based on options
                        src_lang,
                        target_lang,
                        options['doc'],
                        options['set'],
                        opt_dict['hide_orig'],
                        anmor,
                        None  # this is for batch -- definitely not here
                        )
if __name__ == '__main__':
    everything()
# input logic
# 1. corpus: two parallel text files, sentences separated by line breaks
# 2. general options: path to translator mode and to tagger/anmor -- by the way, will we resolve anmor? I say refactor
#    language pair (names)
#    set id - optional, also doc id, no one needs it, really
# 3. mode-specific options. will go as a variadic argument. each iteration is a string, which should then be parsed
#    into options. any way to go automatically?
#    mode-specific options go as follows: mode, keyword, relative, density, pos, hide original, mt
