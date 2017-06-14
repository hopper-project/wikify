import sys
import os
import pickle
import argparse

def main():
    parser = argparse.ArgumentParser(
    description='Generates topranks.tsv file from ranks.p file'
    )
    parser.add_argument('input_path',
    help='Path to directory containing ranks.p')

    parser.add_argument('output_path',
    help='Path to topranks.tsv output directory')

    args = parser.parse_args()
    data_path = args.input_path
    output_path = args.output_path

    rank_path = os.path.join(data_path, 'ranks.p')
    with open(rank_path, 'rb') as fh:
        ranks = pickle.load(fh)

    tsv_path = os.path.join(output_path, 'topranks.tsv')
    with open(tsv_path, 'w') as fh:
        counter = 0
        for key in ranks.keys():
            if not counter==0:
                topchoice = ranks[key][0]
                toptitle = topchoice[0]
                topfreq  = topchoice[1]
                fh.write("{}\t{}\t{}\n".format(key, toptitle, topfreq))
                if counter % 1000 == 0:
                    print(counter)
            counter += 1
    sys.exit(0)

if sys.flags.interactive:
    pass
else:
    if __name__=='__main__':
        main()
