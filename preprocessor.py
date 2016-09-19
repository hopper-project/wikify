#!/usr/bin/env python 2

##############
## Anchor-Title Index Preprocessor
## Written by Jeremiah Milbauer for Hopper Project @ UChicago
## Version: June 14, 2015
#######
## This program runs on a dataset of raw wikipedia files (in XML format)
## It produces a large number of xml files for all of wikipedia
##############
## Thursday: Have things preprocessed, fix the extractor.
## Run the extractor on half of the preprocessor.
#######

import datetime as d
import os
import sys

GLOBAL_PAGES_PER_FILE = 10
GLOBAL_MULTI_FILE_BUFFER = "" #rework the main to move multifile functionality into dump_buffer
GLOBAL_DUMP_INDEX = 0
GLOBAL_TOTAL_PAGES = 0
GLOBAL_SCIENCE_PAGES = 0


#takes an input file, reads through, and breaks it into output files of 100
# articles each.
def main(i_path, o_path):
    global GLOBAL_PAGES_PER_FILE

    page_buffer = ""#"<bunch>" #This will contain up to 100 pages, all placed together in one file.
    multi_page_buffer = ""
    buffercount = 0

    fp = open(i_path)

    header = "<page>"
    footer = "</page>"
    index = 0
    inside = False
    mini_buffer = ""
    page_read_cycler = 0


    while True:
        if page_read_cycler == 1000:
            print_report()
            page_read_cycler = 0
        char = fp.read(1)
        if not char:
            break
        if not inside:
            if char == header[index]:
                index += 1
                mini_buffer += char
                if mini_buffer == header:
                    page_buffer += mini_buffer
                    index = 0
                    mini_buffer = ""
                    inside = True
            else:
                index = 0
                mini_buffer = ""
        else:
            if char == footer[index]:
                index += 1
                mini_buffer += char
                if mini_buffer == footer:
                    page_buffer += mini_buffer
                    index = 0
                    mini_buffer = ""
                    if sci_check(page_buffer):
                        multi_page_buffer += page_buffer
                        buffercount += 1
                    page_buffer = ""
                    page_read_cycler += 1
                    if buffercount >= GLOBAL_PAGES_PER_FILE:
                        #print(multi_page_buffer)
                        dump_buffer(multi_page_buffer, o_path)
                        multi_page_buffer = ""
                        buffercount = 0
                    inside = False
            else:
                page_buffer += mini_buffer
                page_buffer += char
                index = 0
                mini_buffer = ""
    if len(multi_page_buffer) != 0:
        dump_buffer(multi_page_buffer, o_path)

    fp.close()
    #
    # wikipedia = fp.read()
    # soup = BeautifulSoup(wikipedia)
    # fp.close()
    #
    # all_articles_xml = soup.find_all('page')
    # for page_xml in all_articles_xml:
    #     if pagetype_check(page_xml) and sci_check(page_xml):
    #         page_buffer += page_xml.prettify()
    #         buffercount += 1
    #     if buffercount == 100:
    #         dump_buffer(page_buffer, o_path)
    #         buffercount = 0
    # dump_buffer(page_buffer, o_path)
    print_report()
    sys.exit(0)

def print_report():
    fp = open("report.txt", 'a')
    global GLOBAL_TOTAL_PAGES
    global GLOBAL_SCIENCE_PAGES
    fp.write("With {} pages scanned, {} math pages found.".format(GLOBAL_TOTAL_PAGES, GLOBAL_SCIENCE_PAGES))

#Dumps the contents of that buffer, with a few alterations, into the target path.
def dump_buffer(buffer_contents, target_path):
    global GLOBAL_DUMP_INDEX
    page_dump = "<bunch>" + buffer_contents + "</bunch>"
    dump_name = "dump_number-" + str(GLOBAL_DUMP_INDEX) + ".xml"
    GLOBAL_DUMP_INDEX += 1
    file_path = os.path.join(target_path, dump_name)
    print("dumping to: " + file_path)
    fp = open(file_path, 'w')
    fp.write(page_dump)
    fp.close()
    return

#This is a filter to determine if the page is an article, disambiguation, etc.
#Returns a boolean :/
def pagetype_check(file_xml):
    return True

#This is a filter to determine if the article is appropriately technical

def sci_check(file_xml):
    global GLOBAL_TOTAL_PAGES
    global GLOBAL_SCIENCE_PAGES
    if "&lt;math&gt;" in file_xml:
        GLOBAL_TOTAL_PAGES += 1
        GLOBAL_SCIENCE_PAGES += 1
#        print("Found science page.")
        return True
    else:
        GLOBAL_TOTAL_PAGES += 1
        return False

if __name__ == '__main__':
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_dir = sys.argv[2] #directory of output directories.
    else:
        sys.stderr.write("Formatting/Usage error.\n")
        sys.exit(1)

    today = d.datetime.today()
    unique_id = today.strftime("%Y-%m-%d-%Hh-%Mm-%Ss") #for some reason my syntax highlighting makes the 'h' seem like a format char.
    output_path = os.path.join(output_dir, unique_id)
    os.mkdir(output_path)

    main(input_path, output_path)
