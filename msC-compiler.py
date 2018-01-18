from msc import *
from argparse import ArgumentParser
from libs.parse import *
import re

def removeComments(text):
    text = re.sub(
       '(?:\\/\\*(?=(?:[^"]*"[^"]*")*[^"]*$)(.|\\n)*?\\*\\/)|(?:\\/\\/(?=(?:[^"]*"[^"]*")*[^"]*$).*)', 
       '', 
       text
    )
    return text

    
def compileString(fileText):
    fileBlock = TopBlock(removeComments(fileText))

def compileFile(filepath):
    with open(filepath, 'r') as f:
        return compileString(f.read())

def main(args):
    for file in args.files:
        b = compileFile(file)

if __name__ == "__main__":
    with open('test.c', 'r') as f:
        t = f.read()
        print(t+'\n\n')
        print(removeComments(t))
    parser = ArgumentParser(description="Compile msC to MSC bytecode")
    parser.add_argument('files', metavar='files', type=str, nargs='+',
                        help='files to compile')
    main(parser.parse_args())