from ssl_context import ssl_context
import flask
import os
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
        f = flask.request.files['file']
        f.save(f"Backup/{f.filename}")
        return f"Uploaded {f.filename}"
    return "Upload failed"


app.run("0.0.0.0", 4385, ssl_context=ssl_context, debug=True)
