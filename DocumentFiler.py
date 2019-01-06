# SPDX-License-Identifier: MIT

import os
import sys

import json
import shutil
import argparse
import re

from pprint import pprint

from subprocess import call

def dayToInt(d):
    return int(d)

def monthToInt(m):
    months = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "0ct": 10, # OCR error
        "nov": 11,
        "dec": 12
    }

    k = m[:3].lower()

    if k in months:
        return months[k]
    return None

def yearToInt(y):
    y = int(y)

    if y < 70:
        y = 2000 + y
    if y < 100:
        y = 1900 + y

    return y

def processFile(input, config, args):
    """
    Given an input PDF document, the configuration information and the standard argument object,
    process the document.
    """
    filebase, _ = os.path.splitext(input)

    txtFile = filebase + ".txt"

    call([args['p2t'], "-layout", "-nopgbrk", input, txtFile])

    with open(txtFile,'r') as f:
        s = f.read()

    # Date first
    # Various formats, which will undoubedly need adding to later

    md = None
    date = ""

    mdt = re.search(r'(([1-3]?[0-9])((th)|(nd)|(rd)|(st))?)[ -/]*'
                     '((January)|(February)|(March)|(April)|(May)|(June)|(July)|(August)|(September)|((O|0)ctober)|(November)|(December))[ -/]*'
                     '((20|19)[0-9][0-9])', s, re.IGNORECASE)

    if mdt is not None:
        if (md is None) or (mdt.start() < md.start()):
            md = mdt
            date = "%04d-%02d-%02d" % (yearToInt(md.group(22)), monthToInt(md.group(8)), dayToInt(md.group(2)))

    mdt = re.search(r'(([1-3]?[0-9])((th)|(nd)|(rd)|(st))?)[ -/]*'
                     '((Jan)|(Feb)|(Mar)|(Apr)|(May)|(Jun)|(Jul)|(Aug)|(Sep)|((O|0)ct)|(Nov)|(Dec))[ -/]*'
                     '((20|19)?[0-9][0-9])', s, re.IGNORECASE)

    if mdt is not None:
        if (md is None) or (mdt.start() < md.start()):
            md = mdt
            date = "%04d-%02d-%02d" % (yearToInt(md.group(22)), monthToInt(md.group(8)), dayToInt(md.group(2)))

    mdt = re.search(r'([0-3]?[0-9])/([0-1]?[0-9])/(((19[6789])|(20[012]))[0-9])'
                    , s, re.IGNORECASE)

    if mdt is not None:
        if (md is None) or (mdt.start() < md.start()):
            md = mdt
            date = "%04d-%02d-%02d" % (int(md.group(3)), int(md.group(2)), dayToInt(md.group(1)))

    if date == "":
        print("Warning: Unable to process file [%s], leaving text file for reference" % (input))
        return None

    # Company second
    # Then account number third

    if 'companiesRegexp' in config:

        m = re.search(config['companiesRegexp'], s, re.IGNORECASE)

        if m is not None:
            company = config['companiesMatch'][m.group(0).lower()]

            c = config['companies'][company]

            account = ""
            if 'accounts' in c:
                l = []
                m = {}

                for a in c['accounts']:
                    for n in c['accounts'][a]:
                        m = re.search(n, s, re.IGNORECASE)
                        if m is not None:
                                account = a
                            
        else:
            company = "Unknown"
            account = ""
    else:
        company = ""
        account = ""

    if 'output' in args and args['output'] is not None:
        # Make the directories
        p = args['output']
        if not company == "":
            p = os.path.join(p, company)
            if not os.path.exists(p):
                os.mkdir(p)
        if not account == "":
            p = os.path.join(p, account)
            if not os.path.exists(p):
                os.mkdir(p)

        # Then pick a suffix to avoid overwrites
        suffix = 1
        filename = ""
        while True:
            filename = os.path.join(p, "%s-%04d.pdf" % (date, suffix))
            if not os.path.exists(filename):
                break
            suffix = suffix + 1
        
        # And we are done
        shutil.move(input, filename)
        
    else:
        print("Would move %s -> <output>/%s/%s/%s-%04d.pdf" % (input, company, account, date, 1))

    os.remove(txtFile)

    return

def expandCompanies(data):
    if 'companies' in data:
        l = []
        data['companiesMatch'] = {}

        for n in data['companies']:
            l.append("(" + n + ")")
            data['companiesMatch'][n.lower()] = n
            if 'aliases' in data['companies'][n]:
                for a in data['companies'][n]['aliases']:
                    data['companiesMatch'][a.lower()] = n
                    l.append("(" + a + ")")

        r = "(" + "|".join(l) + ")"
        data['companiesRegexp'] = r

    return data

def loadConfig(path):
    """
    Load a JSON document containing configuration data.
    Existance of file should already have been checked
    """
    with open(path) as f:
        data = json.load(f)

    data = expandCompanies(data)
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
    for path, _, files in os.walk(input):
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