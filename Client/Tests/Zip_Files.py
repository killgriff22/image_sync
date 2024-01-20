import zipfile
import os

with zipfile.ZipFile("sample.zip", mode="r") as archive:
    archive.printdir()
exit()
with zipfile.ZipFile("sample.zip", mode="w") as archive:
    archive.printdir()
    for file in os.listdir("Folder"):
        archive.write(f"Folder/{file}")
    archive.printdir()
