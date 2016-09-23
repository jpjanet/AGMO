import os
import subprocess

ll = subprocess.check_output('qstat | grep ncsd_geo',shell=True)
ll = ll.split("\n")
n_runs = len(ll)
for lines in ll:
        this_list  = lines.split()
        if len(this_list) >2:
                this_status = this_list[4]
                this_name = this_list[2]
                print(this_name)
