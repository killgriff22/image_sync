from modules import *

Name = input("What would you like to call the containing folder?:\n>")
if not Name:
    raise Exception("Name is required")
Path = os.path.realpath(os.path.curdir)
tmp = input(
    f"Current path to deploy into: {Path}\nWrite the new path you would like to use\nLeave Blank To Continue\n>")
Path = os.path.join(tmp if tmp else Path, Name)
print(Path)
Url = input(
    "What is the url of the server?\nInclude the port if it has been changed.\n>")
if not Url:
    raise Exception("Url is required")
print("Requesting Availible Trackers...")
Version_Resp = NotImplemented
Inventory_Resp = requests.get(
    f"http://{Url}{':4385' if ':' not in Url else ''}/inventory")
Availible_Trackers = Inventory_Resp.json()
subscribed = []
List_of_Trackers = ""
for i, Tracker in enumerate(Availible_Trackers):
    List_of_Trackers += f"{i+1}: {Tracker}\n"
Message = List_of_Trackers+"Write the number of the tracker you want to subscribe to\nLeave Blank to Continue\nWrite a name that isnt present to create a new tracker\n>"
print(subscribed)
subscribe = input(Message)
while subscribe:
    print(subscribed)
    try:
        int(subscribe)
        if int(subscribe) <= len(Availible_Trackers) and int(subscribe) < 0:
            subscribed.append(Availible_Trackers[int(subscribe)-1])
    except:
        pass
    subscribe = input(Message)
print(f"Deploying into {Path}")
print("Copying files...")
shutil.copytree(os.path.join(os.path.dirname(__file__), "Client"), Path)
print("Customizing files...")
with open(os.path.join(Path, "Client.py"), "w") as f:
    f.write(f"""from classes import *
os.chdir(os.path.dirname(os.path.abspath(__file__)))
Url = "{Url}"
Trackers = {subscribed}
for tracker in Trackers:
  Tracker(tracker, Url).sync()
""")
