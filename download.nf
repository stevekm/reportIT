// load the JSON config, if present
params.configFile = "config.json"
import groovy.json.JsonSlurper
def jsonSlurper = new JsonSlurper()
def Config
def configFile_obj = new File("${params.configFile}")
if ( configFile_obj.exists() ) {
    log.info("Loading configs from ${params.configFile}")
    String ConfigJSON = configFile_obj.text
    Config = jsonSlurper.parseText(ConfigJSON)
}

// check for server
// 0. use CLI passed arg
// 1. check for config.json values
// params.server = "198.1.1.168"
def server
if(params.server == null){
    if ( Config && Config.containsKey("server") && Config.server != null ) {
        server = "${Config.server}"
    } else {
        server = "198.1.1.168" // dummy IP address
    }
} else {
    server = "${params.server}"
}

// check for server_login
// 0. use CLI passed arg
// 1. check for config.json values
// params.server_login = "username@198.1.1.168"
def server_login
if(params.server_login == null){
    if ( Config && Config.containsKey("server_login") && Config.server_login != null ) {
        server_login = "${Config.server_login}"
    } else {
        server_login = "username@198.1.1.168" // dummy server login
    }
} else {
    server_login = "${params.server_login}"
}

// check for server_output_dir
// 0. use CLI passed arg
// 1. check for config.json values
// params.server_output_dir = "/results/analysis/output/Home"
def server_output_dir
if(params.server_output_dir == null){
    if ( Config && Config.containsKey("server_output_dir") && Config.server_output_dir != null ) {
        server_output_dir = "${Config.server_output_dir}"
    } else {
        server_output_dir = "/results/analysis/output/Home"
    }
} else {
    server_output_dir = "${params.server_output_dir}"
}

// Ion Torrent run data output directory
params.runDir = "runs"

// find all the locally stored Ion Torrent runs
Channel.fromPath("${params.runDir}/*", type: 'dir').set{ local_runs_ch }
local_runs_ch.map{ path ->
    def basename = path.getName()
    def items = [basename, path]
    return basename
    }
    .collect().toList()
    .set{ all_local_runs }

process check_available_runs {
    // logs into the remote Ion Torrent server and gets a list of all runs available
    executor "local"
    echo true

    input:
    val(x) from Channel.from('')

    output:
    file("${output_txt}") into remote_runs_txt

    script:
    all_runs_txt = "all_runs.txt"
    output_txt = "remote_runs.txt"
    // separates the login banner from the command output
    separator = "xxxSCRIPTSEPARATORxxx"
    """
    # login and get the list of run dirs
    ssh "${server_login}" > "${all_runs_txt}" <<EOF
echo "${separator}"
ls -1 "${server_output_dir}"
EOF

    # find the line with the separator
    num="\$(cat -n "${all_runs_txt}" | grep "${separator}" | cut -f 1 | sed -e 's|^[[:space:]]*\\([[:digit:]]*\\)[[:space:]]*\$|\\1|g')"

    # add one for 'tail'
    num="\$(( \${num} + 1 ))"

    # get all lines following the serparator
    tail -n +\${num} "${all_runs_txt}" > "${output_txt}"
    """
}

// read the list of runs from the file
remote_runs_txt.map{ txt ->
    def runs = txt.readLines()
    return([runs])
}.collect().set{ all_remote_runs }

// find all the remote runs that are not present locally
all_remote_runs.combine(all_local_runs).map { remote_runs_list, local_runs_list ->
    def missing_runs = []
    for (remote_run in remote_runs_list) {
        if ( ! local_runs_list.contains(remote_run) ){
            missing_runs.add(remote_run)
        }
    }
    return(missing_runs)
}.flatten().set { missing_remote_runs }

process validate_remote_run {
    // validate that a remote run is ready for download
    // contains 'status.txt'; only exists if run is complete
    // add other criteria here as needed
    // output an integer status code representing validation; 0 = good, anything else is bad
    executor "local"
    maxForks 1
    echo true
    tag "${runID}"

    input:
    val(runID) from missing_remote_runs

    output:
    set val(runID), file("${status_file_exitcode_txt}") into remote_run_validations

    script:
    remote_run_dir = "${server_output_dir}/${runID}" // /results/analysis/output/Home/Auto_user_SN2-282-IT17-26-1_375_368
    run_status_file = "${remote_run_dir}/status.txt"
    status_file_exitcode_txt = "status_code.txt"
    """
    # check if status file exists
    ssh "${server_login}" > tmp <<'E0F'
ls "${run_status_file}"; echo \$?
E0F
    tail -n1 tmp > "${status_file_exitcode_txt}"
    """
}

// filter out the bad runs that didn't pass validation
valid_remote_runs_validations = Channel.create()
invalid_remote_runs_validations = Channel.create()

remote_run_validations.choice( valid_remote_runs_validations, invalid_remote_runs_validations ) { items ->
    def runID = items[0]
    def status_code_file = items[1]
    def output = 1 // bad by default; good = 0
    // read the exit code from the file; 0 = good
    int status_code = status_code_file.readLines()[0].toInteger()
    if (status_code == 0) output = 0
    return(output)
}

valid_remote_runs_validations.map { runID, status_code_file ->
    return runID
}.set { valid_remote_runs }

invalid_remote_runs_validations.map { runID, status_code_file ->
    int status_code = status_code_file.readLines()[0].toInteger()
    log.warn "Invalid remote run found: ${runID}, status code: ${status_code}"
    return runID
}.set { invalid_remote_runs }

process download_run {
    // download a run from the remote Ion Torrent server
    // only downloads select files; add criteria here
    maxForks 1
    executor "local"
    tag "${runID}"
    storeDir "${params.runDir}"

    input:
    val(runID) from valid_remote_runs

    output:
    file("${runID}")

    script:
    tmp_dir = "tmp"
    tmp_manifest = "tmp.txt"
    output_dir = "${runID}"
    separator = "xxxSCRIPTSEPARATORxxx"
    remote_run_dir = "${server_output_dir}/${runID}"
    file_manifest = "file_manifest.txt"
    """
    # make temp dir to download files to
    mkdir -p "${tmp_dir}"

    # find the bam & bai files
    ssh "${server_login}" > "${tmp_manifest}" <<E0F
echo "${separator}"

# find coverage .bam and .bai
find "${remote_run_dir}"/plugin_out -path "*/coverageAnalysis_out*" -name "*.bam" -o -name "*.bai" -type l | \
grep -v 'link.bam' | \
grep -v 'rawlib' | \
grep -v 'variantCaller'

# find .vcfs
find "${remote_run_dir}"/plugin_out -path "*/variantCaller*" -name "TSVC_variants.vcf"

# find .bam files for .vcfs
find "${remote_run_dir}"/plugin_out -path "*/variantCaller*" -name "*_processed.bam*"

# find other files
find "${remote_run_dir}" -name "report.pdf"
find "${remote_run_dir}" -name "*bcmatrix.xls" ! -name "link.bcmatrix.xls"
find "${remote_run_dir}" -name "*.xls" -path "*/variantCaller_out*/*"
find "${remote_run_dir}" -name "ion_params*.json"

E0F

    # get all the file lines
    # find the line with the separator
    num="\$(cat -n "${tmp_manifest}" | grep "${separator}" | cut -f 1 | sed -e 's|^[[:space:]]*\\([[:digit:]]*\\)[[:space:]]*\$|\\1|g')"

    # add one for 'tail'
    num="\$(( \${num} + 1 ))"

    # get all lines following the serparator
    tail -n +\${num} "${tmp_manifest}" | \
    sed -e 's|^${remote_run_dir}/||g' \
    > "${file_manifest}"

    # download the files from the manifest
    rsync -avhR --chmod=o-rw --copy-links --files-from="${file_manifest}" -e "ssh" "${server_login}":"${remote_run_dir}/" "${tmp_dir}/"

    # check that .bam files and .vcf files were downloaded
    num_bams="\$(find "${tmp_dir}" -path "*/variantCaller_out*" -name "*.bam" | wc -l)"
    num_vcfs="\$(find "${tmp_dir}" -path "*/variantCaller_out*" -name "TSVC_variants.vcf" | wc -l)"
    num_bais="\$(find "${tmp_dir}" -path "*/variantCaller_out*" -name "*.bam.bai" | wc -l)"

    [ "\${num_bams}" -ge 1 ] && : || { echo "ERROR: .bam files not found"; exit 1;}
    [ "\${num_bais}" -ge 1 ] && : || { echo "ERROR: .bai files not found"; exit 1;}
    [ "\${num_vcfs}" -ge 1 ] && : || { echo "ERROR: .vcf files not found"; exit 1;}

    # assume all checks passed sucessfully..
    mv "${tmp_dir}" "${runID}"
    """
}
