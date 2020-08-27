#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT PROGRAM

author: Alix Chagué
date: 26/08/2020
"""

import argparse
import os

from bs4 import BeautifulSoup
import tqdm

from utils import utils


DUMMY_FILE = "..\data\lectaurep_dummy_v2.xml"
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


def get_image_filename(xml_filename, mode='manual'):
    """Get the value that will be added in //Description/sourceImageInformation/fileName (image filename)

    :param filename str: name of the XML ALTO file
    :param mode str: default if based on XML filename, csv if based on an external mapping
    :return str: image file name (None if sth went wrong)
    """
    # TODO @alix: CSV mode needs to become the default behavior, and then there will be a manual option
    # TODO @alix: add parameter for the location of the mapping file
    utils.report("Hey, there's some serious improvement to make in 'def get_image_filename()'!", "W")
    value = None
    if mode != 'manual' and mode != 'csv':
        utils.report(f"I'll switch to default, I don't know mode '{mode}'.", "W")
        mode = 'manual'
    if mode == 'csv':
        # TODO @alix: add an option to use a csv file to map an XML ALTO file with the corresponding image filename
        # For now, we switch to manuel as default
        utils.report(f"I don't know yet how to handle csv mode, I'll switch to default.", "W")
        mode = 'manual'
    # eventually this will become an elif statement
    if mode == 'manual':
        # there is no way to know what is the extension of the image file...
        utils.report("Remember to re-enable the manual input for file extension in 'def get_image_filename()'", "W")
        extension = "dummy"  # this won't stay!
        #extension = input("What is the extension of the original image file? [png|jpeg|jpg|tif] > ")
        value = xml_filename.split(os.sep)[-1].replace(".xml", f".{extension.lower()}")
        utils.report(f"'{value}' will be added to //Description/sourceImageInformation/fileName", "S")
    return value


def add_sourceimageinformation(xml_tree):
    """Create a <sourceImageInformation> component in <Description> with the corresponding metadata

    :param xml_tree: ALTO XML tree
    :return: None
    """
    image_filename = get_image_filename(DUMMY_FILE)
    src_img_info_tag = BeautifulSoup(
        f"<sourceImageInformation><fileName>{image_filename}</fileName></sourceImageInformation>", "xml")
    try:
        xml_tree.Description.MeasurementUnit.insert_after(src_img_info_tag)
    except Exception as e:
        utils.report("Oops, something went wrong with injecting <sourceImageInformation> in the XML file", "E")
        utils.report("e")


def switch_to_v4(xml_tree):
    """Replace schema and namespace declaration in <alto> to ALTO v4

    :param xml_tree: ALTO XML tree
    :return: None
    """
    # no need for PAGE namespace in the alto xml...
    if "xmlns:page" in [k for k in xml_tree.alto.attrs.keys()]:
        del xml_tree.alto.attrs["xmlns:page"]
    xml_tree.alto.attrs['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
    xml_tree.alto.attrs['xmlns'] = "http://www.loc.gov/standards/alto/ns-v4#"
    xml_tree.alto.attrs['xsi:schemaLocation'] = "http://www.loc.gov/standards/alto/ns-v4# http://www.loc.gov/standards/alto/v4/alto-4-0.xsd"


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
            switch_to_v4(xml_tree)
            utils.report("I'm adding a <sourceImageInformation> element to point toward the image file.", "H")
            add_sourceimageinformation(xml_tree)
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



