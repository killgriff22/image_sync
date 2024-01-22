from ssl_context import ssl_context
from classes import *
os.chdir(os.path.dirname(os.path.abspath(__file__)))
app = flask.Flask(__name__)
basepath = "../"


@app.route('/upload', methods=['POST'])
def upload():
    if flask.request.method == 'POST':
        f = flask.request.files['upload_file']
        print(info(f"{flask.request.remote_addr} is uploading {f.filename}"))
        f.save(f"Backup/{f.filename}")
        if f.filename.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(f"Backup/{f.filename}", mode="r") as archive:
                for file in archive.namelist():
                    archive.extract(file, path="Backup/")
            os.remove(f"Backup/{f.filename}")
            print(success(f"Uploaded {f.filename}"))
            return f"Uploaded {f.filename}"
    print(error("Upload failed"))
    return "Upload failed"


@app.route('/request', methods=['POST'])
def request():
    if flask.request.method == 'POST':
        Tracker = flask.request.args.get('Name')
        Errors = eval(flask.request.args.get('Errors'))
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
            'NotFound': [],
            'NotMatch': [],
            'Success': [],
            'NoMatch': []
        }
        hashes_there = flask.request.json
        hashes_here = create_hashes(hashes_there['Name'])
        TrackerName = hashes_there['Name']
        if not os.path.isdir(f"Backup/{TrackerName}"):
            os.mkdir(f"Backup/{TrackerName}")
        files = list(hashes_there.keys())
        files.remove('Name')
        for file in files:
            if not os.path.isfile(f"Backup/{TrackerName}/{file}"):
                Errors['NotFound'].append(
                    f"{file}")
                continue
            if hashes_there[file] != hashes_here[file]:
                Errors['NotMatch'].append(
                    f"{file}")
                continue
            else:
                Errors['Success'].append(
                    f"{file}")
        Errors['NoMatch'] = [
            file for file in hashes_here.keys() if file not in hashes_there.keys()]
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
    return ([dir for dir in os.listdir("Backup") if os.path.isdir(os.path.join("Backup", dir))])


app.run("0.0.0.0", 4385, debug=True)  # , ssl_context=ssl_context)
