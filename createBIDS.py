#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A short script that will convert raw DICOM files into to NIFTI.GZ, and then create a BIDS compatible structure (https://bids.neuroimaging.io/)
Created By: Or Duek, February 2019
Updated by: Ziv Ben-Zion, April 2024
"""

# convert to NIFTI
import os
import glob
import json
import os
from nipype.interfaces.dcm2nii import Dcm2niix
import shutil


# %% Convert functions Converts DICOM to NIFTI.GZ
def convert(source_dir, output_dir, subName,
            session):  # this is a function that takes input directory, output directory and subject name and then converts everything accordingly
    output_dir = os.path.join(os.path.join(output_dir, subName), session)
    try:
        os.makedirs(output_dir)
    except:
        print("folder already there")
    #    try:
    #       os.makedirs(os.path.join(output_dir, subName, ))
    #    except:
    #       print("Folder Exist")
    converter = Dcm2niix()
    converter.inputs.source_dir = source_dir
    converter.inputs.compression = 7
    converter.inputs.output_dir = output_dir
    converter.inputs.out_filename = subName + '_%d , %a, %c'
    converter.run()


# %% Check functions
def checkGz(extension):
    # check if nifti gz or something else
    if extension[1] == '.gz':
        return '.nii.gz'
    else:
        return extension[1]


def checkTask(filename):
    sep = 'bold'
    rest = filename.split(sep)[1]  # takes the last part of filename
    taskName = rest.split('.', 1)[0]
    if taskName.find('(MB4iPAT2)') != -1:  # if the filename contains these words - remove it
        taskName = taskName.split(
            '(MB4iPAT2)')  # this is the part that will be omitted from the file name. If you have an extra - you should add that too.
        taskName = taskName[0] + taskName[1]  # cmobine toghether

    return taskName.replace("_", "")


# %%
def organizeFiles(output_dir, subName, session):
    fullPath = os.path.join(output_dir, subName, session)
    os.makedirs(fullPath + '/dwi')
    os.makedirs(fullPath + '/anat')
    os.makedirs(fullPath + '/func')
    os.makedirs(fullPath + '/misc')

    a = next(os.walk(fullPath))  # list the subfolders under subject name

    # run through the possibilities and match directory with scan number (day)
    for n in a[2]:
        print(n)
        b = os.path.splitext(n)
        # add method to find (MB**) in filename and scrape it
        if n.find('diff') != -1:
            print('This file is DWI')
            shutil.move((fullPath + '/' + n), fullPath + '/dwi/' + n)
            os.rename((os.path.join(fullPath, 'dwi', n)),
                      (fullPath + '/' + 'dwi' + '/' + subName + '_' + session + '_dwi' + checkGz(b)))

        elif n.find('MPRAGE') != -1:
            print(n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath, 'anat', n),
                      (fullPath + '/anat/' + subName + '_' + session + '_acq-mprage_T1w' + checkGz(b)))
        elif n.find('t1_flash') != -1:
            print(n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath, 'anat', n),
                      (fullPath + '/anat/' + subName + '_' + session + '_acq-flash_T1w' + checkGz(b)))
        elif n.find('t1_fl2d') != -1:
            print(n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath, 'anat', n),
                      (fullPath + '/anat/' + subName + '_' + session + '_acq-fl2d1_T1w' + checkGz(b)))
        elif n.find('GRE_3D_Sag_Spoiled') != -1:
            print(n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath, 'anat', n),
                      (fullPath + '/anat/' + subName + '_' + session + '_acq-gre_spoiled_T1w' + checkGz(b)))
        elif n.find('bold') != -1:
            print(n + ' Is functional')
            taskName = checkTask(n)
            shutil.move((fullPath + '/' + n), (fullPath + '/func/' + n))
            os.rename(os.path.join(fullPath, 'func', n),
                      (fullPath + '/func/' + subName + '_' + session + '_task-' + taskName + '_bold' + checkGz(b)))
        else:
            print(n + 'Is MISC')
            shutil.move((fullPath + '/' + n), (fullPath + '/misc/' + n))
        # os.rename(os.path.join(fullPath, 'misc', n), (fullPath +'/misc/' +'sub-'+subName+'_ses-' +sessionNum + '_MISC' + checkGz(b)))


# need to run thorugh misc folder and extract t1's when there is no MPRAGE - Need to solve issue with t1 - as adding the names is not validated with BIDS


def fullBids(subNumber, sessionDict, output_dir: str):
    subName = 'sub-' + subNumber
    #  folder_name = ['anat','func','dwi','other']

    for i in sessionDict:
        session = i
        source_dir = sessionDict[i]
        print(session, source_dir)
        fullPath = os.path.join(output_dir, subName, session)
        print(fullPath)
        convert(source_dir, output_dir, subName, session)
        organizeFiles(output_dir, subName, session)

        # print (v)


# %%
def main():
    config_path = 'config.json'
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    sessions = config['sessions']
    subNumber = config["subNumber"]
    root_dir = config['data_root_dir']
    output_dir = config['data_root_dir']
    # glober = root_dir+file_stracture
    ses = {}
    ses[f'sub-{subNumber}'] = {}
    for session in sessions:
        # get all subjects data in a dicionary
        path_to_sub_dir = os.path.join(root_dir,f"sub-{subNumber}")
        path_to_session_dir = os.path.join(path_to_sub_dir,f'ses-{session}')
        path_to_func_dir = os.path.join(path_to_session_dir,f'func')
        # for sub in glob.glob(path_to_func_dir+f'/sub-{subNumber}_ses-{session}*.nii.gz'):
        convert(path_to_func_dir, output_dir, subNumber, str(session))
        # fullBids(subNumber, {},output_dir)


# %%
if __name__ == "__main__":
    main()
