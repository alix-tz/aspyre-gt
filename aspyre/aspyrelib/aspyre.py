#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT PROGRAM

author: Alix Chagué
date: 01/11/2020
"""

import os

from tqdm import tqdm

from .utils import utils
from .manage import manage


def main(src, dest=None, talktome=False):
    """Aspyre is a program transforming ALTO XML files exported from Transkribus (ALTO 2.x) to make them compatible with eScriptorium (ALTO 4.x)

    :param src: path to the source containing a 'mets.xml' file and a 'alto/' directory full of ALTO XML files
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
        utils.report("No path to input was provided, Apsyre can't proceed.", "E")
        return {"failed": True, "msg": "Something went wrong locating the source files."}

    # 2. parsing params
    talkative = talktome
    source = src
    if not dest:
        destination = os.path.join(source, 'alto_escriptorium')
    else:
        destination = dest
        if not utils.path_is_valid(destination):
            destination = os.path.join(source, 'alto_escriptorium')
            utils.report(
                f"'{dest}' is not a valid path, will save output in default location: {destination}",
                "W")

    # 3. collecting data
    package = utils.list_directory(source)
    images_files = manage.extract_mets(package, source)
    alto_files = manage.locate_alto_files(package)

    # if data wasn't properly collected, Aspyre has to stop.
    if len(images_files) == 0:
        utils.report("Aspyre can't run properly: there is no image reference to pair with the ALTO XML files", "E")
        utils.report("Interrupting execution", "E")
        return {"failed": True, "msg": "There is no reference to images in the METS XML file you provided. Make sure to check the \"Export Image\" option in Transkribus."}

    if alto_files is False:
        utils.report("Aspyre can't run without ALTO XML files.", "E")
        utils.report("Interrupting execution", "E")
        return {"failed": True, "msg": "There is no ALTO XML file in the data you provided."}

    # 4. modifying files
    for file in tqdm(alto_files, desc="Processing ALTO XML files", unit=' file'):
        manage.handle_a_file(file, images_files, source, destination, talkative)
    utils.report("Finished!", "S")

    # 5. in some case knowing the program ran until the end can be useful,
    # so we always return True if main() successfully reach this point.
    return {"failed": False, "msg": "Aspyre ran successfully."}

