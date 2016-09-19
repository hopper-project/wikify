#!/usr/bin/env python 2
# -*- coding: utf-8 -*-

import os
import sys
import multiprocessing as mp
import cPickle as pickle
import operator

#Pipeline:
#Directory -> [Subfiles] -> [[Pairs]] -> merge it up

def extract_links(text):
    results = []

    searching = True
    inside = False
    firstpart = False
    secondpart = False
    index = 0
    matcher_index = 0
    header = "[["
    footer = "]]"
    divider = "|"

    title_buffer = ""
    anchor_buffer = ""
    mini_buffer = ""

    while True:
        if index >= len(text):
            break
        char = text[index].lower()
        index += 1
        if not inside:
            if char == header[matcher_index]:
                matcher_index += 1
                if matcher_index == len(header):    #if we get the whole header
                    inside = True
                    firstpart = True
                    secondpart = False
                    matcher_index = 0
            else:
                matcher_index = 0
        elif inside:
            if char == footer[matcher_index]:
                matcher_index += 1
                if matcher_index == len(footer):
                    inside = False
                    firstpart = False
                    secondpart = False
                    matcher_index = 0

                    if len(anchor_buffer) < 1:
                        anchor_buffer = title_buffer
                    results.append((anchor_buffer, title_buffer))
                    anchor_buffer = ""
                    title_buffer = ""

            else:
                matcher_index = 0
                if char == divider:
                    firstpart = False
                    secondpart = True
                else:
                    if firstpart:
                        title_buffer += char
                    if secondpart:
                        anchor_buffer += char

    return results

def processFile(filepath):
    fp = open(filepath)
    text = fp.read()
    fp.close()
    anchor_title_map = extract_links(text)
    print("Processed: {}".format(filepath))
    return anchor_title_map

def flatten_list(list):
    return [item for sublist in list for item in sublist]

def build_hashmap(pairs):
    #print(pairs)
    result = {}
    for pair in pairs:
        result[pair[0]] = {}
        #print(result)
    for pair in pairs:
        result[pair[0]][pair[1]] = 0
        #print(result)
    for pair in pairs:
        result[pair[0]][pair[1]] += 1
    #print(result)
    return result

def build_ranking(dictionary):
    result = {} #From key to ordered list.
    for key in dictionary.keys():
        choices = dictionary[key]
        sorted_tuples = list(reversed(sorted(choices.items(), key=operator.itemgetter(1))))
        #sorted_dict = map(lambda x: x[0], sorted_tuples)
        result[key] = sorted_tuples
    return result

def main(input_path, output_path):
    allfiles = os.listdir(input_path)
    allpaths = map(lambda x: os.path.join(input_path, x), allfiles)

    pool = mp.Pool(processes=mp.cpu_count())
    shallow_articles = pool.map(processFile, allpaths) #returns a list from mapping.

    #shallow_articles = map(processFile, allpaths)   #[path] -> [[(anchor, title)]]
    merged_articles = flatten_list(shallow_articles) #[[(anchor, title)]] -> [(anchor, title)]
    anchor_title_map = build_hashmap(merged_articles) #[(anchor, title)] -> { anchor : {title : freq}}

    ranking = build_ranking(anchor_title_map)

    #STORE THE MASTER DICTIONARY
    dict_path = os.path.join(output_path, 'data.p')
#    print(anchor_title_map)
    fp = open(dict_path, 'wb')
    pickle.dump(anchor_title_map, fp)
    fp.close()
    #STORE THE RANKING
    rank_path = os.path.join(output_path, 'ranks.p')
#    print(ranking)
    fp = open(rank_path, 'wb')
    pickle.dump(ranking, fp)
    fp.close()

    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        sys.stderr.write("Usage : python {} input_path output_path\n"
                         "\t* The input path should be a directory containing the xml wikipedia dump files of type \"pages-articles\"\n"
                         "\t* The output path should be where you want the extracted maps to be stored.\n".format(sys.argv[0]))
        sys.exit(1)
    all_anchors = {}
    main(input_path, output_path)
