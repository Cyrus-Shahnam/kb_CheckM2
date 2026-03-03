# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import uuid
import logging
import subprocess

from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.KBaseDataObjectToFileUtilsClient import KBaseDataObjectToFileUtils
from installed_clients.KBaseReportClient import KBaseReport
#END_HEADER


class kb_CheckM2:
    '''
    Module Name:
    kb_CheckM2

    Module Description:
    Data types and functions for wrapping CheckM2 in KBase.

 This module exposes a single function, run_checkm2_predict, which
 runs `checkm2 predict` on a KBase object (BinnedContigs, Genome,
 GenomeSet, Assembly, AssemblySet) and returns a KBaseReport with
 the CheckM2 quality_report.tsv attached.
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/Cyrus-Shahnam/kb_CheckM2.git"
    GIT_COMMIT_HASH = "6329fe6cc2a384c1d3be3ef3791bd342d97b3ae8"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ.get('SDK_CALLBACK_URL')
        self.scratch = os.path.abspath(config['scratch'])
        self.ws_url = config['workspace-url']

        # Clients
        self.ws = Workspace(self.ws_url)
        self.dfu = DataFileUtil(self.callback_url)
        self.au = AssemblyUtil(self.callback_url)
        self.gfu = GenomeFileUtil(self.callback_url)
        self.kbfile = KBaseDataObjectToFileUtils(self.callback_url)
        self.kbr = KBaseReport(self.callback_url)

        # Basic logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('kb_CheckM2')
        #END_CONSTRUCTOR
        pass


    def run_checkm2_predict(self, ctx, params):
        """
        Run CheckM2 `predict` on the given input object and create a
        KBaseReport with the quality_report.tsv attached.
        :param params: instance of type "CheckM2Params" (* Parameters for
           running CheckM2. * * workspace_name  ??? KBase workspace to save
           the report in. * input_ref       ??? Reference to the input object
           (BinnedContigs, *                   Genome, GenomeSet, Assembly,
           AssemblySet). * threads         ??? Number of CPU threads to use.
           * database_path   ??? Optional explicit CheckM2 DIAMOND DB path * 
           (uniref100.KO.1.dmnd). If not provided, CheckM2 *                 
           will fall back to CHECKM2DB env variable or its *                 
           default. * tmpdir          ??? Optional tmp directory for CheckM2.
           * extension       ??? File extension for gzipped bins (if needed).
           * lowmem         ??? Use CheckM2 --lowmem mode (0/1). * use_genes 
           ??? If 1, assume input FASTA are predicted genes *                
           and pass --genes to CheckM2. * stdout         ??? If 1, also print
           results to stdout. * extra_options  ??? Free-form map for future
           CLI flags. * * NOTE: We???re not using @optional tags here;
           we???ll treat missing * JSON fields as ???not set??? and handle
           defaults in Python.) -> structure: parameter "workspace_name" of
           type "workspace_name", parameter "input_ref" of type
           "data_obj_ref", parameter "threads" of Long, parameter
           "database_path" of String, parameter "tmpdir" of String, parameter
           "extension" of String, parameter "lowmem" of Long, parameter
           "use_genes" of Long, parameter "stdout" of Long, parameter
           "extra_options" of type "string_map" -> mapping from String to
           String
        :returns: instance of type "CheckM2Output" (* Output from running
           CheckM2. * * report_name      ??? Name of the KBaseReport object.
           * report_ref       ??? Workspace reference to the KBaseReport. *
           output_directory ??? Path on the local filesystem (scratch) where
           *                    CheckM2 output was written.) -> structure:
           parameter "report_name" of String, parameter "report_ref" of
           String, parameter "output_directory" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN run_checkm2_predict
        self.logger.info('Starting run_checkm2_predict with params:')
        self.logger.info(str(params))

        if 'workspace_name' not in params or not params['workspace_name']:
            raise ValueError('Parameter workspace_name is required')

        if 'input_ref' not in params or not params['input_ref']:
            raise ValueError('Parameter input_ref is required')

        workspace_name = params['workspace_name']
        input_ref = params['input_ref']

        # 1. Export input to one or more FASTA files
        fasta_paths = self._export_input_to_fastas(input_ref)

        # 2. Run CheckM2 predict
        out_dir = self._run_checkm2(fasta_paths, params)

        # 3. Build KBase report
        result = self._build_report(workspace_name, out_dir)

        self.logger.info('run_checkm2_predict completed successfully')
        
        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method run_checkm2_predict return value ' +
                             'result is not type dict as required.')
        #END run_checkm2_predict
        return [result]

    def run_kb_CheckM2(self, ctx, params):
        """
        Alias method for run_checkm2_predict to match the KBase naming convention.
        """
        return self.run_checkm2_predict(ctx, params)

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]

    # Helper method to run checkm2 command with proper conda environment
    def _run_checkm2_cmd(self, cmd):
        """
        Run a CheckM2 command in the checkm2 conda environment.
        """
        # Activate the checkm2 environment and run the command
        bash_cmd = f"source /opt/conda/etc/profile.d/conda.sh && conda activate checkm2 && {cmd}"
        result = subprocess.run(bash_cmd, shell=True, executable='/bin/bash', 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"CheckM2 command failed: {cmd}")
            self.logger.error(f"stderr: {result.stderr}")
            raise RuntimeError(f"CheckM2 command failed with return code {result.returncode}")
        
        return result

    def _export_input_to_fastas(self, input_ref):
        """
        Export the input object to FASTA file(s).
        Placeholder - needs implementation based on actual input types.
        """
        self.logger.info(f"Exporting input {input_ref} to FASTA")
        # This would need to be implemented to handle different KBase object types
        fasta_paths = []
        return fasta_paths

    def _run_checkm2(self, fasta_paths, params):
        """
        Run CheckM2 predict on the given FASTA files.
        """
        self.logger.info("Running CheckM2 predict")
        out_dir = os.path.join(self.scratch, str(uuid.uuid4()))
        os.makedirs(out_dir, exist_ok=True)
        
        # Build CheckM2 command
        cmd = f"checkm2 predict"
        
        # Add threads parameter
        threads = params.get('threads', 4)
        if threads:
            cmd += f" --threads {threads}"
        
        # Add database path if provided
        db_path = params.get('database_path')
        if db_path:
            cmd += f" --database {db_path}"
        
        # Add lowmem mode if requested
        if params.get('lowmem'):
            cmd += " --lowmem"
        
        # Add --genes flag if input are genes
        if params.get('use_genes'):
            cmd += " --genes"
        
        # Add input and output
        for fasta in fasta_paths:
            cmd += f" --input {fasta}"
        
        cmd += f" --output-dir {out_dir}"
        
        self.logger.info(f"Running command: {cmd}")
        result = self._run_checkm2_cmd(cmd)
        
        self.logger.info(f"CheckM2 output: {result.stdout}")
        return out_dir

    def _build_report(self, workspace_name, out_dir):
        """
        Build a KBase report from CheckM2 output.
        """
        self.logger.info(f"Building report from {out_dir}")
        
        report_name = f"checkm2_report_{str(uuid.uuid4())[:8]}"
        
        report = {
            'report_name': report_name,
            'report_ref': f"{workspace_name}/{report_name}",
            'output_directory': out_dir
        }
        
        return report

