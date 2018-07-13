#!/usr/bin/env python
# check_sigs.py - EnergyWolf 2016
# Take a file path as argument, and check it for known file
# signatures using www.filesignatures.net

# pickling the signatures file makes subsequent look ups
# significantly faster

import os
import urllib
import json
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from bs4 import BeautifulSoup

# the {} will be used to dynamically enter different ints with .format()
URL = "http://www.filesignatures.net/index.php?page=all&currentpage={}"
PATH = 'sigs.json'
signatures = [] # contains all (signatures, descriptions)

def compile_sigs():
    ''' Compile the list of file signatures '''
    global signatures, PATH

    if not os.path.exists(PATH):
        for i in range(19): # 19 pages of signatures on the site
            response = urllib.request.urlopen(URL.format(i))
            html = response.read() # get the html as a string

            soup = BeautifulSoup(html, "lxml") # parse the source

            t_cells = soup.find_all("td", {"width": 236}) # find td elements with width=236
            for td in t_cells:
                # append (signature, description) to signatures
                sig = str(td.get_text()).replace(' ', '').lower() # strip spaces, lowercase
                desc = str(td.find_next_sibling("td").get_text())
                signatures.append([sig, desc])

        # pickle them sigs
        with open(PATH, 'w') as f:
            json.dump(signatures, f)

    else:
        with open(PATH, 'rb') as f:
            signatures = json.load(f)


def check_sig(fn):
    ''' Hex dump the file and search for signatures '''

    p = Popen(['xxd', '-p', fn], stdout=PIPE) # get plain(-p) hex dump of the file
    dump = p.communicate()[0]           # execute and extract stdout

    res = []

    for sig, desc in signatures:
        if sig in dump:
            res.append([sig, desc, dump.find(sig)])

    return res # [(sig, desc, offset), (sig, desc, offset), ... etc.]


# script really starts here
if __name__ == "__main__":

    compile_sigs()

    parser = ArgumentParser()
    parser.add_argument("file_path", help="Detect signatures in file at this path")

    args = parser.parse_args()

    print("[*] Checking File for Known Signatures")
    print("[*] This may take a moment...")

    
    results = check_sig(args.file_path)

    if results:
        results.sort(key=lambda x: x[2]) # sort results by offset in file
        # find longest signature, and desc for output formatting purposes
        big_sig = len(max([i[0] for i in results], key=lambda x: len(x)))
        big_desc = len(max([i[1] for i in results], key=lambda x: len(x)))

        print("\n[*] File Signature(s) detected:\n")
        for sig, desc, offset in results:
            print("[+] {0:<%ds} : {1:<%d} {2:<20s}" % (big_sig, big_desc)).format(
                sig, desc, "<- Offset: "+str(offset))
    else:
        print("\n[!] No File Signature Detected.\n")
