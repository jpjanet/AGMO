import glob
import datetime
import math
import numpy
import subprocess
import argparse
import os
import random
import shutil
from prep_calc import *
from tree_classes import *
from ga_main import *
from process_scf import *
def launch_job(job):
    gen,slot,gene,spin,base_name  = translate_job_name(job)
    subprocess.call('qsub -N' +str(base_name) + '  gibraltar_wrap_GA.sh ' + str(job), shell=True)

def update_current_gf_dictionary(gene,fitness):
     ## set up environment:        
     path_dictionary = setup_paths()
     new_tree = tree_generation('temp tree')
     ## read in info

     new_tree.read_state()
     new_tree.gene_fitness_dictionary.update({gene:fitness})
     logger(path_dictionary['state_path'],str(datetime.datetime.now())
                            + " Gen "+ str(new_tree.status_dictionary['gen']) + " :  updating gene-fitness dictionary")
     ## save
     new_tree.write_state()

def find_current_jobs():
    ## set up environment:        
    path_dictionary = setup_paths()
    ## previously dispatched jobs:
    submitted_job_dictionary = find_submmited_jobs()
    ## live jobs:
    live_job_dictionary = find_live_jobs()

    ## set of jobs to dispatch
    joblist  = load_jobs(path_dictionary["job_path"])
    for jobs in joblist:
        if not (jobs in live_job_dictionary.keys()): ## check the job isn't live
            if not (jobs in submitted_job_dictionary.keys()):
                ## launch
                submitted_job_dictionary.update({jobs:1})
                launch_job(jobs)
            else:
                number_of_attempts = submitted_job_dictionary[jobs]
                if (number_of_attempts <= 3):
                    submitted_job_dictionary.update({jobs: (number_of_attempts+1)})
                    launch_job(jobs)
                else:
                    logger(path_dictionary['state_path'],str(datetime.datetime.now())
                           + " Giving up on job after 3 attempts: : " + str(jobs))
                    gen,slot,gene,spin,base_name  = translate_job_name(jobs)
                    update_current_gf_dictionary(gene,0)
    write_dictionary(submitted_job_dictionary, path_dictionary["job_path"] + "/submitted_jobs.csv")
    return joblist


def find_submmited_jobs():
    path_dictionary = setup_paths()
    if os.path.exists(path_dictionary["job_path"]+"/submmitted_jobs.csv"):
        submitted_job_dictionary = read_dictionary(path_dictionary["job_path"]+"/submmitted_jobs.csv")
    else:
        submitted_job_dictionary = dict()

    return submitted_job_dictionary
def find_live_jobs():
    path_dictionary = setup_paths()
    if os.path.exists(path_dictionary["job_path"]+"/live_jobs.csv"):
        live_job_dictionary = read_dictionary(path_dictionary["job_path"]+"/live_jobs.csv")
    else:
       live_job_dictionary = dict()
    return live_job_dictionary
def analyze_all_current_jobs():

    ## set up environment:        
    path_dictionary = setup_paths()
    ## previously dispatched jobs:
    submitted_job_dictionary = find_submmited_jobs()
    ## live jobs:
    live_job_dictionary = find_live_jobs()

    joblist  = load_jobs(path_dictionary["job_path"])
    all_runs = dict() 
    for jobs in joblist:
        if jobs not in live_job_dictionary.keys():
            print(jobs)
            this_run = test_terachem_sp_convergence(jobs)
            print("is this run conv: ",this_run.converged)
            if this_run.converged == True:
                gen,slot,gene,spin,base_name  = translate_job_name(jobs)
                all_runs.update({base_name:this_run})
    print(all_runs)
    final_results = process_runs(all_runs)
    print(final_results)
    for keys in final_results.keys():
        print(final_results[keys].splitenergy,final_results[keys].fitness)
        update_current_gf_dictionary(keys,final_results[keys].fitness)


