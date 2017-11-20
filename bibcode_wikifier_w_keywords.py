#######
## Bibdoc Wikifier
## This takes a file containing json'd bib-docs, and produces a table from bibcode to a list of top titles for that bibcode.
## @author jmilbauer, jdhanoa for Hopper Project @ UChicago
## Modified to account for keywords
#######

import ahocorasick
import sys, os
import json
from core.funcs import *
import re
import argparse
import string
globalcount = 0
global anchor_df


def remove_latex(text):
    text = clean_inline_math(text)
    for match in grab_inline_math(text):
        text = text.replace(match, "")
    text = re.sub(non_capture_math, '', text)
    text = re.sub(r'\\begin\{title\}(.+?)\\end\{title\}', r'\1', text)
    text = re.sub(r'(?s)\\begin\{picture\}.+?\\end\{picture\}', '', text)
    text = re.sub(r'\\def.+', '', text)
    text = re.sub(r'\\section\*?\{(.+?)\}', r'\1', text)
    text = re.sub(r'\\def.+|\\\@ifundefined.+|(?s)\\begin\{thebibliography\}.+?\\end\{thebibliography\}|(?s)\\begin\{eqnarray\*?\}.+?\\end\{eqnarray\*?\}|\\[\w@]+(?:\[.+?\])?(?:\{.+?\})*|\[.+?\](?:\{.+?\})?|\{cm\}','', text)
    text = re.sub(r'\}', '', text)
    text = re.sub(r'\{', '', text)
    text = re.sub(r'\(\)', '', text)
    text = re.sub(r'\}', '', text)
    text = re.sub(r'\\', '', text)
    text = re.sub(r'\n{3,}', '', text)

    text = re.sub(r'\\begin\{title\}(.+?)\\end\{title\}',r'\1',text)
    text = re.sub(r'(?s)\\begin\{picture\}.+?\\end\{picture\}','',text)
    text = re.sub(r'\\def.+','',text)
    text = re.sub(r'\\section\*?\{(.+?)\}',r'\1',text)
    text = re.sub(r'\\def.+|\\\@ifundefined.+|(?s)\\begin\{thebibliography\}.+?\\end\{thebibliography\}|(?s)\\begin\{eqnarray\*?\}.+?\\end\{eqnarray\*?\}|\\[\w@]+(?:\[.+?\])?(?:\{.+?\})*|\[.+?\](?:\{.+?\})?|\{cm\}','',text)
    text = re.sub(r'\}','',text)
    text = re.sub(r'\{','',text)
    text = re.sub(r'\(\)','',text)
    text = re.sub(r'\}','',text)
    text = re.sub(r'\\','',text)
    text = re.sub(r'\n{3,}','',text)
    text = text.strip()
    return text

def get_keywords(text):
    #copy of remove_latex and modified to account for the keywords field
    #TODO: Needs further cleaning of redundant code
    text = clean_inline_math(text)
    for match in grab_inline_math(text):
        text = text.replace(match, "")
    text = re.sub(non_capture_math, '', text)
    text = re.sub(r'\\begin\{title\}(.+?)\\end\{title\}', r'\1', text)
    text = re.sub(r'(?s)\\begin\{picture\}.+?\\end\{picture\}', '', text)
    text = re.sub(r'\\def.+', '', text)
    text = re.sub(r'\\section\*?\{(.+?)\}', r'\1', text)
    text = re.sub(r'\}', '', text)
    text = re.sub(r'keywords', '', text)
    text = re.sub(r'\{', '', text)
    text = re.sub(r'\(\)', '', text)
    text = re.sub(r'\}', '', text)
    text = re.sub(r'\\', '', text)
    text = re.sub(r'\\', '', text)
    text = re.sub(r'(?<!\\)((?:\\\\)*)(\\\$)', '\1escapeddollarsign', text)
    text = re.sub(r'\\nonumber(?![A-Za-z\@\*])', '',text)
    text = re.sub(r'\\tag(?![A-Za-z\@\*])', '',text)
    text = re.sub(r'(?<!\\)&', '',text)
    remove = string.punctuation
    remove = remove.replace("-", "")
    remove = remove.replace(",", "")# don't remove hyphens
    remove = remove.replace("\'", "")
    pattern = r"[{}]".format(remove)
    text = re.sub(pattern, "", text)
    text = re.sub(r'\n{3,}', '', text)
    return text


def find_anchors_tex(file, automaton):
    global anchor_df
    global topranks
    global keywords
    global input_path
    global output_path
    ahc_automaton = automaton

    seen_anchor = dict()

    file = file.replace("./", "")
    file_path = os.path.join(input_path, file)
    print(file_path)
    print(input_path)
    print(file)

    with open(file_path, 'r', encoding='latin-1') as fh:
        text = fh.read()

    keywords = get_keywords(grab_keywords(text))
    keywords = keywords.lower().split(",")

    folder, fname = os.path.split(file_path)
    basename, ext = os.path.splitext(fname)
    output_filename = os.path.join(output_path, basename + '.keywords')
    keywords_file = open(output_filename, 'w', encoding='latin-1')
    for keyword in keywords:
        keywords_file.write(keyword.strip()+"\n")
    keywords_file.close()

    haystack = remove_latex(grab_body(text))
    with open(file_path + '.txt3', mode='w', encoding='utf-8') as fh:
        fh.write(haystack)
    fh.close()
    #print(haystack)
    article_anchors = {}  #{anchor : freq}

    for end_index, (anchor, title) in ahc_automaton.iter(haystack):
        start_index = end_index - len(anchor) + 1
        if (topranks.get(anchor)==None):
            continue
        if (article_anchors.get(anchor) != None):
            article_anchors[anchor] += 1
        else:
            article_anchors[anchor] = 1
            if (seen_anchor.get(anchor) == None):
                seen_anchor[anchor] = True
                if (anchor_df.get(anchor) != None):
                    anchor_df[anchor] += 1
                else:
                    anchor_df[anchor] = 1

    output_filename = os.path.join(output_path, basename + '.wikified')
    with open(output_filename, 'w') as fh:
        for anchor in list(article_anchors.keys()):
            fh.write("{}\t{}\t{}\t{}\t{}\n".format(basename, anchor, topranks[anchor][0], article_anchors[anchor], topranks[anchor][1]))

def pad_keyword(string):
    return " " + string + " "


def main():
    global anchor_df
    global topranks
    global automaton
    global keywords
    global input_path
    global output_path

    parser = argparse.ArgumentParser(
        description='''Takes a file containing json\'d bib docs and returns a list
    of top titles. One of either the --json or --tex flags must be specified'''
    )
    parser.add_argument('-data_path',
                        default="/Users/kriste/work/hopper/wikify/data",
                        type=str, help='Directory containing data.p and ranks.p from extractor')
    parser.add_argument('-input_path',
                        default="/Users/kriste/work/hopper/wikify/data/1000",
                        type=str, help='Directory containing articles')
    parser.add_argument('-fl',
                        default="tex",
                        type=str, help='Directory containing articles')

    parser.add_argument('-output_path',
                        default="/Users/kriste/work/hopper/wikify/data/1000/wikified",
                        type=str,
                        help='The output path should be where you want a document containing the json\'d extracted titles to be stored')

    args = parser.parse_args()
    input_path = args.input_path
    output_path = args.output_path
    data_path = args.data_path

    anchor_df = dict()
    rank_path = os.path.join(data_path, 'topranks.tsv')
    topranks = {}
    with open(rank_path, 'r') as fp:
        for line in fp:
            contents = line.split('\t')
            #contents = line.split('###TAB###')
            if len(contents) == 3:
                if (contents[0] == "dual norm"):
                    bla = ""
                anchor = pad_keyword(contents[0]).strip()
                title = contents[1]
                freq = contents[2].strip()
                topranks[anchor] = (title, freq)

    keywords = list(topranks.keys())
    print("About to run ahocorasick.autmaton")

    automaton = ahocorasick.Automaton()

    for key in keywords:
        automaton.add_word(key, (key, topranks[key][0]))  # keep in mind for mem reduction
    automaton.make_automaton()

    actual_filename = args.fl + ".fl"

    flist = []
    filelist = open(os.path.join(args.input_path, actual_filename), 'r')
    for fname in filelist.readlines():
        fname = fname.strip()

        flist.append(fname)
        find_anchors_tex(fname, automaton)

    df_out = open(os.path.join(args.data_path, str(actual_filename) + ".df"), 'w')

    for anchors in anchor_df.keys():
        df_out.write(anchors + "\t" + str(anchor_df[anchors]) + "\n")
    df_out.close()


if sys.flags.interactive:
    pass
else:
    if __name__ == '__main__':
        main()