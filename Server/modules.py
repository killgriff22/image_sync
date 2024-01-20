import sys
import os
import subprocess
import time
import hashlib
import flask
import json
import zipfile
import os


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
