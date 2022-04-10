#!/usr/bin/env bash
# Build and run the CI test
# This is intended to be run in a fresh environment,
# such as a GitHub action, where no prior
# images exist.  If you want to test your CI locally,
# use `runci-local.sh` instead.
set -o errexit
set -o nounset

COMP=${COMPOSE_PATH:-docker-compose}

# First, a syntax, style, and poor usage check
# Nonconforming code will cause a CI fail
#
# Turn off errexit so we can give a better message on fail
set +o errexit
echo
echo "Checking flake8 conformance ..."
flake8 $(cat flake-dirs.txt)

if [[ $? -eq 0 ]]; then
  echo
  echo "Code conforms."
else
  echo
  echo "Code does not conform---CI fails."
  exit 1
fi
set -o errexit

set -o xtrace
# Turn off errexit so we continue even if CI test returns failure
set +o errexit
${COMP} -f compose.yaml up --build --abort-on-container-exit --exit-code-from test
# Return code from 'up' is the test result
trc=$?
# Shutdown and delete all the containers before returning
${COMP} -f compose.yaml down
exit ${trc}
