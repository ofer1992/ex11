from CompilationEngine import CompilationEngine #TODO
import sys
import os
import glob
from os.path import isfile, join, splitext
from os import listdir

INPUT_FILE_SUFFIX = "/*.jack"
OUTPUT_FILE_SUFFIX = ".xml"


class JackAnalyzer:
    """ translate a vm file/directory to an asm file """

    def __init__(self, inputData):
        # Get files to process
        if os.path.isfile(inputData):
            self.files = [inputData]
        else:
            self.files = glob.glob(inputData + INPUT_FILE_SUFFIX)

        # engine all file
        for filePath in self.files: #TODO
            print(filePath)
            comp = CompilationEngine(filePath)
            f = open(filePath[:-5]+OUTPUT_FILE_SUFFIX,'w')
            f.write(comp.get_xml().decode())
            f.close()



def main():
    JackAnalyzer(sys.argv[1])


if __name__ == "__main__":
    main()















