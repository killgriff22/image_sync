from modules import *
import hashlib


class Tracker:
    def __init__(self, name, url="http://localhost:4385"):
        self.Name = name
        self.archivepath = None
        self.url = url

    def __repr__(self) -> str or None:
        return self.archivepath

    def bundle(self, files_to_bundle=None):
        # Create a zip file
        z = zipfile.ZipFile(f'Archives/{self.Name}.zip', "w")
        if files_to_bundle:
            for file in files_to_bundle:
                z.write(self.Name+"/"+file)
            z.close()
            self.archivepath = f'Archives/{self.Name}.zip'
            return
        # Add all files in the directory
        for root, dirs, files in os.walk(self.Name):
            for file in files:
                z.write(os.path.join(root, file))
        # Close the zip file
        z.close()
        # Return the zip file name
        self.archivepath = f'Archives/{self.Name}.zip'

    def create_hashes(self):
        # Create a dictionary for the hashes
        # Create a hash for each file in the in the dir with the same name as self.Name
        hashes = {}
        for root, dirs, files in os.walk(self.Name):
            for file in files:
                hashes[file] = hashlib.md5(
                    open(os.path.join(root, file), 'rb').read()).hexdigest()
        # Return the dictionary
        return hashes

    def sync(self):
        # Create a dictionary for the hashes
        hashes = self.create_hashes()
        hashes['Name'] = self.Name
        # Send the dictionary to the server
        r = requests.post(self.url+"/compare", json=hashes)
        # Return the response
        Errors = r.json()
        return Errors
