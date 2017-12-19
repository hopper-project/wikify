# -*- coding: utf-8 -*-

import os
import sys
import multiprocessing as mp
import pickle
import operator
import argparse

#Pipeline:
#Directory -> [Subfiles] -> [[Pairs]] -> merge it up

# input: xml text of a given page
# output: list of (anchor, title) tuples in page
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

# returns list of (anchor, title) tuples in file
def processFile(filepath):
    fp = open(filepath)
    text = fp.read()
    fp.close()

    # anchor_title_map = [(anchor, title), ...]
    anchor_title_map = extract_links(text)
    print("Processed: {}".format(filepath))
    return anchor_title_map

def flatten_list(list):
    return [item for sublist in list for item in sublist]

# converts list of (anchor, title)
# to dict[anchor] = {title1:count1, title2:count2}
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

# converts dict[anchor] = {title1:count1, title2:count2}
# to dict[anchor] = title_with_highest_count
def build_ranking(dictionary):
    result = {} #From key to ordered list.
    for key in dictionary.keys():
        choices = dictionary[key]
        sorted_tuples = list(reversed(sorted(choices.items(), key=operator.itemgetter(1))))
        #sorted_dict = map(lambda x: x[0], sorted_tuples)
        result[key] = sorted_tuples
    return result

# def get_math_titles_list(anchor_title_map):
#     math_titles = []

#     for anchor, title_count_dict in anchor_title_map.items():
#         for title, count in title_count_dict.items():
#             math_titles.append(title.lower())

#     math_titles = list(set(math_titles))
#     return math_titles

def main():
    parser = argparse.ArgumentParser(
        description='Converts xml wikipedia dump files to maps')

    parser.add_argument('input_path',
        help='Input directory of wikipedia dump files from preprocessor.py')
    parser.add_argument('output_path',
        help='Directory to store the extracted maps')
    args = parser.parse_args()
    
    input_path = args.input_path
    output_path = args.output_path
    
    # create output dir if needed
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # list of paths for all math articles
    allfiles = os.listdir(input_path)
    allpaths = map(lambda x: os.path.join(input_path, x), allfiles)
    
    pool = mp.Pool(processes = mp.cpu_count())

    all_anchors = {}
    shallow_articles = pool.map(processFile, allpaths)

    merged_articles = flatten_list(shallow_articles) #[[(anchor, title)]] -> [(anchor, title)]
    anchor_title_map = build_hashmap(merged_articles) #[(anchor, title)] -> { anchor : {title : freq}}

    ranking = build_ranking(anchor_title_map)

    # save anchor_title_map as data.p
    dict_path = os.path.join(output_path, 'data.p')
    with open(dict_path, 'wb') as fp:
        pickle.dump(anchor_title_map, fp)

    # save the ranking dict as ranks.p
    rank_path = os.path.join(output_path, 'ranks.p')
    with open(rank_path, 'wb') as fp:
        pickle.dump(ranking, fp)

    # math_titles = get_math_titles_list(anchor_title_map)
    # # save the math titles list as math_titles.p
    # math_path = os.path.join(output_path, 'math_titles.p')
    # with open(math_path, 'wb') as fp:
    #     pickle.dump(math_titles, fp)

    pool.close()
    pool.join()


if sys.flags.interactive:
    pass
else:
    if __name__=='__main__':
        main()

