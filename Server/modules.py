import sys
import os
import subprocess
import time
import hashlib
import flask
import json
import zipfile
import os
from pytonik_ip_vpn_checker.ip import ip
from tqdm import tqdm


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
        for file in tqdm(files):
            hashes[file] = hashlib.md5(
                open(os.path.join(root, file), 'rb').read()).hexdigest()
    # Return the dictionary
    return hashes


def bundle(name, files_to_bundle=None):
    # Create a zip file
    if type(files_to_bundle) == str:
        files_to_bundle = eval(files_to_bundle)
    z = zipfile.ZipFile(f'Archives/{name}.zip', "w")
    if files_to_bundle:
        for file in tqdm(files_to_bundle):
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


app = flask.Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload():
    if flask.request.method == 'POST':
        f = flask.request.files['upload_file']
        print(info(f"{flask.request.remote_addr} is uploading {f.filename}"))
        f.save(f"Backup/{f.filename}")
        if f.filename.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(f"Backup/{f.filename}", mode="r") as archive:
                for file in tqdm(archive.namelist()):
                    archive.extract(file, path="Backup/")
            os.remove(f"Backup/{f.filename}")
            print(success(f"Uploaded {f.filename}"))
            return f"Uploaded {f.filename}"
    print(error("Upload failed"))
    return "Upload failed"


@app.route('/request', methods=['POST'])
def request():
    if flask.request.method == 'POST':
        Tracker = flask.request.json['Name']
        Errors = flask.request.json['Errors']
        bundle(Tracker, Errors if Errors != [] else None)
        print(lightblue(f"Requested {len(Errors)} from {Tracker}"))
        return flask.send_file(f"Archives/{Tracker}.zip")
    print(error("Request failed"))
    return "Request failed"


@app.route('/compare', methods=['POST'])
def compare():
    if flask.request.method == 'POST':
        print(warn(f"Comparing hashes with {flask.request.remote_addr}"))
        Errors = {
            'NotFound': set(),
            'NotMatch': set(),
            'Success': set(),
            'NoMatch': set()
        }
        hashes_there = flask.request.json
        TrackerName = hashes_there['Name']
        hashes_here = create_hashes(TrackerName)
        hash_set = set(list(hashes_here.keys()))
        if not os.path.isdir(f"Backup/{TrackerName}"):
            os.mkdir(f"Backup/{TrackerName}")
        files = set(list(hashes_there.keys()))
        files.remove('Name')
        Errors['NotFound'] = files - hash_set
        Errors['NoMatch'] = hash_set - files
        for file in hash_set & files:
            if hashes_here[file] != hashes_there[file]:
                Errors['NotMatch'].add(file)
            else:
                Errors['Success'].add(file)
        print(success(f"Compared hashes with {flask.request.remote_addr}"))
        copy = Errors.copy()
        copy.pop('Success')
        for key in copy:
            print(f"{key}: {len(Errors[key])}")
        return Errors
    print(error("Compare failed"))
    return "Compare failed"


@app.route("/inventory")
def listall():
    return [dir for dir in os.listdir("Backup") if os.path.isdir(os.path.join("Backup", dir))]


block_all = False


def get_location(ip_):
    obj = ip()
    obj.property(ip_)
    location_data = {
        "IP": ip_,
        "City": obj.city,
        "Country": obj.country,
        "Region": obj.region,
        "Is_VPN": obj.is_vpn
    }
    return location_data


@app.route("/")
@app.route("/<path>")
def Nothing(path):
    return "", 404


@app.route("/blockoff", methods=['POST'])
def blockalloff():
    if "auth" in flask.request.json.keys():
        if flask.request.json['auth'] == "thisisx-xburnme<3":
            block_all = False
            return str(block_all), 200
    return "Bad Auth", 403


@app.route("/blockon", methods=['POST'])
def blockallon():
    if "auth" in flask.request.json.keys():
        if flask.request.json['auth'] == "thisisx-xburnme<3":
            block_all = True
            return str(block_all), 200
    return "Bad Auth", 403


@app.before_request
def before_request_func():
    with open("blacklist", "r") as f:
        lines = f.readlines()
#    return f"Please do not interact with this domain!<br>"
        for i, line in enumerate(lines[:]):
            lines[i] = line.strip()
        if flask.request.remote_addr in lines or flask.request.path in ['', '/'] or (block_all and not 'block' in flask.request.path):
            return f"This domain has blocked you.<br>\n{get_location(flask.request.remote_addr)}", 418


@app.route('/blacklist', methods=['POST'])
def blacklist():
    if 'ips' in flask.request.json.keys():
        with open(blacklist, "+a") as f:
            if f.read()[-1] != "\n":
                f.write("\n")
            for ip in flask.request.json['ips']:
                f.write(f"{ip}\n")
        return f"added {len(flask.request.json['ips'])} ip{'s' if len(flask.request.json['ips']) > 1 else ''} to blacklist"
    return "Please add at least one ip to block", 500
