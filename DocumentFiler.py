# SPDX-License-Identifier: MIT

import os
import sys

import json
import shutil
import argparse

def processFile(input, config, args):
    """
    Given an input PDF document, the configuration information and the standard argument object,
    process the document.
    """

    print(input)
    print(config)
    print(args)
    return

def loadConfig(path):
    """
    Load a JSON document containing configuration data.
    Existance of file should already have been checked
    """
    with open(path) as f:
        data = json.load(f)
    return data

def processInput(input, args):
    """
    Given an input path and the standard argument object, load the relevant config
    file and then process each input file.
    """

    if not os.path.isdir(input):
        print("Error: No such folder [%s]\n" % (input))
        return None

    # Load a config file
    if os.path.isfile(input + os.sep + "config.json"):
        config = loadConfig(input + os.sep + "config.json")
    elif 'config' in args and os.path.isfile(args['config']):
        config = loadConfig(args['config'])
    else:
        print("Warning: Can\'t find a config for [%s]\n" % (input))
        config = {}
    
    # Find and process each PDF file
    for path, dirs, files in os.walk(input):
        print(path)
        for f in files:
            if f.endswith(".pdf"):
                processFile(os.path.join(path,f), config, args)

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
        processInput(i, vars(args))

# End