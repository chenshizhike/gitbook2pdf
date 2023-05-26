import sys
from gitbook2pdf import Gitbook2PDF

def usage() :
    print("usage : python gitbook.py <url|file path> [pdfname]")

if __name__ == '__main__':
    if len(sys.argv) == 3 :
        fname = sys.argv[2]
        url = sys.argv[1]
    elif len(sys.argv) == 2 and sys.argv[1] != "--help" :
        fname = None
        url = sys.argv[1]
    else :
        usage()
        exit(0)
        
    Gitbook2PDF(url,fname).run()
