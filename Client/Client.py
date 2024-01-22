from classes import *
os.chdir(os.path.dirname(os.path.abspath(__file__)))
defualt_url = "http://raspberrypi:4385"
TestDir = Tracker('TrackerName', defualt_url)
TestDir.sync()
