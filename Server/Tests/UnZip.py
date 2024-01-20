import zipfile
import os

with zipfile.ZipFile("sample.zip", mode="r") as archive:
    for file in archive.namelist():
        print(file)
        archive.extract(file, path="./")
