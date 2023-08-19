import os
import csv
import itertools as itr

re_path = r"xfoil_executables\re data"
alfa_strt = 0
alfa_end = 20
alfa_step = 1

outfile_path = 'xfoil_executables\output4.csv'

with open(outfile_path, 'w', newline='') as outfile:
    write = csv.writer(outfile)
    header = ['Reynolds','File', 'Angle', 'Cl', 'Cd']
    write.writerow(header)

    for file_name in os.listdir(re_path):
        re = file_name.split("_")[0]
        naca_name = file_name.split("_")[1]
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

                    if aa == angle - 1:
                        idx_below = j
                        break

                if idx_above is not None and idx_below is not None:
                    cl_above = cl_list[idx_above]
                    cl_below = cl_list[idx_below]
                    cd_above = cd_list[idx_above]
                    cd_below = cd_list[idx_below]
                    avg_cl = (cl_above + cl_below) / 2
                    avg_cd = (cd_above + cd_below) / 2
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

        for angle, cl, cd in sorted_tuples:
            row = [f"{re}",f"{naca_name}", angle, cl, cd]
            write.writerow(row)
