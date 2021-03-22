#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT zip package

author: Alix Chagué
date: 19/03/2021
"""

import os
from zipfile import ZipFile

from ..utils import utils

ALLOWED_EXTENSIONS = ["zip"]


# ------------------------- ZIP

def allowed_file(filename, allowed_extensions=ALLOWED_EXTENSIONS):
    """Control that file extension is accepted

    :param filename: name of the file
    :param allowed_extensions: list of allowed extension for a compressed archive
    :type filename: str
    :type allowed_extensions: list
    :return: True if allowed, False otherwise
    :rtype: bool
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.lower() in allowed_extensions:
        return True
    else:
        return False


def safely_unzip(zip_src, unpack_dest, scenario):
    """Unzip a zip file with as many precautions as possible

    :param zip_src: path to the directory where the uploaded zip file is located
    :param unpack_dest: path to the directory where the zip file should be unzipped
    :type zip_src: str
    :type unpack_dest: str
    :return: ('error', '<message>') if an error occurred, (None, None) otherwise
    :rtype: tuple
    """
    zph = ZipFile(zip_src, 'r')
    files = zph.infolist()
    ignored_files = []
    if scenario == "tkb":
    # then we are only interested in xml files
        ignored_files += [f for f in files if not f.filename.lower().endswith('.xml')]
    elif scenario == "pdfalto":
        ignored_files += [f for f in files if not (f.filename.lower().endswith('.xml') or f.filename.lower().endswith('.png'))]
    # ignoring hidden files and folder
    ignored_files += [f for f in files if f.filename.split(os.sep)[-1].startswith('.') or f.filename.startswith('.')]
    # ignoring OSX generated folders
    ignored_files += [f for f in files if f.filename.lower().startswith('__macosx')]
    files = [f for f in files if f not in ignored_files]
    # additional control
    # ignoring files containing .exe, .php or .asp - ex: 'my_suspicious_file.exe.xml' will be ignored
    # note that this might cause unexpected errors TODO: test
    ignored_files += [f for f in files if '.exe' in f.filename.lower() or '.php' in f.filename.lower() or \
                      '.asp' in f.filename.lower() or '.py' in f.filename.lower()]
    if scenario == "tkb":
        if 'mets.xml' not in [f.filename.split(os.sep)[-1] for f in files]:
            zph.close()
            return "error", "This is not a valid Transkribus Archive (not mets.xml file)"
    for file in files:
        zph.extract(file, path=unpack_dest)
    zph.close()
    utils.report(f"Ignored {len(ignored_files)} non-eligible file(s) while unpacking\n---", "W")
    # TODO : add talkative mode enabling to display which files were ignored.
    return None, None


def unzip_scenario(source, scenario):
    """Take an archive and safely unzip it

    :param source: path to archive
    :type source: str
    :return: False if failed, else path to the unzipped source
    :rtype: bool or str
    """
    if not (os.path.basename(source) != "" and allowed_file(os.path.basename(source))):
        utils.report("This file extension is not allowed\n---", "E")
        return False

    unpack_dest = os.path.join(os.path.dirname(source), f"{os.path.basename(source).split('.')[0]}_unpacking")
    try:
        os.mkdir(unpack_dest)
    except FileExistsError as e:
        utils.report("Got a FileExistsError while trying to unpack source archive:", "W")
        utils.report(e, "W")
        utils.report("This may cause Aspyre to run on data not up-to-date with the content of the source archive\n---",
                     "W")
    flag, msg = safely_unzip(source, unpack_dest, scenario)
    if flag == 'error':
        utils.report(msg, "E")
        return False
    if flag is None:
        utils.report(f"Unpacked source archive here: '{unpack_dest}'\n---", "I")
        return unpack_dest


def zip_dir(destination, sourcepath):
    """Create a zip file out of a directory

    :param destination: path where the archive should be stored
    :param sourcepath: initial path to source
    :type destination: str
    :type sourcepath: str
    :return: path to the created zip file
    :rtype: str
    """
    source = destination  # what is in the destination is the XML files that were created, isn't it?
    destination = os.sep.join(destination.split(os.sep)[:-1])
    zip_destination = os.path.abspath(
        os.path.join(destination, f"aspyre_{os.path.basename(sourcepath).replace('_unpacking', '')}.zip"))
    xmls = [f for f in os.listdir(source) if f.endswith('.xml')]
    try:
        ziph = ZipFile(zip_destination, "w")
        for file in xmls:
            ziph.write(os.path.join(source, file), arcname=os.path.join("alto4eScriptorium", file))
        ziph.close()
        failed = False
    except Exception as e:
        print(e)
        failed = True
    if failed:
        print("---")
        utils.report("Failed at creating a ZIP archive.\n---", "W")  # No big deal technically
        return None
    # TODO : which is best? alto4escriptorium? or aspyre_{basename} ?
    #utils.report(f"Creating a new archive at: {os.path.join(destination, 'alto4eScriptorium.zip')}", "I")
    print("---")
    utils.report(f"Creating a new archive at: {zip_destination}", "I")
    utils.report(f"You can directly import it into eScriptorium! :)\n---", "I")
    return zip_destination
