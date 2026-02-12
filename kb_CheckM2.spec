/*
 * Data types and functions for wrapping CheckM2 in KBase.
 *
 * This module exposes a single function, run_checkm2_predict, which
 * runs `checkm2 predict` on a KBase object (BinnedContigs, Genome,
 * GenomeSet, Assembly, AssemblySet) and returns a KBaseReport with
 * the CheckM2 quality_report.tsv attached.
 */

module kb_CheckM2 {

    typedef string workspace_name;
    typedef string data_obj_ref;
    typedef mapping<string, string> string_map;

    /*
     * Parameters for running CheckM2.
     *
     * workspace_name  – KBase workspace to save the report in.
     * input_ref       – Reference to the input object (BinnedContigs,
     *                   Genome, GenomeSet, Assembly, AssemblySet).
     * threads         – Number of CPU threads to use.
     * database_path   – Optional explicit CheckM2 DIAMOND DB path
     *                   (uniref100.KO.1.dmnd). If not provided, CheckM2
     *                   will fall back to CHECKM2DB env variable or its
     *                   default.
     * tmpdir          – Optional tmp directory for CheckM2.
     * extension       – File extension for gzipped bins (if needed).
     * lowmem         – Use CheckM2 --lowmem mode (0/1).
     * use_genes      – If 1, assume input FASTA are predicted genes
     *                  and pass --genes to CheckM2.
     * stdout         – If 1, also print results to stdout.
     * extra_options  – Free-form map for future CLI flags.
     *
     * NOTE: We’re not using @optional tags here; we’ll treat missing
     * JSON fields as “not set” and handle defaults in Python.
     */
    typedef structure {
        workspace_name workspace_name;
        data_obj_ref   input_ref;
        int            threads;
        string         database_path;
        string         tmpdir;
        string         extension;
        int            lowmem;
        int            use_genes;
        int            stdout;
        string_map     extra_options;
    } CheckM2Params;

    /*
     * Output from running CheckM2.
     *
     * report_name      – Name of the KBaseReport object.
     * report_ref       – Workspace reference to the KBaseReport.
     * output_directory – Path on the local filesystem (scratch) where
     *                    CheckM2 output was written.
     */
    typedef structure {
        string report_name;
        string report_ref;
        string output_directory;
    } CheckM2Output;

    /*
     * Run CheckM2 `predict` on the given input object and create a
     * KBaseReport with the quality_report.tsv attached.
     */
    funcdef run_checkm2_predict (CheckM2Params params)
        returns (CheckM2Output)
        authentication required;

};
