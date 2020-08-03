#!/bin/bash
set -e

ST2_EXEC_ID=$1
ST2_REPO=$2
ST2_LOG_DIR=$3
BACKUP_DIR=$4

# Cleanup anything from the backup directory older than a week
find ${BACKUP_DIR}/* -type d -ctime +7 | xargs rm -rf

# Create a new directory for this execution
BACKUP_PATH=${BACKUP_DIR}/${ST2_EXEC_ID}
if [[ ! -d "${BACKUP_PATH}" ]]; then
    mkdir -p ${BACKUP_PATH}
fi

# Backup st2 logs
if [[ -d "${ST2_LOG_DIR}" ]]; then
    echo "Backing up st2 logs..."
    cp ${ST2_LOG_DIR}/*.log ${BACKUP_PATH}
fi

# Stop services to clear locks so the backup steps below can run.
${ST2_REPO}/tools/launchdev.sh stop
sleep 3
