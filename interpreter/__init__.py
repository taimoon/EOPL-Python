import sys
from os import getcwd

def add_path(p:str) -> None:
    if p not in sys.path:
        sys.path.append(p)

add_path(getcwd())
