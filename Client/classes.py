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
        print("Creating hashes...")
        hashes = self.create_hashes()
        hashes['Name'] = self.Name
        # Send the dictionary to the server
        print("Sending hashes...")
        r = requests.post(self.url+"/compare", json=hashes)
        # Return the response
        print(f"Server Responded. {r.status_code}")
        Errors = r.json()
        print(
            f"Sending: {Errors['NotFound']+Errors['NotMatch']}\nReciving: {Errors['NoMatch']}")
        # print what percent of our files are present on the server
        print(
            f"Percent of files on the server: {round(100*(len(Errors['NotFound'])+len(Errors['NotMatch']))/len(hashes), 2)}%")
        # Bundle the files that are not on the server
        if not Errors['NotFound'] and not Errors['NotMatch']:
            return True
        print("Bundling files...")
        self.bundle(Errors['NotFound']+Errors['NotMatch'])
        # Send the bundle to the server
        print("Sending bundle...")
        files = {'upload_file': open(self.archivepath, 'rb')}
        r = requests.post(self.url+"/upload", files=files)
        print(f"Server Responded. {r.status_code}")
        # request the files we dont have (Not Implemented)
        if not Errors['NoMatch']:
            return True
        print("Requesting files...")
        self.request(Errors)
        print("Final Hash Check...")
        hashes = self.create_hashes()
        hashes['Name'] = self.Name
        # Send the dictionary to the server
        r = requests.post(self.url+"/compare", json=hashes)
        print(f"Server Responded. {r.status_code}")
        # Return the response
        Errors = r.json()
        Errors.pop('Success')
        # check if all the entries in Errors are empty
        if all([Errors[key] == [] for key in Errors]):
            return True

    def request(self, Errors: dict):
        if not Errors['NoMatch']:
            return
        args = {
            'Name': self.Name,
            'Errors': str(Errors['NoMatch'])
        }
        print(args)
        r = requests.post(self.url+"/request", params=args,
                          stream=True, allow_redirects=True)
        open('files.zip', 'wb').write(r.content)
        # unzip the files
        with zipfile.ZipFile('files.zip', mode="r") as archive:
            for file in archive.namelist():
                archive.extract(file)
        # remove the zip file
        os.remove('files.zip')
        # copy the recived files into the Tracker
        # you can find the recived files in the Backup folder
        for file in Errors['NoMatch']:
            shutil.copy(f"Backup/{self.Name}/{file}", self.Name)
        # remove the Backup folder
        shutil.rmtree(f"Backup/")
