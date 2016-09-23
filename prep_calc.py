import os

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        print('creating' + dir_path)
        os.makedirs(dir_path)
def get_run_dir():
    rdir = "/home/jp/GA/" 
    return rdir

def translate_job_name(job):
    base = os.path.basename(job)
    base = base.strip("\n")
    base_name = base.strip(".in")
    ll = (str(base)).split("_")
    slot = ll[4]
    gen = int(ll[1])
    gene = str(ll[4]+"_"+ll[5]+"_"+ll[6])
    spin = int(ll[7].rstrip(".in"))
    return gen,slot,gene,spin,base_name


def setup_paths():
    working_dir = get_run_dir()
    path_dictionary = {"out_path"     : working_dir + "outfiles",
                   "job_path"         : working_dir + "jobs",
                   "done_path"        : working_dir + "completejobs",
                   "initial_geo_path" : working_dir + "initial_geo",
                   "optimial_geo_path": working_dir + "optimized_geo",
                   "state_path"       : working_dir + "statespace",
                   "molsimplify_inps" : working_dir + "ms_inps",
                   "infiles"          : working_dir + "infiles",
                   "molsimp_path"     : working_dir + "molSimplify"}
    for keys in path_dictionary.keys():
        ensure_dir(path_dictionary[keys])
    return path_dictionary
def advance_paths(path_dictionary,generation):
    new_dict = dict()
    for keys in path_dictionary.keys():
        if not (keys == "molsimp_path"):
            new_dict[keys] = path_dictionary[keys] + "/gen_" +  str(generation) + "/"
            ensure_dir(new_dict[keys])
    return new_dict
def get_ligands():
    ligands_list =[['thiocyanate',[1,'SCN','S',-1]],
                   ['chloride',[1,'Cl','Cl',-1]],
                   ['water',[1,'H2O','O',0]],
                   ['isothiocyanate',[1,'NCS','N',-1]],
                   ['ammonia',[1,'NH3','N',0]],
                   ['cyanide',[1,'CN','C',-1]],
                   ['carbonyl',[1,'CO','C',0]],
                   ['misc',[1,'C2H3N','S',0]],
                   ['pisc',[1,'pisc','C',0]],
                   ['bipy',[2,'bipy','N',0]],
                   ['phen',[2,'phen','N',0]],
                   ['ox',[2,'ox','O',-2]],
                   ['acac',[2,'acac','O',0]],
                   ['en',[2,'en','O',0]],
                   ['tbuc',[2,'tbuc','O',-2]],
                   ['porphyrin',[4,'porphyrin','N',-2]]]
    return ligands_list


def write_dictionary(dictionary,path):
    emsg =  False
    try:
        with open(path,'w') as f:
            for keys in dictionary.keys():
                f.write(str(keys).strip("\n") + ',' + str(dictionary[keys]) + '\n')
    except:
        emsg = "Error, could not write state space: " + path
    return emsg
def write_summary_list(outcome_list,path):
    emsg =  False
    try:
        with open(path,'w') as f:
            for tups  in outcome_list:
                for items in tups:
                    f.write(str(items) + ',')
                f.write('\n')
    except:
        emsg = "Error, could not write state space: " + path
    return emsg

def read_dictionary(path):
    emsg =  False
    dictionary = dict()
    try:
        with open(path,'r') as f:
            for lines in f:
                ll = lines.split(",")
                key = ll[0]
                value = ll[1].rstrip("\n")
                dictionary[key] = value
    except:
        emsg = "Error, could not read state space: " + path
    return emsg,dictionary
def logger(path, message):
    ensure_dir(path)
    with open(path + '/log.txt', 'a') as f:
        f.write(message + "\n")
def add_jobs(path,list_of_jobs):
    ensure_dir(path)
    with open(path + '/current_jobs.txt', 'w') as f:
        for jobs in list_of_jobs:
            f.write(jobs + "\n")
def load_jobs(path):
    ensure_dir(path)
    list_of_jobs = list()
    if os.path.exists(path + '/current_jobs.txt'):
        with open(path + '/current_jobs.txt', 'r') as f:
            for lines in f:
                list_of_jobs.append(lines)
    return list_of_jobs

