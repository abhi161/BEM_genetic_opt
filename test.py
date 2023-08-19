
from subprocess import Popen, PIPE, STDOUT
import numpy as np
import itertools as itr
import csv
import os  
import numpy as np
import re

def xfoil_interact(foil, reynolds, aoa):

    def get_cmd(foil, reynolds, aoa):
        if foil is not None:
            load_cmd = 'LOAD ' + foil
        else:
            load_cmd = 'NACA 0012'
        cmd = '''    
        {}
        NORM
        OPER
        VISC {}
        ITER
        1100
        ALFA {}
        CPWR cd
        '''.format(load_cmd, reynolds, aoa)
        return cmd

    p = Popen(['xfoil_executables\\xfoil.exe'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout = p.communicate(input=get_cmd(foil=foil, reynolds=reynolds, aoa=aoa).encode())[0]

    # Extract the cd value from the XFOIL output using string parsing
    cd_value = []
    for line in stdout.decode().split('\n'):
        cd_match = re.search(r'CD\s*=\s*([+-]?\d*\.\d+)', line)
      
        if cd_match:
            cd_value.append(float(cd_match.group(1)))
            

    # print("XFOIL Output:")
    # print(stdout.decode())  # Print the full XFOIL output for inspection
    # print("CD Value:", cd_value[-1])  # Print the extracted CD value

    return cd_value[-1]

# Replace 'airfoil.dat' with your airfoil file if available
foil = r'xfoil_executables\dat files\KAP101.dat'
reynolds = 100000
aoa = 18

cd_value = xfoil_interact(foil, reynolds, aoa)
print(f"Drag Coefficient (CD) at {aoa} degrees: {cd_value}")

