try:
    from modules import *
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Trackers = []
    Port = 4385
    Name = input("What would you like to call the containing folder?:\n>")
    if not Name:
        raise Exception("Name is required")
    if input("Would you like to change the port? (y/N) (defualt:4385) ").lower() in ["y"]:
        Port = int(input("Enter the port: "))
    Location = os.path.dirname(os.path.abspath(__file__))
    if input(f"Current Path: {Location}\nWould you like to change the location? (y/N) ").lower() in ["y"]:
        Location = input("Enter the path: ")
    print(f"Current Trackers: {Trackers}\nLeave Blank to Continue")
    Tracker_Name = input("What would you like to call the tracker?: ")
    while Tracker_Name:
        Trackers.append(Tracker_Name)
        print(f"Current Trackers: {Trackers}\nLeave Blank to Continue")
        Tracker_Name = input("What would you like to call the tracker?: ")
    use_ssl = input("Would you like to use SSL? (y/N) ").lower() in ["y"]
    if use_ssl:
        print("You can leave these blank and it will defualt to Certs/Key.pem and Certs/Cert.pem")
        print("These can also be changed in the ssl_context.py file")
        Key_Path = input("Enter the path to the key: ")
        Cert_Path = input("Enter the path to the cert: ")
        if Key_Path == "":
            Key_Path = "Certs/Key.pem"
        if Cert_Path == "":
            Cert_Path = "Certs/Cert.pem"
        print("Generating SSL Context...")
        with open("Server/ssl_context.py", "w") as f:
            f.write(f"""ssl_context = (
        '{Cert_Path}',
        '{Key_Path}'
    )""")
        print("SSL Context Generated")
    print("Generating Server...")
    with open("Server/server.py", "w") as f:
        f.write(f"""from classes import *
{'from ssl_context import ssl_context' if use_ssl else ''}
app.run('0.0.0.0', {Port}, debug=True{' , ssl_context=ssl_context' if use_ssl else ''})
    """)
    print("Server Generated")
    if Port in [80, 443]:
        print("You will need to run this as root")
    print(f"Deploying Server into {Location}")
    for tracker in Trackers:
        print(f"Adding Tracker {tracker}")
        os.mkdir(os.path.join(os.path.join("Server", "Backup"), tracker))
    print("Copying files...")
    shutil.copytree("Server", os.path.join(Location, Name))
    print("Cleaning Up...")
    shutil.rmtree("Server")
except Exception as e:
    print("An Error Occured")
    print(e)
    input("Press Enter to Exit")
    for tracker in Trackers:
        print(f"removing Tracker {tracker}")
        os.rmdir(os.path.join(os.path.join("Server", "Backup"), tracker))
    try:
        print("Removing Server")
        shutil.rmtree(os.path.join(Location, Name))
    except:
        print("Server not found")
    try:
        os.remove("Server/server.py")
    except:
        print("server.py not found")
    try:
        os.remove("Server/ssl_context.py")
    except:
        print("ssl_context.py not found")
    exit()
