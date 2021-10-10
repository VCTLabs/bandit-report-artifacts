#!/bin/sh -l

echo "🔥🔥🔥🔥🔥Running security check🔥🔥🔥🔥🔥🔥"
mkdir -p $GITHUB_WORKSPACE/output
touch $GITHUB_WORKSPACE/output/security_report.txt

if [ -f "${INPUT_CONFIG_FILE}" ]; then
    echo "Using config file: ${INPUT_CONFIG_FILE}"
    BANDIT_CONFIG="-c ${INPUT_CONFIG_FILE}"
elif [ -f "${INPUT_BASELINE_FILE}" ]; then
    echo "Using baseline file: ${INPUT_BASELINE_FILE}"
    BANDIT_CONFIG="-b ${INPUT_BASELINE_FILE}"
fi

bandit ${BANDIT_CONFIG} -r "${INPUT_PROJECT_PATH}" -o "${GITHUB_WORKSPACE}/output/security_report.txt" -f 'txt'
BANDIT_STATUS="$?"

GITHUB_TOKEN=$INPUT_REPO_TOKEN python /main.py -r $INPUT_PROJECT_PATH

if [ $BANDIT_STATUS -eq 0 ]; then
    echo "🔥🔥🔥🔥Security check passed🔥🔥🔥🔥"
    exit 0
fi

echo "🔥🔥🔥🔥Security check failed🔥🔥🔥🔥"
cat $GITHUB_WORKSPACE/output/security_report.txt
if $INPUT_IGNORE_FAILURE; then
    exit 0
fi

exit $BANDIT_STATUS
