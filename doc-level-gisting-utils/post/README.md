# Appraise results postprocessing

This README does not correspond yet to the actual code — working on it

## filter_results.py

This file will be invoked by the s2.bash shell described below. It reads an XML results file downloaded from Appraise and extracts the records corresponding to a specific user in CSV format.

``` 
usage: filter_results.py [-h] inputfile user

positional arguments:
  inputfile   Input XML file exported from Appraise
  user        Select records from this user

optional arguments:
  -h, --help  show this help message and exit
```

## s2.bash

This file reads a file (results) in which each line contains the name of an XML results file and the name of the informant for whom results will be extracted and generated a single results.csv file (and a .bsv version of it). Then, the code looks at specific results and computes average scores, standard deviations and statistical significance tests.

It assumes 4 systems: NONE, Yandex, Google and Apertium. There is some legacy code that is useless for these experiments and which should be removed.

It is called without arguments.

## sigtest.py

This file is called by s2.bash to compute statistical significance results, namely a Welch t-test and a Kolmogorov-Smirnov test.
