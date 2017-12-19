import os
import argparse
import pickle
from tqdm import tqdm
import multiprocessing as mp
import sys

# Prunes topranks.tsv to only contain math articles as title text

# returns the first 2 lines of a wikipedia XML file
def processes_file(file):
    with open(file) as f:
        line1, line2 = next(f), next(f)
    return (line1, line2)

# returns the first 2 lines of all mathpages
def get_mathpage_list(splices_path):
    math_files = os.listdir(splices_path)    
    allpaths = map(lambda x: os.path.join(splices_path, x), math_files)

    pool = mp.Pool(processes = mp.cpu_count())
    lines = pool.map(processes_file, allpaths)
    pool.close()
    pool.join()

    return lines

# returns a list of all math_titles
def get_math_titles(splices_path, math_titles_path):
    if os.path.exists(math_titles_path):
        with open(math_titles_path, 'rb') as f:
            return pickle.load(f)

    lines = get_mathpage_list(splices_path)

    count_dict = {}
    math_titles = []
    for line in lines:
        # count_dict not used in pipeline but is useful for analysis
        title = line[1].strip().replace('<title>','').replace('</title>','').lower()

        count_dict[title] = count_dict.get(title, 0) + 1
        math_titles.append(title)

    with open(math_titles_path, 'wb') as f:
        pickle.dump(math_titles, f)

    return math_titles

def open_mathpage_titles(splices_path):
    with open(path, 'rb') as f:
        math_titles = pickle.load(f)
        
    math_titles = set([title.lower() for title in math_titles])
    return math_titles

# returns list of all titles in topranks.tsv
def get_topranks_titles(input_path):
    with open(input_path, 'r') as f:
        lines = f.readlines()

    top_titles = []

    for line in lines:
        line = line.split('\t')
        if len(line) != 3:
            continue
        top_titles.append(line[1])

    return top_titles

def analyze_pruned_list(math_titles, input_path, analysis_path):
    top_titles = get_topranks_titles(input_path)
    print(len(top_titles), 'titles from topranks.tsv')

    hit_titles = []
    miss_titles = []

    math_titles = set(math_titles)

    for title in tqdm(top_titles):
        if title in math_titles:
            hit_titles.append(title)
        else:
            miss_titles.append(title)

    # hit_titles = 64572
    # miss_titles = 952631
    print(len(hit_titles), 'titles were math titles and will be saved in pruned_topranks.tsv')
    print(len(miss_titles),'titles were *not* math titles and will be discarded from pruned_topranks.tsv')

    if not os.path.exists(analysis_path):
        os.makedirs(analysis_path)

    with open(os.path.join(analysis_path, 'hit_titles.p'), 'wb') as f:
        pickle.dump(hit_titles, f)

    with open(os.path.join(analysis_path, 'hit_titles.txt'), 'wb') as f:
        f.write('\n'.join(hit_titles))

    with open(os.path.join(analysis_path, 'miss_titles.p'), 'wb') as f:
        pickle.dump(miss_titles, f)
        
    with open(os.path.join(analysis_path, 'miss_titles.txt'), 'wb') as f:
        f.write('\n'.join(miss_titles))

def main():
    parser = argparse.ArgumentParser(
        description='Prune topranks.tsv to only contain math articles as title text')

    parser.add_argument('input_path',
        help='Directory containing topranks.tsv from extractor')
    parser.add_argument('splices_path', 
            help='Directory containing XML wikipedia pages')
    parser.add_argument('analysis_path',
            help='The path where files for analysis should be saved')

    args = parser.parse_args()

    topranks_path = os.path.join(args.input_path, 'topranks.tsv')
    splices_path = args.splices_path
    analysis_path = args.analysis_path
    
    math_titles_path = os.path.join(args.input_path, 'math_titles.p')
    pruned_topranks_path = os.path.join(args.input_path, 'pruned_topranks.tsv')

    print('getting list of all math_titles')
    # construct list of math titles
    math_titles = get_math_titles(splices_path, math_titles_path)
    
    print('analysing which titles will be pruned')
    analyze_pruned_list(math_titles, topranks_path, analysis_path)

    print('\npruning topranks to only contain math titles')
    with open(topranks_path, 'r') as f:
        lines = f.readlines()

    # list to save lines that will go into pruned_top_titles
    pruned_topranks_lines = []
    math_titles = set(math_titles)

    for line in tqdm(lines):
        line_list = line.split('\t')

        if len(line_list) != 3:
            continue

        if line_list[1] in math_titles:
            pruned_topranks_lines.append(line)

    with open(pruned_topranks_path, 'w') as f:
        for title in pruned_topranks_lines:
            f.write(title)

if sys.flags.interactive:
    pass
else:
    if __name__=='__main__':
        main()





