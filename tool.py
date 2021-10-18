import matplotlib

# This backend config avoids $DISPLAY errors in headless machines
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pdfkit
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

    # Get the data from the input files
    # context.set_progress(message='found ' + str(len(context.get_files('input'))) + ' input files')

    # for file_handler in context.get_files('input'):
    #     path = file_handler.download('/root/input/')  # Download and automatically unpack  

    context.set_progress(message='This is container 20211019')

    file_handler_0 = context.get_files('input_0')[0]
    path_0 = file_handler_0.download(f'/root/input_0/') # Download and automatically unpack 
    ima_files = glob.glob(f'/root/input_0/*/*.IMA') # two folders, should be 160 .IMA in each  
    context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after unpacking in sub-path')
    context.set_progress(message='path is '+str(path_0))
    ima_files = glob.glob(f'/root/input_0/*.IMA') # two folders, should be 160 .IMA in each  
    context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after unpacking in path')
    context.set_progress(message='path is '+str(path_0))

    file_handler_1 = context.get_files('input_1')[0]
    path_1 = file_handler_1.download(f'/root/input_1/') # Download and automatically unpack 
    ima_files = glob.glob(f'/root/input_1/*/*.IMA') # two folders, should be 160 .IMA in each  
    context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after unpacking in sub-path')
    context.set_progress(message='path is '+str(path_1))
    ima_files = glob.glob(f'/root/input_1/*.IMA') # two folders, should be 160 .IMA in each  
    context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after unpacking in path')
    context.set_progress(message='path is '+str(path_1))


    # for count, file_handler in enumerate(context.get_files('input')):
    #     path = file_handler.download(f'/root/input_{count}/') # Download and automatically unpack 
    #     ima_files = glob.glob(f'/root/input_{count}/.IMA') # two folders, should be 160 .IMA in each  
    #     context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after unpacking in path')
    #     context.set_progress(message='path is '+str(path))

    #     if len(ima_files) == 0:
    #         zip_files = glob.glob(path+"/*.zip")
    #         context.set_progress(message='found ' + str(len(zip_files)) + ' archives in download path')
    #         for file in zip_files:
    #             context.set_progress(message='unpacking '+str(file))
    #             call(["unzip", '-d', path, file])
    #         ima_files = glob.glob(path+"/*/*.IMA")
    #         context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after unpacking')

    # context.set_progress(message='Sorting mag DICOM data...')
    # call([
    # "python3",
    # "/opt/QSMxT/run_0_dicomSort.py",
    # "/root/input_0/", 
    # "/00_dicom"
    # ])
    # context.set_progress(message='Sorting phase DICOM data...')
    # call([
    # "python3",
    # "/opt/QSMxT/run_0_dicomSort.py",
    # "/root/input_1/", 
    # "/00_dicom"
    # ])
    context.set_progress(message='Sorting DICOM data...')
    call([
    "python3",
    "/opt/QSMxT/run_0_dicomSort.py",
    "/root/", 
    "/00_dicom"
    ])


    # zip_files = glob.glob(path+"/*.zip")
    # ima_files = glob.glob(path+"/*.IMA")

    # context.set_progress(message='found ' + str(len(zip_files)) + ' archives in download path')
    # context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files before unpacking in path')
    # for file in zip_files:
    #     context.set_progress(message='unpacking '+str(file))
    #     call(["unzip", '-d', path, file])


    # ima_files = glob.glob(path+"/*.IMA")
    # context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after unpacking')


    # context.set_progress(message='Sorting DICOM data...')
    # call([
    # "python3",
    # "/opt/QSMxT/run_0_dicomSort.py",
    # path, 
    # "/00_dicom"
    # ])


    context.set_progress(message='Converting DICOM data...')
    call([
    "python3",
    "/opt/QSMxT/run_1_dicomToBids.py",
    "/00_dicom", 
    "/01_bids"
    ])

    qsm_iterations = settings['qsm_iterations']
    context.set_progress(message='Run QSM pipeline ...')
    call([
    "python3",
    "/opt/QSMxT/run_2_qsm.py",
    "--qsm_iterations",
    str(qsm_iterations),
    "--two_pass",
    "/01_bids", 
    "/02_qsm_output"
    ])

    output_file = glob.glob("/02_qsm_output/qsm_final/_run_run-1/*.nii")


    # Generate an example report
    # Since it is a head-less machine, it requires Xvfb to generate the pdf
    context.set_progress(message='Creating report...')

    report_path = '/root/report.pdf'

    data_report = {
        'logo_main': '/root/qmenta_logo.png',
        'ss': analysis_data['patient_secret_name'],
        'ssid': analysis_data['ssid'],
        'this_moment': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
        'version': 1.0
    }

    loader = template.Loader('/root/')
    report_contents = loader.load('report_template.html').generate(data_report=data_report)

    if isinstance(report_contents, bytes):
        report_contents = report_contents.decode("utf-8")
    pdfkit.from_string(report_contents, report_path)

    # Upload the data and the report
    context.set_progress(message='Uploading results...')

    context.upload_file(report_path, 'report.pdf')
    context.upload_file(output_file[0], 'final.nii')
