import sys
import os
import subprocess
import time
import hashlib
import flask
import json
import zipfile
import os


class Fore:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'


class Back:
    BLACK = '\033[40m'
    RED = '\033[41m'
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    BLUE = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN = '\033[46m'
    WHITE = '\033[47m'


RESET = '\033[0m'


def info(message: str) -> None:
    return (f"{Fore.BLACK}{Back.BLUE}{message}{RESET}")


def warn(message: str) -> None:
    return (f"{Fore.BLACK}{Back.YELLOW}{message}{RESET}")


def error(message: str) -> None:
    return f"{Fore.BLACK}{Back.RED}{message}{RESET}"


def success(message: str) -> None:
    return (f"{Fore.BLACK}{Back.GREEN}{message}{RESET}")


def lightblue(message: str) -> None:
    return (f"{Fore.BLACK}{Back.CYAN}{message}{RESET}")


def create_hashes(TrackerName):
    # Create a dictionary for the hashes
    # Create a hash for each file in the in the dir with the same name as self.Name
    hashes = {}
    for root, dirs, files in os.walk(f'Backup/{TrackerName}'):
        for file in files:
            hashes[file] = hashlib.md5(
                open(os.path.join(root, file), 'rb').read()).hexdigest()
    # Return the dictionary
    return hashes


def bundle(name, files_to_bundle=None):
    # Create a zip file
    z = zipfile.ZipFile(f'Archives/{name}.zip', "w")
    if files_to_bundle:
        for file in files_to_bundle:
            z.write("Backup/"+name+"/"+file)
        z.close()
        return
    # Add all files in the directory
    for root, dirs, files in os.walk(name):
        for file in files:
            z.write(os.path.join(root, file))
    # Close the zip file
    z.close()
    return
