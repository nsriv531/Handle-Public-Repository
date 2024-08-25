#!/bin/bash

ENV="${DEPLOY_ENV:-prod}"
PYTHONPATH=${PYTHONPATH}:/:/src/

echo "Environment: ${ENV}"
echo "User: $(whoami)"
echo "PATH: ${PATH}"
echo "PYTHONPATH: ${PYTHONPATH}"
echo "DEBUG: ${DEBUG}"

python manage.py rqworker default
#rq worker-pool high default low -n 3
#https://python-rq.org/docs/workers/
