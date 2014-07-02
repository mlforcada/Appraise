To use the toolkit, download the files. The Python files are required, and you may either use the default text 
files for testing or provide your own data. The toolkit has two dependencies, networkx and click, which can be 
installed from pip:

 $ pip install click

To generate tasks, run 

 $ python gist_eval.py [OPTIONS] ORIGINAL REFERENCE TAGS [TASK] [KEYS] 

ORIGINAL is the path to untranslated text, REFERENCE - to reference translation, from which the gapped text will 
be created, TAGS - the reference translation put through Apertium tagger. TASK and KEYS are optional arguments, 
which specify the path to save output files - the task itself and the answer keys, respectively. If those are 
left out, the defaults will be task.txt and keys.txt in the script folder.

The following options are supported:
* -mt, --machine FILENAME – original text translated through Apertium, if the tasks should contain machine 
translation as a tip for evaluator;
* -m, --mode [simple | choices | lemmas] - specifies task mode. Simple just removes the words, choices gives 
a choice of three options for each gap, and lemmas leaves the word's lemma in place, and the user is to fill in 
the correct grammatical form. The default mode is 'simple';
* -k, --keyword - if on, the words to be removed will be determined with keyword selection algorithm, if off - 
the words will be randomly selected;
* -d, --density - an integer from 1 to 100, specifies gap density. The default is 50;
* -r, --relative - if on, the gap density is calculated against the number of words which were selected to be 
removed, if off - against the total number of words in the text (but not more than the number of keywords found, 
if the keyword mode is on);
* -p, --pos - if you wish to remove only specific parts of speech, specify them here as a string of Apertium 
part-of-speech tags separated by commas, i.e. 'vblex, n, adj'.

To check the task completed by the user, run

 $ python text_checker.py TASK KEYS

TASK is a path to the filled-in task, and KEYS is a path to the answer keys, which were generated with the task. 
Note that the script assumes that the filled-in task structure is unchanged, and that the evaluator only filled 
in / changed the words in the gaps. The script returns the number and percentage of correct answers based on the 
answer key.
