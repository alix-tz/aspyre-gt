#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT Classes

author: Alix Chagué
date: 19/03/2021
"""

import os
import time

from tqdm import tqdm

from .utils import utils
from .manage import (manage_tkbtoes, manage_pdfaltotoes, zip)

SUPPORTED_SCENARIOS = ["tkb", "pdfalto"]  # + ["limb", "finereader"]
ARCHIVE_EXTENSIONS = ["zip"]


class AspyreArgs():
    def add_log(self, msg):
        """Append a timed execution message to self.log"""
        self.log.append(f"{time.ctime()}: {msg}")

    def proceed(self):
        """return True if self.execution_status is 'Running'"""
        return self.execution_status == "Running"

    def __init__(self, scenario=None, source=None, destination=None, talkative=False, test_type=False, vpadding=0):
        """Process essentiel information to run Aspyre

        :param scenario: keyword describing the scenario
        :type scenario: bool or string
        :param source: path to source file
        :type source: bool or string
        :param destination: path to output
        :type destination: bool or string
        :param talkative: activate a few print commands
        :type talkative: bool
        :param test_type: simple initiation for test purpose
        :type test_type: bool
        """
        if test_type == True:
            self.execution_status = "Debug"
        else:
            self.log = []
            self.add_log("Creation")

            # parsing talkative
            self.talkative = talkative
            if self.talkative:
                utils.report("Talkative mode activated.\n---", "H")

            # parsing source
            self.source = source
            if not self.source:
                self.execution_status = 'Failed'
                self.add_log("no source provided.")
            else:
                self.execution_status = 'Running'

            if self.proceed():
                # parsing destination
                if not destination:
                    self.destination = os.path.join('.'.join(source.split(".")[:-1]), 'alto_escriptorium')
                    self.add_log(f"Destination set to {self.destination}.")
                else:
                    self.destination = destination
                    if not utils.path_is_valid(self.destination):
                        destination = os.path.join('.'.join(source.split(".")[:-1]), 'alto_escriptorium')
                        self.add_log(f"{destination} is not valid. Output is sent to default location.")
                        self.add_log(f"Output destination is now {self.destination}")
                        if talkative:
                            utils.report(f"'{destination}' is not a valid path!", "W")
                            utils.report(f"Output destination is now: {self.destination}.\n---", "W")
            else:
                self.destination = None

            if self.proceed():
                # parsing scenario
                if isinstance(scenario, type(str())) and scenario.lower() in SUPPORTED_SCENARIOS:
                    self.scenario = scenario.lower()
                else:
                    self.scenario = None
                    self.add_log(f"{scenario} is not a valid scenario.")
                    self.execution_status = "Failed"
            else:
                self.scenario = None

            if self.proceed():
                # parsing vpadding
                # only valid with PDFALTO scenario
                if self.scenario != 'pdfalto':
                    self.vpadding = 0
                else:
                    self.vpadding = vpadding

                if self.vpadding == 0:
                    self.padding = False
                else:
                    self.padding = True

                if self.talkative:
                    if self.padding and self.scenario == 'pdfalto':
                        utils.report(f'Will add padding to y-axis coords in string nodes: {self.vpadding}\n---',
                                     "H")
                    elif self.scenario == 'pdflato' and not self.padding:
                        utils.report(f"No modification made to y-axis coords in string nodes\n---", "H")


class TkbToEs():
    def show_warning(self):
        """Display a message."""
        utils.report("===/!\===\nTransferring data from Transkribus to eScriptorium using ALTO files and Aspyre", "W")
        utils.report("is not recommended: Trankribus' ALTO is too poor to guarantee the validity of the", "W")
        utils.report("resulting segments. Instead, use PAGE XML directly!\n===/!\===", "W")

    def __init__(self, args):
        """Handle a Transkribus to eScriptorium transformation scenario

        :param args: essential information to run transformation scenario
        :type args: AspyreArgs object
        """
        self.show_warning()
        if isinstance(args, type(AspyreArgs(test_type=True))):
            self.args = args
            self.args.add_log("Starting Transkribus transformation scenario.")

            # 1. handling zip
            self.unzipped_source = None
            if self.args.source.split(".")[-1] in ARCHIVE_EXTENSIONS:
                if self.args.talkative:
                    utils.report("Source is an archive, running unzipping scenario.\n---", "H")
                self.unzipped_source = zip.unzip_scenario(self.args.source, self.args.scenario)
                if self.unzipped_source is False:
                    self.args.execution_status = "Failed"
                    self.add_log("Something went wrong while unpacking the source.")
                    utils.report("Failing at unpacking the archive, Apsyre can't proceed.\n---", "E")
                else:
                    self.args.add_log("Successfully unzipped source.")
            else:
                if self.args.talkative:
                    utils.report("Source is not an archive.\n---", "H")

            if self.args.proceed():
                # 2. collecting data
                package = utils.list_directory(self.unzipped_source)
                self.image_files = manage_tkbtoes.extract_mets(package, self.unzipped_source)
                self.alto_files = manage_tkbtoes.locate_alto_files(package, self.args.source)

                if len(self.image_files) == 0:
                    self.add_log("There is no reference to images in the METS XML file you provided.")
                    self.add_log("Make sure to check the \"Export Image\" option in Transkribus.")
                    self.args.execution_status = 'Failed'
                    if self.args.talkative:
                        utils.report("Aspyre can't pair unreferenced images with the ALTO XML files", "E")
                        utils.report("Interrupting execution!", "E")
                elif self.alto_files is False:
                    self.args.add_log("Couldn't find any ALTO XML file.")
                    utils.report("Aspyre can't run Transkribus scenario without ALTO XML files.\n---", "E")
                    self.args.execution_status = "Failed"
                else:
                    self.args.add_log("Successfully collected data.\n---")

            if self.args.proceed():
                # 3. transforming files
                if self.args.talkative:
                    iterator = tqdm(self.alto_files, desc="Processing ALTO XML files", unit=' file')
                else:
                    iterator = self.alto_files
                for file in iterator:
                    processed = 0
                    try:
                        manage_tkbtoes.handle_a_file(file, self)
                    except Exception as e:
                        if self.args.talkative:
                            utils.report(f"===[!]===\nError while processing {file} :", "E")
                            print(e)
                        self.args.add_log(f"Failed to process {file}.")
                    else:
                        processed += 1
                if processed == 0:
                    self.args.execution_status = "Failed"
                elif processed < len(self.alto_files):
                    self.args.add_log(f"Successfully transformed {processed} out of {len(self.alto_files)}")
                else:
                    self.args.add_log(f"Successfully processed sources files!")

                if self.args.proceed():
                    # 4. serve a zip file
                    try:
                        zip.zip_dir(self.args.destination, self.unzipped_source)
                    except Exception as e:
                        if self.args.talkative:
                            print(e)
                        self.args.execution_status = "Failed"
                        self.args.add_log('Failed to zip output.')
                    else:
                        self.args.execution_status = 'Finished'
                        self.args.add_log('Aspyre ran Transkribus scenario successufully!')
        else:
            self.args = None
            utils.report("===[!]===\nFailed to run TkbToEs: args must be an AspyreArgs object!", "E")


class PdfaltoToEs():
    def __init__(self, args):
        """Handle a PDFALTO to eScriptorium transformation scenario

        :param args: essential information to run transformation scenario
        :type args: AspyreArgs object
        """
        if isinstance(args, type(AspyreArgs(test_type=True))):
            self.args = args
            self.args.add_log("Starting PDFALTO transformation scenario.")

            # TODO gérer les tar.gz?
            """
            https://stackoverflow.com/questions/30887979/i-want-to-create-a-script-for-unzip-tar-gz-file-via-python

            import tarfile

            if fname.endswith("tar.gz"):
                tar = tarfile.open(fname, "r:gz")
                tar.extractall()
                tar.close()
            elif fname.endswith("tar"):
                tar = tarfile.open(fname, "r:")
                tar.extractall()
                tar.close()
            """

            # 1. handling zip
            self.unzipped_source = None
            if self.args.source.split(".")[-1] in ARCHIVE_EXTENSIONS:
                if self.args.talkative:
                    utils.report("Source is an archive, running unzipping scenario.\n---", "H")
                self.unzipped_source = zip.unzip_scenario(self.args.source, self.args.scenario)
                if self.unzipped_source is False:
                    self.args.execution_status = "Failed"
                    self.add_log("Something went wrong while unpacking the source.")
                    utils.report("Failing at unpacking the archive, Apsyre can't proceed.\n---", "E")
                else:
                    self.args.add_log("Successfully unzipped source.\n---")
            else:
                if self.args.talkative:
                    utils.report("Source is not an archive.\n---", "H")

            if self.args.proceed():
                # 2. collecting data
                package = utils.list_directory(self.unzipped_source)
                self.alto_files, self.image_files = manage_pdfaltotoes.locate_alto_and_image_files(package)
                if self.alto_files is False:
                    self.args.add_log("Couldn't find any XML file or any image file.")
                    utils.report("Aspyre can't run without either of these.\n---", "E")
                    self.args.execution_status = "Failed"
                else:
                    self.args.add_log("Successfully collected data.")

            if self.args.proceed():
                # 3. transforming files
                if self.args.talkative:
                    iterator = tqdm(self.alto_files, desc="Processing ALTO XML files", unit=' file')
                else:
                    iterator = self.alto_files
                for file in iterator:
                    processed = 0
                    try:
                        manage_pdfaltotoes.handle_a_file(file, self)
                    except Exception as e:
                        if self.args.talkative:
                            utils.report(f"Error while processing {file} :", "E")
                            print(e)
                        self.args.add_log(f"Failed to process {file}.")
                    else:
                        processed += 1
                if processed == 0:
                    self.args.execution_status = "Failed"
                elif processed < len(self.alto_files):
                    self.args.add_log(f"Successfully transformed {processed} out of {len(self.alto_files)}")
                else:
                    self.args.add_log(f"Successfully processed sources files!")

            if self.args.proceed():
                # 4. serve a zip file
                try:
                    zip.zip_dir(self.args.destination, self.unzipped_source)
                except Exception as e:
                    if self.args.talkative:
                        print(e)
                    self.args.execution_status = "Failed"
                    self.args.add_log('Failed to zip output.')
                else:
                    utils.report("Task completed ✓", "S")
                    self.args.execution_status = 'Finished'
                    self.args.add_log('Aspyre ran PDFALTO scenario successufully!')

        else:
            self.args = None
            utils.report("Failed to run PdfaltoToEs: args must be an AspyreArgs object!\n===[!]===", "E")

