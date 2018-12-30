# SPDX-License-Identifier: MIT

import os
import sys

import shutil
import argparse

def processFile(input, config, args):
    """
    Given an input PDF document, the configuration information and the standard argument object,
    process the document.
    """


def processInput(input, args):
    """
    Given an input path and the standard argument object, load the relevant config
    file and then process each input file.
    """
    print(input, args)

    # Load a config file

    # Find and process each PDF file


if __name__ == "__main__":
    # Locate default config file
    df = os.path.realpath(__file__)
    defConfig = os.path.dirname(df) + os.sep + "config.json"

    # Locate default pdftotext
    pdftotext = shutil.which('pdftotext')
    if pdftotext is None:
        if sys.platform == "win32":
            pdftotext = "pdftotext.exe"
        else:
            pdftotext = "pdftotext"

    # Get command line arguments
    parser = argparse.ArgumentParser(description='Automatic PDFtoText and refiling of scanned PDF documents')

    parser.add_argument('--config', required=False, default=defConfig,
                        help='The confguration file to use if there isn\'t one in the input')
    parser.add_argument('--p2t', required=False, default=pdftotext,
                        help='The location of pdttotext if not in the default path')

    parser.add_argument('input', nargs='+',
                        help='An input folder of material to process')
    parser.add_argument('--output', required=False,
                        help='The output folder to use')

    args = parser.parse_args()

    if not os.path.isfile(args.p2t):
        print("Cannot find pfdtotext [%s], try using --p2t\n" % (args.p2t))
        exit(1)

    for i in args.input:
        processInput(i, args)

# End