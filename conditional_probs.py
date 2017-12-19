# -*- coding: utf-8 -*-
import pickle
from tqdm import tqdm
import argparse
import sys
import os

# Calculates the conditional probabilities of anchor text given title text

def main():
    parser = argparse.ArgumentParser(
        description='''Calculates the conditional probability of \
            anchor text given title text''')
    
    parser.add_argument('data_path', 
            help='Directory containing data.p from extractor')
    parser.add_argument('output_path',
            help='The output path should be where pickle of \
            conditional probabilities should be stored')

    args = parser.parse_args()

    data_path = os.path.join(args.data_path, 'data.p')
    output_path = args.output_path

    # create output dir if needed
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print('reading data.p')

    with open(data_path, 'r') as f:
        # maps anchor text to (dict mapping titles to counts 
        #   of anchor-title mapping)
        data_dict = pickle.load(f)

    print('constucting empty title_anchor_dict')

    # maps titles to (dict mapping anchors to counts)
    title_anchor_dict = {}

    for v in tqdm(data_dict.values()):
        for t in v.keys():
            title_anchor_dict[t] = {}

    print('filling in title_anchor_dict with anchor counts')

    for anchor, v in tqdm(data_dict.items()):
        for t, count in v.items():
            title_anchor_dict[t][anchor] = title_anchor_dict[t].get(anchor, 0) + count

    print('normalizing counts in title_anchor_dict')

    i = 0
    for title, v in tqdm(title_anchor_dict.items()):
        total_count = sum(list(v.values()))

        for anchor, count in v.items():
            title_anchor_dict[title][anchor] = 1.0*title_anchor_dict[title][anchor]/total_count

            if i % 20000 == 0:
                print(title, anchor, title_anchor_dict[title][anchor], total_count)
            i += 1

    print('saving title_anchor_dict to pickle file')
    # dict giving the conditional prob of anchor text
    #   given title text
    # dict[title][anchor] = P(anchor | title)
    output_path = os.path.join(output_path, 'cond_prob_anchor_given_title.p')
    with open(output_path, 'wb') as f:
        pickle.dump(title_anchor_dict, f)

if sys.flags.interactive:
    pass
else:
    if __name__=='__main__':
        main()










