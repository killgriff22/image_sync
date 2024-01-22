from ssl_context import ssl_context
from classes import *
os.chdir(os.path.dirname(os.path.abspath(__file__)))
app.run("0.0.0.0", 4385, debug=True)  # , ssl_context=ssl_context)
