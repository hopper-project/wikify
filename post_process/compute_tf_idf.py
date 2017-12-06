#######
## Compute precision and recall
## @author kriste.krstovski @ Columbia
#######

from core.funcs import *
import argparse
import numpy as np
import pickle


def main():


    parser = argparse.ArgumentParser(
    description='''Reads .wikified files and computes tf-idf values using document frequency statistics from the article and Wikipedia colleciton''')
    parser.add_argument('-work_dir',
                        default="/Users/kriste/work/hopper/wikify/data/1000/84articles",
                        type=str, help='Directory containing data.p and ranks.p from extractor')
    parser.add_argument('-fl',
                        default="84wikified.fl",
                        type=str, help='Directory containing articles')
    parser.add_argument('-wiki_df',
                        default="/Users/kriste/work/hopper/wikify/data/para_document_AT_count_dict.pkl",
                        type=str, help='Directory containing articles')
    parser.add_argument('-article_df',
                        default="84articles.fl.df",
                        type=str, help='Directory containing articles')

    args = parser.parse_args()

    #read article based document frequencies
    df_file = open(os.path.join(args.work_dir,args.article_df),'r')

    df = dict()
    for line in df_file.readlines():
        line = line.strip()
        elem = line.split("\t")
        article_id = elem[0]
        df_val = int(elem[1])
        df[article_id]=df_val
    df_file.close()

    fl_file = open(os.path.join(args.work_dir, args.fl), 'r')

    #read wikipedia based document frequencies:
    input_file = open(args.wiki_df, "rb")
    wiki_df = pickle.load(input_file, encoding='latin1')


    # read discovered wikipedia anchor text and concepts
    for line in fl_file.readlines():
        line = line.strip()
        wiki_file = open(os.path.join(args.work_dir,line),'r')
        article_tf = 0
        article_wtf=0
        for line2 in wiki_file.readlines():
            elem = line2.split("\t")
            article = elem[0]
            anchor = elem[1]
            concept = elem[2]
            article_fc = int(elem[3])
            wiki_fc = int(elem[4])
            article_tf+=article_fc
            article_wtf+=wiki_fc
            article_df = df[anchor]
        wiki_file.close()

        #open file list for reading
        wiki_file = open(os.path.join(args.work_dir, line), 'r')
        wiki_file_out = open(os.path.join(args.work_dir, line + ".tf-idf"), 'w')

        #go over each file and compute tf-idf for each wikipedia concept
        for line2 in wiki_file.readlines():
            line2 = line2.strip()
            elem = line2.split("\t")
            article = elem[0]
            anchor = elem[1]
            if (len(anchor)<4):
                continue
            concept = elem[2]
            article_fc = int(elem[3])
            wiki_fc = int(elem[4])
            adf = df[anchor]
            if (wiki_df.get(anchor)==None):
                continue
            wdf = wiki_df[anchor]
            #Compute article (aidf) and Wikipedia (widf) collection based idfs:
            aidf = np.round(np.log(1000.0 / adf),4)
            widf =np.round(np.log(64000.0 / wdf),4)

            tf = np.round(article_fc*1.0/article_tf,4)
            wtf = np.round(wiki_fc * 1.0 / article_wtf, 4)

            tf_aidf = np.round(tf*aidf,4)
            wtf_widf = np.round(wtf * widf, 4)

            #Experiment with various tf-idf combinations:
            new = article_fc*wtf_widf
            new2 = tf_aidf*wtf_widf
            new3 = tf * wtf_widf
            '''
            adf = "---"
            aidf = "---"
            tf_aidf = "---"
            article_df ="---"
            '''
            wiki_file_out.write(line2+"\t"+str(article_df)+"\t"+str(tf)+"\t"+str(aidf)+"\t"+str(widf)+"\t"+str(tf_aidf)+"\t"+str(wtf_widf)+"\t"+str(new)+"\t"+str(new2)+"\t"+str(new3)+"\n")
        wiki_file.close()
        wiki_file_out.close()

if __name__=='__main__':
    main()
