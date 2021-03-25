#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT manage limbtoes package
  LIMB: XML ALTO generated with LIMB

author: Alix Chagué
date: 25/03/2021
"""

import os

from bs4 import BeautifulSoup
from tqdm import tqdm
from PIL import Image

from ..utils import utils


# ALTO_V_4_0 = 'http://www.loc.gov/standards/alto/v4/alto-4-0.xsd'
# ALTO_V_4_1 = 'http://www.loc.gov/standards/alto/v4/alto-4-1.xsd'
ALTO_V_SCRIPTA = 'https://gitlab.inria.fr/scripta/escriptorium/-/raw/develop/app/escriptorium/static/alto-4-1-baselines.xsd'
ALTO2SPECS = ['http://www.loc.gov/standards/alto/ns-v2#']
ALTO3SPECS = ['http://www.loc.gov/standards/alto/ns-v3#']
ALTO4SPECS = ['http://www.loc.gov/standards/alto/v4/alto.xsd',
              'http://www.loc.gov/standards/alto/v4/alto-4-0.xsd',
              'http://www.loc.gov/standards/alto/v4/alto-4-1.xsd',
              'https://gitlab.inria.fr/scripta/escriptorium/-/raw/develop/app/escriptorium/static/alto-4-1-baselines.xsd']


# for ACCEPTED_SCHEMAS in eScriptorium, see:
# https://gitlab.inria.fr/scripta/escriptorium/-/blob/master/app/apps/imports/parsers.py#L297

# ------------------------- LIMB

## SCHEMA RESOLUTION
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
        schema = root[0].attrs["xmlns"].split()
    return schema


def control_schema_version(schemas):
    """Control the validity of schema specification (only accept ALTO 3 or ALTO 4 specs)

    :param schemas: list of values contained in //alto/xsi:schemaLocation
    :type schemas: list
    :return: 2 if ALTO v2, 4 if ALTO v4, None otherwise
    :rtype: int or None
    """
    for spec2 in ALTO2SPECS:
        if spec2 in schemas:
            return 2
    for spec4 in ALTO4SPECS:
        if spec4 in schemas:
            return 4
    for spec3 in ALTO3SPECS:
        if spec3 in schemas:
            return 3
    # We return None if it isn't ALTO 2 nor ALTO 4.
    utils.report("I'm not supposed to get something else than ALTO 2, 3 or 4... !", "E")
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


## SOURCEIMAGEINFORMATION RESOLUTION
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
    xml_numbering = base_file_name.replace('.xml', '').split("_")[-1]
    #ex: 'AD075BI_PER232_0005_0003.xml' -> '0003'

    image_filename = None
    for image in list_of_image_files:
        img_basename = os.path.basename(image).split('.')[0]
        if xml_numbering in img_basename.split('_')[-1]:
            image_filename = image
            # ex: if xml_numbering == '0005':
            # ex: 'AD075BI_PER232_0005_1907_0005.jpg' -> ok
            # ex: 'AD075BI_PER232_0005_1907_0004.jpg' -> not ok
            # we only target the last element, not the whole basename
    if image_filename is False:
        utils.report(f"Couldn't find an image matching {base_file_name}", "W")
        image_filename = None
    else:
        ideal_image_filename = os.path.basename(image_filename)
    # why do we do this: because we need the info to the actual image for the next step
    # but we may as well put the ideal filename info now
    return f"{image_filename}||{ideal_image_filename}"


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
    #src_img_info_tag = BeautifulSoup(
    #    f"<sourceImageInformation><fileName>{image_filename}</fileName></sourceImageInformation>", "xml")
    try:
        xml_tree.sourceImageInformation.fileName.string = image_filename
    except Exception as e:
        utils.report("Oops, something went wrong with injecting <sourceImageInformation> in the XML file", "E")
        utils.report("e")


def clean_filename(xml_tree):
    """remove second half of the filename (absolute path) and keep only the base name
    :param xml_tree: parsed xml tree
    :type xml_tree: BeautifulSoup
    :return: None
    """
    # we only keep the ideal image filename
    filename_elem = xml_tree.find_all("fileName")[0]
    filename_elem.string = filename_elem.string.split("||")[-1]
    return xml_tree


## COORDINATES/RATIO RESOLUTION
def get_canvas_size(xml_tree):
    """Open an image file and get its actual size

    :param xml_tree: parsed XML tree
    :type xml_tree: BeautifulSoup
    :return: image size (width, height)
    :rtype: tuple
    """
    input_im = xml_tree.find_all("fileName")[0].string.split("||")[0]
    im = Image.open(input_im)
    return im.size


def get_ratio(canvas_size, xml_tree):
    """Compare source image size and canvas size as it appears in XML file to get ratio
    Ratio should be 16.67

    :param canvas_size: source image size (width, height)
    :type canvas_size: tuple
    :return: ratio
    :rtype: float

    """
    xml_size = xml_tree.find_all("Page")[0]
    xml_height = xml_size.attrs["HEIGHT"]
    xml_width = xml_size.attrs["WIDTH"]
    #print("in xml : ", xml_width, ", ", xml_height)
    original_width, original_height = canvas_size
    #print("original :", original_width, ", ", original_height)
    ratio_width = round(float(original_width) / float(xml_width), 2)
    ratio_height = round(float(original_height) / float(xml_height), 2)
    if ratio_width != 3.00 or ratio_height != 3.00:
        utils.report(f"ratio height : {ratio_height} \nratio width : {ratio_width}", "W")
        # TODO be smart about this case if necessary!
        pass
    ratio = 3.00
    return ratio


def apply_ratio_to_coordinates(xml_tree):
    """Modify coordinates based on a ratio to match source image size

    :param xml_tree: parsed XML file
    :type xml_tree: BeautifulSoup
    :return: modified XML tree
    :rtype: BeautifulSoup
    """
    canvas_size = get_canvas_size(xml_tree)
    ratio = get_ratio(canvas_size, xml_tree)
    tags = xml_tree.PrintSpace.find_all(True)
    for tag in tags:
        if "HPOS" in tag.attrs:
            tag.attrs["HPOS"] = int(float(tag.attrs["HPOS"]) * ratio)
        if "VPOS" in tag.attrs:
            tag.attrs["VPOS"] = int(float(tag.attrs["VPOS"]) * ratio)
        if "WIDTH" in tag.attrs:
            tag.attrs["WIDTH"] = int(float(tag.attrs["WIDTH"]) * ratio)
        if "HEIGHT" in tag.attrs:
            tag.attrs["HEIGHT"] = int(float(tag.attrs["HEIGHT"]) * ratio)
    return xml_tree


def apply_padding(xml_tree, vpadding):
    """Change values of VPOS attributes in String and TextLine nodes

    :param xml_tree: parsed XML file
    :type xml_tree: BeautifulSoup
    :param vpadding: value to add to VPOS attributes
    :type vpadding: int
    """
    # un-necessary:
    #for tl in xml_tree.find_all('TextLine'):
    #    if "VPOS" in tl.attrs:
    #        tl.attrs['VPOS'] = int(tl.attrs['VPOS'] + vpadding)
    for st in xml_tree.find_all('String'):
        if 'VPOS' in st.attrs:
            st.attrs['VPOS'] = int(st.attrs['VPOS'] + vpadding)
    # un-necessary:
    #for sp in xml_tree.find_all('SP'):
    #    if "VPOS" in sp.attrs:
    #        sp.attrs['VPOS'] = int(sp.attrs['VPOS'] + vpadding)
    return xml_tree


## COLLECTING INFORMATION && I/O
def locate_alto_and_image_files(package):
    """List the files contained in the 'out/' directory inside the archive

    :param package: list of files contained in the archive
    :type package: list
    :return: list of XML file names contained in out/
    :rtype: list
    """
    if len(package) == 1:
        main_dir_content = utils.list_directory(package[0])
    else:
        main_dir_content = package

    alto_files = []
    image_files = []
    for file in main_dir_content:
        if file.endswith(".xml"):
            alto_files.append(file)
        else:
            image_files.append(file)
    if len(alto_files) == 0:
        utils.report("Found no eligible XML file.\n---")
        return False, False
    if len(image_files) == 0:
        utils.report("Found no eligible image file.\n---")
        return False, False
    if len(image_files) != len(alto_files):
        utils.report(f"Didn't find as many images ({len(image_files)}) as xml files ({len(alto_files)}).", "W")
        utils.report(f"It's not necessarily an issue.\n---", "W")
    return alto_files, image_files


def save_processed_file(xml_file_name, xml_content, destination):
    """Calculate the path to writing in a new XML file, make sure it is valid and then dump the XML content

    :param xml_file_name: ALTO XML file base name
    :param xml_content: parsed XML tree
    :type xml_file_name: str
    :type xml_content: type(BeautifulSoup())
    :return: None
    """
    if not os.path.isdir(destination):
        os.makedirs(destination)
    path_to_file = os.path.join(destination, xml_file_name)
    # TODO @alix improve the export with prettify(): remove the blank space inside '//Measurements'
    utils.write_file(path_to_file, str(xml_content))


## main function
def handle_a_file(file, limb_to_es_obj):
    """Take an ALTO XML file and convert it so it is compatible with eScriptorium's import module

    :param file: path to an ALTO XML file
    :type file: str
    :param limb_to_es_obj: Limb to Es object
    :type limb_to_es_obj: LimbToEs
    :return: None
    """
    if limb_to_es_obj.args.padding:
        length = 8
    else:
        length = 7

    xml_tree = utils.read_file(file, 'xml')
    pbar = tqdm(total=length, desc="Processing...", unit=" step")
    pbar.update(1)  # getting schema version
    schemas = get_schema_spec(xml_tree)

    if schemas:
        if limb_to_es_obj.args.talkative:
            utils.report(f"Found the following schema specs declaration(s): {schemas}\n---", "H")
        pbar.update(1)  # controlling schema version
        alto_version = control_schema_version(schemas)
        if limb_to_es_obj.args.talkative:
            if alto_version:
                utils.report(f"Detected ALTO version: v{alto_version}\n---", "H")

        if alto_version in [2, 3, 4]:  # even if the schema spec is ALTO 4, there may be other issues...
            # and we still need to switch to SCRIPTA ALTO specs anyways...
            if limb_to_es_obj.args.talkative:
                utils.report("Buckle up, we're fixing the schema declaration!\n---", "H")
            pbar.update(1)  # changing schema declaration to ALTO 4 (SCRIPTA flavored)
            switch_to_v4(xml_tree)

            if limb_to_es_obj.args.talkative:
                utils.report("I'm adding a <sourceImageInformation> element to point towards the image file\n---", "H")
            pbar.update(1)  # adding file name in source image information
            add_sourceimageinformation(xml_tree, file, limb_to_es_obj.image_files)
            # modifier les coordonnées
            if limb_to_es_obj.args.talkative:
                utils.report("Fixing the ratio (coordinates)\n---", "H")
            pbar.update(1)  # fixing baseline declarations
            xml_tree = apply_ratio_to_coordinates(xml_tree)

            if limb_to_es_obj.args.padding:
                if limb_to_es_obj.args.talkative:
                    utils.report("Adjusting y-axis coords in textline and strings nodes\n---", "H")
                pbar.update(1)
                xml_tree = apply_padding(xml_tree, limb_to_es_obj.args.vpadding)

            if limb_to_es_obj.args.talkative:
                utils.report("Wrapping up\n---", "H")
            pbar.update(1)  # fixing baseline declarations
            xml_tree = clean_filename(xml_tree)

            # TODO @alix: improve the saving process, obviously!
            pbar.update(1)  # saving file
            save_processed_file(file.split(os.sep)[-1], xml_tree, limb_to_es_obj.args.destination)
        pbar.close()

