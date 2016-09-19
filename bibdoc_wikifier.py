#######
## Bibdoc Wikifier
## This takes a file containing json'd bib-docs, and produces a table from bibcode to a list of top titles for that bibcode.
## @author jmilbauer for Hopper Project @ UChicago
#######

import cPickle as pickle
import ahocorasick
import sys, os
import json

globalcount = 0

def find_anchors(json_file_path, output_path, anchor_list, topranks, ahc_automaton):
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

def main(data_path, input_path, output_path):
    rank_path = os.path.join(data_path, 'topranks.tsv')
    topranks = {}
    with open(rank_path, 'r') as fp:
        for line in fp:
            contents = line.split('\t')
            if len(contents) == 3:
                anchor = pad_keyword(contents[0])
                title = contents[1]
                freq = contents[2]
                topranks[anchor] = (title, freq)

    keywords = topranks.keys()
    automaton = ahocorasick.Automaton()
    for key in keywords:
        automaton.add_word(key, (key, topranks[key][0])) #keep in mind for mem reduction
    automaton.make_automaton()

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
    #     all_anchors += path_anchors
    #
    # result = {}
    # for anchor in all_anchors:
    #     title = topranks[anchor][0]
    #     print("Found: {}, Incrementing: {}".format(anchor, title))
    #     if title in result.keys():
    #         result[title] += 1
    #     else:
    #         result[title] = 1
    sys.exit(0)

#get to the point where we can read the json bodies
#test ahc, on a simple string; you can just copy-paste a body into the script.
        #measure the time for loading ahc, time for loading topranks.
#combine them
#article -> [relevant substrings] (substr that are keys)
#[relevant substrings] -> [top title for each]

# don't need to load the whole hashmap
# we should chunk arxiv articles
    #

#tsv:
#       bibcode \t anchor \t anchorfreq \t title \t title freq

        # 1       2           3   4           5
        # 101010  math        20  mathematics 4905
        # 101010  arithmetic  10  mathematics 300




if __name__ == '__main__':
    if len(sys.argv) == 4:
        data_path = sys.argv[1]
        input_path = sys.argv[2]
        output_path = sys.argv[3]
    else:
        sys.stderr.write("Usage : python {} data_path input_path output_path\n"
                         "\t* The data path should be a directory containing data.p and ranks.p from the extractor\n"
                         "\t* The input path should be a directory containing the json'd tables of articles\n"
                         "\t* The output path should be where you want a document containing the json'd extracted titles to be stored\n".format(sys.argv[0]))
        sys.exit(1)
    all_anchors = {}
    main(data_path, input_path, output_path)
