# wikify

Prerequisites: Python 3.4+, pyahocorasick (pip3 install pyahocorasick)

This folder and its associated scripts can be used for the following pipeline:

* Processing of wikipedia (preprocessor.py)
    * Input: Wikipedia XML dump
    * Output: Extracted XML dumps of math articles
* Generation of metadata (extractor.py)
    * Input: XML dumps generated by preprocessor.py
    * Output: data.p, ranks.p
* Generation of topranks.tsv file (repickler.py)
    * Input: Directory containing data.p
    * Output: topranks.tsv
* Bibdoc wikification (bibdoc_wikifier.py)
    * Input: Directory containing topranks.tsv, LaTeX files
    * Output: One correspondingly named TSV/document containing conceptually relevant article titles from Wikipedia, and corresponding metrics (see bibdoc_wikifier.py for details)
