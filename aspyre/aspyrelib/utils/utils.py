#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ASPYRE GT utils package

author: Alix Chagué
date: 19/03/2021
"""

import csv
import json
import os

from bs4 import BeautifulSoup
from termcolor import cprint


# ---- I/O
def read_file(path, mode="default"):
    """Open a file and return its content (parsed if possible)
    :param path: (abs) path to the file
    :param mode: "default|json"
    :type path: str
    :type mode: str
    :return: content of the file
    :rtype: str or dict
    """
    if mode == "default":
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    elif mode == "json":
        with open(path, "r", encoding="utf-8") as fh:
            content = json.load(fh)
    elif mode == "csv":
        with open(path, "r", newline="", encoding="utf-8") as fh:
            content = [r for r in csv.reader(fh)]
    elif mode == "xml":
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        content = BeautifulSoup(content, 'xml')
    else:
        content = False
    return content


def write_file(path, content, mode=False):
    """Create/Open a file and write a content in it

    :param path: (abs) path to file
    :param content: content to write in the file
    :param mode: mode (json)
    :type path: str
    :type content: str
    :type mode: str or bool
    :return: None
    """
    if mode is False:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    elif mode == "json":
        # make content JSON serializable
        # transform objects into dictionaries
        content = [obj.__dict__ for obj in content]
        with open(path, "w") as fh:
            json.dump(content, fh)
    else:
        report(f'{mode} is not valid', 'E')


# ---- LOG
def report(message, code_type="I"):
    """Print a (colored) report

    :param message: message to display
    :param code_type: letter code to specify type of report [I]nfo | [W]arning | [E]rror | [S]uccess | [H]ighlight
    :return: None
    """
    if code_type == "I":  # Info
        print(f"[I] {message}")
    elif code_type == "W":  # Warning
        cprint(f"[W] {message}", "yellow")
    elif code_type == "E":  # Error
        cprint(f"[E] {message}", "red")
    elif code_type == "S":  # Success
        cprint(f"[S] {message}", "green")
    elif code_type == "H":  # Highlight
        cprint(f"[H] {message}", "blue")
    else:
        # unknown color parameter, treated as "normal" text
        print(message)


def list_directory(dirpath):
    """Get the list of files and directories contained in a given directory excluding .DS_Store files

    :param dirpath: path to a directory
    :type dirpath: str
    :return: list of absolute paths | None if not a directory
    :retype: list
    """
    files = []
    if os.path.isdir(dirpath):
        files = [os.path.join(os.path.abspath(dirpath), f) for f in os.listdir(dirpath) if f != ".DS_Store"]
    else:
        report(f"{dirpath} is not a directory", "E")
    return files


def path_is_valid(tested_path):
    """Verify if a given path to a directory is valid

    :return: True is the path is valid, False otherwise
    :rtype: bool
    """
    try:
        valid = os.path.isdir(tested_path)
    except Exception as e:
        valid = False
    return valid
