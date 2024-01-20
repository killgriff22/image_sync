import sys
import os
import subprocess
import time
import hashlib
import flask
import json


def bundle(name, files_to_bundle=None):
    with open("Backup/Bundler.py", "r+") as f:
        f.write(f"""import zipfile
import os
# Create a zip file
z = zipfile.ZipFile('../Archives/{name}.zip', "w")
if files_to_bundle:
    for file in files_to_bundle:
        z.write(name+"/"+file)
    z.close()
    exit()
# Add all files in the directory
for root, dirs, files in os.walk(name):
    for file in files:
        z.write(os.path.join(root, file))
# Close the zip file
z.close()
""")
        subprocess.run(["python3", "Backup/Bundler.py"])
