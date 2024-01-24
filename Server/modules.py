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
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class Back:
    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"


RESET = "\033[0m"


def info(message: str) -> None:
    return f"{Fore.BLACK}{Back.BLUE}{message}{RESET}"


def warn(message: str) -> None:
    return f"{Fore.BLACK}{Back.YELLOW}{message}{RESET}"


def error(message: str) -> None:
    return f"{Fore.BLACK}{Back.RED}{message}{RESET}"


def success(message: str) -> None:
    return f"{Fore.BLACK}{Back.GREEN}{message}{RESET}"


def lightblue(message: str) -> None:
    return f"{Fore.BLACK}{Back.CYAN}{message}{RESET}"


def create_hashes(TrackerName):
    # Create a dictionary for the hashes
    # Create a hash for each file in the in the dir with the same name as self.Name
    hashes = {}
    for root, dirs, files in os.walk(f"Backup/{TrackerName}"):
        for file in files:
            hashes[file] = hashlib.md5(
                open(os.path.join(root, file), "rb").read()
            ).hexdigest()
    # Return the dictionary
    return hashes


def bundle(name, files_to_bundle=None):
    # Create a zip file
    if type(files_to_bundle) == str:
        files_to_bundle = eval(files_to_bundle)
    z = zipfile.ZipFile(f"Archives/{name}.zip", "w")
    if files_to_bundle:
        for file in files_to_bundle:
            z.write("Backup/" + name + "/" + file)
        z.close()
        return
    # Add all files in the directory
    for root, dirs, files in os.walk(name):
        for file in files:
            z.write(os.path.join(root, file))
    # Close the zip file
    z.close()
    return


app = flask.Flask(__name__)

@app.route("/remove", methods=["POST"])
def remove():
    if flask.request.method == "POST":
        TrackerName = flask.request.json["Name"]
        Files_to_remove = flask.request.json["Files"]
        Errors = {"Client":[],"Server":[]}
        print(warn(f"Removing {len(Files_to_remove)} files from {TrackerName}"))
        for i,file in enumerate(Files_to_remove):
            if os.path.isfile(f"Backup/{TrackerName}/{file}"):
                os.remove(f"Backup/{TrackerName}/{file}")
                print(success(f"Removed {i}/{len(Files_to_remove)} from {TrackerName}"))
            else:
                Errors["Client"].append(f"Client gave bad filename {file}")
        return Errors
    print(error("Remove failed"))
    return "Remove failed"

@app.route("/upload", methods=["POST"])
def upload():
    if flask.request.method == "POST":
        f = flask.request.files["upload_file"]
        print(info(f"{flask.request.remote_addr} is uploading {f.filename}"))
        f.save(f"Backup/{f.filename}")
        if f.filename.endswith(".zip"):
            with zipfile.ZipFile(f"Backup/{f.filename}", mode="r") as archive:
                for file in archive.namelist():
                    archive.extract(file, path="Backup/")
            os.remove(f"Backup/{f.filename}")
            print(success(f"Uploaded {f.filename}"))
            return f"Uploaded {f.filename}"
    print(error("Upload failed"))
    return "Upload failed"


@app.route("/request", methods=["POST"])
def request():
    if flask.request.method == "POST":
        Tracker = flask.request.json["Name"]
        Errors = flask.request.json["Errors"]
        bundle(Tracker, Errors if Errors != [] else None)
        print(lightblue(f"Requested {len(Errors)} from {Tracker}"))
        return flask.send_file(f"Archives/{Tracker}.zip")
    print(error("Request failed"))
    return "Request failed"


@app.route("/compare", methods=["POST"])
def compare():
    if flask.request.method == "POST":
        print(warn(f"Comparing hashes with {flask.request.remote_addr}"))
        Errors = {"NotFound": [], "NotMatch": [], "Success": [], "NoMatch": []}
        hashes_there = flask.request.json
        hashes_here = create_hashes(hashes_there["Name"])
        TrackerName = hashes_there["Name"]
        if not os.path.isdir(f"Backup/{TrackerName}"):
            os.mkdir(f"Backup/{TrackerName}")
        files = list(hashes_there.keys())
        files.remove("Name")
        for file in files:
            if not os.path.isfile(f"Backup/{TrackerName}/{file}"):
                Errors["NotFound"].append(f"{file}")
                continue
            if hashes_there[file] != hashes_here[file]:
                Errors["NotMatch"].append(f"{file}")
                continue
            else:
                Errors["Success"].append(f"{file}")
        Errors["NoMatch"] = [
            file for file in hashes_here.keys() if file not in hashes_there.keys()
        ]
        print(success(f"Compared hashes with {flask.request.remote_addr}"))
        copy = Errors.copy()
        copy.pop("Success")
        for key in copy:
            print(f"{key}: {len(Errors[key])}")
        return Errors
    print(error("Compare failed"))
    return "Compare failed"


@app.route("/inventory")
def listall():
    return [
        dir
        for dir in os.listdir("Backup")
        if os.path.isdir(os.path.join("Backup", dir))
    ]
