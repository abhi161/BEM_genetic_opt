
from subprocess import Popen, PIPE, STDOUT
import numpy as np
import itertools as itr
import csv
import os  
import numpy as np
import shutil
import statistics
import time
from subprocess import Popen, PIPE, STDOUT
import subprocess


def xfoil_interact(foil, re, alfa_strt, alfa_end, alfa_step):  

    def get_cmd(foil, re, alfa_strt, alfa_end, alfa_step):
        
        if foil is not None:
            load_cmd = 'LOAD ' + foil
        else:
            load_cmd = 'NACA 0012'
        cmd = '''    
        {}
        

        
        OPER
        VISC {}
        ITER
        800
        PACC
        xfoil_executables/re data/{}_{}_SAVE
        
        ASEQ
        {} 
        {}
        {}
        
        '''.format(load_cmd, re, re,naca_name, alfa_strt, alfa_end, alfa_step)
        
        return cmd
    
    p = Popen(['xfoil_executables\\xfoil.exe'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
    process = p.communicate(input=get_cmd(foil=foil, re=re, alfa_strt=alfa_strt, 
                                         alfa_end=alfa_end, 
                                         alfa_step=alfa_step).encode())[0]
 
    return None

######################## PARAMETERS ########################


re_strt = 200000
re_end = 200000
re_step = 1
re_num = int((re_end-re_strt)/re_step) + 1


alfa_strt = 0
alfa_end = 22
alfa_step = 1
alfa_num = int((alfa_end-alfa_strt)/alfa_step)+1

foil = "xfoil_executables\kap38.dat" # None or file name 'example.dat'
folder_path = r"D:\AI\BEM_genetic_opt\xfoil_executables\dat files"
x =len(os.listdir(folder_path))


tbl = np.zeros([int(x*re_num*alfa_num), 4]) # main output in csv
# Generate an array of strings for the new column
new_column = np.array(['string'] * tbl.shape[0])

# Reshape the new column to match the shape of tbl
new_column = np.reshape(new_column, (tbl.shape[0], 1))

# Concatenate the new column to tbl
tbl = np.concatenate(( new_column,tbl), axis=1)
i = 0

re_path =r"xfoil_executables\re data"
# List all files in the folder
file_list = os.listdir(re_path)


for file_name in os.listdir(folder_path):
    if file_name.endswith(".dat"):
        file_path = os.path.join(folder_path, file_name)
    
    naca_name = file_name[:-4] 

    
    ############################################################

    for re in range(re_strt , re_end+re_step, re_step):
        name = str(re)+ "_"+ naca_name+"_"+"SAVE"
        
        file_exists = False

        # Iterate through the files and remove them
        for file_name in file_list:
            if file_name == name:
                print(f"already there {name}")
                file_exists = True

                break
        if not file_exists:
            
            xfoil_interact(file_path, re, alfa_strt, alfa_end, alfa_step)
            i = i + 1
            tbl_end = alfa_num*i
            
            if i == 1:
                tbl_strt = 0
            else:
                tbl_strt = (alfa_num*i-alfa_num)
                
            aa_list = []
            cl_list = []
            cd_list = []
            # print(tbl)
            tbl[tbl_strt:tbl_end,0] = re  # stores set of Reynolds
            tbl[tbl_strt:tbl_end,1] = str(naca_name)
            # print(tbl)
            # Define file paths and names
            file_path = f'xfoil_executables/re data/{re}_{naca_name}_save'

            # Check if the file exists before attempting to open it
            if os.path.exists(file_path):
                aa_list = []
                cl_list = []
                cd_list = []

                try:
                    with open(file_path, 'r') as infile:
                        for x in itr.islice(infile, 12, None):  # ignores first 13 lines
                            if len(x) >= 3:
                                x = x.split()
                                aa_list.append(float(x[0]))
                                cl_list.append(float(x[1]))
                                cd_list.append(float(x[2]))
                except Exception as e:
                    print("An error occurred while processing the file:", str(e))
            else:
                print("File not present:", file_path)
                    
            # Check if any angle is missing and append zeros
            # for angle in range(alfa_strt, alfa_end+1, alfa_step):
            #     if angle not in aa_list:
            #         aa_list.append(angle)
            #         cl_list.append(0.0)
            #         cd_list.append(0.0)
                        
            for angle in range(alfa_strt, alfa_end + 1, alfa_step):
                if angle not in aa_list:
                    aa_list.append(angle)
                    idx_above = None
                    idx_below = None

                    for j, aa in enumerate(aa_list):
                        if aa > angle:
                            idx_above = j
                            break

                    for j in range(len(aa_list) - 1, -1, -1):
                        aa = aa_list[j]
        
                        if aa== angle-1:
                            idx_below = j
                            break

                    if idx_above is not None and idx_below is not None:
                        cl_above = cl_list[idx_above]
                        cl_below = cl_list[idx_below]
                        cd_above = cd_list[idx_above]
                        cd_below = cd_list[idx_below]
                        avg_cl = (cl_above+cl_below)/2
                        avg_cd = (cd_above+cd_below)/2
                        cl_list.append(avg_cl)
                        cd_list.append(avg_cd)
                    elif idx_above is not None:
                        cl_list.append(cl_list[idx_above])
                        cd_list.append(cd_list[idx_above])
                    elif idx_below is not None:
                        cl_list.append(cl_list[idx_below])
                        cd_list.append(cd_list[idx_below])
                    else:
                        cl_list.append(0.0)
                        cd_list.append(0.0)
            
            angle_cl_cd_tuples = list(zip(aa_list, cl_list, cd_list))

            # Sort the list of tuples based on the angle
            sorted_tuples = sorted(angle_cl_cd_tuples, key=lambda x: x[0])
            aa_list = [angle for angle, _, _ in sorted_tuples]
            cl_list = [cl for _, cl, _ in sorted_tuples]
            cd_list = [cd for _, _, cd in sorted_tuples]

            tbl[tbl_strt:tbl_end,2] = aa_list
            tbl[tbl_strt:tbl_end,3] = cl_list
            tbl[tbl_strt:tbl_end,4] = cd_list
       

outfile_path = 'xfoil_executables\output11.csv'

should_write = True
for row in tbl:
    if any("string"  in cell for cell in row):
        should_write = False
        break

if should_write:
    with open(outfile_path, 'a+', newline='') as outfile:
        write = csv.writer(outfile)
        write.writerows(tbl)
else:
    print("Skipped writing due to presence of 'string' in tbl.")