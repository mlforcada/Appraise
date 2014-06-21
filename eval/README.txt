To use the task generator, you should have the following files in one folder:
- gaps.py
- kw_gen.py
- similar_words.py
- tag_pairing.py
- text_generator.py

You should also have the following text files in the same directory:
- reference.txt, which contains reference translation and from which the words will be removed;
- tag.txt, which contains the tagged version of reference.txt, obtained from apertium-tagger;
- original.txt, which contains the original untranslated text and
- (optionally) machine.txt, which is original.txt translated through Apertium, 
  if you wish to give the evaluators machine translation for support.
  
The text files should have the same number of sentences (because they are the same text).

To make the tasks, run gaps.py. You can specify the following options in-file:
- keyword (bool) - if True, the program tries to determine and remove significant words, 
  if False, it will remove words at random;
- pos (a list of Apertium pos tags) - if you want to remove any specific parts of speech, specify them here;
- gap_density (0-1) - a float from 0 to 1 which determines the percentage of gaps to be created;
- relative_density (bool) - if True, the keywords will be determined and then the specified percentage
  of those will be taken out, if False - the gap density will be calculated against the number of words 
  in the original text (but not more than the number of keywords found if keyword is True);
- multiple_choice or lemmas (bool) - specifies the task mode. If multiple choice is True, 
  a choice of options is given for each gap. If lemmas is True, a word lemma is left in each gap to help 
  the evaluator. If both are False, no help is given;
- mt (bool) specifies whether or not to give machine translation as assistance.

After you run gaps.py, files task.txt and keys.txt will be generated. To check the answers, 
run text_checker.py with task.txt and keys.txt in the same directory. The structure of task.txt should 
be unchanged, we assume that the evaluators only change the words in brackets. For testing purposes, 
if on task generation both multiple_choice and lemmas are False, the script will not remove correct 
answers from the gaps, so the task.txt can be fed to the checking module without any modifications.
