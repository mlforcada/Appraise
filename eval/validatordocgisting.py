# -*- coding: utf-8 -*-
"""
Project: Appraise evaluation system
 Author: Mikel L. Forcada <mlf@ua.es>
 Based on Appraise code by Author: Christian Federmann <cfedermann@gmail.com>
"""

import logging

from xml.etree.ElementTree import Element, fromstring, ParseError

from django.core.exceptions import ValidationError

from appraise.settings import LOG_LEVEL, LOG_HANDLER  

# Setup logging support.
logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger('eval.validator_docgisting')
LOGGER.addHandler(LOG_HANDLER)


TASK_REQUIRED_ATTRIBUTES = (
  'id', 'source-language', 'target-language'
)


def validate_task_xml_file(value):
    """
    Validates the given tasks XML source value.
    
    The given value can either be an XML string or an ElementTree.
    
    """
    # First, we try to instantiate an ElementTree from the given value.
    try:
        if isinstance(value, Element):
            _tree = value
        
        else:
            _tree = fromstring(value.encode("utf-8"))
        
        # Then, we check that the top-level tag name is <hits>.
        assert(_tree.tag == 'set'), 'expected <set> on top-level'
        
        # Check that all children are valid <seg> elements (only one in principle)
        for _child in _tree:
            validate_segment_xml(_child)
    
    except (AssertionError, ParseError), msg:
        raise ValidationError('Invalid XML: "{0}".'.format(msg))

        
    return value


def validate_segment_xml(value, require_systems=False):
    """
    Checks that the given segment XML value contains all required elements.
    
    These are:
    - one <source> element;
    - one <reference> element; and
    - five <translation> elements.
    
    The given value can either be an XML string or an ElementTree.
    
    """
    try:
        if isinstance(value, Element):
            _tree = value
        else:
            _tree = fromstring(value)

        if not _tree.tag == 'seg':
            raise ValidationError('Invalid XML: illegal tag: "{0}".'.format(
              _tree.tag))
        
        assert(len(_tree.findall('source')) == 1), \
          'exactly one <source> element expected'
        
        assert(_tree.find('source').text is not None), \
          'missing required <source> text value'
        
        assert(len(_tree.findall('reference')) == 1), \
          'exactly one <reference> element expected'
        
        assert(_tree.find('reference').text is not None), \
          'missing required <reference> text value'
        
        assert(len(_tree.findall('translation')) == 1), \
          'exactly one <translation> element expected'
        
        for _translation in _tree.iterfind('translation'):
            assert(_translation.text is not None), \
              'missing required <translation> text value'
            if require_systems:
                assert('system' in _translation.attrib.keys()), \
                  'missing "system" attribute on <seg> level'

       # Perhaps other attributes should be validated, but we'll leave that for later
    
    except (AssertionError, ParseError), msg:
        raise ValidationError('Invalid XML: "{0}".'.format(msg))
    
