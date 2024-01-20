from modules import *
args = sys.argv
pass
if len(args) >= 2:
    name = args[1]
else:
    name = "server.py"
try:
    process = subprocess.Popen(['python3', name])
    while True:
        oldcontent = hash(open(name, "r").read())
        subprocess.check_output(
            ["git", "pull"])
        is_same = hash(open(name, "r").read()) == oldcontent
        if is_same:
            time.sleep(1)
        else:
            oldcontent = hash(open(name, "r").read())
except KeyboardInterrupt:
    process.kill()
    print("Exiting...")
    exit()
