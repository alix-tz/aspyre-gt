#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT PROGRAM

author: Alix Chagué
date: 26/08/2020
"""

import argparse

from bs4 import BeautifulSoup
import tqdm

from utils import utils


def main():
    # TODO @ alix: well, write the program, no?
    # TODO @ alix: open XML file
    # TODO @ alix: identify XML ALTO version (make sure it's ALTO 2
    # TODO @ alix: verify that there are all the info we need in the file
    # TODO @ alix: to magiv to transform this ALTO 2 into ALTO 4 escriptorium compatible
    # TODO @ alix: aka change schema declaration
    # TODO @ alix: aka add filename
    # TODO @ alix: and stuff...
    pass


# ============================================================================================================
parser = argparse.ArgumentParser(description="How much wood would a wood chop chop in a wood chop could chop wood?")
parser.add_argument('-m', '--mode', action='store', nargs=1, default='default', help="default|test")
# parser.add_argument('-m', '--mode', action='store', nargs=1, default='test', help="default|test")
args = parser.parse_args()

if vars(args)['mode'].lower() == 'test':
    pass
elif vars(args)['mode'].lower() == 'default':
    main()
else:
    utils.report(f"{vars(args)['mode']} is not a valid mode", "E")



