import sys
import os
import pickle
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Generates topranks.tsv file from ranks.p file')
    parser.add_argument('input_path',
        help='Path to directory containing ranks.p')

    args = parser.parse_args()
    input_path = args.input_path

    # open ranks.p
    rank_path = os.path.join(input_path, 'ranks.p')
    with open(rank_path, 'rb') as fh:
        ranks = pickle.load(fh)

    # create topranks.tsv file
    tsv_path = os.path.join(input_path, 'topranks.tsv')
    
    with open(tsv_path, 'w') as fh:
        counter = 0
        
        # key = article
        for key in ranks.keys():
            if counter != 0:
                topchoice = ranks[key][0]
                toptitle = topchoice[0]
                topfreq  = topchoice[1]

                # write article, title, freq
                fh.write("{}\t{}\t{}\n".format(key, toptitle, topfreq))
                
                if counter % 10000 == 0:
                    print('rows processed = ', counter)
            counter += 1

if sys.flags.interactive:
    pass
else:
    if __name__=='__main__':
        main()
