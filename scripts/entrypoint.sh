#!/bin/bash

if [ -f /kb/deployment/user-env.sh ]; then
    . /kb/deployment/user-env.sh
fi

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
    export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
    sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
    echo "Run Tests"
    make test
elif [ "${1}" = "async" ] ; then
    sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
    echo "Initializing CheckM2 reference data..."
    mkdir -p /data/checkm2_db
    /opt/conda/envs/checkm2/bin/checkm2 database --download --path /data/checkm2_db

    # Find the actual dmnd file location (path may vary by CheckM2 version)
    DMND_FILE=$(find /data/checkm2_db -name "*.dmnd" | head -1)

    if [ -n "$DMND_FILE" ]; then
        echo "CheckM2 database found at: $DMND_FILE"
        touch /data/__READY__
        echo "CheckM2 database initialized successfully"
    else
        echo "ERROR: No .dmnd file found under /data/checkm2_db"
        find /data/checkm2_db -type f
        exit 1
    fi
elif [ "${1}" = "bash" ] ; then
    bash
elif [ "${1}" = "report" ] ; then
    export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
    make compile
else
    echo "Unknown command: ${1}"
fi
