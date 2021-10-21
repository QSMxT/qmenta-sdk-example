import matplotlib

# This backend config avoids $DISPLAY errors in headless machines
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pdfkit
import subprocess
from subprocess import call
from time import gmtime, strftime
from tornado import template
import glob


# AnalysisContext documentation: https://docs.qmenta.com/sdk/sdk.html
def run(context):
    
    # Get the analysis information dictionary (patient id, analysis name...)
    analysis_data = context.fetch_analysis_data()

    # Get the analysis settings (histogram range of intensities)
    settings = analysis_data['settings']

    context.set_progress(message='This is container 20211021')

    file_handler_0 = context.get_files('input_0')[0]
    path_0 = file_handler_0.download(f'/root/input_0/') 

    file_handler_1 = context.get_files('input_1')[0]
    path_1 = file_handler_1.download(f'/root/input_1/')


    context.set_progress(message='Sorting DICOM data...')
    call([
    "python3",
    "/opt/QSMxT/run_0_dicomSort.py",
    "/root/", 
    "/00_dicom"
    ])

    ima_files = glob.glob("/00_dicom/**/*.IMA", recursive=True)
    context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after Sorting DICOM data in /00_dicom')


    context.set_progress(message='Converting DICOM data...')
    try:
        retcode = call([
            "python3",
            "/opt/QSMxT/run_1_dicomToBids.py",
            "/00_dicom/", 
            "/01_bids"
            ])
        if retcode < 0:
            context.set_progress(message="Converting DICOM data was terminated by signal" + str(retcode))
        else:
            context.set_progress(message="Converting DICOM data returned " + str(retcode))
    except OSError as e:
       context.set_progress(message="Converting DICOM data failed:" + e)

    nii_files = glob.glob("/01_bids/**/*.nii.gz", recursive=True)
    context.set_progress(message='found ' + str(len(nii_files)) + ' nii_files after Converting DICOM data in /01_bids')


    qsm_iterations = int(settings['qsm_iterations'])
    context.set_progress(message='Run QSM pipeline ...')
    
    CompletedProcess = subprocess.run([
        "python3",
        "/opt/QSMxT/run_2_qsm.py",
        "--qsm_iterations",
        str(qsm_iterations),
        "--two_pass",
        "/01_bids", 
        "/02_qsm_output"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    context.set_progress(message='QSM pipeline stdout: ' + CompletedProcess.stdout)
    context.set_progress(message='QSM pipeline stderr: ' + CompletedProcess.stderr)

    output_file = glob.glob("/02_qsm_output/qsm_final/_run_run-1/*.nii")
    context.set_progress(message='outputfile is ... ' + output_file[0])

    # Upload the results
    context.set_progress(message='Uploading results...')

    context.upload_file(output_file[0], 'final.nii')
