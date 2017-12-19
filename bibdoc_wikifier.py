import pickle
import ahocorasick
import sys, os
import json
import shutil
from core.funcs import *
import re
import argparse

globalcount = 0
prob_threshold = 0.1

def remove_latex(text):
    text = clean_inline_math(text)
    for match in grab_inline_math(text):
        text = text.replace(match, "")
    text = re.sub(non_capture_math, '', text)
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
    return text

def get_anchor_title_prob(anchor, title, title_anchor_dict):
    anchor = anchor.strip()

    # check p(anchor|title) > prob_threshold
    if title in title_anchor_dict:
        if anchor in title_anchor_dict[title]:
            return round(title_anchor_dict[title][anchor], 2)
    return 'NaN Prob'


def find_anchors_tex(input_file_path, output_path):
    global topranks
    global keywords
    global automaton
    global title_anchor_dict
    ahc_automaton = automaton

    if not input_file_path.endswith('.tex'):
        print('empty return!!')
        return

    with open(input_file_path,'r') as fh:
        text = fh.read()

    haystack = text

    # construct {anchor : freq}
    article_anchors = {} 
    for end_index, (anchor, title) in ahc_automaton.iter(haystack):
        start_index = end_index-len(anchor)+1
        if anchor in set(article_anchors.keys()):
            article_anchors[anchor] += 1
        else:
            article_anchors[anchor] = 1

    folder, fname = os.path.split(input_file_path)
    basename, ext = os.path.splitext(fname)
    output_path = os.path.join(output_path, os.path.splitext(fname)[0]+'.tsv')
    
    print(input_file_path, output_path)

    skip_list = []
    haystack_list = haystack.split()

    with open(output_path, 'w') as fh:
        # print original text with in-body wikified title
        for anchor in list(article_anchors.keys()):
            # mapping: topranks[anchor] = (title, freq)
            title = topranks[anchor][0]
            anchor_title_freq = topranks[anchor][1]
            anchor_freq = article_anchors[anchor]

            anchor = anchor.strip()
            prob = str(get_anchor_title_prob(anchor, title, title_anchor_dict))

            op_str = '*('+ anchor + ', ' + title + ', ' + prob + ')*'

            haystack_list = map(lambda x: op_str if x == anchor else x, haystack_list)

        # print(' '.join(haystack_list))
        fh.write(' '.join(haystack_list))

        # print columns
        fh.write('\n\n\nbasename, anchor, anchor_freq_in_doc,  title,   anchor_title_freq, prob\n')

        for anchor in list(article_anchors.keys()):
            # mapping: topranks[anchor] = (title, freq)
            title = topranks[anchor][0]
            anchor_title_freq = topranks[anchor][1].strip()
            anchor_freq = article_anchors[anchor]

            anchor = anchor.strip()

            prob = get_anchor_title_prob(anchor, title, title_anchor_dict)
            
            # Keep if prob above threshold
            if prob >= prob_threshold:
                # print('kept:', title, anchor, title_anchor_dict[title][anchor])

                # basename, anchor, anchor_freq, title, anchor-title freq, prob
                fh.write("{}\t{}\t   {}\t\t{}\t{}\t{}\n".format(basename, anchor,
                        anchor_freq, title, anchor_title_freq, prob))

            # Skip if below prob_threshold
            else:
                skip_list.append((basename, anchor, anchor_freq,
                                    title, anchor_title_freq, prob))
                # print('skipped:', title, anchor, prob)
                continue
               
        fh.write('\n_________pairs below threshold_________\n')

        for item in skip_list:
            basename, anchor, anchor_freq, title, anchor_title_freq, prob = item
            anchor = anchor.strip()

            fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(basename, anchor,
                    anchor_freq, title, anchor_title_freq, prob, 2))


def find_anchors(json_file_path, output_path, anchor_list, topranks,
                                                     ahc_automaton):
    if not json_file_path.endswith('.json'):
        return
    filename = os.path.basename(json_file_path)
    #os.path .up().down().enter("...")
    output_file_path = output_path + filename + '.a-t.tsv'
    jsons = []
    path_anchors = []
    with open(json_file_path, 'r') as fp:
        for line in fp:
            jsons += (json.loads(line))
#    print(len(jsons))

    #good up to here

    fp = open(output_file_path, 'w')
    #fp.close()
    # fp = open(output_file_path, 'a')
    js_counter = 0
    for article in jsons:
        global globalcount
        js_counter += 1
        globalcount += 1
        if (globalcount % 5000 == 0):
            print("{} bibdocs processed.".format(globalcount))

        bibcode = article["bibcode"]
        if "body" not in article.keys():
            fp.write("{}\tnone\tnone\tnone\tnone".format(bibcode))
            continue #do not execute following code in loop.

        abstract = article["abstract"]
        body = article["body"]

        haystack = body.encode('utf8', 'ignore') #convert the unicode from json into ascii so pyahocorasick can read it

        article_anchors = {} #{anchor : freq}

        for end_index,(anchor,title) in ahc_automaton.iter(haystack):
            start_index = end_index - len(anchor) + 1
            if anchor in article_anchors.keys():
                article_anchors[anchor] += 1
            else:
                article_anchors[anchor] = 1
            assert haystack[start_index:start_index + len(anchor)] == anchor
            assert title == topranks[anchor][0]

        for anchor in article_anchors.keys():
            fp.write("{}\t{}\t{}\t{}\t{}".format(bibcode, anchor, article_anchors[anchor], topranks[anchor][0], topranks[anchor][1]))

    #print("{} jsons".format(js_counter))
    fp.close()

def pad_keyword(string):
    return " " + string + " "

def load_cond_prob_dict(path):
    print('loading conditional prob dict')

    with open(path, 'rb') as f:
        title_anchor_dict = pickle.load(f)

    print('done loading title_anchor_dict')
    return title_anchor_dict

def main():
    global topranks
    global automaton
    global keywords
    global title_anchor_dict

    parser = argparse.ArgumentParser(
        description='''Takes a file containing json\'d bib docs and returns a list
        of top titles. One of either the --json or --tex flags must be specified''')
    
    parser.add_argument('data_path', 
            help='Directory containing data.p and ranks.p from extractor')
    parser.add_argument('cond_prob_path',
            help='Path to anchor given title conditional probs pickle file')
    parser.add_argument('input_path',
            help='Directory containing articles to be wikified')
    parser.add_argument('output_path',
            help='The output path should be where you want wikified input files to be stored')

    parser.add_argument('--json', action='store_true',
            help='Specifies if the input is a JSON of articles')
    parser.add_argument('--tex', action='store_true',
            help='Specifies if the input is a folder of .tex files',)
    
    args = parser.parse_args()
    input_path = args.input_path
    cond_prob_path = args.cond_prob_path
    output_path = args.output_path
    data_path = args.data_path

    title_anchor_dict = load_cond_prob_dict(cond_prob_path)

    # parse topranks.tsv
    topranks = {}
    rank_path = os.path.join(data_path, 'pruned_topranks.tsv')
    with open(rank_path, 'r') as fp:
        for line in fp:
            contents = line.split('\t')
            if len(contents) == 3:
                anchor = pad_keyword(contents[0])
                title = contents[1]
                freq = contents[2]
                topranks[anchor] = (title, freq)

    # constructing ahocorasick automaton
    keywords = list(topranks.keys())
    automaton = ahocorasick.Automaton()
    for key in keywords:
        automaton.add_word(key, (key, topranks[key][0])) #keep in mind for mem reduction
    automaton.make_automaton()    

    if args.tex:
        flist = []

        for root, folders, files in os.walk(input_path):
            for fname in files:
                if fname.endswith('.tex'):
                    flist.append(os.path.join(root, fname))

        for f in flist:
            find_anchors_tex(f, output_path)

    elif args.json:
        allfiles = os.listdir(input_path)
        allpaths = map(lambda x: os.path.join(input_path, x), allfiles)
        bibcode_map = {} #{bibcode : [(title, freq)]}

            #freq will represent the TOTAL occurences of an anchor that mapped to the appropriate title

        fp2 = open('bibdoc_wikifier_log.txt', 'w')
        for path in allpaths:
            fp2.write("About to process {}".format(path))
            find_anchors(path, output_path, keywords, topranks, automaton)
            fp2.write("\tCompleted {}\n".format(path))
        fp2.close()
       
    else:
        print("Error: Must choose either tex or json flag")

if sys.flags.interactive:
    pass
else:
    if __name__=='__main__':
        main()

