import argparse
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



def main():
    global GLOBAL_PAGES_PER_FILE
    parser = argparse.ArgumentParser(
    description='Converts wikipedia XML dump to list of XML Files'
    )
    parser.add_argument('input_path', help='Input directory')
    parser.add_argument('output_dir', help='Path to directory of output folders')
    args = parser.parse_args()
    input_path = args.input_path
    output_dir = args.output_dir
    today = d.datetime.now()
    unique_id = today.strftime("%Y-%m-%d-%Hh-%Mm-%Ss")
    output_path = os.path.join(output_dir, unique_id)
    os.makedirs(output_path)

    page_buffer = ""
    multi_page_buffer = ""
    buffercount = 0
    fp = open(input_path)
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
                        dump_buffer(multi_page_buffer, output_path)
                        multi_page_buffer = ""
                        buffercount = 0
                    inside = False
            else:
                page_buffer += mini_buffer
                page_buffer += char
                index = 0
                mini_buffer = ""
    if len(multi_page_buffer) != 0:
        dump_buffer(multi_page_buffer, output_path)

    fp.close()
    print_report()
    sys.exit(0)


if sys.flags.interactive:
    pass
else:
    if __name__=='__main__':
        main()
