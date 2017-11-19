# Appraise results postprocessing

## filter_results.py

This file will be invoked by the s2.bash shell described below. It reads an XML results file downloaded from the status of a job in Appraise and extracts the records corresponding to a specific user (informant) in CSV format.

``` 
usage: filter_results.py [-h] inputfile user

positional arguments:
  inputfile   Input XML file exported from Appraise
  user        Select records from this user

optional arguments:
  -h, --help  show this help message and exit
```

## s2.bash

This file reads a file (called "results") in which each line contains the name of an XML results file and the name of the informant for whom results will be extracted, as in

```
exported-task-job000-2017-06-27.xml inf000
exported-task-job001-2017-07-02.xml  inf060
exported-task-job002-2017-06-27.xml inf002
exported-task-job003-2017-07-04.xml inf003
[...]
```
and generates a single results.csv file (and a blank-seprated values or .bsv version of it). Then, the code looks at specific results and computes average scores, standard deviations and statistical significance tests. The results file has to be generated by hand at the moment.

It assumes 5 systems: NONE, Bing, Google, Moses and Apertium (this is hardwired, and related to the CREG corpus prepared
by Scarton and Specia (LREC 2016). 

It is called without arguments.

## sigtest.py

This file is called by s2.bash to compute statistical significance results, namely a Welch t-test and a Kolmogorov-Smirnov test.

## iaa.py

This file reads the results.csv file and generates Pearson correlations among the scores obtained by informants. All of 
the parameters for this particular experiment (60 informants, with informants i, 20+i and 40+i dealing with the same set
of problems) are hardwired.
