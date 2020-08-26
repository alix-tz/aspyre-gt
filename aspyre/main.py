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


DUMMY_FILE = "../data/lectaurep_dummy_v2.xml"
ALTO4SPECS = ['http://www.loc.gov/standards/alto/v4/alto.xsd',
              'http://www.loc.gov/standards/alto/v4/alto-4-0.xsd',
              'http://www.loc.gov/standards/alto/v4/alto-4-1.xsd',
              'https://gitlab.inria.fr/scripta/escriptorium/-/raw/develop/app/escriptorium/static/alto-4-1-baselines.xsd']
# for ACCEPTED_SCHEMAS in eScriptorium, see https://gitlab.inria.fr/scripta/escriptorium/-/blob/master/app/apps/imports/parsers.py#L297

ALTO2SPECS = ['http://www.loc.gov/standards/alto/ns-v2#']


def get_schema_spec(xml_tree):
    """Look for ALTO schema specification(s) in an XML document

    :param xml_tree: parsed xml tree
    :return: False if not a valid ALTO file, else the value(s) in //alto/xsi:schemaLocation as a list
    """
    schema = False
    root = xml_tree.find_all("alto")
    if len(root) == 0:
        utils.report("This is no ALTO XML file, duh!", "E")
    elif len(root) > 1:
        utils.report(f"Too many <alto> tags ({len(root)}) in this file, I'm freaking out!", "E")
    else:
        schema = root[0].attrs["xsi:schemaLocation"].split()
    return schema


def control_schema_version(schemas):
    """Control the validity of schema specification (only accept ALTO 2 or ALTO 4 specs)

    :param schemas list: list of values contained in //alto/xsi:schemaLocation
    :return: 2 if ALTO v2, 4 if ALTO v4, None otherwise
    """
    # TODO @alix: syntax is not very pythonesque...
    for spec4 in ALTO4SPECS:
        if spec4 in schemas:
            return 4
    for spec2 in ALTO2SPECS:
        if spec2 in schemas:
            return 2
    # We return None if it isn't ALTO 2 nor ALTO 4.
    # TODO @alix: do we need to look for version of another ALTO?
    utils.report("I can't handle anything else than ALTO v2 or v4!", "E")
    return None


def switch_to_v4(xml_tree):
    # TODO @alix: build this function
    utils.report("Hey, I don't know how to change the schema yet!", "W")
    utils.report("See 'def switch_to_v4()'", "W")
    # <alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.loc.gov/standards/alto/ns-v2#"
    # xmlns:page="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
    # xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v2# http://www.loc.gov/standards/alto/alto.xsd">
    # changing to
    # <alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.loc.gov/standards/alto/ns-v4#"
    # xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v4# http://www.loc.gov/standards/alto/v4/alto-4-0.xsd">
    return xml_tree



def main():
    xml_tree = utils.read_file(DUMMY_FILE, 'xml')
    schemas = get_schema_spec(xml_tree)
    if schemas:
        utils.report(f"Schema Specs: {schemas}", "H")
        alto_version = control_schema_version(schemas)
        if alto_version:
            utils.report(f"Detected ALTO version: v{alto_version}", "H")
        if alto_version == 2:
            utils.report("Buckle up, we're fixing the schema declaration!", "H")
            xml_tree = switch_to_v4(xml_tree)
        # TODO @alix: is there a //Description/sourceImageInformation/fileName? No? Well, fix it!
        # TODO @alix: what do you mean you don't know where to find the filename?
        # TODO @alix: is there any weird layout, like a 'composedBlock' for example? That might be a problem...
        # TODO @alix: do we need the tag declaration? (cf. /alto/Tags/otherTags)
        # TODO @alix: do we need to remove the Margin declaration and the OCRProcessingStep info?
        # specifically, see: /alto/Description/OCRProcessingStep
        #               and: /alto/Layout/Page/TopMargin|LeftMargin|RightMargin|BottomMargin
        # It might be an idea to just keep the //TextLine as long as their ID start with "line_"
        # If they start with TableCell_, they should become region (maybe?)
        # And if they start with Table_, they don't need to stay (maybe?)
        # There'll be some test import to do with eScriptorium at that point anyway.
        # But let's keep in mind that if we just want to import the data into eScriptorium to train a segmenter
        #     really we only need the TextLine and their baseline, we could remove the rest. Just sayin'
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



