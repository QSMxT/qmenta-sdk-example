#!/usr/bin/env python

import os
import glob
import subprocess

def sys_cmd(cmd, print_output=True, print_command=True):
    if print_command:
        print(cmd)
    
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = process.returncode
    std_out = process.stdout.decode('UTF-8')[:-1]
    std_err = process.stderr.decode('UTF-8')[:-1]
    
    if print_output:
        print(std_out, end="")
    
    return std_out, std_err, exit_code

def run(context):
    """
    Function invoked by the SDK that passes a context object. This object can then be used
    to communicate with the platform in the context of that particular analysis to fetch files,
    report progress, and upload results, among others.

    Parameters
    ----------
    context : qmenta.sdk.context.AnalysisContext
        Analysis context object to communicate with the QMENTA Platform.
    """
    
    # Define directories for the input and output files inside the container
    context.set_progress(value=0, message="Finding input directories...")
    input_dir = os.path.join(os.path.expanduser("~"), "local_exec_input")
    output_dir = os.path.join(os.path.expanduser("~"), "local_exec_output")
    work_dir = os.path.join(os.path.expanduser("~"), "local_exec_resources")

    # Retrieve settings
    settings = context.get_settings()
    premade = settings.get('premade')

    with open(os.path.join(work_dir, "qsm", "full_output.log"), 'w') as outfile:
        try:
            # QMENTA: Prepare input files
            context.set_progress(value=0, message="Preparing input files...")
            for f in context.get_files("dicoms"): f.download(input_dir)

            # QSMxT: Sort DICOMS
            context.set_progress(value=1, message="Sorting DICOMs...")
            std_out, std_err, exit_code = sys_cmd(f"run_0_dicomSort.py {input_dir} {os.path.join(work_dir, 'dicoms-sorted')}")
            outfile.write(std_out)
            if exit_code != 0:
                outfile.write(std_err)
                raise RuntimeError(f"Error {exit_code} while sorting DICOMS!")
            
            # QSMxT: Convert to BIDS
            context.set_progress(value=5, message="Converting to BIDS...")
            std_out, std_err, exit_code = sys_cmd(f"run_1_dicomConvert.py {os.path.join(work_dir, 'dicoms-sorted')} {os.path.join(work_dir, 'bids')} --auto_yes")
            outfile.write(std_out)
            if exit_code != 0:
                outfile.write(std_err)
                raise RuntimeError(f"Error {exit_code} while sorting DICOMS!")

            # QSMxT: QSM pipeline
            context.set_progress(value=10, message="Running QSM pipeline...")
            std_out, std_err, exit_code = sys_cmd(f"run_2_qsm.py {os.path.join(work_dir, 'bids')} {os.path.join(work_dir, 'qsm')} --premade {premade} --auto_yes")
            outfile.write(std_out)
            if exit_code != 0:
                outfile.write(std_err)
                raise RuntimeError(f"Error {exit_code} while sorting DICOMS!")

            # QMENTA: Upload results
            context.set_progress(value=95, message="Uploading results")
            qsm_files = glob.glob(os.path.join(work_dir, "qsm", "qsm_final", "*", "*"))
            for qsm_file in qsm_files:
                context.upload_file(qsm_file, os.path.split(qsm_file)[1], modality="QSM")
            for f in glob.glob(os.path.join(work_dir, 'qsm', '*.*')):
                context.upload_file(f, os.path.split(f)[1])
        except Exception as e:
            context.set_progress(value=0, message=str(e))
            outfile.write(str(e))
            raise e


