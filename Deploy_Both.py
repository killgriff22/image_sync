import os
if os.path.exists("DevTools"):
    os.rmdir("DevTools")
if input("Would you like to deploy the server? (y/N) ").lower() in ["y"]:
    import Deploy_Server
if input("Would you like to deploy the client? (y/N) ").lower() in ["y"]:
    import Deploy_Client
exit()
