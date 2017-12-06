#######
## Compute precision and recall
## @author kriste.krstovski @ Columbia
#######


import argparse
import numpy as np
import os

def main():
    parser = argparse.ArgumentParser(description='''Takes as an input a list of sorted .tf-idf files.
    The code assumes that tf-idf files generated from the compute_tf_idf.py step have been sorted.
    For each article it uses its set of keywords (stored in a .keywords) to compute precision and recall.
    Here is an example on how to sort based on the 10th column which contains the tf-aidf values:'
    >ls *.tf-idf > 84tf_idf.fl
    >cat 84tf_idf.fl | awk '{print "sort -t$\047\\t\047 -k10 -nr " $0 " > " $0 ".s10"}' | bash
    >ls *.s10 > ./84tf_idf_sorted.fl
    ''')
    parser.add_argument('-work_dir',
                        default="/Users/kriste/work/hopper/wikify/data/1000/84articles",
                        type=str, help='Directory containing data.p and ranks.p from extractor')
    parser.add_argument('-fl',
                        default="84tf_idf_sorted.fl",
                        type=str, help='Directory containing articles')

    args = parser.parse_args()

    pos_rel = 10

    fl_file = open(os.path.join(args.work_dir, args.fl), 'r')
    #Summary file for storing precision and recall values:
    fl_file_out = open(os.path.join(args.work_dir, args.fl+".rel_res"), 'w')

    total_overal_recall=0.0
    total_recall = 0.0
    total_precision = 0.0
    num_files=0
    for line in fl_file.readlines():
        num_files+=1
        line = line.strip()
        filename = line.split(".wikified")[0]

        rel_dict = read_relevant(os.path.join(args.work_dir,filename+".keywords"))
        total_rel = len(rel_dict.keys())

        wiki_file = open(os.path.join(args.work_dir, line), 'r')
        wiki_file_out = open(os.path.join(args.work_dir, line+".rel"), 'w')

        num_rel_at_point =0
        num_rel = 0
        count=0
        file_concept_covered =dict()
        for line2 in wiki_file.readlines():
            count+=1
            line2 = line2.strip()
            elem = line2.split("\t")
            article = elem[0]
            anchor = elem[1]
            concept = elem[2]
            wiki_fc = elem[3]
            article_fc = int(elem[4])
            article_df = elem[5]
            tf = elem[6]
            idf = elem[7]
            tf_idf = elem[8]

            if (rel_dict.get(concept)!=None):
                if (file_concept_covered.get(concept)==None):
                    file_concept_covered[concept]=True
                    wiki_file_out.write(str(count)+"\t"+line2+"\n")
                    num_rel+=1
                    if (count<=pos_rel):
                        num_rel_at_point+=1
        wiki_file.close()
        wiki_file_out.close()
        recall = np.round(num_rel_at_point*1.0/total_rel,4)
        total_recall+=recall
        precision = np.round(num_rel_at_point*1.0/pos_rel,4)
        total_precision+=precision
        overall_recall = np.round(num_rel * 1.0 / total_rel, 4)
        total_overal_recall+=overall_recall
        fl_file_out.write(filename + "\t" + str(num_rel) +"\t"+str(total_rel)+"\t"+str(precision)+"\t"+str(recall)+"\t"+str(overall_recall)+"\t"+str(count)+"\n")

    avg_precision = np.round(total_precision/num_files,4)
    avg_recall = np.round(total_recall/num_files,4)
    avg_overall_recall = np.round(total_overal_recall/num_files,4)
    fl_file_out.write("SUMMARY\t---\t---\t"+str(avg_precision)+"\t"+str(avg_recall)+"\t"+str(avg_overall_recall)+"\t---\n")
    fl_file_out.close()

def read_relevant(file):
    rel_dict = dict()

    rel_fl = open(file,'r', encoding='latin1')

    for line in rel_fl.readlines():
        line = line.strip()
        #elem = line.split("\t")
        #concept = elem[0]
        #freq = int(elem[1])
        concept = line
        #if (freq>1):
        #    rel_dict[concept]=freq
        rel_dict[concept]=1
    rel_fl.close()
    return rel_dict

if __name__=='__main__':
    main()
