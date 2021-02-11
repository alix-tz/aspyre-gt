#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT PROGRAM

author: Alix Chagué
date: 01/11/2020
"""

import os

from tqdm import tqdm

from .utils import utils
from .manage import manage_tkbtoes
from .manage import zip


ARCHIVE_EXTENSIONS = ["zip"]


def main(src, dest=None, talktome=False):
    """Aspyre is a program transforming ALTO XML files exported from Transkribus (ALTO 2.x) to make them compatible with eScriptorium (ALTO 4.x)

    :param src: path to the source containing a 'mets.xml' file and a 'alto/' directory full of ALTO XML files (directory or zip)
    :param dest: path to where new files should be save
    :param talktome: highlighted messages will be displayed if activated (verbosity)
    :type talktome: bool
    :type src: str
    :type dest: str
    :return: an execution status and a description of the possible error
    :rtype: dict
    """
    # 1. do we proceed?
    # if orig_source is False the program will not be able to do anything...
    if src is False:
        utils.report("No source was specified, Apsyre can't proceed.", "E")
        return {"failed": True, "msg": "Something went wrong locating the source."}

    # 2. parsing params
    talkative = talktome
    source = src

    # 3. handling zip
    if src.split(".")[-1] in ARCHIVE_EXTENSIONS:
        if talkative:
            utils.report("Source is an archive, running unzipping scenario.", "H")
        unzipped_source = zip.unzip_scenario(source)
        if unzipped_source is False:
            utils.report("Failing at unpacking the archive, Apsyre can't proceed.", "E")
            return {"failed": True, "msg": "Something went wrong unpacking the source."}
        else:
            source = unzipped_source
            utils.report(f"Source is now: {source}", "I")
    else:
        if talkative:
            utils.report("Source is not an archive.", "H")

    # 2b: parsing params
    if not dest:
        destination = os.path.join(source, 'alto_escriptorium')
    else:
        destination = dest
        if not utils.path_is_valid(destination):
            destination = os.path.join(source, 'alto_escriptorium')  # TODO make that work with zip scenario
            utils.report(
                f"'{dest}' is not a valid path, will save output in default location: {destination}",
                "W")

    # 4. collecting data
    package = utils.list_directory(source)
    images_files = manage_tkbtoes.extract_mets(package, source)
    alto_files = manage_tkbtoes.locate_alto_files(package)

    # if data wasn't properly collected, Aspyre has to stop.
    if len(images_files) == 0:
        utils.report("Aspyre can't run properly: there is no image reference to pair with the ALTO XML files", "E")
        utils.report("Interrupting execution", "E")
        return {"failed": True, "msg": "There is no reference to images in the METS XML file you provided. Make sure to check the \"Export Image\" option in Transkribus."}

    if alto_files is False:
        utils.report("Aspyre can't run without ALTO XML files.", "E")
        utils.report("Interrupting execution", "E")
        return {"failed": True, "msg": "There is no ALTO XML file in the data you provided."}

    # 5. modifying files
    for file in tqdm(alto_files, desc="Processing ALTO XML files", unit=' file'):
        manage_tkbtoes.handle_a_file(file, images_files, source, destination, talkative)

    # 6. serve a zip file
    zip.zip_dir(destination, source)
    utils.report("Finished!", "S")

    # 7. in some case knowing the program ran until the end can be useful,
    # so we always return True if main() successfully reach this point.
    return {"failed": False, "msg": "Aspyre ran successfully."}

