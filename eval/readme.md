Assimilation evaluation toolkit
======

This readme describes the scripts used to create assimilation evaluation tasks.

Requirements
----
For the toolkit to work, you should have Python 2.6+ installed (see python.org). The toolkit has three package dependencies: networkx, sh and click, which can be installed with python package manager, e.g. pip:
```
$ pip install click
```

gist_xml.py
-----

The gist_xml program produces sets of tasks for gisting evaluation of machine
translation output from Apertium system, formatted for import into Appraise
evaluation platform. *Reference*, *original*,
*machine* and *tags* are text files containing the following data:

- original - an untranslated text;
- reference - a literary translation of original;
- tags - the reference translation put through Apertium morphological analyzer.
You may also specify path to Apertium morphological analyzer, e.g.
/foo/bar/apertium-eo-en/modes/en-eo-morph.mode
In this case, the file will be generated using this analyzer;
- machine - (optional) original text translated through Apertium,
if the task should contain machine translation for assistance.

The program generates task to path specified in TASK.

If no mode is specified, the words will simply be removed from the text.
In multiple choice mode, a choice of three options will be given for each gap,
including the correct answer. In lemmas mode, each gap will contain a lemma, and
the user will be prompted to enter the correct word form.

The available options are:

  -l, --lang TEXT                 Codes for source and target languages,
                                  separated by hyphen, e.g. 'eo-en'.
                                  
  --doc TEXT                      Document ID. Used to calculate context for
                                  sentences from the same text.
                                  
  --set TEXT                      Set ID. A unique and descriptive name for
                                  the task.
                                  
  -mt, --machine PATH             Path to original text translated through
                                  Apertium (.txt file),or path to Apertium
                                  .mode file if the translation needs to be
                                  generated,e.g. /foo/bar/apertium-eo-en/en-
                                  eo.mode
                                  
  -m, --mode [simple|choices|lemmas]
                                  Select task mode: simple gaps, multiple
                                  choice gaps or gaps with lemmas
                                  
  -k, --keyword                   Remove words based on keyword selection
                                  rather than at random
                                  
  -r, --relative                  Calculate keyword density against the number
                                  of keywords found rather than the total
                                  number of words in the text
                                  
  -d, --density INTEGER RANGE     A percentage of words to be removed (0-100)
  
  -p, --pos TEXT                  Specify parts of speech to be removed based
                                  on Apertium POS tags, e.g. "n, vblex"
                                  
  -hd, --hide_orig                Hide source-language sentences from the
                                  task.
                                  
  -b, --batch                     Batch create files with all assistance modes
                                  and the same gaps.
                                  
  -h, --help                      Show this message and exit.
  
 task_spread.py
 ------
This script spreads sentences across evaluators or groups of evaluators. It returns sentence numbers to be used in each group and each evaluation mode.

- SENTENCES - a number of sentences to be evaluated. Note that the same sentences with a different number of gaps are counted as separate;
- MODES - a number of modes, e.g. with MT, with source sentences, etc.;
- GROUPS - a number of evaluators or groups of evaluators accross which the sentences should be distributed.

For an experiment with 4 evaluation modes, 4 groups of evaluators and 36 sentences, where each 12 sentences have 10, 20 and 30 percent gaps, the script would be run three times:

```
$ python task_spread.py 12 4 4 
```

auto_task_gen.py
-----

This script combines the functionality of the previous two scripts and is the recommended way to generate tasks for large experiments.

This script generates tasks for evaluation of Apertium language pairs from a pair of parallel texts, and evenly distributes sentences in different modes among the evaluators.

Arguments:

- ORIGINAL - a text file with sentences in source language. Each sentence should begin from a new line;

- REFERENCE - a text file with sentences in target language, parallel to those in ORIGINAL. Each sentence should begin from a new line. This is the reference translation of source-language sentences, i.e. produced by humans;

- SENTENCES - an integer indicating how many sentences should be drawn from the provided files;

- GROUPS - an integer indicating among how many groups of evaluators the sentences should be distributed;

- MT PATH - path to Apertium translation mode, e.g. /foo/apertium-eo-en/modes/eo-en.mode. Note that the source language code should come first in your mode name, in case of evaluating translation from Esperanto to English this would be "eo-en.mode";

- MORPH PATH - path to Apertium morphological analyzer mode, e.g. /foo/apertium-eo-en/modes/en-eo-morhp.mode. Note that in this case target language code comes first. For Esperanto to English that would be en-eo-morph.mode. This mode may need to be created first depending on a language pair.

- MODES - an arbitrary number of modes in which you would like to evaluate the sentences. Each mode is an option string for a script and should contain the options described below. The script will generate a set of tasks for each mode provided, the tasks will be split according to the number of groups and contain a total number of sentences specified. An example of a mode string:
```
"-mt -hd -k -m lemmas -d 30 -r -p vblex,n,adv"
```
    * -mt, --machine - a boolean flag indicating whether machine translation should be shown as assistance in a task;

    * -hd, --hide_orig - a boolean flag indicating whether source-language sentences should be hidden from the
    evaluators in a given task;

    * -k, --keyword - a boolean flag indicating whether the words to be removed from sentences are to be selected arbitrarily or with a keyword selection algorithm;

    * -m, --mode - gap modes, e.g. -m simple - an open answer task, -m lemmas - an open answer task with word lemmas
     provided in gaps for assistance, -m choices - a multiple choice task with three choices of possible words per
      gap. Defaults to 'simple';

    * -d, --density - an integer from 0 to 100 indicating what percentage of words in the sentence should be removed;

    * -r, --relative - a boolean flag indicating whether gap density should be calculated against the total number of words in the sentence (not toggled) or against the number of keywords found (toggled).

    * -p, --pos - if only specific parts of speech should be removed, provide their Apertium part-of-speech tags separated by commas, e.g. "vblex, n, adj";

    * --set - a unique and descriptive name for a task. Optional but useful when collecting results. If not provided, a unique but undescriptive number will be assigned automatically.

Options:
 
--dir - path to the directory where the task files should be written. Must exist before running the script;

--lang - codes for source and target languages separated by hyphen, e.g. en-eo.

gist_eval.py
-----
This script works similarly to gist_xml.py, but generates tasks to text file that can be sent out to evaluators. 
Reference, original and tags are text files containing the following data:

ORIGINAL — an untranslated text;

REFERENCE — a literary translation of original;

TAGS — the reference translation put through Apertium morphological analyzer.
You may also specify path to Apertium morphological analyzer here, e.g.
/apertium-eo-en/modes/en-eo-morph.mode
In this case, the file will be generated using this analyzer;

TASK - path to the output task file (defaults to task.txt);

KEYS - path to the output file with answer keys (defaults to keys.txt).

The program will generate the task and the answer keys to paths
specified in task and keys, respectively. If no output is specified,
these will be the files task.txt and keys.txt.

If no mode is specified, the words will simply be removed from the text.
In multiple choice mode, a choice of three options will be given for each gap,
including the correct answer. In lemmas mode, each gap will contain a lemma, and
the user will be prompted to enter the correct word form.

Options:

 -mt, --machine PATH             Path to original text translated through
                                  Apertium (.txt file),or path to Apertium
                                  .mode file if the translation needs to be
                                  generated,e.g. /foo/bar/apertium-eo-en/en-
                                  eo.mode
                                  
  -m, --mode [simple|choices|lemmas]
                                  Select task mode: simple gaps, multiple
                                  choice gaps or gaps with lemmas
                                  
  -k, --keyword                   Remove words based on keyword selection
                                  rather than at random
                                  
  -r, --relative                  Calculate keyword density against the number
                                  of keywords found rather than the total
                                  number of words in the text
                                  
  -d, --density INTEGER RANGE     A percentage of words to be removed (0-100)
  
  -p, --pos TEXT                  Specify POS to be removed ("n, vblex")
  
  -hd, --hide_orig                Hide source-language sentences from the
                                  task.

text_checker.py
-----
The program checks user-filled text file tasks for gisting evaluation. The task structure should be unchanged for the script to work (assume the users only wrote/changed the words in brackets.

Two arguments are required:

TASK - path to the user's text file with the gaps filled in;

KEYS - path to answer keys generated with the task.

The program prints the number of correct answers to terminal.



synonyms.py
-----
This script finds words that could potentially be used as synonyms in the gaps instead of reference answer keys. It searches the result XML from Appraise and records the words that have been submitted to one gap by more than a specified number of evaluators, and outputs these words, the sentences in which they have been found and the original answer key.

TASK - the XML file that was used to add the task to Apppraise evaluation system;

RESULT - the XML file obtained through result export for this task from Appraise;

OUTPUT - a .txt file to write the synonyms;

THRESHOLD - a minimal number of evaluators to give the same answer for it to be considred a synonym.

For example, in the sentence "I like { }" the intended answer is "apples". The evaulators gave the following answers:

1: apples

2: oranges

3: peaches

4: oranges

If threshold is set to 2, only "oranges" will appear as a synonym for this gap. If threshold is set to 1, it will be "oranges" and "peaches", but not "apples", because this was the original answer.

Note that it is possible to export results for several tasks in one file from Appraise. In this case, the TASK file should contain all task XMLs in the correct order, and also the task XMLs should be enclosed into an additional root tag, e.g. <root> (task 1 XML) (task 2 XML) </root>.

fleiss_kappa.py
-----
This script computes Fleiss' Kappa measure for a given task. Input is an arbitrary number of strings that contain path to task file and path to result file for the corresponding task, separated by a colon. Example:
```
python fleiss_kappa.py /path/to/task1:/path/to/result1 /path/to/task2:/path/to/result2
```
The Fleiss' Kappa measure will be printed to terminal along with the corresponding result path. Note that Fleiss' Kappa calculations require a constant number of evaluators in each group. 

generate_tsv.py
-----
This script converts data from Appraise XML result files to TSV file to be used
with gnuplot. The table can be used to plot a histogram, where x axis is user-specified,
and y-axis shows the percentage of correct answers in a given task.
output - path to output file (evaluation.data by default);
data - a string of "path:label", where PATH is a path to Appraise XML result file,
and VALUE is the x-axis value for this particular task, separated by a colon (:).

For example, if you would like to plot the results of evaluation from two tasks,
one of which offered machine translation for assistance and the other did not,
the input would look something like
```
generate_tsv.py 'result1.xml:with mt' 'result2.xml:without mt' output.data
```
Use gnuplot to create the plot from data file generated by this script.

latex.py
-----
This script calculates completion rates for evaluation tasks based on result XML exported from Appraise evaulation system and formats them as a LaTeX table.

DATA - an arbitrary number of result XML files exported from Appraise evaluation system and their parameters formatted as follows: 
```
/path/to/file:parameter1:parameter2
```
Provided parameters will be used to name table rows and columns. For example, to construct a table for 4 tasks with gap densities of 10 and 20 percent, with and without machine translation, the DATA argument would look like this:
```
1.xml:10:MT 2.xml:20:MT 3.xml:10:noMT 4.xml:20:noMT
```

Options:

- --title - table title;

- --par1 - name of the first parameter (see below);

- --par2 - name of the second parameter;

- --output - path to the output table, defaults to evaluation_result.tex in the script folder;
- -m, --mode [average|percentage|time|holes] - specify what will be calculated to fill the table (see description below).

Specify parameter names in options if you wish them to be included into the table. They will be used as labesl for the corresponding values. In our example, this would be
```
--par1 "gap density" --par2 "machine translation"
```
The *-mode* option lets you select whether the numbers calculated are average and standard deviation, or the percentage of holes filled correctly by all evaluators. For example, if three evaluators correctly answered 3/4, 2/3 and 1/5 questions respectively, the "average" mode will be calculated as follows:

average = (75 + 66 + 20) / 3 = 52.6, where numbers in parentheses are rates of correct answers for each evaluator multiplied by 100;

standard deviation = 29.5

In "percentage" mode, the rate is calculated as follows:

rate = 100 * (3 + 2 + 1) / (4 + 3 + 5) = 50, which indicates a total fraction of correct answers given by all evaluators.

The "time" mode calculates average time spend on one sentence in each task along with its standard deviation.

The "holes" mode calculates a total number of holes to be filled for each task type.