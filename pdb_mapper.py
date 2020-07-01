#!/usr/bin/env python3

## Import built-in libraries
import os, sys, gzip
from pymol import cmd
from Bio.Data.IUPACData import protein_letters_3to1
from Bio.PDB import *

## Header
__author__ = "Gurdeep Singh"
__license__ = "GPL"
__email__ = "gurdeep330@gmail.com"

#query = 'P0DTD8'
query = 'P0DTC2'
motif = 'Arm_LIG_1-37'
#motif = 'DOC_MAPK_MEF2A_6'
domain = 'Arm'
#domain = 'PF00069'
startm = 812
#startm = 1211
endm = 815
#endm = 1220
#pdb = '4mz5'
source = '3DID'
#source = 'ELM'


## Make an output folder
outdir = 'output/'+query+'+'+motif+'+'+domain+'/'
if os.path.isdir(outdir) == False:
    os.system('mkdir '+outdir)

fasta = ''
for line in open('../covid19/data/fasta_ncbi/covid_fasta/'+query+'.fasta', 'r'):
    if line[0] != '>':
        fasta += line.replace('\n', '')

match = fasta[startm-1:endm]
print (match)
#sys.ext()

def run_blast(query, pdbs, domain, motif):
    fasta = ''
    for pdb in pdbs:
        parser = PDBParser()
        if True:
            #print (pdb)
            for chains in pdbs[pdb]['chains']:
                for gprotein_chain in chains:
                    structure = parser.get_structure(pdb, 'pdbs/'+pdb+'.pdb')
                    for model in structure:
                        for chain in model:
                            if (chain.id == gprotein_chain):
                                fasta += '>'+pdb+'_'+gprotein_chain+'\n'
                                for residue in chain:
                                    for atom in residue:
                                        if (atom.id == 'CA'):
                                            if residue.id[0] == ' ':
                                                #print (pdb, chain.id, residue.get_resname(), residue.id)
                                                AA = protein_letters_3to1[residue.get_resname()]
                                                fasta += AA
                                fasta += '\n'

                                #print (fasta)
                                #open('../../data/i2/input_'+pdb+'_'+gprotein_chain+'.txt', 'w').write(fasta)
                                #sys.exit()
    print (fasta)
    open(outdir+query+'_pdb.fasta', 'w').write(fasta)
    os.system('makeblastdb -in '+outdir+query+'_pdb.fasta -dbtype "prot" -out '+outdir+query+'_pdb -title '+outdir+query+'_pdb')
    os.system('blastp -query ../covid19/data/fasta_ncbi/covid_fasta/'+query+'.fasta -db '+outdir+query+'_pdb -out '+outdir+'blastp.txt')

def extract_fasta_from_pdb(pdb, new_elm_pdbs):
    fasta = ''
    parser = PDBParser()
    for chain_set in [new_elm_pdbs[pdb]['chains'], new_elm_pdbs[pdb]['domain_chains']]:
        print (pdb, new_elm_pdbs[pdb]['chains'], new_elm_pdbs[pdb]['domain_chains'])
        for given_chain in chain_set:
            structure = parser.get_structure(pdb, 'pdbs/'+pdb+'.pdb')
            for model in structure:
                for chain in model:
                    if (chain.id == given_chain):
                        fasta += '>'+pdb+'_'+given_chain+'\n'
                        for residue in chain:
                            for atom in residue:
                                if (atom.id == 'CA'):
                                    if residue.id[0] == ' ':
                                        print (pdb, chain.id, residue.get_resname(), residue.id)
                                        AA = protein_letters_3to1[residue.get_resname()]
                                        fasta += AA
                        fasta += '\n'
    #print ('hello')
    #print (fasta)
    #sys.exit()
    return (fasta)

def filter_pdbs(elm_pdbs, domain):
    new_elm_pdbs = {}
    for line in gzip.open('/home/gurdeep/projects/DB/SIFTS/pdb_chain_pfam.tsv.gz', 'rt'):
        pdb = line.split()[0].upper()
        pfam = line.split()[3]
        chain = line.split()[1]
        #print (pfam)
        if pdb in elm_pdbs:
            print (pdb, domain)
            if pdb not in new_elm_pdbs:
                new_elm_pdbs[pdb] = {}
                new_elm_pdbs[pdb]['chains'] = []
                new_elm_pdbs[pdb]['domain_chains'] = []
            if pfam == domain:
                new_elm_pdbs[pdb]['domain_chains'].append(chain)
            ## All chains
            new_elm_pdbs[pdb]['chains'].append(chain)
    '''
    for pdb in new_elm_pdbs:
        if os.path.isfile('pdbs/'+pdb+'.pdb') == False:
            os.system('wget https://files.rcsb.org/view/'+pdb+'.pdb -O '+'pdbs/'+pdb+'.pdb')
        extract_fasta_from_pdb(pdb, new_elm_pdbs)
    '''
    run_blast(query, new_elm_pdbs, domain, motif)
    return (new_elm_pdbs)
    #print (fasta)

    #sys.exit()


pdbs={}
if source == '3DID':
    flag  = 0
    for line in gzip.open('/home/gurdeep/projects/DB/3did/3did_dmi_flat.gz', 'rt'):
        if line.split()[0] == '#=ID':
            pdbs = {}
            if line.split()[1] == domain and line.split()[3] == motif:
                flag = 1
        elif line.split()[0] == '#=3D' and flag == 1:
            pdb = line.split()[1].upper()
            if pdb not in pdbs:
                pdbs[pdb] = {}
                pdbs[pdb]['motif_chains'] = []
                pdbs[pdb]['domain_chains'] = []
            pdbs[pdb]['motif_chains'].append(line.split()[3])
            pdbs[pdb]['domain_chains'].append(line.split()[2])
            if os.path.isfile('pdbs/'+pdb+'.pdb') == False:
                os.system('wget https://files.rcsb.org/view/'+pdb+'.pdb -O '+'pdbs/'+pdb+'.pdb')
        elif line[:2] == '//' and flag == 1:
            print (pdbs)
            #run_blast(query, pdbs, domain, motif)
            flag = 0
            break
elif source == 'ELM':
    elm_pdbs = []
    for line in open('/home/gurdeep/projects/DB/ELM/elm_instances.tsv', 'r'):
        if line[0] != '#':
            if line.split('\t')[2].replace('"', '') == motif:
                #print (line)
                elm_pdbs += line.split('\t')[11].replace('"', '').split()
    print (elm_pdbs)
    pdbs = filter_pdbs(elm_pdbs, domain)
    #sys.exit()

## Function to map positions of PDB-AA to its residues numbers in the PDB file
def reassign_pdb(pdb, given_chain):
    parser = PDBParser()
    structure = parser.get_structure(pdb, 'pdbs/'+pdb+'.pdb')
    map = {}
    for model in structure:
        for chain in model:
            if (chain.id == given_chain):
                num = 0
                for residue in chain:
                    for atom in residue:
                        if (atom.id == 'CA'):
                            #print (residue.id)
                            if residue.id[0] == ' ':
                                map[num] = int(residue.id[1])
                                num += 1
                                #print (pdb, chain.id, residue.get_resname(), residue.id)
                break
    return map

'''
flag = 1
dic = {}
#print (len(dic))
#print (domain, motif)
for line2 in open(outdir+'blastp.txt', 'r'):
    if len(line2.split()) >= 1:
        if 'No hits found' in line2:
            flag = 0
            break
        elif line2[0] == '>' and len(dic) == 0:
            #print (motif, domain, startm, endm)
            #print (line2)
            pdb = line2.split('>')[1].split('_')[0]
            chain = line2.split('_')[1].replace('\n', '')
            #print (chain)
            dic = {}
            #break
        elif line2[0] == '>' and len(dic) != 0:
            exit_blastp = 0
            for position in range(startm, endm+1):
                if position in dic:
                    exit_blastp = 1
                    break
            if exit_blastp == 1:
                break
            else:
                dic = {}
                pdb = line2.split('>')[1].split('_')[0]
                chain = line2.split('_')[1].replace('\n', '')
                continue
        elif line2.split()[0] == 'Query':
            startq = int(line2.split()[1])
            endq = int(line2.split()[-1].replace('\n', ''))
            query = line2.split()[2]
        elif line2.split()[0] == 'Sbjct':
            starts = int(line2.split()[1])
            ends = int(line2.split()[-1].replace('\n', ''))
            sbjct = line2.split()[2]
            for num, (q, s) in enumerate(zip(query, sbjct)):
                if q not in ['.', '-'] and s not in ['.', '-']:
                    dic[startq + num] = starts + num

print (domain, motif, pdb, chain, startm, endm, dic)
## Remove the motif chains from domain_chains if the source is ELM
for given_pdb in pdbs:
    if given_pdb == pdb:
        for num, given_chain in enumerate(pdbs[given_pdb]['domain_chains']):
            if given_chain == chain:
                pdbs[given_pdb]['domain_chains'].pop(num)
                print ('removed', chain, given_pdb)

#sys.exit()
if len(dic) == 0:
    print ('No match found')
    sys.exit()
else:
    #print (dic)
    exit_blastp = 0
    for position in range(startm, endm+1):
        if position in dic:
            exit_blastp = 1
            break
    if exit_blastp == 1:
        print (motif, domain, startm, endm)
        print (dic)
    else:
        print ('No match found')
        sys.exit()

map = reassign_pdb(pdb, chain)
'''
## Pymol starts from here
#pdb = '6mnl'
print (pdb)
print (chain, pdbs[pdb]['domain_chains'][0])
dom_chain = pdbs[pdb]['domain_chains'][0].split(':')[0]
dom_chain_res = pdbs[pdb]['domain_chains'][0].split(':')[1]
mot_chain = pdbs[pdb]['motif_chains'][0].split(':')[0]
mot_chain_res = pdbs[pdb]['motif_chains'][0].split(':')[1]
cmd.load('pdbs/'+pdb.upper()+'.pdb')
cmd.fab(match, 'query_motif')
cmd.hide('everything')
cmd.show('cartoon', 'chain '+str(mot_chain)+'+'+str(dom_chain))
cmd.show('cartoon', 'query_motif')
cmd.color('red', 'chain '+mot_chain)
cmd.color('grey', 'chain '+str(dom_chain))
cmd.color('yellow', 'query_motif')
cmd.select('struc_motif', 'resi '+mot_chain_res+' and chain '+mot_chain)
cmd.color('cyan', 'struc_motif')
cmd.color('orange', 'resi '+dom_chain_res+' and chain '+dom_chain)
cmd.super('query_motif', 'struc_motif')
cmd.center('struc_motif')
#select  struct, resi 11-15 and chain C
#cmd.color('yellow', 'chain B')
#cmd.color('red', 'resi '+str(map[dic[startm]])+'-'+str(map[dic[endm]]))
#cmd.color('yellow', 'resi '+str(int_chain_res))
#cmd.label('mot, i. '+str(map[dic[startm]])+' and n. CA and chain '+chain, 'motif')
#cmd.label('dom, i. '+str(int_chain_res.split('-')[0])+' and n. CA and chain '+int_chain, 'domain')