#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Project: Appraise evaluation system
 Author: Mikel Forcada <mlf@ua.es>


[Modification started MLF 20170323, based on existing code by
Christian Federmann for import_wmt14_xml.py]

usage: python import_valgist.py
               [-h] [--wait SLEEP_SECONDS] [--dry-run] 
               task-file [task-file ...]

Imports one from a given XML file into the Django database. 

Will use appraise.eval.validatordocgisting.validate_task_xml_file() for validation
positional arguments:
  tasks-file             XML file(s) containing tasks. Can be multiple files
                        using patterns such as '*.xml' or similar.

optional arguments:
  -h, --help            Show this help message and exit.
  --wait SLEEP_SECONDS  Amount of seconds to wait between individual files.
  --dry-run             Enable dry run to simulate import.


"""
from time import sleep 
import argparse
import os
import sys
from django.core.exceptions import SuspiciousOperation

from xml.etree.ElementTree import fromstring, tostring

PARSER = argparse.ArgumentParser(description="Imports one-item tasks from a given " \
  "XML file into the Django database.\nUses appraise.eval.validatordocgisting." \
  "validate_task_xml_file() for validation.")
PARSER.add_argument("task_file", metavar="task-file", help="XML file(s) " \
  "containing one-item tasks.  Can be multiple files using patterns such as '*.xml' " \
  "or similar.", nargs='+')
PARSER.add_argument("--wait", action="store", default=5, dest="sleep_seconds",
  help="Amount of seconds to wait between individual files.", type=int)
PARSER.add_argument("--dry-run", action="store_true", default=False,
  dest="dry_run_enabled", help="Enable dry run to simulate import.")


if __name__ == "__main__":
    args = PARSER.parse_args()
    
    # Properly set DJANGO_SETTINGS_MODULE environment variable.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    # Do I need this?
    PROJECT_HOME = os.path.normpath(os.getcwd() + "/..")
    sys.path.append(PROJECT_HOME)

    # I have to change this to import the right code
    # We have just added appraise to the system path list, hence this works.
    # Oh well, there is a problem related to settings.
    from appraise.evaluation.models import EvaluationTask, validate_source_xml_file #, EvaluationItem
    # Was: from appraise.wmt14.models import HIT
    from eval.validatordocgisting import validate_task_xml_file # seems to work
    # Was: from appraise.wmt14.validators import validate_hits_xml_file
    
    # We might potentially be dealing with more than a single input file.
    first_run = True
    for _task_file in args.task_file:
        if not first_run and args.sleep_seconds > 0:
            print 'Waiting {0} second(s)'.format(args.sleep_seconds),
            for i in range(args.sleep_seconds):
                print ' .',
                sys.stdout.flush()
                sleep(1)
            print
            print
        
        else:
            first_run = False
        
        task_xml_string = None
        with open(_task_file) as infile:
            task_xml_string = unicode(infile.read(), "utf-8")
        
        # Validate XML before trying to import anything from the given file.
        validate_task_xml_file(task_xml_string) # working?
    
        _errors = 0
        _total = 0
        _tree = fromstring(task_xml_string.encode("utf-8"))
        
        task_id = _tree.attrib["id"]
        language_pair = '{0}2{1}'.format(_tree.attrib["source-language"],
             _tree.attrib["target-language"])
        if args.dry_run_enabled:
                    _ = EvaluationTask(task_id=task_id, task_xml=_task_file)
            
        else:
                    t = EvaluationTask(task_id=task_id, task_xml=_task_file)
                    try:  # trying to catch the exception
                       t.save()
                    except SuspiciousOperation as e :
					   print e
        
         
#        for _child in _tree:        
#            task_id = _child.attrib["id"]
        
            # Hotfix potentially wrong ISO codes;  we are using ISO-639-3.
            # iso_639_2_to_3_mapping = {'cze': 'ces', 'fre': 'fra', 'ger': 'deu'}
            # for part2_code, part3_code in iso_639_2_to_3_mapping.items():
            #    language_pair = language_pair.replace(part2_code, part3_code)
        
#            try:
#                _total = _total + 1
#                _task_xml = tostring(_child, encoding="utf-8").decode('utf-8')
          
                # This code to be checked to use EvaluationTask, etc.
                # Are all relevant parameters for EvaluationTask OK?
#                if args.dry_run_enabled:
#                    _ = EvaluationTask(task_id=task_id, task_xml=_task_xml,
#                      language_pair=language_pair)
            
#                else:
                    # Use get_or_create() to avoid exact duplicates?
                    # This code to be checked to use  EvaluationTask, etc
#                    t = EvaluationTask(task_id=task_id, task_xml=_task_xml,
#                      language_pair=language_pair)
#                    t.save()
        
            # pylint: disable-msg=W0703
#            except Exception, msg:
#                print msg
#                _errors = _errors + 1
    
        print
        print '[{0}]'.format(_task_file)
        print 'Successfully imported {0} tasks, encountered errors for ' \
          '{1} tasks.'.format(_total, _errors)
        print
