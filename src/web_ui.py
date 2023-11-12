#!/usr/bin/env python3.10

##prints out the path to the currently running Python interpreter executable file. 
import sys
print(sys.executable)

import os
import subprocess

def start_web_server():
    web_ui_dir = os.path.join(os.path.dirname(__file__), 'www')
    subprocess.run(['python', '-m', 'http.server', '8080'], cwd=web_ui_dir)

if __name__ == "__main__":
    start_web_server()
