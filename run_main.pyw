

def run_main():
    import subprocess as sp
    import shlex
    import webbrowser
    import os
    import sys

    executable = sys.executable
    path_to_main = os.path.join(os.path.dirname(__file__), "main.py")

    
    command = f"streamlit run {path_to_main} --server.headless=true --global.developmentMode=false --server.port=8501"


    #webbrowser.open("http://localhost:8501")
    #os.system(f"start /wait cmd /k {command}")
    os.system(f'cmd /k "{command}"')
    #sp.call(shlex.split(f"{executable} streamlit run {path_to_main} --server.headless=true --global.developmentMode=false"), shell=True)

import ctypes, sys
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
if is_admin():
    # Code of your program here
    run_main()
else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
