#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT CLI

author: Alix Chagué
date: 19/03/2021
"""

import argparse
import os

from aspyrelib.aspyre import (AspyreArgs, TkbToEs, PdfaltoToEs, LimbToEs)
from aspyrelib.utils import utils as utils


parser = argparse.ArgumentParser(description="Aspyre is a program transforming files to make them compatible" +
                                             "with eScriptorium Import XML module")
parser.add_argument('-i', '--source', action='store', nargs=1, required=True,
                    help='Location of the source files')
parser.add_argument('-sc', '--scenario', action='store', nargs=1, required=True,
                    help='Determines which transformation scenario will be applied' +
                         '(tkb|limb|finereader|pdfalto)')
parser.add_argument('-o', '--destination', action='store', nargs=1, default=[False],
                    help='Location where resulting files should be stored' +
                         '(path to an existing directory)')
parser.add_argument('-t', '--talktome', action='store_true',
                    help="Will display highlighted messages if activated")
parser.add_argument('-vp', '--vpadding', action='store', nargs=1, type=int, default=[0],
                    help='[PDFALTO, LIMB] adjust vertical coordinates' +
                         '(value will be added to textline and string VPOS attr)')
parser.add_argument('-m', '--mode', action='store', nargs=1, default='default',
                    help="default|test")
args = vars(parser.parse_args())

# basic controls:
if int(args['vpadding'][0]) != 0 and not args['scenario'][0] in ['pdfalto', 'limb']:
    utils.report('vpadding option is only valid for PDFALTO and LIMB scenarios\n---', 'W')


# start main task
if args['mode'].lower() == 'test':
    pass
elif args['mode'].lower() == 'default':
    aspyre_args = AspyreArgs(scenario=args['scenario'][0], source=args['source'][0],
                             destination=args['destination'][0], talkative=args['talktome'],
                             vpadding=args['vpadding'][0])
    if aspyre_args.proceed():
        if aspyre_args.scenario == 'tkb':
            transfo = TkbToEs(aspyre_args)
        elif aspyre_args.scenario == "pdfalto":
            transfo = PdfaltoToEs(aspyre_args)
        elif aspyre_args.scenario == "limb":
            transfo = LimbToEs(aspyre_args)
    if args['talktome']:
        utils.report(f"Displaying execution log (status: {aspyre_args.execution_status}):", "I")
        for entry in aspyre_args.log:
            utils.report(entry, "I")
else:
    utils.report(f"{args['mode']} is not a valid mode", "E")



