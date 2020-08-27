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
DUMMY_FILE2 = "..\data\\tu_dummy.xml"

DEMOFILE = "..\data\demo\\basnage_dummy.xml"

TESTFILE = DEMOFILE

ALTO_V_4_0 = 'http://www.loc.gov/standards/alto/v4/alto-4-0.xsd'
ALTO_V_4_1 = 'http://www.loc.gov/standards/alto/v4/alto-4-1.xsd'
ALTO_V_SCRIPTA = 'https://gitlab.inria.fr/scripta/escriptorium/-/raw/develop/app/escriptorium/static/alto-4-1-baselines.xsd'
ALTO2SPECS = ['http://www.loc.gov/standards/alto/ns-v2#']
ALTO4SPECS = ['http://www.loc.gov/standards/alto/v4/alto.xsd',
              'http://www.loc.gov/standards/alto/v4/alto-4-0.xsd',
              'http://www.loc.gov/standards/alto/v4/alto-4-1.xsd',
              'https://gitlab.inria.fr/scripta/escriptorium/-/raw/develop/app/escriptorium/static/alto-4-1-baselines.xsd']
            # for ACCEPTED_SCHEMAS in eScriptorium, see:
            # https://gitlab.inria.fr/scripta/escriptorium/-/blob/master/app/apps/imports/parsers.py#L297


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
    """Replace schema and namespace declaration in <alto> to ALTO v4

    :param xml_tree: ALTO XML tree
    :return: None
    """
    # as far as I know, there's no need for a PAGE namespace in an alto xml file...
    if "xmlns:page" in [k for k in xml_tree.alto.attrs.keys()]:
        del xml_tree.alto.attrs["xmlns:page"]
    xml_tree.alto.attrs['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
    xml_tree.alto.attrs['xmlns'] = "http://www.loc.gov/standards/alto/ns-v4#"
    xml_tree.alto.attrs['xsi:schemaLocation'] = f"http://www.loc.gov/standards/alto/ns-v4# {ALTO_V_SCRIPTA}"


def get_image_filename(xml_filename, mode='manual'):
    #TODO @alix: we can do better if we use the METS exported by Transkribus!
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
        utils.report(f"I don't know yet how to handle csv mode, I'll switch to default", "W")
        mode = 'manual'
    # eventually this will become an elif statement
    if mode == 'manual':
        # there is no way to know what is the extension of the image file...
        utils.report("Remember to re-enable the manual input for file extension in 'def get_image_filename()'", "W")
        #extension = "dummy"  # this won't stay!
        extension = input("What is the extension of the original image file? [png|jpeg|jpg|tif] > ")
        value = xml_filename.split(os.sep)[-1].replace(".xml", f".{extension.lower()}")
        utils.report(f"'{value}' will be added to //sourceImageInformation/fileName", "H")
    return value


def remove_commas_in_points(xml_tree):
    for polygon in xml_tree.find_all('Polygon', POINTS=True):
        polygon.attrs['POINTS'] = polygon.attrs['POINTS'].replace(',', ' ')


def add_sourceimageinformation(xml_tree, xml_filename):
    """Create a <sourceImageInformation> component in <Description> with the corresponding metadata

    :param xml_tree: ALTO XML tree
    :return: None
    """
    image_filename = get_image_filename(xml_filename)
    src_img_info_tag = BeautifulSoup(
        f"<sourceImageInformation><fileName>{image_filename}</fileName></sourceImageInformation>", "xml")
    try:
        xml_tree.Description.MeasurementUnit.insert_after(src_img_info_tag)
    except Exception as e:
        utils.report("Oops, something went wrong with injecting <sourceImageInformation> in the XML file", "E")
        utils.report("e")


def remove_composed_block(xml_tree):
    # TODO @alix: Documentation...
    # We simply remove the <composedBlock> element
    # This is one way to go, but not very pretty once it is transferred to eScriptorium
    for composed_block in xml_tree.find_all('ComposedBlock'):
        composed_block = composed_block.unwrap()



def extrapolate_baseline_coordinates(xml_tree):
    """Parse the values in all //TextLine/@BASELINE and extrapolate complete coordinates if necessary

    :param xml_tree: ALTO XML tree
    :return: None
    """
    """
    If there's only 1 value in //TextLine/@BASELINE
    then we need to use the //TextLine/ancestor::TextBlock/Shape/Polygon/@POINTS values to imagine a baseline
    EX :
    <TextBlock HEIGHT="181" HPOS="486" ID="r_1_2" VPOS="917" WIDTH="2406">
      <Shape>
          <Polygon POINTS="486,917 2892,917 2892,1098 486,1098"/>
      </Shape>
      <TextLine BASELINE="1097" HEIGHT="179" HPOS="487" ID="tl_2" VPOS="918" WIDTH="2404">
          <String CONTENT="UNIVERSEL." HEIGHT="179" HPOS="487" ID="string_tl_2" VPOS="918" WIDTH="2404"/>
      </TextLine>
    </TextBlock>
    -------
    BASELINE = 1097
    ZONE = 486,917 2892,917 2892,1098 486,1098
    -------
    """
    invalid = 0
    for text_line in xml_tree.find_all("TextLine"):
        if len(text_line.attrs["BASELINE"].split()) == 1:
            baseline_y = int(text_line.attrs["BASELINE"])
            parent = text_line.find_parents("TextBlock")[0]
            if len(parent.Shape.Polygon.attrs["POINTS"].split()) == 4:
                # okay, this is a quadrilateral
                points = [coords.split(',') for coords in parent.Shape.Polygon.attrs["POINTS"].split()]
                start_x = points[0][0]
                stop_x = points[1][0]
                baseline = f"{start_x} {baseline_y} {stop_x} {baseline_y}"
                text_line.attrs["BASELINE"] = baseline
            else:
                invalid += 1
    if invalid > 0:
        utils.report(f"I couldn't extrapolate the coordinates of {invalid_conditions} baselines that needed it...", "E")


def main():
    xml_tree = utils.read_file(TESTFILE, 'xml')
    schemas = get_schema_spec(xml_tree)
    if schemas:
        utils.report(f"Schema Specs: {schemas}", "H")
        alto_version = control_schema_version(schemas)
        if alto_version:
            utils.report(f"Detected ALTO version: v{alto_version}", "H")
        if alto_version == 2:
            utils.report("Buckle up, we're fixing the schema declaration!", "H")
            switch_to_v4(xml_tree)
            utils.report("I'm adding a <sourceImageInformation> element to point toward the image file", "H")
            add_sourceimageinformation(xml_tree, TESTFILE)
            utils.report("I'm now looking for <ComposedBlock> and removing them", "H")
            remove_composed_block(xml_tree)
            utils.report("I'm looking at the baselines and fixing them", "H")
            extrapolate_baseline_coordinates(xml_tree)
            remove_commas_in_points(xml_tree)
            # TODO @alix: improve the saving process, obviously!
            #"""
            write_in_file = input(f"Do you want to save the result in {TESTFILE}? [Y/n] >")
            if write_in_file.lower() == 'y':
                utils.write_file(TESTFILE, str(xml_tree))  # TODO @alix improve the export with prettify()
            else:
                utils.report("Alright, then I'm showing you here:", "H")
                print("##########################\n\n##########################\n\n")
                utils.report(xml_tree.prettify())
            #"""
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
        # TODO @alix: make it possible to load a directory rather than an individual file
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



