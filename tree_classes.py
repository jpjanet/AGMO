import glob
import math
import numpy
import subprocess
import argparse
import os
import random
import shutil


from prep_calc import * 

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

class octahedral_complex:
    def __init__(self,ligands_list):
        self.free_sites = [1,2,3,4,5,6]
        ### mark 3x bidentate
        self.three_bidentate = False
        self.ready_for_assembly = False
        self.ligands_list=ligands_list
        self.core  = "Mn"
        self.oxidation_state = 2
        self.ax_dent =  False
        self.eq_dent = False
        self.eq_ligands = list()
        self.ax_ligands= list()
        self.ax_inds = list()
        self.eq_inds = list()
    def random_gen(self):
        self._get_random_equitorial()
        self._get_random_axial()
        self._name_self()
    def _name_self(self):
        self.name = str(self.eq_inds[0]) + '_' + str(self.ax_inds[0]) + '_' + str(self.ax_inds[1])
    def copy(self,partner):
         self.ax_dent = partner.ax_dent
         self.ax_inds = partner.ax_inds
         self.ax_ligands = partner.ax_ligands
         self.eq_dent = partner.eq_dent
         self.eq_inds = partner.eq_inds
         self.eq_oc = partner.eq_oc
         self.eq_ligands = partner.eq_ligands
         self.three_bidentate = partner.three_bidentate
         self._name_self()
    def _get_random_equitorial(self):
        ### choose the equitorial ligand
        n = len(self.ligands_list)
        eq_ind = numpy.random.randint(low = 0,high = n)
        eq_ligand_properties  = self.ligands_list[eq_ind][1]
        self.eq_dent = eq_ligand_properties[0]
        self.eq_oc  = int(4/self.eq_dent)
        self.eq_ligands = [self.ligands_list[eq_ind][0] for i in range(0,self.eq_oc)]
        self.eq_inds = [eq_ind]
    def  _get_random_axial(self):
        ### choose axial ligands:
        n = len(self.ligands_list)
        self.ready_for_assembly =  False
        self.ax_ligands = list()
        self.ax_inds = list()
        while not self.ready_for_assembly:
            ax_ind = numpy.random.randint(low = 0,high = n)
            ax_ligand_properties  = self.ligands_list[ax_ind][1]
            ax_dent = ax_ligand_properties[0]
            if ax_dent > 1:
                if ((self.eq_dent == 2) and (ax_dent == 2) and (len(self.ax_ligands) == 0)):
                    three_bidentate  = True
                    self.ax_ligands = [self.ligands_list[ax_ind][0],ligands_list[ax_ind][0]]
                    self.ax_inds = [ax_ind, ax_ind]
                    self.ready_for_assembly = True
                    self.ax_dent = 2
                    self.ax_oc = [2]
                else:
                    self.ready_for_assembly = False
            else:
                self.ax_ligands.append(ligands_list[ax_ind][0])
                self.ax_inds.append(ax_ind)
                if (len(self.ax_ligands) ==2):
                    self.ax_dent = 1
                    self.ax_oc = [1,1]
                    self.ready_for_assembly = True

    def examine(self):
        print("name is " + self.name)
        print("eq", self.eq_ligands, self.eq_inds)
        print("axial", self.ax_ligands, self.ax_inds)

    def encode(self,gene):
        self.random_gen()
        ll = gene.split("_")
        ll = [int(item) for item in ll]
        self.replace_equitorial([ll[0]])
        self.replace_axial(ll[1:])
        self._name_self()

    def replace_equitorial(self,new_eq_ind):
        eq_ligand_properties  = self.ligands_list[new_eq_ind[0]][1]
        self.eq_dent = eq_ligand_properties[0]
        self.eq_oc  = int(4/self.eq_dent)
        self.eq_ligands = [self.ligands_list[new_eq_ind[0]][0] for i in range(0,self.eq_oc)]
        self.eq_inds = new_eq_ind
        if (self.ax_dent == 1) or ((self.ax_dent == 2) and (self.eq_dent ==2)):
                ## everything is ok!
                if (self.ax_dent == 2):
                    self.three_bidentate = True
        else: ## this complex cannot exist. keeping  equitorial,
              ## regenerating axial ligands
           print("complex with" + str(self.eq_ligands) + " and " + str(self.ax_ligands) + " cannot exist, randomizing axial")
           self._get_random_axial()
        self._name_self()

    def replace_axial(self,new_ax_ind):
        self.ax_ligands = list()
        self.ax_inds = list()
        n = len(self.ligands_list)
        #print(new_ax_ind)
        self.three_bidentate =  False
        for i,indices in enumerate(new_ax_ind):
            #print('trying to add ',indices )
            ax_ligand_properties = self.ligands_list[indices][1]
            ax_dent = ax_ligand_properties[0]  
            #print('ax dent ' + str(ax_dent))
            if (ax_dent > 1):
                if (ax_dent == 2) and (i == 0):
                    three_bidentate  = True
                    self.ax_ligands = [self.ligands_list[indices][0],ligands_list[indices][0]]
                    self.ax_inds = [indices, indices]
                    self.ax_dent = 2
                    self.three_bidentate = True
                    break
                else:
                    print('impossible, ax_dent  = ' + str(ax_dent))
            else:
                self.ax_ligands.append(ligands_list[indices][0])
                self.ax_inds.append(indices)
                self.ax_dent = 1

        if (self.three_bidentate) and not (self.eq_dent == 2):
            ## this complex cannot exist
            ## regenerating equitorial ligands
            print("complex with" + str(self.eq_ligands) + " and " + str(self.ax_ligands) +
                  " cannot exist, regenerating equitorial ligands")
            self.ready_for_assembly  = False
            while not self.ready_for_assembly:
                eq_ind = numpy.random.randint(low = 0,high = n)
                eq_ligand_properties  = self.ligands_list[eq_ind][1]
                eq_dent = eq_ligand_properties[0]
                if (eq_dent == 2):
                    self.eq_dent = 2
                    self.eq_inds = [eq_ind]
                    self.eq_oc = int(4/eq_dent)
                    self.eq_ligands = [self.ligands_list[eq_ind][0] for i in range(0,self.eq_oc)]
                    self.ready_for_assembly =  True
        self._name_self()

    def exchange_ligands(self,partner,eq_swap):
        child = octahedral_complex(self.ligands_list)
        child.copy(self) # copies this parent
        print("\n")
        print("swapping from",partner.name," to ",self.name)
        self.examine()
        if eq_swap:
            print("swapping equitorial " + str(child.eq_inds) + ' -> ' + str(partner.eq_inds))
            child.replace_equitorial(partner.eq_inds)
        else:
            print("swapping axial"+ str(child.ax_inds) + ' -> ' + str(partner.ax_inds))
            child.replace_axial(partner.ax_inds)
        child.examine()
        return child


    def mutate(self):
        ## mutates either the axial
        ## or equitorial ligand a random
        lig_to_mutate = random.randint(0,2)
        child = octahedral_complex(self.ligands_list)
        child.copy(self) # copies this parent
        n = len(self.ligands_list)
        self.examine()
        print('I think this is 3xbidentate: ',self.three_bidentate,self.ax_dent)
        if (lig_to_mutate == 0):
            print("mutating equitorial")
            rand_ind = numpy.random.randint(low = 0,high = n)
            child.replace_equitorial([rand_ind])
        else:
            ready_flag = False
            while not ready_flag:
                new_ax_list = list()
                rand_ind = numpy.random.randint(low = 0,high = n)
                ax_ligand_properties  = self.ligands_list[rand_ind][1]
                ax_dent = ax_ligand_properties[0]
                if (ax_dent == self.ax_dent):
                    if (lig_to_mutate == 1):
                        print("mutating axial 1 ")
                        new_ax_list = [rand_ind,self.ax_inds[1]]
                    elif (lig_to_mutate == 2):
                        print("mutating axial 2 ")
                        new_ax_list = [self.ax_inds[0],rand_ind]
                    child.ax_dent = 1
                    child.three_bidentate = False
                    ready_flag = True
                elif (ax_dent  == 2) and (self.ax_dent == 1):
                    ## here, we want to add a bidentate but 
                    ## need to swap the second ligand too
                    print("swapping both axial ")
                    new_ax_list = [rand_ind,rand_ind]
                    child.ax_dent = 2
                    child.three_bidentate = True
                    ready_flag =  True
            print("trying to add " + str(new_ax_list))
            child.replace_axial(new_ax_list)
        child._name_self()
        child.examine()
        return child

    def generate_geometery(self,prefix,spin,path_dictionary,rundirpath,molsimpath):
        ligloc_cont = True

        mol_name = prefix + self.name + "_" + str(spin)
        if self.ax_dent == 1:
           liglist = (str([str(element).strip("'[]'") for element in (self.eq_ligands)]  + [str(element).strip("'[]'") for element in self.ax_ligands]).strip("[]")).replace("'","")
           ligloc = 1

        elif self.ax_dent == 2:
           liglist = (str([str(element).strip("'[]'") for element in (self.eq_ligands)]  + [str(self.ax_ligands[0]).strip("'[]'")]).strip("[]")).replace("'", "") 
           ligloc = 0
        geometry = "oct"
        ms_dump_path = path_dictionary["molsimplify_inps"] +  'ms_output.txt'
        with open(ms_dump_path,'a') as ms_pipe:
            print(molsimpath + 'main.py')
            print(molsimpath + 'main.py')
            print(molsimpath + 'main.py')


            subprocess.call([molsimpath + 'main.py','-core ' + self.core,'-lig ' +liglist,
                     '-rundir ' + rundirpath +'\n','-jobdir temp', '-keepHs yes,yes,yes,yes,yes,yes',
                     '-coord 6','-ligalign 1','-ligloc ' + str(ligloc),'-calccharge yes','-name ' +mol_name + '\n',
                     '-geometry ' + geometry,'-spin ' + str(spin),'-oxstate II',
                             '-qccode TeraChem','-runtyp energy','-method UDFT'],stdout = ms_pipe)
        shutil.move(rundirpath + 'temp/' + mol_name + '.molinp', path_dictionary["molsimplify_inps"] + mol_name + '.molinp')
        shutil.move(rundirpath + 'temp/' + mol_name + '.xyz', path_dictionary["initial_geo_path"] + mol_name + '.xyz')
        jobpath = path_dictionary["job_path"]  + mol_name + '.in'
        with open(jobpath,'w') as newf:
            with open(rundirpath + 'temp/' + mol_name + '.in','r') as oldf: 
                for line in oldf:
                    if not ("coordinates" in line) and (not "end" in line) and not ("scrdir" in line):
                        newf.writelines(line)

#            newf.writelines("min_coordinates cartesian \n")
            newf.writelines("scrdir scr/" + mol_name + "\n")
            os.remove(rundirpath + 'temp/' + mol_name + '.in')
        return jobpath

#print("\n\n\n\n")
#susan = octahedral_complex(ligands_list)
#susan.random_gen()
#susan.examine()
#print("\n ~~~~~~~~~~~~ \n")
#jack = octahedral_complex(ligands_list)
#jack.random_gen()
#jack.examine()
#print("\n ~~~~~~~~~~~~ \n")
#fred = susan.exchange_ligands(jack)
#fred.examine()
#print("\n ~~~~~~~~~~~~ \n")
#fred = susan.exchange_ligands(jack)
#fred.examine()
#print("\n ~~~~~~~~~~~~ \n")
#fred = fred.mutate()
#fred.examine()
#path_dictionary = setup_paths()
#fred.generate_geometery(prefix = "gen_1_",spin = 3,path_dictionary = path_dictionary) 



