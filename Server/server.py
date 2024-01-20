from ssl_context import ssl_context
from classes import *
app = flask.Flask(__name__)
basepath = "../"


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root(path):
    if "favicon" in flask.request.full_path:
        return ""
    if not os.path.isdir(basepath+path):
        return flask.send_from_directory(basepath, path)
    with open("visits", "r+") as f:
        content = f.read()
        content += f"{flask.request.remote_addr} {flask.request.full_path}\n"
        f.write(content)
    page = f"<a href='..'>..</a><br>"
    for file in os.listdir(basepath+path):
        if file in ['$RECYCLE.BIN', "System Volume Information"]:
            continue
        page += f"<a href='{file}'>{file}</a><br>"
    return page


@app.route('/upload', methods=['POST'])
def upload():
    if flask.request.method == 'POST':
        f = flask.request.files['upload_file']
        f.save(f"Backup/{f.filename}")
        if f.filename.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(f"Backup/{f.filename}", mode="r") as archive:
                for file in archive.namelist():
                    archive.extract(file, path="Backup/")
            os.remove(f"Backup/{f.filename}")
            print(f"Uploaded {f.filename}")
            return f"Uploaded {f.filename}"
    print("Upload failed")
    return "Upload failed"


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


@app.route('/compare', methods=['POST'])
def compare():
    if flask.request.method == 'POST':
        Errors = {
            'NotFound': [],
            'NotMatch': [],
            'Success': [],
            'NoMatch': []
        }
        hashes_there = flask.request.json
        hashes_here = create_hashes(hashes_there['Name'])
        print(hashes_there)
        print(hashes_here)
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
        return Errors
    return "Compare failed"


app.run("0.0.0.0", 4385, debug=True)  # , ssl_context=ssl_context)
