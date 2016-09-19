#!/usr/bin/env python 2

##############
## Anchor-Title Index Tester
## Written by Jeremiah Milbauer for The Hopper Project @ UChicago
## Version: August 4, 2016
#######
## This program is licensed under the most recent version of CC-BY-SA
#######
## This program runs on a dataset of extracted ranks and indices
## It produces a wikipedia article when given a phrase
##############

import os
import sys
import cPickle as pickle

#TODO: make the queries streamlined: have it take a text file where each line is a query.

def main(data_path):
#    dict_path = os.path.join(data_path, 'data.p')
    rank_path = os.path.join(data_path, 'ranks.p')
 #   dict_handle = open(dict_path, 'rb')
    rank_handle = open(rank_path, 'rb')
  #  master_dictionary = pickle.load(dict_handle)
    ranks = pickle.load(rank_handle)
   # dict_handle.close()
    rank_handle.close()

    #total_anchors = len(master_dictionary.keys())
    #print("There are a total of {} anchors.".format(total_anchors))

    while True:
        user_input = raw_input("> ").lower()
        if user_input == "quit()":
            sys.exit(0)
        else:
            if user_input in ranks.keys():
                all_choices = ranks[user_input]

                top_choice = all_choices[0]
                other_choices = all_choices[1:10]

                print("The top choice was:")
                print("\t {}, occurences: {}".format(top_choice[0], top_choice[1]))
                print("The other options were:")
                for choice in other_choices:
                    print("\t {}, occurences: {}".format(choice[0], choice[1]))

            else:
                print("No appropriate titles found.")

    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        data_path = sys.argv[1]
    else:
        sys.stderr.write("Usage : python {} data_path\n"
                         "\t* The data path should be a directory containing the pickled files data.p and ranks.p\n".format(sys.argv[0]))
        sys.exit(1)
    main(data_path)
