#! /usr/bin/env bash

echo "🔥🔥🔥🔥🔥Running security check🔥🔥🔥🔥🔥🔥"
mkdir -p $GITHUB_WORKSPACE/output
touch $GITHUB_WORKSPACE/output/security_report.txt

if [[ -f "${INPUT_CONFIG_FILE}" ]]; then
    echo "Using config file: ${INPUT_CONFIG_FILE}"
    BANDIT_CONFIG="-c ${INPUT_CONFIG_FILE}"
elif [[ -n "${INPUT_EXCLUDE_PATHS}" ]]; then
    echo "Using exclude path(s): ${INPUT_EXCLUDE_PATHS}"
    BANDIT_CONFIG="${BANDIT_CONFIG} -x ${INPUT_EXCLUDE_PATHS}"
fi

if [[ -n "${BANDIT_CONFIG}" ]]; then
    echo "Running bandit with extra args: ${BANDIT_CONFIG}"
fi

echo "Running bandit with: " ${BANDIT_CONFIG} -r "${INPUT_PROJECT_PATH}" -o "${GITHUB_WORKSPACE}/output/security_report.txt" -f 'txt'
bandit ${BANDIT_CONFIG} -r "${INPUT_PROJECT_PATH}" -o "${GITHUB_WORKSPACE}/output/security_report.txt" -f 'txt'
BANDIT_STATUS="$?"

GITHUB_TOKEN=$INPUT_REPO_TOKEN python /main.py $BANDIT_CONFIG -r $INPUT_PROJECT_PATH

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
