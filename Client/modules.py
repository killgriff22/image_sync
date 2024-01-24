import zipfile
import os
import requests
import json
import shutil
import sys
from tqdm import tqdm


def clear() -> None:
    lines = []
    for i in range(os.get_terminal_size()[1]):
        lines.append(" "*os.get_terminal_size()[0])
    for i, line in enumerate(lines):
        print_at(0, i, line)


def print_at(x, y, content):
    sys.stdout.write(f"\x1b7\x1b[{y+1};{x+1}f{content}\x1b8")
    sys.stdout.flush()
