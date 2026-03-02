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
    GIT_COMMIT_HASH = "ef7fa8af8334641f0517b1865cde3c116f68abb8"

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
        return [result]
        #END run_checkm2_predict

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method run_checkm2_predict return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
