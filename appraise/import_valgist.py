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

    from appraise.evaluation.models import EvaluationTask #, validate_source_xml_file #, EvaluationItem
    # from eval.validatordocgisting import validate_task_xml_file # not used
    
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
        # validate_task_xml_file(task_xml_string) # working?
    
        _errors = 0
        _total = 0
        _tree = fromstring(task_xml_string.encode("utf-8"))

        task_id = _tree.attrib["id"]		
        # needed? Not passed on yet ****TODO*****        
        language_pair = '{0}2{1}'.format(_tree.attrib["source-language"],
             _tree.attrib["target-language"])
        if args.dry_run_enabled:
             _ = EvaluationTask(task_xml=_task_file, task_name=task_id, task_type="7")
        else:
			        # making the task_name equal to the task_id
             t = EvaluationTask(task_xml=_task_file, task_name=task_id, task_type="7")
             try:  # trying to catch the exception
                 _total=_total + 1
                 t.save()
             except Exception, msg:
                print msg
                _errors = _errors + 1
            
        print
        print '[{0}]'.format(_task_file)
        print 'Successfully imported {0} tasks, encountered errors for ' \
          '{1} tasks.'.format(_total, _errors)
        print
	
