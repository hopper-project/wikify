import time
import sys
import os
import pickle
import argparse

def main():
    parser = argparse.ArgumentParser(description='Save\
            only math articles from Wikipedia dump')

    parser.add_argument('input_path', 
        help='Path to directory containing Wikipedia dump')
    parser.add_argument('output_path',
        help='Path to directory where math articles should be saved')

    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # stream through the file
    # save each math page to file
    # save counts of total pages, math pages and so on statistics

    math_page_count = 0
    page_count = 1

    start_time = time.time()

    with open(input_path) as f:
        # start parsing dump line by line
        for l1 in f:
            # ignore all lines until a page start is reached
            if l1 == '  <page>\n':
                # initialize variables for this page
                math_page_flag = 0
                page_buffer = []

                page_buffer.append(l1)

                # parse till the end of this page
                for l2 in f:
                    page_buffer.append(l2)

                    # if contains the opening tag for math
                    if '&lt;math' in l2:
                        math_page_flag = 1

                    # if the end of the page is reached
                    # stop parsing
                    if l2 == '  </page>\n':
                        page_count += 1
                        break

                # if page just parsed was a math page
                if math_page_flag:
                    # tested saving every page isn't appreciably slower
                    fname = output_path + '/file_number_'+str(math_page_count)+'.xml'
                    
                    with open(fname, 'w') as op_fd:
                        op_fd.write(''.join(page_buffer))

                    math_page_count += 1

                    # reset page buffer
                    page_buffer = []

                if page_count % 1000 == 0:
                    print(page_count, 'pages parsed in', time.time() - start_time, \
                        'seconds')
                    start_time = time.time()

    print(page_count, 'pages parsed of which', math_page_count, 'were math pages')

if sys.flags.interactive:
    pass
else:
    if __name__=='__main__':
        main()


