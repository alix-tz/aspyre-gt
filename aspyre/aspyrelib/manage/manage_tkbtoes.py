#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT manage tkbtoes package

author: Alix Chagué
date: 19/03/2021
"""

import os

from bs4 import BeautifulSoup
from tqdm import tqdm

from ..utils import utils


# ALTO_V_4_0 = 'http://www.loc.gov/standards/alto/v4/alto-4-0.xsd'
# ALTO_V_4_1 = 'http://www.loc.gov/standards/alto/v4/alto-4-1.xsd'
ALTO_V_SCRIPTA = 'https://gitlab.inria.fr/scripta/escriptorium/-/raw/develop/app/escriptorium/static/alto-4-1-baselines.xsd'
ALTO2SPECS = ['http://www.loc.gov/standards/alto/ns-v2#']
ALTO4SPECS = ['http://www.loc.gov/standards/alto/v4/alto.xsd',
              'http://www.loc.gov/standards/alto/v4/alto-4-0.xsd',
              'http://www.loc.gov/standards/alto/v4/alto-4-1.xsd',
              'https://gitlab.inria.fr/scripta/escriptorium/-/raw/develop/app/escriptorium/static/alto-4-1-baselines.xsd']


# for ACCEPTED_SCHEMAS in eScriptorium, see:
# https://gitlab.inria.fr/scripta/escriptorium/-/blob/master/app/apps/imports/parsers.py#L297

# ------------------------- TRP

def get_schema_spec(xml_tree):
    """Look for ALTO schema specification(s) in an XML document

    :param xml_tree: parsed xml tree
    :type xml_tree: type(BeautifulSoup())
    :return: False if not a valid ALTO file, else the value(s) in //alto/xsi:schemaLocation as a list
    :rtype: bool or list
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

    :param schemas: list of values contained in //alto/xsi:schemaLocation
    :type schemas: list
    :return: 2 if ALTO v2, 4 if ALTO v4, None otherwise
    :rtype: int or None
    """
    # This syntax is not very pythonesque...
    for spec4 in ALTO4SPECS:
        if spec4 in schemas:
            return 4
    for spec2 in ALTO2SPECS:
        if spec2 in schemas:
            return 2
    # We return None if it isn't ALTO 2 nor ALTO 4.
    # TODO @alix: do we need to look for other versions of ALTO?
    utils.report("I can't handle anything other than ALTO v2 or v4!", "E")
    return None


def switch_to_v4(xml_tree):
    """Replace schema and namespace declaration in <alto> to ALTO v4

    :param xml_tree: ALTO XML tree
    :type xml_tree: type(BeautifulSoup())
    :return: None
    """
    if "xmlns:page" in [k for k in xml_tree.alto.attrs.keys()]:
        # as far as I know, there's no need for a PAGE namespace in an alto xml file...
        del xml_tree.alto.attrs["xmlns:page"]
    xml_tree.alto.attrs['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
    xml_tree.alto.attrs['xmlns'] = "http://www.loc.gov/standards/alto/ns-v4#"
    xml_tree.alto.attrs['xsi:schemaLocation'] = f"http://www.loc.gov/standards/alto/ns-v4# {ALTO_V_SCRIPTA}"


def remove_commas_in_points(xml_tree):
    """Remove the commas in the value of all //Polygon/@POINTS in an ALTO XML tree

    :param xml_tree: ALTO XML tree
    :type xml_tree: type(BeautifulSoup())
    :return: None
    """
    for polygon in xml_tree.find_all('Polygon', POINTS=True):
        polygon.attrs['POINTS'] = polygon.attrs['POINTS'].replace(',', ' ')


def get_image_filename(file_name, list_of_image_files):
    """Compare an ALTO XML file name with a list of image file names and try to find a pair

    :param file_name: absolute path to an ALTO XML file
    :param list_of_image_files: list of image file names
    :type file_name: str
    :type list_of_image_files: list
    :return: pairing image file name, None if no pair found
    :rtype: str
    """
    """
    ex: if 'myfile.xml' and 'myfile.png' in list_of_image_files, then return 'myfile.png'
    ex: if 'myfile.xml' and not 'myfile.*" in list_of_image_files, then return None 
    """
    base_file_name = os.path.basename(file_name).replace('.xml', '')
    image_filenames = [os.path.basename(img) for img in list_of_image_files if
                       os.path.basename(img).split('.')[0] == base_file_name]
    image_filename = None
    if len(image_filenames) == 0:
        utils.report(f"I didn't find a matching image file name in 'mets.xml' for '{base_file_name}'", "W")
    elif len(image_filenames) > 1:
        utils.report(f"I found too many matching image file names in 'mets.xml' for '{base_file_name}", "W")
        utils.report(f"\tI'll use '{image_filenames[0]}'", "W")
        image_filename = image_filenames[0]
    else:
        image_filename = image_filenames[0]
    return image_filename


def add_sourceimageinformation(xml_tree, filename, image_files):
    """Create a <sourceImageInformation> component in <Description> with the corresponding metadata

    :param xml_tree: ALTO XML tree
    :param filename: absolute path to an ALTO XML file
    :param image_files: list of image file names
    :type xml_tree: type(BeautifulSoup())
    :type filename: str
    :type image_files: list
    :return: None
    """
    image_filename = get_image_filename(filename, image_files)
    src_img_info_tag = BeautifulSoup(
        f"<sourceImageInformation><fileName>{image_filename}</fileName></sourceImageInformation>", "xml")
    try:
        xml_tree.Description.MeasurementUnit.insert_after(src_img_info_tag)
    except Exception as e:
        utils.report("Oops, something went wrong with injecting <sourceImageInformation> in the XML file", "E")
        utils.report("e")


def remove_composed_block(xml_tree):
    """Remove every ComposedBlock in an ALTO XML tree by unwrapping its content

    :param xml_tree: ALTO XML tree
    :type xml_tree: type(BeautifulSoup())
    :return: None
    """
    # We simply remove the <composedBlock> element
    # This is one way to go, but it's not very pretty once it is transferred to eScriptorium
    for composed_block in xml_tree.find_all('ComposedBlock'):
        composed_block = composed_block.unwrap()


def extrapolate_baseline_coordinates(xml_tree):
    """Parse the values in all //TextLine/@BASELINE and extrapolate complete coordinates if necessary

    :param xml_tree: ALTO XML tree
    :type xml_tree: type(BeautifulSoup())
    :return: None
    """
    """
    If there's only 1 value in //TextLine/@BASELINE
    then we need to use the //TextLine/@HPOS and //TextLine/@WIDTH values to imagine a baseline
    EX :
      <TextLine BASELINE="1097" HEIGHT="179" HPOS="487" ID="tl_2" VPOS="918" WIDTH="2404">
          <String CONTENT="UNIVERSEL." HEIGHT="179" HPOS="487" ID="string_tl_2" VPOS="918" WIDTH="2404"/>
      </TextLine>
    """
    for text_line in xml_tree.find_all("TextLine"):
        if len(text_line.attrs["BASELINE"].split()) == 1:
            baseline_y = int(text_line.attrs["BASELINE"])
            baseline_ax = int(text_line.attrs["HPOS"])
            baseline_bx = int(text_line.attrs["HPOS"]) + int(text_line.attrs["WIDTH"])
            baseline = f"{baseline_ax} {baseline_y} {baseline_bx} {baseline_y}"
            text_line.attrs["BASELINE"] = baseline


def save_processed_file(xml_file_name, xml_content, destination):
    """Calculate the path to writing in a new XML file, make sure it is valid and then dump the XML content

    :param xml_file_name: ALTO XML file base name
    :param xml_content: parsed XML tree
    :type xml_file_name: str
    :type xml_content: type(BeautifulSoup())
    :return: None
    """
    # Do we need a try except here?
    print(f"[DEBUG] {destination}")
    if not os.path.isdir(destination):
        os.makedirs(destination)
    path_to_file = os.path.join(destination, xml_file_name)
    # TODO @alix improve the export with prettify(): remove the blank space inside '//Measurements'
    utils.write_file(path_to_file, str(xml_content))


def handle_a_file(file, tkb_to_es_obj):
    #images_files, src, dest, talk):
    """Take an ALTO XML file and convert it so it is compatible with eScriptorium's import module

    :param file: path to an ALTO XML file
    :param images_files: list of image file names
    :param src: verified path to the source containing a 'mets.xml' file and a 'alto/' directory full of ALTO XML files
    :param dest: verified path to where new files should be save
    :param talk: highlighted messages will be displayed if activated (verbosity)
    :type file: str
    :type images_files: list
    :type talk: bool
    :type src: str
    :type dest: str
    :return: None
    """

    #global talkative
    #global source
    #global destination
    #talkative = talk
    #source = src
    #destination = dest

    xml_tree = utils.read_file(file, 'xml')
    pbar = tqdm(total=7, desc="Processing...", unit=" step")
    pbar.update(1)  # getting schema version
    schemas = get_schema_spec(xml_tree)
    if schemas:
        if tkb_to_es_obj.args.talkative:
            utils.report(f"Schema Specs: {schemas}", "H")
        pbar.update(1)  # controlling schema version
        alto_version = control_schema_version(schemas)
        if tkb_to_es_obj.args.talkative:
            if alto_version:
                utils.report(f"Detected ALTO version: v{alto_version}", "H")
        if alto_version == 2 or alto_version == 4:  # even if the schema spec is ALTO 4, there may be other issues...
            # and we still need to switch to SCRIPTA ALTO specs anyways...
            if tkb_to_es_obj.args.talkative:
                utils.report("Buckle up, we're fixing the schema declaration!", "H")
            pbar.update(1)  # changing schema declaration to ALTO 4 (SCRIPTA flavored)
            switch_to_v4(xml_tree)
            if tkb_to_es_obj.args.talkative:
                utils.report("I'm adding a <sourceImageInformation> element to point towards the image file", "H")
            pbar.update(1)  # adding file name in source image information
            add_sourceimageinformation(xml_tree, file, tkb_to_es_obj.image_files)
            if tkb_to_es_obj.args.talkative:
                utils.report("I'm now looking for <ComposedBlock> and removing them", "H")
            pbar.update(1)  # removing ComposedBlock elements
            remove_composed_block(xml_tree)
            if tkb_to_es_obj.args.talkative:
                utils.report("I'm looking at the baselines and fixing them", "H")
            pbar.update(1)  # fixing baseline declarations
            extrapolate_baseline_coordinates(xml_tree)
            if tkb_to_es_obj.args.talkative:
                utils.report("I'm cleaning the file", "H")
            pbar.update(1)  # fixing polygons' points' declaration
            remove_commas_in_points(xml_tree)
            # TODO @alix: improve the saving process, obviously!
            pbar.update(1)  # saving file
            save_processed_file(file.split(os.sep)[-1], xml_tree, tkb_to_es_obj.args.destination)
        pbar.close()

        # It might be an idea to just keep the //TextLine as long as their ID start with "line_"
        # If they start with TableCell_, they should become region (maybe?)
        # And if they start with Table_, they don't need to stay (maybe?)
        # There'll be some test import to do with eScriptorium at that point anyway.
        # But let's keep in mind that if we just want to import the data into eScriptorium to train a segmenter
        #     really we only need the TextLine and their baseline, we could remove the rest. Just sayin'
        # TODO @alix: add an else statement to record which file were not processed


def get_list_of_source_images(mets):
    """Process a series of METS XML files and extract all image filename available in //ns3:fileGrp[@ID="IMG"] elements

    :param mets: list of path to METS XML files
    :type mets: list
    :return: list of image file names
    :rtype: list
    """
    source_images = []
    for mets_file in mets:
        content = utils.read_file(mets_file, 'xml')
        # if "Image" option wasn't checked when requesting export on Transkribus
        # there will be no #//ns3:fileGrp[@ID="IMG"]/ns3:file/ns3:Flocat/@ns2:href
        # so Aspyre will not be able to run
        if len(content.find_all("ns3:fileGrp", ID="IMG")) == 0:
            utils.report(
                "There is no reference to images in mets.xml! Make sure to check the \"Export Image\" option in Transkribus",
                "W")
        # image filename location : #//ns3:fileGrp[@ID="IMG"]/ns3:file/ns3:Flocat/@ns2:href
        for image_file_tag in content.find_all("ns3:fileGrp", ID="IMG"):
            for flocat in image_file_tag.find_all("ns3:FLocat"):
                source_images.append(flocat.attrs["ns2:href"])
    return source_images


def extract_mets(package, trp_export):
    """Parse a METS XML file (mets.xml) in a TRP Export directory and extract a list of image file names

    :param package: list of files contained in the TRP Export directory
    :param trp_export: absolute path to the TRP Export directory
    :type package: list
    :type trp_export: str
    :return: list of image file name contained in the METS XML file
    :rtype: list
    """
    mets = [element for element in package if os.path.basename(element) == "mets.xml"]
    if len(mets) > 0:
        list_of_image_filenames = get_list_of_source_images(mets)
        # commenting this because it is now redundant
        # if len(list_of_image_filenames) == 0:
        #    utils.report("I couldn't find any reference to image files in mets.xml...", "W")
    else:
        utils.report(
            f"There is no 'mets.xml' file in the indicated location. Are you sure '{trp_export}' is an export from Transkribus?",
            "E")
        list_of_image_filenames = False
    return list_of_image_filenames


def locate_alto_files(package, source):
    """List the files contained in the 'alto/' directory inside the TRP Export directory

    :param package: list of files contained in the TRP Export directory
    :type package: list
    :return: list of XML file name contained in the TRP Export directory
    :rtype: list
    """
    alto_dir = [element for element in package if os.path.basename(element) == "alto" and os.path.isdir(element)]
    if len(alto_dir) == 0:
        utils.report(f"There is no 'alto' directory in '{source}'", "W")
        return False
    else:
        # There cannot be 2 'alto' directories
        alto_dir_content = utils.list_directory(alto_dir[0])
        alto_dir_content = [f for f in alto_dir_content if f.endswith('.xml')]
    return alto_dir_content
