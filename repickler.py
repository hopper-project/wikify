import sys
import os
import cPickle as pickle

def main(data_path, output_path):
    rank_path = os.path.join(data_path, 'ranks.p')
    rank_handle = open(rank_path, 'rb')
    ranks = pickle.load(rank_handle)
    rank_handle.close()

    tsv_path = os.path.join(output_path, 'topranks.tsv')
    tsv_handle = open(tsv_path, 'a')

    counter = 0
    for key in ranks.keys():
        if not counter == 0:
            topchoice = ranks[key][0]
            toptitle = topchoice[0]
            topfreq = topchoice[1]
            tsv_handle.write("{}\t{}\t{}\n".format(key, toptitle, topfreq))
            if counter % 1000 == 0:
                print(counter)
        counter += 1

    tsv_handle.close()

    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print("argument count error")
        sys.exit(1)
    main(input_path, output_path)