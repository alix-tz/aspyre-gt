#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT PROGRAM

author: Alix Chagué
date: 26/08/2020
"""

import argparse
import os

from aspyrelib import aspyre
from aspyrelib.utils import utils as utils


parser = argparse.ArgumentParser(description="Aspyre is a program transforming ALTO XML files exported from Transkribus (ALTO 2.x) to make them compatible with eScriptorium (ALTO 4.x)")
parser.add_argument('-i', '--source', action='store', nargs=1, default=[False], help='Location of the Transkirbus Export directory')
parser.add_argument('-o', '--destination', action='store', nargs=1, default=[False], help='Location where resulting files should be stored (path to an existing directory)')
parser.add_argument('-t', '--talktome', action='store_true', help="Will display highlighted messages if activated")
parser.add_argument('-m', '--mode', action='store', nargs=1, default='default', help="default|test")
# parser.add_argument('-m', '--mode', action='store', nargs=1, default='test', help="default|test")
args = vars(parser.parse_args())

# start main task
if args['mode'].lower() == 'test':
    pass
elif args['mode'].lower() == 'default':
    aspyre_report = aspyre.main(orig_source=args['source'][0], orig_destination=args['destination'][0], talktome=args['talktome'])
    utils.report(f"report:{aspyre_report}")
else:
    utils.report(f"{args['mode']} is not a valid mode", "E")



