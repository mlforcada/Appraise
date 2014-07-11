Gisting evaluation system

1.	Overview
This readme descirbes the gisting evaluation toolkit for Apertium machine translation system.
Gisting, or understanding the main points of text, is one of the applications of machine translation.
This system facilitates such evaluation by providing a platform for both evaluators and administrators
to work on the tasks.
Each evaluation task consists of sets of sentences based on parallel texts in a pair of languages. For
the translation from L1 to L2, each set contains:
•	a sentence in L2 with some keywords removed;
•	(optional) a corresponding sentence in L1;
•	(optional) a sentence in L2, which has been automatically translated from L1.
In addition, the system features three types of tasks according to the types of gaps left in the L2
sentence:
•	simple gaps, with the keywords removed from the sentence;
•	lemmas, where the words in gaps are replaced with their respective lemmas (dictionary forms, e.g.
‘replace’ instead of ‘replaced’);
•	multiple choice, where each gap is provided with a list of word choices.
The evaluators may view and complete the tasks. The administrators may generate new tasks from parallel
texts, add tasks into the system, assign tasks to specific users and export evaluation results.
The system’s web interface extends Appraise evaluation system by Chris Federmann [1].
For more information on gisting evaluation, see [2].

2.	Installation
The toolkit is based on Python, which must be installed first (see python.org for instructions). The
recommended version is Python 2.7. The following additional Python packages are required to run Appraise,
 which is the base for the web-interface of the toolkit:
•	Django 1.3.5
•	(optional) NLTK
To generate new tasks from parallel texts, you will also need the following packages:
•	networkx
•	click
•	sh
To install Python packages, use a package manager, such as pip. See [3] for installation instructions.
 Then, for each package, run
$ pip install (package name)
e.g. 
$ pip install sh
or, for specific versions,
$ pip install django==1.3.5
Unless you are provided with ready tasks, you should also install Apertium for task generation [4].
To launch Appraise development server, in /appraise/evaluation run 
$ python manage.py runserver
The web-interface will be available at http://127.0.0.1:8000/appraise

3.	How to use
The project comes with a sample database, which contains one superuser and three tasks, one for each
kind of gaps. To log into the system, use the login and password 'admin' (consider changing this).

a.	Using the toolkit as an evaluator
After logging into the system, you should see an overview of available tasks. Click the task name to
start evaluating. The general goal is to fill in the gaps in the sentence with the most suitable words.
Depending on task type, the gaps may be pre-filled with assisting information. You may also be provided
with the same sentence in the other language of the pair, which is being evaluated, or with machine
translation of that sentence. Each task comes with a set of instructions displayed before every question.
After filling in the gaps, press the ‘submit’ button to move on to the next sentence. When all the
sentences are completed in the current task, you will be automatically redirected to task overview,
and may then complete another task.

b.	Using the toolkit as an administrator
Administrators may participate in evaluation as users (see above), but they also have access to the
Status menu (the link in the menu bar, top of the page). In this menu, you may see the completion status
for all the tasks. Click on task name to view details. On this page, you will be able to see the users
who completed evaluation, their average completion time and also the answer statistics, which lists all
the answers given and their frequency. Use the links on the bottom of the page to export task results as
XML or export user agreement data (for two or more users).

c.	Importing new tasks into the database
In Appraise, the tasks are presented in XML format. To add tasks to the database, access the
administrative part of the site at /appraise/admin. A superuser account is required. In the site
admin, select “EvaluationTask objects” to see available tasks. In this menu, click “Add Evaluation
Task object” in the right upper corner to add new task. Enter a descriptive task name, select task
type (“Gisting”), XML source file (will be described below). Also enter user instructions in task
description and select the users who are allowed to complete the task. Click “save” in the lower right
corner to add the task. There are also EvaluationItem objects, which will be generated automatically
from the task, and EvaluationResult objects, which will be created as the evaluators submit their work.
The toolkit comes with scripts to generate XML source files from parallel texts. The script to run is
called gist_xml.py. In the folder with the script run

$ python gist_xml.py –h

to see help for arguments and options. In general, the usage goes as follows:

gist_xml ORIGINAL REFERENCE TAGS,

where 
original is a text in L1, 
reference is the same text in literary translation into L2, and 
tags is the reference text put through Apertium part-of-speech tagger (see notes below).
The available options include:
* -mt, --machine FILENAME – original text translated through Apertium, if the tasks should contain
machine translation as a tip for evaluator;
* -m, --mode [simple | choices | lemmas] - specifies task mode. Simple just removes the words, choices
gives a choice of three options for each gap, and lemmas leaves the word's lemma in place, and the
user is to fill in the correct grammatical form. The default mode is 'simple';
* -k, --keyword - if on, the words to be removed will be determined with keyword selection algorithm,
if off - the words will be randomly selected;
* -d, --density - an integer from 1 to 100, specifies gap density. The default is 50;
* -r, --relative - if on, the gap density is calculated against the number of words which were selected
to be removed, if off - against the total number of words in the text (but not more than the number of
keywords found, if the keyword mode is on);
* -p, --pos - if you wish to remove only specific parts of speech, specify them here as a string of
Apertium part-of-speech tags separated by commas, i.e. 'vblex, n, adj' [5].
* -l, --lang - a language pair of the task, two language codes separated by a hyphen, e.g. 'eo-en'. The first
code specifies the source language, the second - the target language. This information is optional but useful
for user selection in the system.
* --doc - document ID. Appraise uses this to find the sentences from the same text to provide context. If not specified,
a random id will be generated.
* --set - set ID. A unique and descriptive name for the current set of tasks, will be seen in exported results.
If not specified, will be set to a unique but undescriptive randomized ID.
* -hd, --hide_orig - hide original sentences from the task (please provide them to the script anyway).

Note: for tags and machine translation, you may generate them on the go by specifying path to Apertium
modes. Each Apertium language pair contains the /modes folder with .mode files. The simple translation
modes are called L1-L2.mode, where L1 and L2 are abbreviations for languages of the language pair. These are the modes that should be used to generate machine translation. For example, if you translate a text from Esperanto into English, you would specify “/foo/apertium-eo-en/modes/eo-en.mode” for the “--machine" option. To generate tagged text, specify path to Apertium tagger mode for your language pair, e.g. /foo/apertium-eo-en/modes/eo-en-tagger.mode. See your Apertium folder for mode names.

d.	Adding new users
To add new users, log in to the admin site at /appraise/admin and click Users -> Add user (right upper corner).

References and links
[1] https://github.com/cfedermann/Appraise/
[2] Jim O'Regan and Mikel L. Forcada (2013) "Peeking through the language barrier: the development of
a free/open-source gisting system for Basque to English based on apertium.org". Procesamiento del
Lenguaje Natural 51, 15-22.
[3] http://pip.readthedocs.org/en/latest/installing.html
[4] http://wiki.apertium.org/wiki/Installation
[5] http://wiki.apertium.org/wiki/List_of_symbols
